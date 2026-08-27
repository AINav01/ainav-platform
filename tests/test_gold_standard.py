from __future__ import annotations

import json
from importlib.resources import files

import pytest

from agent_gov import (
    Action,
    ConsumeLedger,
    EffectLedger,
    FileAuthorityStore,
    IntegrityError,
    MemoryAuthorityStore,
    action_hash,
    admit,
    default_lockfile,
    export_envelope,
    grant_id,
    verify_export,
    verify_record,
)
from agent_gov.hashing import canonical_json, hashes_equal, normalize_action
from agent_gov.invariants import check_admit_ok, check_effect_applied, check_lockfile

from tests.helpers import sample_action


def _vectors():
    return json.loads(files("agent_gov.gold").joinpath("vectors.json").read_text(encoding="utf-8"))


def test_frozen_action_hash_vector():
    vec = _vectors()
    assert canonical_json(normalize_action(vec["action"])) == vec["canonical_json"]
    assert hashes_equal(action_hash(vec["action"]), vec["action_hash"])
    assert hashes_equal(
        grant_id(
            action_hash=vec["action_hash"],
            seat_a=vec["seats"]["seat_a"],
            seat_b=vec["seats"]["seat_b"],
            policy_hash=default_lockfile().policy_hash,
        ),
        vec["grant_id"],
    )


def test_typed_action_matches_dict_hash():
    raw = sample_action()
    typed = Action(
        action_class=raw["action_class"],
        payload=raw["payload"],
        proposal_id=raw["proposal_id"],
        sor_target=raw["sor_target"],
        policy_id=raw["policy_id"],
    )
    assert action_hash(typed) == action_hash(raw)
    rec = admit(typed, default_lockfile(), seat_a="oid-1", seat_b="oid-2")
    assert rec["action_hash"] == action_hash(raw)


def test_grant_id_changes_when_a_seat_swaps():
    digest = action_hash(sample_action())
    policy = default_lockfile().policy_hash
    left = grant_id(action_hash=digest, seat_a="oid-1", seat_b="oid-2", policy_hash=policy)
    right = grant_id(action_hash=digest, seat_a="oid-2", seat_b="oid-1", policy_hash=policy)
    assert left != right


def test_executable_invariants_on_happy_path():
    lock = default_lockfile()
    check_lockfile(lock)
    store = MemoryAuthorityStore()
    rec = admit(
        sample_action(),
        lock,
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    check_admit_ok(rec, policy_hash=lock.policy_hash)
    out = EffectLedger(store=store).effect(rec["request_id"], rec["action_hash"])
    check_effect_applied(out)
    verify_record(out)
    assert out.get("effected_at")
    assert out["seq"] >= 2


def test_export_envelope_round_trip():
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
    assert verify_export(envelope) == store.tip()
    broken = dict(envelope)
    broken["tip"] = "0" * 64
    with pytest.raises(IntegrityError):
        verify_export(broken)


def test_file_tip_sidecar_mismatch_fails_closed(tmp_path):
    path = tmp_path / "ledger.jsonl"
    store = FileAuthorityStore(path)
    admit(
        sample_action(),
        default_lockfile(),
        ledger=ConsumeLedger(store=store),
        seat_a="oid-1",
        seat_b="oid-2",
    )
    tip = path.with_name(path.name + ".tip")
    assert tip.exists()
    tip.write_text(json.dumps({"alg": "sha256", "count": 99, "tip": "0" * 64}))
    with pytest.raises(IntegrityError) as exc:
        FileAuthorityStore(path)
    assert exc.value.reason_code == "TIP_MISMATCH"


def test_property_any_payload_byte_changes_hash():
    base = sample_action()
    seen = {action_hash(base)}
    for amount in ("101", "100.0", "100 "):
        seen.add(action_hash(sample_action(payload={**base["payload"], "amount": amount})))
    assert len(seen) == 4


def test_frozen_clock_and_hash_compare():
    from agent_gov.clock import FrozenClock, reset_clock, set_clock, utc_now
    from agent_gov.hashing import hashes_equal

    set_clock(FrozenClock("2026-01-01T00:00:00.000000Z"))
    try:
        assert utc_now() == "2026-01-01T00:00:00.000000Z"
    finally:
        reset_clock()
    assert hashes_equal("aa", "aa")
    assert not hashes_equal("aa", "ab")
    assert not hashes_equal("aa", "aaa")
    assert not hashes_equal(None, "aa")


def test_export_rejects_bad_envelope():
    with pytest.raises(IntegrityError):
        verify_export({"schema_version": "nope", "product": "job_c", "count": 0, "tip": "", "records": []})
    with pytest.raises(IntegrityError):
        verify_export(
            {
                "schema_version": "agent_gov.export.v1",
                "product": "job_a",
                "count": 0,
                "tip": "",
                "records": [],
            }
        )
