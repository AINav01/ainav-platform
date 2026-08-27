from __future__ import annotations

from agent_gov import ConsumeLedger, ConsumeReplay, LuaSimulator, admit, default_lockfile
from agent_gov.lua_simulator import ERR, OK, dual_consume

from tests.helpers import sample_action


def test_validate_all_then_write_all_is_atomic():
    sim = LuaSimulator()
    # Two keys; first free, second already taken — must write NOTHING.
    sim.eval(["already"], ["req0", "h", "a", "b", "t0"])
    result = sim.eval(["fresh", "already"], ["req1", "h", "a", "b", "t1"])
    assert result == ERR
    assert sim.exists("already")
    assert not sim.exists("fresh")


def test_same_slot_keys_share_one_write():
    sim = LuaSimulator()
    assert dual_consume(sim, ["dual:abc", "dual:abc"], {"request_id": "req_1"}) == OK
    # Same key listed twice still occupies one slot; replay is err.
    assert dual_consume(sim, ["dual:abc"], {"request_id": "req_2"}) == ERR
    assert sim.get("dual:abc")["request_id"] == "req_1"


def test_consume_ledger_honors_simulator_err():
    sim = LuaSimulator()
    ledger = ConsumeLedger(simulator=sim)
    admit(
        sample_action(),
        default_lockfile(),
        ledger=ledger,
        seat_a="oid-1",
        seat_b="oid-2",
    )
    try:
        admit(
            sample_action(),
            default_lockfile(),
            ledger=ledger,
            seat_a="oid-3",
            seat_b="oid-4",
        )
    except ConsumeReplay as exc:
        assert exc.reason_code == "CONSUME_REPLAY"
    else:
        raise AssertionError("expected ConsumeReplay")
