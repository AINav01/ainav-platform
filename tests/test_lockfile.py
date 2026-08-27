from __future__ import annotations

import json

import pytest

from agent_gov import default_lockfile, load_lockfile
from agent_gov.lockfile import LOCKFILE_SCHEMA, dumps_lockfile, lockfile_json


def test_default_lockfile_pins_job_c():
    lock = default_lockfile()
    assert lock.schema_version == LOCKFILE_SCHEMA
    assert lock.product == "job_c"
    assert lock.policy_id == "dual-admit-v1"
    assert lock.effect_gate == "strict"
    assert lock.invariants["distinct_principals"] is True
    assert lock.invariants["single_use_consume"] is True
    assert lock.invariants["fail_closed"] is True
    assert lock.policy_hash == lock.digest()


def test_load_round_trip():
    lock = default_lockfile()
    loaded = load_lockfile(json.loads(lockfile_json(lock)))
    assert loaded.policy_hash == lock.policy_hash
    assert "dual-admit-v1" in dumps_lockfile(lock)


def test_unknown_product_rejected():
    from agent_gov import LockfileError

    doc = default_lockfile().to_canonical()
    doc["product"] = "job_a"
    with pytest.raises(LockfileError):
        load_lockfile(doc)
