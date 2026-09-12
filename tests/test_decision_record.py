from __future__ import annotations

from agent_gov import ConsumeLedger, action_hash, admit, default_lockfile
from agent_gov.hashing import canonical_json
from agent_gov.records import RECORD_TYPES, SCHEMA_VERSION

from tests.helpers import sample_action


def test_admit_record_carries_v1_fields():
    action = sample_action()
    rec = admit(
        action,
        default_lockfile(),
        ledger=ConsumeLedger(),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert rec["schema_version"] == SCHEMA_VERSION
    assert rec["record_type"] in RECORD_TYPES
    assert rec["record_id"].startswith("dr_")
    assert rec["proposal"]["action_class"] == "custody.withdraw.execute"
    assert rec["proposal"]["action_hash"] == rec["action_hash"]
    assert rec["action_hash"] == action_hash(action)
    assert rec["slot_key"] == f"dual:{rec['action_hash']}"


def test_canonical_json_is_stable():
    a = {"z": 1, "a": {"b": 2, "a": 1}}
    b = {"a": {"a": 1, "b": 2}, "z": 1}
    assert canonical_json(a) == canonical_json(b)
    assert canonical_json(a) == '{"a":{"a":1,"b":2},"z":1}'


def test_hash_is_64_hex_and_changes_with_proposal_id():
    h1 = action_hash(sample_action(proposal_id="p1"))
    h2 = action_hash(sample_action(proposal_id="p2"))
    assert h1 != h2
    assert len(h1) == 64
    int(h1, 16)
