"""AINav Job C admit plane: dual seats, single-use consume, fail-closed effect.

Canonical caller shape::

    from agent_gov import admit, ConsumeLedger, default_lockfile, EffectLedger

    rec = admit(action, default_lockfile(), ledger=ConsumeLedger(),
                seat_a="oid-1", seat_b="oid-2")
    EffectLedger().effect(rec["request_id"], rec["action_hash"])

SoR writes are allowed only after ``admit`` returns and ``effect`` succeeds.
Everything else raises. Lockfiles cannot weaken those invariants.
"""

from agent_gov.admit import admit, run_and_apply
from agent_gov.consume import ConsumeLedger
from agent_gov.effect import EffectLedger
from agent_gov.errors import (
    AdmitDenied,
    AgentGovError,
    ConsumeReplay,
    EffectBlocked,
    LockfileError,
)
from agent_gov.hashing import action_hash
from agent_gov.lockfile import Lockfile, default_lockfile, load_lockfile
from agent_gov.lua_simulator import LuaSimulator
from agent_gov.store import MemoryAuthorityStore, default_store, reset_default_store

__version__ = "2.1.0"

__all__ = [
    "AdmitDenied",
    "AgentGovError",
    "ConsumeLedger",
    "ConsumeReplay",
    "EffectBlocked",
    "EffectLedger",
    "Lockfile",
    "LockfileError",
    "LuaSimulator",
    "MemoryAuthorityStore",
    "action_hash",
    "admit",
    "default_lockfile",
    "default_store",
    "load_lockfile",
    "reset_default_store",
    "run_and_apply",
    "__version__",
]
