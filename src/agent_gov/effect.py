"""Effect gate. Privileged SoR writes happen only after admit ok."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from agent_gov.clock import utc_now
from agent_gov.errors import EffectBlocked
from agent_gov.records import decision_record
from agent_gov.store import AuthorityStore, default_store

ApplyFn = Callable[[dict[str, Any]], Any]


def _parse_created(ts: str) -> datetime:
    raw = str(ts or "").replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise EffectBlocked("admit created_at is not parseable", reason_code="EFFECT_GRANT_TIME") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


class EffectLedger:
    """Bind an effect to an admitted (request_id, action_hash) pair.

    Default construction shares the process-wide authority store used by
    ``ConsumeLedger()``, which is why this works::

        rec = admit(action, default_lockfile(), ledger=ConsumeLedger(),
                    seat_a="oid-1", seat_b="oid-2")
        EffectLedger().effect(rec["request_id"], rec["action_hash"])

    Lifecycle is reserve → apply → finalize. A failed SoR apply records
    ``effect_apply_failed`` (not ``effect_applied``) and consumes the slot
    so a retry cannot double-write.

    An orphan ``effect_reserved`` (crash before finalize) is fail-closed when
    an apply callback is present — retrying apply could double-write. Use
    ``abort_effect`` for ops recovery. A reserved grant with no apply can
    finalize as applied (no SoR side effect).
    """

    def __init__(
        self,
        store: AuthorityStore | None = None,
        *,
        grant_ttl_seconds: int | None = None,
    ) -> None:
        self.store = store or default_store()
        self.grant_ttl_seconds = grant_ttl_seconds

    def effect(
        self,
        request_id: str,
        action_hash: str,
        *,
        apply: ApplyFn | None = None,
        recover: bool = False,
        grant_ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        if not request_id or not isinstance(request_id, str):
            raise EffectBlocked("request_id is required", reason_code="EFFECT_NO_REQUEST")
        if not action_hash or not isinstance(action_hash, str):
            raise EffectBlocked("action_hash is required", reason_code="EFFECT_NO_HASH")

        admit = self.store.get_admit(request_id)
        ttl = self.grant_ttl_seconds if grant_ttl_seconds is None else grant_ttl_seconds
        if ttl is not None:
            if not admit:
                raise EffectBlocked("grant TTL requires an admit", reason_code="EFFECT_NO_ADMIT")
            created = _parse_created(str(admit.get("created_at") or ""))
            now = _parse_created(utc_now())
            if (now - created).total_seconds() > int(ttl):
                self._record_blocked(request_id, action_hash, admit, "EFFECT_GRANT_EXPIRED")
                raise EffectBlocked(
                    "admit grant expired before effect",
                    reason_code="EFFECT_GRANT_EXPIRED",
                )
        if recover:
            existing = self.store.get_effect(request_id)
            if existing and existing.get("record_type") == "effect_reserved":
                if apply is not None:
                    self._record_blocked(
                        request_id,
                        action_hash,
                        admit,
                        "EFFECT_RESERVED_ORPHAN",
                    )
                    raise EffectBlocked(
                        "reserved effect cannot retry SoR apply; abort first",
                        reason_code="EFFECT_RESERVED_ORPHAN",
                    )
                return self.store.finalize_effect(
                    request_id,
                    action_hash,
                    record_type="effect_applied",
                )
            raise EffectBlocked(
                f"no reserved effect to recover for request_id={request_id}",
                reason_code="EFFECT_NOT_RESERVED",
            )

        try:
            reserved = self.store.reserve_effect(request_id, action_hash)
        except EffectBlocked as exc:
            self._record_blocked(request_id, action_hash, admit, exc.reason_code)
            raise

        apply_result: Any = None
        if apply is not None:
            try:
                apply_result = apply(dict(admit) if admit else dict(reserved))
            except Exception as exc:
                self.store.finalize_effect(
                    request_id,
                    action_hash,
                    record_type="effect_apply_failed",
                )
                raise EffectBlocked(
                    f"SoR apply failed after admit: {exc}",
                    reason_code="EFFECT_APPLY_FAILED",
                ) from exc

        return self.store.finalize_effect(
            request_id,
            action_hash,
            record_type="effect_applied",
            apply_result=apply_result,
        )

    def abort_effect(self, request_id: str, action_hash: str) -> dict[str, Any]:
        """Finalize a reserved effect as failed. Ops recovery, not a live pin."""
        current = self.store.get_effect(request_id)
        if current is None or current.get("record_type") != "effect_reserved":
            raise EffectBlocked(
                f"effect is not reserved for request_id={request_id}",
                reason_code="EFFECT_NOT_RESERVED",
            )
        return self.store.finalize_effect(
            request_id,
            action_hash,
            record_type="effect_apply_failed",
            apply_result={"aborted": True},
        )

    def _record_blocked(
        self,
        request_id: str,
        action_hash: str,
        admit: dict[str, Any] | None,
        reason_code: str,
    ) -> None:
        proposal = (admit or {}).get("proposal") or {}
        blocked = decision_record(
            record_type="effect_blocked",
            request_id=request_id,
            action_hash=action_hash,
            action=proposal,
            seat_a=(admit or {}).get("seat_a"),
            seat_b=(admit or {}).get("seat_b"),
            policy_id=(admit or {}).get("policy_id"),
            reason_code=reason_code,
        )
        self.store.put_denied(blocked)
