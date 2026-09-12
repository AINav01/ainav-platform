from __future__ import annotations

import pytest

from agent_gov import (
    AdmitClient,
    ConsumeLedger,
    EffectBlocked,
    EffectLedger,
    FileAuthorityStore,
    IntegrityError,
    MemoryAuthorityStore,
    admit,
    default_lockfile,
    export_envelope,
    merkle_root,
    prove_record,
    verify_export,
    verify_inclusion,
)
from agent_gov.merkle import GENESIS_HASH, inclusion_proof, leaf_hash
from agent_gov.reasons import ALL, known
from agent_gov.records import DecisionRecord, GENESIS_HASH as REC_GENESIS

from tests.helpers import sample_action


def test_merkle_empty_is_genesis():
    assert merkle_root([]) == GENESIS_HASH == REC_GENESIS


def test_merkle_single_leaf_is_itself():
    assert merkle_root(["aa" * 32]) == "aa" * 32


def test_inclusion_proof_round_trip():
    store = MemoryAuthorityStore()
    client = AdmitClient(store=store)
    first = client.admit(sample_action(), seat_a="oid-1", seat_b="oid-2")
    client.effect(first["request_id"], first["action_hash"])
    client.admit(sample_action(proposal_id="prp-2"), seat_a="oid-1", seat_b="oid-2")
    audit = client.audit()
    assert audit["ok"] is True
    assert audit["count"] == 4  # admit, reserve, apply, admit
    assert audit["merkle_root"]
    proof = client.prove(first["record_id"])
    verify_inclusion(proof["leaf"], proof["proof"], proof["merkle_root"])
    assert proof["merkle_root"] == audit["merkle_root"]


def test_tampered_proof_fails():
    store = MemoryAuthorityStore()
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    EffectLedger(store=store).effect(rec["request_id"], rec["action_hash"])
    proof = store.prove(rec["record_id"])
    bad = list(proof["proof"])
    if bad:
        bad[0] = dict(bad[0], hash="0" * 64)
        with pytest.raises(IntegrityError) as exc:
            verify_inclusion(proof["leaf"], bad, proof["merkle_root"])
        assert exc.value.reason_code == "MERKLE_MISMATCH"
    with pytest.raises(IntegrityError):
        prove_record(store.decisions(), "dr_missing")
    with pytest.raises(IntegrityError):
        inclusion_proof(["a"], 3)


def test_export_includes_verifiable_merkle_root():
    store = MemoryAuthorityStore()
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    EffectLedger(store=store).effect(rec["request_id"], rec["action_hash"])
    envelope = export_envelope(store.decisions(), tip=store.tip())
    assert envelope["merkle_root"] == store.merkle_root()
    verify_export(envelope)
    envelope["merkle_root"] = "0" * 64
    with pytest.raises(IntegrityError) as exc:
        verify_export(envelope)
    assert exc.value.reason_code == "MERKLE_MISMATCH"


def test_grant_mismatch_blocks_effect():
    store = MemoryAuthorityStore()
    rec = admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    store._admits[rec["request_id"]]["grant_id"] = "0" * 64
    with pytest.raises(EffectBlocked) as exc:
        store.reserve_effect(rec["request_id"], rec["action_hash"])
    assert exc.value.reason_code == "GRANT_MISMATCH"


def test_sealed_mutators_all_fail():
    rec = DecisionRecord({"request_id": "req_x"}).seal()
    assert rec.sealed is True
    with pytest.raises(IntegrityError):
        del rec["request_id"]
    with pytest.raises(IntegrityError):
        rec.clear()
    with pytest.raises(IntegrityError):
        rec.pop("request_id")
    with pytest.raises(IntegrityError):
        rec.popitem()
    with pytest.raises(IntegrityError):
        rec.update({"x": 1})
    with pytest.raises(IntegrityError):
        rec.setdefault("y", 1)


def test_reason_codes_are_closed():
    assert known("SEATS_NOT_DISTINCT")
    assert known("GRANT_MISMATCH")
    assert known("MERKLE_MISMATCH")
    assert not known("NEW_SKU")
    assert "LIVE_PIN_OK" not in ALL


def test_file_audit_and_cli(tmp_path, capsys):
    from agent_gov.__main__ import main

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
    assert main(["audit", "--ledger", str(path)]) == 0
    out = capsys.readouterr().out
    assert "merkle_root" in out
    assert main(["prove", str(path), rec["record_id"]]) == 0
    assert rec["record_id"] in capsys.readouterr().out
    assert main(["audit"]) == 0


def test_invariants_fail_closed():
    from agent_gov import LockfileError
    from agent_gov.invariants import check_admit_ok, check_effect_applied, check_lockfile
    from agent_gov.lockfile import Lockfile

    with pytest.raises(LockfileError):
        check_lockfile(Lockfile(product="job_a"))
    rec = admit(sample_action(), default_lockfile(), seat_a="oid-1", seat_b="oid-2")
    with pytest.raises(IntegrityError):
        check_admit_ok(rec, policy_hash="0" * 64)
    with pytest.raises(IntegrityError):
        check_effect_applied(rec)
