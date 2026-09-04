from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov import (
    AdmitClient,
    AdmitDenied,
    EffectBlocked,
    LockfileError,
    MemoryAuthorityStore,
    default_lockfile,
    load_lockfile,
)
from agent_gov.clock import FrozenClock, reset_clock, set_clock
from agent_gov.errors import IntegrityError
from agent_gov.hashing import HASH_FIELDS, action_hash
from ainav.admit_client import DraftAdmitClient, wrap
from ainav.business import public_business, public_business_plane, validate_business
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard
from ainav.examiner import action_schema, prove

from tests.helpers import sample_action


def test_release_is_270():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.81.0"
    assert "write rail" in cat["equations"]["proof"]
    assert "examiner prove" in cat["equations"]["instrument"]
    assert "proof-day floor" in cat["equations"]["interface"].lower()


def test_walk_away_ledger_stays_empty():
    cat = load_catalog()
    ledger = cat["expert_review"]["success"]["walk_away_ledger"]
    assert ledger["recorded"] is False
    assert ledger["count"] == 0
    assert ledger["items"] == []
    plane = public_business_plane()
    assert plane["walk_away_ledger"]["count"] == 0
    assert plane["billing"]["attached"] is False
    assert plane["billing"]["provider"] is None


def test_kit_includes_icfr_case_on_l1_wedge():
    cat = load_catalog()
    ids = [case["id"] for case in cat["acceptance_kit"]["cases"]]
    assert "kit.bc.journal" in ids
    assert "kit.icfr.unauthorized_gl" in ids
    icfr = next(case for case in cat["acceptance_kit"]["cases"] if case["id"] == "kit.icfr.unauthorized_gl")
    assert icfr["action"]["action_class"] == "bc.general_journal.post"
    assert icfr["action"]["sor_target"] == "bc.sandbox"


def test_billing_is_unattached_not_a_ninth_complement():
    cat = load_catalog()
    billing = cat["business"]["billing"]
    assert billing["sku"] is False
    assert billing["attached"] is False
    assert billing["provider"] is None
    assert billing["recognized_revenue_claimed"] is False
    assert billing["ninth_complement"] is False
    assert public_business()["billing"]["attached"] is False


def test_action_schema_matches_hash_fields():
    schema = action_schema()
    assert list(schema["required"]) == list(HASH_FIELDS)
    assert set(schema["properties"]) == set(HASH_FIELDS)
    action = {
        "action_class": "bc.general_journal.post",
        "payload": {"account": "1000"},
        "proposal_id": "prp-schema",
        "sor_target": "bc.sandbox",
        "policy_id": "dual-admit-v1",
    }
    digest = action_hash(action)
    assert len(digest) == 64


def test_draft_admit_client_refuses_drafter_as_seat():
    store = MemoryAuthorityStore()
    client = AdmitClient(store=store)
    drafter = DraftAdmitClient("copilot-1", client)
    with pytest.raises(AdmitDenied) as exc:
        drafter.admit(sample_action(), seat_a="copilot-1", seat_b="oid-2")
    assert exc.value.reason_code == "DRAFTER_IS_NOT_SEAT"
    rec = wrap("copilot-1", client).admit(sample_action(), seat_a="oid-1", seat_b="oid-2")
    assert rec["record_type"] == "admit_ok"


def test_draft_admit_client_requires_drafter_id():
    with pytest.raises(AdmitDenied) as exc:
        DraftAdmitClient("")
    assert exc.value.reason_code == "DRAFTER_REQUIRED"


def test_examiner_prove_is_read_only_not_17a4():
    store = MemoryAuthorityStore()
    client = AdmitClient(store=store)
    rec = client.run_and_apply(sample_action(), seat_a="oid-1", seat_b="oid-2")
    proof = prove(rec["record_id"], store=store)
    assert proof["kind"] == "ainav.examiner.v1"
    assert proof["read_only"] is True
    assert proof["seventeen_a4"] is False
    assert proof["worm"] is False
    assert proof["live"] is False
    assert proof["record_id"] == rec["record_id"]


