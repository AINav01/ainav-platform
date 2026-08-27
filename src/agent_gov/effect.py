"""Effect gate. Privileged SoR writes happen only after admit ok."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agent_gov.errors import EffectBlocked
from agent_gov.records import decision_record
from agent_gov.store import AuthorityStore, default_store

ApplyFn = Callable[[dict[str, Any]], Any]


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
    """

    def __init__(self, store: AuthorityStore | None = None) -> None:
        self.store = store or default_store()

    def effect(
        self,
        request_id: str,
        action_hash: str,
        *,
        apply: ApplyFn | None = None,
    ) -> dict[str, Any]:
        if not request_id or not isinstance(request_id, str):
            raise EffectBlocked("request_id is required", reason_code="EFFECT_NO_REQUEST")
        if not action_hash or not isinstance(action_hash, str):
            raise EffectBlocked("action_hash is required", reason_code="EFFECT_NO_HASH")

        admit = self.store.get_admit(request_id)
        try:
            reserved = self.store.reserve_effect(request_id, action_hash)
        except EffectBlocked as exc:
            if admit is not None:
                blocked = decision_record(
                    record_type="effect_blocked",
                    request_id=request_id,
                    action_hash=action_hash,
                    action=(admit.get("proposal") or {}),
                    seat_a=admit.get("seat_a"),
                    seat_b=admit.get("seat_b"),
                    policy_id=admit.get("policy_id"),
                    reason_code=exc.reason_code,
                )
                self.store.put_denied(blocked)
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
