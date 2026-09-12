from __future__ import annotations

import pytest

from agent_gov import (
    AdmitDenied,
    ConsumeLedger,
    action_hash,
    admit,
    default_lockfile,
)

from tests.helpers import sample_action


def test_distinct_seats_admit_ok():
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert rec["record_type"] == "admit_ok"
    assert rec["consumed"] is True
    assert rec["action_hash"] == action_hash(sample_action())
    assert rec["integrity"]["content_hash"]


def test_same_seat_is_denied_and_does_not_consume_slot():
    ledger = ConsumeLedger()
    with pytest.raises(AdmitDenied) as exc:
        admit(
            sample_action(),
            default_lockfile(),
            ledger=ledger,
            seat_a="oid-1",
            seat_b="oid-1",
        )
    assert exc.value.reason_code == "SEATS_NOT_DISTINCT"
    # A later distinct pair must still be able to consume the slot.
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ledger,
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert rec["record_type"] == "admit_ok"


@pytest.mark.parametrize(
    "seat_a,seat_b,code",
    [
        ("", "oid-2", "SEAT_EMPTY"),
        ("oid-1", "   ", "SEAT_EMPTY"),
        (None, "oid-2", "SEAT_MISSING"),
        ("oid-1", None, "SEAT_MISSING"),
        (1, "oid-2", "SEAT_TYPE"),
    ],
)
def test_invalid_seats_fail_closed(seat_a, seat_b, code):
    with pytest.raises(AdmitDenied) as exc:
        admit(
            sample_action(),
            default_lockfile(),
            seat_a=seat_a,  # type: ignore[arg-type]
            seat_b=seat_b,  # type: ignore[arg-type]
        )
    assert exc.value.reason_code == code


def test_whitespace_is_stripped_but_not_case_folded():
    rec = admit(
        sample_action(),
        default_lockfile(),
        seat_a="  oid-1  ",
        seat_b="OID-1",
    )
    assert rec["seat_a"] == "oid-1"
    assert rec["seat_b"] == "OID-1"


def test_payload_change_changes_hash_and_is_a_new_slot():
    first = admit(sample_action(), default_lockfile(), seat_a="a", seat_b="b")
    second = admit(
        sample_action(payload={"amount": "101", "asset": "USDC", "dest": "0xabc"}),
        default_lockfile(),
        seat_a="a",
        seat_b="b",
    )
    assert first["action_hash"] != second["action_hash"]
    assert first["request_id"] != second["request_id"]
