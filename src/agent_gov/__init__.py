"""AINav Job C admit plane: dual seats, single-use consume, fail-closed effect.

Canonical caller shape::

    from agent_gov import admit, ConsumeLedger, default_lockfile, EffectLedger

    rec = admit(action, default_lockfile(), ledger=ConsumeLedger(),
                seat_a="oid-1", seat_b="oid-2")
    EffectLedger().effect(rec["request_id"], rec["action_hash"])

SoR writes are allowed only after ``admit`` returns and ``effect`` succeeds.
Everything else raises. Lockfiles cannot weaken those invariants.
Sealed DecisionRecords are immutable.
"""

from agent_gov.action import Action
from agent_gov.admit import admit, run_and_apply
from agent_gov.client import AdmitClient, DualSession
from agent_gov.consume import ConsumeLedger
from agent_gov.effect import EffectLedger
from agent_gov.errors import (
    AdmitDenied,
    AgentGovError,
    ConsumeReplay,
    EffectBlocked,
    IntegrityError,
    LockfileError,
)
from agent_gov.export import export_envelope, verify_export
from agent_gov.grant import grant_id
from agent_gov.merkle import merkle_root, prove_record, verify_inclusion
from agent_gov.hashing import action_hash
from agent_gov.lockfile import Lockfile, default_lockfile, load_lockfile
from agent_gov.lua_simulator import LuaSimulator
from agent_gov.records import DecisionRecord, verify_chain, verify_record
from agent_gov.redis_consume import RedisDualConsume, SimulatorRedis
from agent_gov.store import (
    FileAuthorityStore,
    MemoryAuthorityStore,
    default_store,
    reset_default_store,
)

__version__ = "2.5.0"

__all__ = [
    "Action",
    "AdmitClient",
    "AdmitDenied",
    "AgentGovError",
    "ConsumeLedger",
    "ConsumeReplay",
    "DecisionRecord",
    "DualSession",
    "EffectBlocked",
    "EffectLedger",
    "FileAuthorityStore",
    "IntegrityError",
    "Lockfile",
    "LockfileError",
    "LuaSimulator",
    "MemoryAuthorityStore",
    "RedisDualConsume",
    "SimulatorRedis",
    "action_hash",
    "admit",
    "default_lockfile",
    "default_store",
    "export_envelope",
    "grant_id",
    "load_lockfile",
    "merkle_root",
    "prove_record",
    "reset_default_store",
    "run_and_apply",
    "verify_chain",
    "verify_export",
    "verify_inclusion",
    "verify_record",
    "__version__",
]
