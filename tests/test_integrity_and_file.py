from __future__ import annotations

import json

import pytest

from agent_gov import (
    ConsumeLedger,
    EffectLedger,
    FileAuthorityStore,
    IntegrityError,
    MemoryAuthorityStore,
    admit,
    default_lockfile,
    verify_chain,
    verify_record,
)

from tests.helpers import sample_action


def test_records_verify_and_chain():
    store = MemoryAuthorityStore()
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    verify_record(rec)
    EffectLedger(store=store).effect(rec["request_id"], rec["action_hash"])
    tip = store.verify()
    assert tip == store.tip()
    assert len(store.decisions()) >= 2
    verify_chain(store.decisions())
    assert store.get_record(rec["record_id"])["request_id"] == rec["request_id"]


def test_decision_record_verify_method():
    from agent_gov.records import DecisionRecord, decision_record

    rec = decision_record(
        record_type="admit_ok",
        request_id="req_v",
        action_hash="a" * 64,
        action=sample_action(),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert rec.verify() is rec
    with pytest.raises(IntegrityError):
        verify_record("nope")
    with pytest.raises(IntegrityError):
        verify_record({"record_type": "admit_ok"})


def test_sealed_record_is_immutable():
    store = MemoryAuthorityStore()
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    with pytest.raises(IntegrityError) as exc:
        rec["seat_a"] = "oid-evil"
    assert exc.value.reason_code == "SEALED"
    tampered = dict(rec)
    tampered["seat_a"] = "oid-evil"
    with pytest.raises(IntegrityError):
        verify_record(tampered)


def test_broken_chain_fails():
    store = MemoryAuthorityStore()
    admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    chain = [dict(store.decisions()[0])]
    chain[0]["prev_receipt_hash"] = "1" * 64
    with pytest.raises(IntegrityError):
        verify_chain(chain)


def test_file_store_survives_reload(tmp_path):
    path = tmp_path / "ledger.jsonl"
    store = FileAuthorityStore(path)
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    EffectLedger(store=store).effect(rec["request_id"], rec["action_hash"])
    reloaded = FileAuthorityStore(path)
    grant = reloaded.get_admit(rec["request_id"])
    assert grant is not None
    assert grant["action_hash"] == rec["action_hash"]
    assert reloaded.get_effect(rec["request_id"])["record_type"] == "effect_applied"
    reloaded.verify()
    # JSONL is real records
    lines = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    assert lines[0]["record_type"] == "admit_ok"


def test_corrupt_jsonl_fails_closed(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text("{not json\n")
    with pytest.raises(IntegrityError):
        FileAuthorityStore(path)
