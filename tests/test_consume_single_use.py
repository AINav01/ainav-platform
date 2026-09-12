from __future__ import annotations

import pytest

from agent_gov import (
    ConsumeLedger,
    ConsumeReplay,
    admit,
    default_lockfile,
    default_store,
)

from tests.helpers import sample_action


def test_second_admit_of_same_action_is_consume_replay():
    action = sample_action()
    ledger = ConsumeLedger()
    admit(action, default_lockfile(), ledger=ledger, seat_a="oid-1", seat_b="oid-2")
    with pytest.raises(ConsumeReplay) as exc:
        admit(action, default_lockfile(), ledger=ledger, seat_a="oid-3", seat_b="oid-4")
    assert exc.value.reason_code == "CONSUME_REPLAY"


def test_denied_records_are_not_retrievable_as_grants():
    from agent_gov import AdmitDenied

    ledger = ConsumeLedger()
    with pytest.raises(AdmitDenied):
        admit(
            sample_action(),
            default_lockfile(),
            ledger=ledger,
            seat_a="same",
            seat_b="same",
        )
    denied = [d for d in default_store().decisions() if d["record_type"] == "admit_denied"]
    assert denied
    assert default_store().get_admit(denied[0]["request_id"]) is None


def test_consume_requires_slot_key():
    with pytest.raises(ConsumeReplay):
        ConsumeLedger().consume("", {"request_id": "req_x"})
