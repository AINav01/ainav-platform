from __future__ import annotations

import pytest

from agent_gov import (
    AdmitDenied,
    ConsumeLedger,
    EffectBlocked,
    EffectLedger,
    LockfileError,
    LuaSimulator,
    MemoryAuthorityStore,
    action_hash,
    admit,
    default_lockfile,
    default_store,
    load_lockfile,
)
from agent_gov.hashing import normalize_action
from agent_gov.lockfile import Lockfile, _as_bool
from agent_gov.lua_simulator import ERR
from agent_gov.records import decision_record
from agent_gov.store import reset_default_store

from tests.helpers import sample_action


class _Canon:
    def to_canonical(self):
        return sample_action(proposal_id="from-obj")


class _BadCanon:
    def to_canonical(self):
        return "not-a-mapping"


def test_action_to_canonical_object():
    digest = action_hash(_Canon())
    assert digest == action_hash(sample_action(proposal_id="from-obj"))
    assert normalize_action(_Canon())["proposal_id"] == "from-obj"


def test_action_to_canonical_must_return_mapping():
    with pytest.raises(AdmitDenied):
        action_hash(_BadCanon())


def test_load_lockfile_rejects_non_mapping():
    with pytest.raises(LockfileError):
        load_lockfile("nope")  # type: ignore[arg-type]


def test_load_lockfile_rejects_bad_invariants_type():
    doc = default_lockfile().to_canonical()
    doc["invariants"] = "nope"
    with pytest.raises(LockfileError):
        load_lockfile(doc)


def test_lockfile_missing_invariant():
    lock = Lockfile(invariants={"fail_closed": True, "single_use_consume": True})
    with pytest.raises(LockfileError) as exc:
        lock.verify()
    assert exc.value.reason_code == "LOCKFILE_INVARIANT"


def test_lockfile_schema_and_slot_key():
    lock = Lockfile(schema_version="v0")
    with pytest.raises(LockfileError) as exc:
        lock.verify()
    assert exc.value.reason_code == "LOCKFILE_SCHEMA"
    with pytest.raises(LockfileError):
        default_lockfile().slot_key("")
    with pytest.raises(LockfileError):
        _as_bool("yes", "fail_closed")


def test_load_lockfile_passthrough_and_parse_error():
    lock = default_lockfile()
    assert load_lockfile(lock).policy_hash == lock.policy_hash
    with pytest.raises(LockfileError):
        load_lockfile({"invariants": {"fail_closed": object()}})


def test_lua_empty_keys_and_extra_argv():
    sim = LuaSimulator()
    assert sim.eval([]) == ERR
    assert sim.eval(["k"], ["r", "h", "a", "b", "t", "extra"]) == "{ok}"
    assert sim.get("k") is not None


def test_unknown_record_type_rejected():
    with pytest.raises(ValueError):
        decision_record(
            record_type="not_a_type",
            request_id="req_x",
            action_hash="a" * 64,
            action=sample_action(),
        )


def test_store_lookups_and_admit_not_ok_blocks_effect():
    store = MemoryAuthorityStore()
    denied = store.put_denied(
        {
            "request_id": "req_denied",
            "record_type": "admit_denied",
            "action_hash": "a" * 64,
        }
    )
    # put_denied must not create an effectable grant
    assert store.get_admit("req_denied") is None
    store._admits["req_denied"] = {**denied, "record_type": "admit_denied"}
    with pytest.raises(EffectBlocked) as exc:
        store.try_effect("req_denied", "a" * 64)
    assert exc.value.reason_code == "EFFECT_ADMIT_NOT_OK"
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert store.get_by_slot(rec["slot_key"])["request_id"] == rec["request_id"]
    EffectLedger(store=store).effect(rec["request_id"], rec["action_hash"])
    assert store.get_effect(rec["request_id"])["record_type"] == "effect_applied"


def test_default_store_is_singleton_until_reset():
    a = default_store()
    b = default_store()
    assert a is b
    c = reset_default_store()
    assert c is not a
    assert default_store() is c


class _WeirdSim:
    def __init__(self):
        self._keys = {}

    # ConsumeLedger.dual_consume calls lua_simulator.dual_consume which uses eval
    # We monkeypatch via a simulator that returns a garbage token.


def test_consume_simulator_garbage_result(monkeypatch):
    from agent_gov import consume as consume_mod

    def fake_dual(_sim, _keys, _fields):
        return "{maybe}"

    monkeypatch.setattr(consume_mod, "dual_consume", fake_dual)
    ledger = ConsumeLedger(simulator=LuaSimulator())
    with pytest.raises(Exception) as exc:
        ledger.consume("dual:x", {"request_id": "req_x"})
    assert getattr(exc.value, "reason_code", "") == "CONSUME_LUA_ERR"
