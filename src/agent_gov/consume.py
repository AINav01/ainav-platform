"""Single-use consume ledger. Second consume of the same slot is an error."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agent_gov.errors import ConsumeReplay
from agent_gov.lua_simulator import ERR, OK, LuaSimulator, dual_consume
from agent_gov.store import AuthorityStore, default_store


class ConsumeLedger:
    """Atomic single-use consume of a dual-admit slot.

    Default construction shares the process-wide authority store so a later
    ``EffectLedger()`` can resolve the grant without being passed the ledger.
    """

    def __init__(
        self,
        store: AuthorityStore | None = None,
        *,
        simulator: LuaSimulator | None = None,
        redis: Any | None = None,
    ) -> None:
        self.store = store or default_store()
        self.simulator = simulator
        self.redis = redis

    def consume(self, slot_key: str, record: Mapping[str, Any]) -> dict[str, Any]:
        if not slot_key:
            raise ConsumeReplay("slot_key is required", reason_code="SLOT_MISSING")
        external_ok = False
        try:
            if self.redis is not None:
                argv = [
                    str(record.get("request_id", "")),
                    str(record.get("action_hash", "")),
                    str(record.get("seat_a", "")),
                    str(record.get("seat_b", "")),
                    str(record.get("consumed_at", "")),
                ]
                result = self.redis.eval([slot_key], argv)
                if result == ERR:
                    raise ConsumeReplay(
                        f"slot already consumed: {slot_key}",
                        reason_code="CONSUME_REPLAY",
                    )
                if result != OK:
                    raise ConsumeReplay(
                        f"redis consume returned {result!r}",
                        reason_code="CONSUME_LUA_ERR",
                    )
                external_ok = True
            elif self.simulator is not None:
                result = dual_consume(self.simulator, [slot_key], record)
                if result == ERR:
                    raise ConsumeReplay(
                        f"slot already consumed: {slot_key}",
                        reason_code="CONSUME_REPLAY",
                    )
                if result != OK:
                    raise ConsumeReplay(
                        f"consume simulator returned {result!r}",
                        reason_code="CONSUME_LUA_ERR",
                    )
                external_ok = True
            return self.store.try_consume(slot_key, record)
        except ConsumeReplay:
            raise
        except Exception:
            if external_ok:
                self._rollback_external(slot_key)
            raise

    def _rollback_external(self, slot_key: str) -> None:
        if self.simulator is not None:
            self.simulator.delete(slot_key)
            return
        if self.redis is not None:
            deleter = getattr(self.redis, "delete", None)
            if callable(deleter):
                deleter(slot_key)
