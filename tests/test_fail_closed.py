from __future__ import annotations

import pytest

from agent_gov import (
    AdmitDenied,
    LockfileError,
    admit,
    default_lockfile,
    load_lockfile,
)
from agent_gov.lockfile import HARD_INVARIANTS, Lockfile

from tests.helpers import sample_action


def test_empty_action_denied():
    with pytest.raises(AdmitDenied) as exc:
        admit({}, default_lockfile(), seat_a="oid-1", seat_b="oid-2")
    assert exc.value.reason_code == "ACTION_EMPTY"


def test_action_class_is_required():
    with pytest.raises(AdmitDenied) as exc:
        admit({"payload": {"x": 1}}, default_lockfile(), seat_a="oid-1", seat_b="oid-2")
    assert exc.value.reason_code == "ACTION_FIELD_REQUIRED"


def test_none_action_denied():
    with pytest.raises(AdmitDenied) as exc:
        admit(None, default_lockfile(), seat_a="oid-1", seat_b="oid-2")
    assert exc.value.reason_code == "ACTION_MISSING"


def test_non_canonical_action_denied():
    with pytest.raises(AdmitDenied) as exc:
        admit({"payload": {1, 2, 3}}, default_lockfile(), seat_a="a", seat_b="b")
    assert exc.value.reason_code == "ACTION_NOT_CANONICAL"


def test_lockfile_cannot_weaken_fail_closed():
    broken = default_lockfile().to_canonical()
    broken["invariants"] = {**HARD_INVARIANTS, "fail_closed": False}
    with pytest.raises(LockfileError) as exc:
        load_lockfile(broken)
    assert exc.value.reason_code == "LOCKFILE_WEAKENED"


def test_lockfile_cannot_set_permissive_effect_gate():
    broken = default_lockfile().to_canonical()
    broken["effect_gate"] = "best_effort"
    with pytest.raises(LockfileError) as exc:
        load_lockfile(broken)
    assert exc.value.reason_code == "LOCKFILE_EFFECT_GATE"


def test_lockfile_hash_mismatch_fails_closed():
    lock = Lockfile(policy_hash="deadbeef")
    with pytest.raises(LockfileError) as exc:
        lock.verify()
    assert exc.value.reason_code == "LOCKFILE_HASH_MISMATCH"


def test_default_lockfile_is_deterministic():
    a = default_lockfile()
    b = default_lockfile()
    assert a.policy_hash == b.policy_hash
    assert a.policy_hash
    a.verify()
