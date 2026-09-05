"""The caller shape this package exists to serve."""

from __future__ import annotations

from agent_gov import ConsumeLedger, EffectLedger, admit, default_lockfile

from tests.helpers import sample_action


def test_user_snippet_admits_then_effects():
    action = sample_action()

    rec = admit(
        action,
        default_lockfile(),
        ledger=ConsumeLedger(),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    out = EffectLedger().effect(rec["request_id"], rec["action_hash"])

    assert rec["record_type"] == "admit_ok"
    assert rec["request_id"].startswith("req_")
    assert len(rec["action_hash"]) == 64
    assert rec["seat_a"] == "oid-1"
    assert rec["seat_b"] == "oid-2"
    assert out["record_type"] == "effect_applied"
    assert out["request_id"] == rec["request_id"]
    assert out["action_hash"] == rec["action_hash"]