def test_examiner_prove_requires_record_id():
    with pytest.raises(IntegrityError) as exc:
        prove("")
    assert exc.value.reason_code == "EXAMINER_NO_RECORD"


def test_grant_ttl_is_outside_policy_hash():
    lock = default_lockfile()
    assert lock.grant_ttl_seconds is None
    assert lock.policy_hash == "79f359756ac2139053260c06ca6a09e18113059b0ba7d0d67f6b8956e47e98ff"
    doc = json.loads(json.dumps(lock.to_canonical()))
    doc["grant_ttl_seconds"] = 90
    doc["policy_hash"] = lock.policy_hash
    loaded = load_lockfile(doc)
    assert loaded.grant_ttl_seconds == 90
    assert loaded.policy_hash == lock.policy_hash
    assert loaded.digest() == lock.digest()


def test_grant_ttl_immediate_effect_still_passes():
    store = MemoryAuthorityStore()
    lock = default_lockfile()
    timed = load_lockfile({**lock.to_canonical(), "policy_hash": lock.policy_hash, "grant_ttl_seconds": 90})
    client = AdmitClient(lockfile=timed, store=store)
    rec = client.admit(sample_action(), seat_a="oid-1", seat_b="oid-2")
    out = client.effect(rec["request_id"], rec["action_hash"])
    assert out["record_type"] == "effect_applied"


def test_grant_ttl_expires_before_effect():
    store = MemoryAuthorityStore()
    lock = default_lockfile()
    timed = load_lockfile({**lock.to_canonical(), "policy_hash": lock.policy_hash, "grant_ttl_seconds": 1})
    set_clock(FrozenClock("2026-01-01T00:00:00.000000Z"))
    try:
        client = AdmitClient(lockfile=timed, store=store)
        rec = client.admit(sample_action(), seat_a="oid-1", seat_b="oid-2")
        set_clock(FrozenClock("2026-01-01T00:00:02.000000Z"))
        with pytest.raises(EffectBlocked) as exc:
            client.effect(rec["request_id"], rec["action_hash"])
        assert exc.value.reason_code == "EFFECT_GRANT_EXPIRED"
    finally:
        reset_clock()


def test_lockfile_refuses_non_positive_ttl():
    lock = default_lockfile()
    doc = {**lock.to_canonical(), "policy_hash": lock.policy_hash, "grant_ttl_seconds": 0}
    with pytest.raises(LockfileError):
        load_lockfile(doc)


def test_dashboard_exports_instrument_plane():
    dash = public_dashboard()
    assert dash["release"] == "2.81.0"
    assert dash["proof_day_floor"]["client_hides"] == ["estate", "audit", "assignment"]
    assert dash["ai_inventory"]["items"] == []
    assert dash["examiner"]["seventeen_a4"] is False
    assert dash["admit_client"]["drafter_is_not_seat"] is True
    assert dash["grant_ttl"]["outside_digest"] is True


