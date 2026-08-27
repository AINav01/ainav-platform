from __future__ import annotations

import pytest

from agent_gov import AdmitClient, AdmitDenied, DualSession, MemoryAuthorityStore

from tests.helpers import sample_action


def test_admit_client_round_trip():
    client = AdmitClient(store=MemoryAuthorityStore())
    rec = client.admit(sample_action(), seat_a="oid-1", seat_b="oid-2")
    out = client.effect(rec["request_id"], rec["action_hash"])
    assert rec["record_type"] == "admit_ok"
    assert out["record_type"] == "effect_applied"


def test_dual_session_binds_seats():
    store = MemoryAuthorityStore()
    session = DualSession("oid-1", "oid-2", store=store)
    rec = session.admit(sample_action())
    out = session.run_and_apply(
        sample_action(proposal_id="prp-2"),
        apply=lambda grant: {"ok": grant["action_hash"]},
    )
    assert rec["seat_a"] == "oid-1"
    assert rec["seat_b"] == "oid-2"
    assert out["apply_result"]["ok"] == out["action_hash"]


def test_dual_session_rejects_same_seat_at_construct():
    with pytest.raises(AdmitDenied) as exc:
        DualSession("oid-1", "oid-1")
    assert exc.value.reason_code == "SEATS_NOT_DISTINCT"


def test_client_session_factory():
    client = AdmitClient(store=MemoryAuthorityStore())
    session = client.session("a", "b")
    rec = session.admit(sample_action())
    out = session.effect(rec["request_id"], rec["action_hash"])
    assert rec["consumed"] is True
    assert out["record_type"] == "effect_applied"
