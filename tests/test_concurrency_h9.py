"""H9: concurrent consume of the same slot yields exactly one ok."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from agent_gov import ConsumeLedger, ConsumeReplay, admit, default_lockfile
from agent_gov.lua_simulator import ERR, OK, LuaSimulator

from tests.helpers import sample_action

WORKERS = 32


@pytest.mark.gold
def test_h9_exactly_one_admit_ok():
    action = sample_action()
    ledger = ConsumeLedger()

    def attempt(i: int):
        try:
            rec = admit(
                action,
                default_lockfile(),
                ledger=ledger,
                seat_a=f"oid-a-{i}",
                seat_b=f"oid-b-{i}",
            )
            return rec["record_type"]
        except ConsumeReplay:
            return "consume_replay"

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = [fut.result() for fut in as_completed(pool.submit(attempt, i) for i in range(WORKERS))]

    assert results.count("admit_ok") == 1
    assert results.count("consume_replay") == WORKERS - 1


@pytest.mark.gold
def test_h9_lua_simulator_exactly_one_ok():
    sim = LuaSimulator()
    keys = ["dual:same-slot"]

    def attempt(_i: int) -> str:
        return sim.eval(keys, ["req", "hash", "a", "b", "now"])

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = [fut.result() for fut in as_completed(pool.submit(attempt, i) for i in range(WORKERS))]

    assert results.count(OK) == 1
    assert results.count(ERR) == WORKERS - 1
    assert sim.keycount() == 1