def test_catalog_refuses_instrument_plane_fiction():
    cat = load_catalog()
    proof = copy.deepcopy(cat)
    proof["equations"]["proof"] = "invented"
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(proof)
    assert exc.value.reason_code == "CATALOG_EQUATION"
    instrument = copy.deepcopy(cat)
    instrument["equations"]["instrument"] = "invented"
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(instrument)
    assert exc2.value.reason_code == "CATALOG_EQUATION"
    iface = copy.deepcopy(cat)
    iface["equations"]["interface"] = iface["equations"]["interface"].replace("proof-day Floor", "floor")
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(iface)
    assert exc3.value.reason_code == "CATALOG_EQUATION"
    ledger = copy.deepcopy(cat)
    ledger["expert_review"]["success"]["walk_away_ledger"]["count"] = 1
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(ledger)
    assert exc4.value.reason_code == "CATALOG_REVIEW"
    named = copy.deepcopy(cat)
    named["expert_review"]["success"]["walk_away_ledger"]["items"] = ["invented"]
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(named)
    assert exc5.value.reason_code == "CATALOG_REVIEW"
    recorded = copy.deepcopy(cat)
    recorded["expert_review"]["success"]["walk_away_ledger"]["recorded"] = True
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(recorded)
    assert exc6.value.reason_code == "CATALOG_REVIEW"
    gate = copy.deepcopy(cat)
    gate["plane_interface"]["floor"]["not_the_gate"] = [
        item for item in gate["plane_interface"]["floor"]["not_the_gate"] if item["id"] != "grc_icfr"
    ]
    with pytest.raises(IntegrityError) as exc7:
        validate_catalog(gate)
    assert exc7.value.reason_code == "CATALOG_PLANE"
    inventory = copy.deepcopy(cat)
    inventory["plane_interface"]["ai_inventory"]["items"] = [{"name": "invented"}]
    with pytest.raises(IntegrityError) as exc8:
        validate_catalog(inventory)
    assert exc8.value.reason_code == "CATALOG_PLANE"
    live_inv = copy.deepcopy(cat)
    live_inv["plane_interface"]["ai_inventory"]["live"] = True
    with pytest.raises(IntegrityError) as exc9:
        validate_catalog(live_inv)
    assert exc9.value.reason_code == "CATALOG_PLANE"
    worm = copy.deepcopy(cat)
    worm["plane_interface"]["examiner"]["worm"] = True
    with pytest.raises(IntegrityError) as exc10:
        validate_catalog(worm)
    assert exc10.value.reason_code == "CATALOG_GOVERNANCE"
    seat = copy.deepcopy(cat)
    seat["plane_interface"]["admit_client"]["drafter_is_not_seat"] = False
    with pytest.raises(IntegrityError) as exc11:
        validate_catalog(seat)
    assert exc11.value.reason_code == "CATALOG_PLANE"
    ttl = copy.deepcopy(cat)
    ttl["plane_interface"]["grant_ttl"]["changes_policy_hash"] = True
    with pytest.raises(IntegrityError) as exc12:
        validate_catalog(ttl)
    assert exc12.value.reason_code == "CATALOG_PLANE"
    client = copy.deepcopy(cat)
    for view in client["plane_interface"]["views"]:
        if view["id"] == "client":
            view["can"] = "Sit the executive board."
    with pytest.raises(IntegrityError) as exc13:
        validate_catalog(client)
    assert exc13.value.reason_code == "CATALOG_PLANE"
    passkey = copy.deepcopy(cat)
    passkey["plane_interface"]["view_assignment"]["mfa"]["passkey"]["is_admit"] = True
    with pytest.raises(IntegrityError) as exc14:
        validate_catalog(passkey)
    assert exc14.value.reason_code == "CATALOG_PLANE"
    formal = copy.deepcopy(cat)
    formal["engineering"]["formal"]["claimed"] = True
    with pytest.raises(IntegrityError) as exc15:
        validate_catalog(formal)
    assert exc15.value.reason_code == "CATALOG_ENGINEERING"
    split = copy.deepcopy(cat)
    split["engineering"]["catalog_shape"]["do_not_split"] = False
    with pytest.raises(IntegrityError) as exc16:
        validate_catalog(split)
    assert exc16.value.reason_code == "CATALOG_ENGINEERING"
    billing = copy.deepcopy(cat)
    billing["business"]["billing"]["attached"] = True
    with pytest.raises(IntegrityError) as exc17:
        validate_business(billing)
    assert exc17.value.reason_code == "CATALOG_BUSINESS"
    ninth = copy.deepcopy(cat)
    ninth["business"]["billing"]["ninth_complement"] = True
    with pytest.raises(IntegrityError) as exc18:
        validate_business(ninth)
    assert exc18.value.reason_code == "CATALOG_BUSINESS"
    rev = copy.deepcopy(cat)
    rev["business"]["billing"]["recognized_revenue_claimed"] = True
    with pytest.raises(IntegrityError) as exc19:
        validate_business(rev)
    assert exc19.value.reason_code == "REVENUE_NOT_CLAIMED"
    kit = copy.deepcopy(cat)
    kit["acceptance_kit"]["cases"].append(
        {
            "id": "kit.invented",
            "action": {
                "action_class": "invented.write",
                "payload": {},
                "sor_target": "bc.sandbox",
                "policy_id": "dual-admit-v1",
            },
        }
    )
    with pytest.raises(IntegrityError) as exc20:
        validate_catalog(kit)
    assert exc20.value.reason_code == "CATALOG_KIT"


