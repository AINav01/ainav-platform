"""Effect gate. Privileged SoR writes happen only after admit ok."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agent_gov.errors import EffectBlocked
from agent_gov.records import decision_record, utc_now
from agent_gov.store import AuthorityStore, default_store

ApplyFn = Callable[[dict[str, Any]], Any]


class EffectLedger:
    """Bind an effect to an admitted (request_id, action_hash) pair.

    Default construction shares the process-wide authority store used by
    ``ConsumeLedger()``, which is why this works::

        rec = admit(action, default_lockfile(), ledger=ConsumeLedger(),
                    seat_a="oid-1", seat_b="oid-2")
        EffectLedger().effect(rec["request_id"], rec["action_hash"])
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
        # Peek before mutate so a failing apply cannot consume the effect slot
        # after a blocked gate, and so we can attach a DecisionRecord.
        try:
            applied = self.store.try_effect(request_id, action_hash)
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

        if apply is not None:
            try:
                apply_result = apply(dict(admit) if admit else dict(applied))
            except Exception as exc:
                # Apply failed after the gate reserved the effect. Fail-closed:
                # do not pretend SoR succeeded. The effect slot stays consumed
                # so a retry cannot double-write; caller must reconcile.
                raise EffectBlocked(
                    f"SoR apply failed after admit: {exc}",
                    reason_code="EFFECT_APPLY_FAILED",
                ) from exc
            applied["apply_result"] = apply_result

        applied["effected_at"] = utc_now()
        if admit is not None:
            applied["record_id"] = admit.get("record_id")
            applied["policy_id"] = admit.get("policy_id")
        applied.setdefault("record_type", "effect_applied")
        return applied
