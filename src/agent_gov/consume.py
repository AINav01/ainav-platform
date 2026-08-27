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
    ) -> None:
        self.store = store or default_store()
        self.simulator = simulator

    def consume(self, slot_key: str, record: Mapping[str, Any]) -> dict[str, Any]:
        if not slot_key:
            raise ConsumeReplay("slot_key is required", reason_code="SLOT_MISSING")
        if self.simulator is not None:
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
        return self.store.try_consume(slot_key, record)