def test_formal_spec_exists_and_is_not_claimed():
    cat = load_catalog()
    formal = cat["engineering"]["formal"]
    assert formal["claimed"] is False
    assert formal["verified"] is False
    text = Path(formal["spec"]).read_text(encoding="utf-8")
    assert "Admit" in text
    assert "Replay" in text


def test_draft_admit_client_run_and_prove():
    store = MemoryAuthorityStore()
    client = AdmitClient(store=store)
    drafter = DraftAdmitClient("copilot-1", client)
    with pytest.raises(AdmitDenied) as exc:
        drafter.run_and_apply(sample_action(), seat_a="oid-1", seat_b="copilot-1")
    assert exc.value.reason_code == "DRAFTER_IS_NOT_SEAT"
    out = drafter.run_and_apply(sample_action(), seat_a="oid-1", seat_b="oid-2")
    proof = drafter.prove(out["record_id"])
    assert proof["record_id"] == out["record_id"]


def test_grant_ttl_bad_time_and_missing_admit():
    from agent_gov.effect import EffectLedger, _parse_created

    with pytest.raises(EffectBlocked) as exc:
        _parse_created("not-a-time")
    assert exc.value.reason_code == "EFFECT_GRANT_TIME"
    naive = _parse_created("2026-01-01T00:00:00")
    assert naive.tzinfo is not None
    store = MemoryAuthorityStore()
    gate = EffectLedger(store=store, grant_ttl_seconds=30)
    with pytest.raises(EffectBlocked) as exc2:
        gate.effect("req_missing", "a" * 64)
    assert exc2.value.reason_code == "EFFECT_NO_ADMIT"


def test_lockfile_refuses_non_integer_ttl():
    lock = default_lockfile()
    doc = {**lock.to_canonical(), "policy_hash": lock.policy_hash, "grant_ttl_seconds": "soon"}
    with pytest.raises(LockfileError):
        load_lockfile(doc)


def test_catalog_refuses_more_instrument_fiction():
    cat = load_catalog()
    shape = copy.deepcopy(cat)
    del shape["engineering"]["catalog_shape"]
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(shape)
    assert exc.value.reason_code == "CATALOG_ENGINEERING"
    path = copy.deepcopy(cat)
    path["engineering"]["catalog_shape"]["path"] = "split.json"
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(path)
    assert exc2.value.reason_code == "CATALOG_ENGINEERING"
    extract = copy.deepcopy(cat)
    extract["engineering"]["catalog_shape"]["extract"] = []
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(extract)
    assert exc3.value.reason_code == "CATALOG_ENGINEERING"
    formal = copy.deepcopy(cat)
    del formal["engineering"]["formal"]
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(formal)
    assert exc4.value.reason_code == "CATALOG_ENGINEERING"
    spec = copy.deepcopy(cat)
    spec["engineering"]["formal"]["spec"] = "invented.tla"
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(spec)
    assert exc5.value.reason_code == "CATALOG_ENGINEERING"
    floor = copy.deepcopy(cat)
    del floor["plane_interface"]["proof_day_floor"]
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(floor)
    assert exc6.value.reason_code == "CATALOG_PLANE"
    sku = copy.deepcopy(cat)
    sku["plane_interface"]["proof_day_floor"]["sku"] = True
    with pytest.raises(IntegrityError) as exc7:
        validate_catalog(sku)
    assert exc7.value.reason_code == "CATALOG_SKU"
    minutes = copy.deepcopy(cat)
    minutes["plane_interface"]["proof_day_floor"]["minutes"] = 30
    with pytest.raises(IntegrityError) as exc8:
        validate_catalog(minutes)
    assert exc8.value.reason_code == "CATALOG_PLANE"
    shows = copy.deepcopy(cat)
    shows["plane_interface"]["proof_day_floor"]["client_shows"] = ["tiles"]
    with pytest.raises(IntegrityError) as exc9:
        validate_catalog(shows)
    assert exc9.value.reason_code == "CATALOG_PLANE"
    hides = copy.deepcopy(cat)
    hides["plane_interface"]["proof_day_floor"]["client_hides"] = []
    with pytest.raises(IntegrityError) as exc10:
        validate_catalog(hides)
    assert exc10.value.reason_code == "CATALOG_PLANE"
    dash = copy.deepcopy(cat)
    dash["plane_interface"]["proof_day_floor"]["included_with"] = "U-DUAL"
    with pytest.raises(IntegrityError) as exc11:
        validate_catalog(dash)
    assert exc11.value.reason_code == "CATALOG_PLANE"
    admit = copy.deepcopy(cat)
    del admit["plane_interface"]["admit_client"]
    with pytest.raises(IntegrityError) as exc12:
        validate_catalog(admit)
    assert exc12.value.reason_code == "CATALOG_PLANE"
    live = copy.deepcopy(cat)
    live["plane_interface"]["admit_client"]["live"] = True
    with pytest.raises(IntegrityError) as exc13:
        validate_catalog(live)
    assert exc13.value.reason_code == "CATALOG_PLANE"
    exam = copy.deepcopy(cat)
    del exam["plane_interface"]["examiner"]
    with pytest.raises(IntegrityError) as exc14:
        validate_catalog(exam)
    assert exc14.value.reason_code == "CATALOG_PLANE"
    live_ex = copy.deepcopy(cat)
    live_ex["plane_interface"]["examiner"]["live"] = True
    with pytest.raises(IntegrityError) as exc15:
        validate_catalog(live_ex)
    assert exc15.value.reason_code == "CATALOG_PLANE"
    ro = copy.deepcopy(cat)
    ro["plane_interface"]["examiner"]["read_only"] = False
    with pytest.raises(IntegrityError) as exc16:
        validate_catalog(ro)
    assert exc16.value.reason_code == "CATALOG_PLANE"
    cli = copy.deepcopy(cat)
    cli["plane_interface"]["examiner"]["cli"] = "invented"
    with pytest.raises(IntegrityError) as exc17:
        validate_catalog(cli)
    assert exc17.value.reason_code == "CATALOG_PLANE"
    inv = copy.deepcopy(cat)
    del inv["plane_interface"]["ai_inventory"]
    with pytest.raises(IntegrityError) as exc18:
        validate_catalog(inv)
    assert exc18.value.reason_code == "CATALOG_PLANE"
    inv_sku = copy.deepcopy(cat)
    inv_sku["plane_interface"]["ai_inventory"]["sku"] = True
    with pytest.raises(IntegrityError) as exc19:
        validate_catalog(inv_sku)
    assert exc19.value.reason_code == "CATALOG_PLANE"
    names = copy.deepcopy(cat)
    names["plane_interface"]["ai_inventory"]["do_not_invent_names"] = False
    with pytest.raises(IntegrityError) as exc20:
        validate_catalog(names)
    assert exc20.value.reason_code == "CATALOG_PLANE"
    seat = copy.deepcopy(cat)
    seat["plane_interface"]["ai_inventory"]["drafter_is_not_seat"] = False
    with pytest.raises(IntegrityError) as exc21:
        validate_catalog(seat)
    assert exc21.value.reason_code == "CATALOG_PLANE"
    ttl = copy.deepcopy(cat)
    del ttl["plane_interface"]["grant_ttl"]
    with pytest.raises(IntegrityError) as exc22:
        validate_catalog(ttl)
    assert exc22.value.reason_code == "CATALOG_PLANE"
    default = copy.deepcopy(cat)
    default["plane_interface"]["grant_ttl"]["default_seconds"] = 90
    with pytest.raises(IntegrityError) as exc23:
        validate_catalog(default)
    assert exc23.value.reason_code == "CATALOG_PLANE"
    outside = copy.deepcopy(cat)
    outside["plane_interface"]["grant_ttl"]["outside_digest"] = False
    with pytest.raises(IntegrityError) as exc24:
        validate_catalog(outside)
    assert exc24.value.reason_code == "CATALOG_PLANE"
    passkey = copy.deepcopy(cat)
    del passkey["plane_interface"]["view_assignment"]["mfa"]["passkey"]
    with pytest.raises(IntegrityError) as exc25:
        validate_catalog(passkey)
    assert exc25.value.reason_code == "CATALOG_PLANE"
    live_pk = copy.deepcopy(cat)
    live_pk["plane_interface"]["view_assignment"]["mfa"]["passkey"]["live"] = True
    with pytest.raises(IntegrityError) as exc26:
        validate_catalog(live_pk)
    assert exc26.value.reason_code == "CATALOG_PLANE"
    identify = copy.deepcopy(cat)
    identify["plane_interface"]["view_assignment"]["mfa"]["passkey"]["identify"] = False
    with pytest.raises(IntegrityError) as exc27:
        validate_catalog(identify)
    assert exc27.value.reason_code == "CATALOG_PLANE"
    note = copy.deepcopy(cat)
    note["plane_interface"]["view_assignment"]["mfa"]["passkey"]["note"] = "wired"
    with pytest.raises(IntegrityError) as exc28:
        validate_catalog(note)
    assert exc28.value.reason_code == "CATALOG_PLANE"
    ledger = copy.deepcopy(cat)
    del ledger["expert_review"]["success"]["walk_away_ledger"]
    with pytest.raises(IntegrityError) as exc29:
        validate_catalog(ledger)
    assert exc29.value.reason_code == "CATALOG_REVIEW"
    invent = copy.deepcopy(cat)
    invent["expert_review"]["success"]["walk_away_ledger"]["do_not_invent_names"] = False
    with pytest.raises(IntegrityError) as exc30:
        validate_catalog(invent)
    assert exc30.value.reason_code == "CATALOG_REVIEW"
    recorded_note = copy.deepcopy(cat)
    recorded_note["expert_review"]["success"]["walk_away_ledger"]["note"] = "silent"
    with pytest.raises(IntegrityError) as exc31:
        validate_catalog(recorded_note)
    assert exc31.value.reason_code == "CATALOG_REVIEW"
    billing = copy.deepcopy(cat)
    del billing["business"]["billing"]
    with pytest.raises(IntegrityError) as exc32:
        validate_business(billing)
    assert exc32.value.reason_code == "CATALOG_BUSINESS"
    provider = copy.deepcopy(cat)
    provider["business"]["billing"]["provider"] = "stripe"
    with pytest.raises(IntegrityError) as exc33:
        validate_business(provider)
    assert exc33.value.reason_code == "CATALOG_BUSINESS"
    sku_bill = copy.deepcopy(cat)
    sku_bill["business"]["billing"]["sku"] = True
    with pytest.raises(IntegrityError) as exc34:
        validate_business(sku_bill)
    assert exc34.value.reason_code == "CATALOG_BUSINESS"


def test_cli_examiner_and_schema(capsys):
    from ainav.__main__ import main

    assert main(["action-schema"]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert schema["required"] == list(HASH_FIELDS)
    assert main(["examiner-prove"]) == 0
    proof = json.loads(capsys.readouterr().out)
    assert proof["kind"] == "ainav.examiner.v1"
    assert proof["seventeen_a4"] is False
