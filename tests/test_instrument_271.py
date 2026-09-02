from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov import default_lockfile
from agent_gov.errors import IntegrityError
from ainav.business import public_business_plane
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard
from ainav.proof_day import run_proof_day


def test_release_is_271():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.71.0"
    assert "pending bind" in cat["equations"]["interface"]
    assert "same l1" in cat["equations"]["motion"].lower()
    assert cat["proof_day"]["grant_ttl_seconds"] == 5400
    assert cat["proof_day"]["lab_oids_are_not_named_seats"] is True


def test_client_offer_does_not_leak_encyclopedia():
    cat = load_catalog()
    included = next(
        item
        for item in cat["plane_interface"]["included_and_upsells"]["first_glance"]["columns"]
        if item["id"] == "included_with_l1"
    )
    blob = " ".join(included["items"]).lower()
    assert "estate — same plane" not in blob
    assert "audit — same plane" not in blob
    assert "encyclopedia" in blob
    assert "dashboard" in blob
    app = Path("institute/app.html").read_text(encoding="utf-8")
    offer = app.split('id="app-floor-offer"', 1)[1].split("</div>", 1)[0].lower()
    assert "estate — same plane" not in offer
    assert "audit — same plane" not in offer
    assert "encyclopedia is a drawer" in offer


def test_pending_bind_stays_empty():
    cat = load_catalog()
    pending = cat["plane_interface"]["pending_bind"]
    assert pending["sku"] is False
    assert pending["live"] is False
    assert pending["count"] == 0
    assert pending["named_pair"] is False
    assert pending["action_class"] == "bc.general_journal.post"
    assert pending["seat_a"] == ""
    assert pending["seat_b"] == ""
    assert pending["action_hash"] == ""
    assert pending["refuse"] is True
    dash = public_dashboard()
    assert dash["pending_bind"]["count"] == 0


def test_freeze_console_is_local_request():
    cat = load_catalog()
    freeze = cat["plane_interface"]["freeze_console"]
    assert freeze["verb"] == "request"
    assert freeze["live"] is False
    assert freeze["catalog_plane_stays_open"] is True
    assert freeze["local_to_browser"] is True
    assert freeze["inference_may_continue"] is True
    assert freeze["consequence_does_not"] is True
    html = Path("institute/app.html").read_text(encoding="utf-8")
    assert 'id="app-floor-freeze-btn"' in html
    js = Path("institute/app.js").read_text(encoding="utf-8")
    assert "ainav-freeze-requested" in js
    assert "catalog plane stays OPEN" in html.lower() or "catalog plane stays open" in html.lower()


def test_examiner_walk_is_not_17a4():
    cat = load_catalog()
    walk = cat["plane_interface"]["examiner_walk"]
    assert walk["read_only"] is True
    assert walk["seventeen_a4"] is False
    assert walk["worm"] is False
    assert walk["named_records"] == 0
    assert walk["demo"]["included"] is False
    assert walk["demo"]["record_id"] == ""
    html = Path("institute/app.html").read_text(encoding="utf-8")
    assert 'id="app-floor-prove"' in html
    assert "Not 17a-4" in html


def test_entra_groups_are_templates_not_live():
    cat = load_catalog()
    groups = cat["plane_interface"]["view_assignment"]["entra_groups"]
    assert groups["assignment_live"] is False
    assert groups["named_head"] is False
    assert groups["cloud_agent_cannot_assign"] is True
    assert groups["do_not_invent_names"] is True
    assert {row["org_node"] for row in groups["templates"]} >= {
        "client.treasury",
        "client.controller",
    }
    assert all(row["named_head"] is False for row in groups["templates"])


def test_motions_are_not_skus():
    cat = load_catalog()
    motions = cat["plane_interface"]["motions"]
    assert motions["sku"] is False
    assert motions["fourth_sku"] is False
    small = motions["small_client"]
    assert small["same_l1"] is True
    assert small["express_sku"] is False
    assert small["discount_udual"] is False
    assert small["price_usd"] == {"min": 28000, "max": 40000}
    large = motions["large_client"]
    assert large["same_three_skus"] is True
    assert large["certificate"] is False
    assert large["sox"] is False
    assert large["seventeen_a4"] is False
    assert large["g12_open"] is True
    plane = public_business_plane()
    assert plane["motions"]["sku"] is False
    assert plane["competitive"]["uncopyable"] is False


def test_hostname_rehearsal_is_not_launch():
    cat = load_catalog()
    host = cat["plane_interface"]["hostname_rehearsal"]
    assert host["launch"] is False
    assert host["asuid_added"] is False
    assert host["cloudflare_edited_from_this_plane"] is False
    assert host["pages_is_not_institute"] is True


def test_competitive_one_pager_does_not_claim_patent():
    cat = load_catalog()
    one = cat["plane_interface"]["competitive"]
    assert one["uncopyable"] is False
    assert one["patent"] is False
    assert one["we_win_only"] == ["consume_once", "fail_closed_sor", "counterparty_ai"]
    job = next(row for row in one["rows"] if row["id"] == "job_c")
    assert job["consume_once"] is True
    copies = [row for row in one["rows"] if row["id"] != "job_c"]
    assert all(row["consume_once"] is False for row in copies)


def test_walk_away_and_billing_stay_honest():
    cat = load_catalog()
    ledger = cat["expert_review"]["success"]["walk_away_ledger"]
    assert ledger["recorded"] is False
    assert ledger["count"] == 0
    assert ledger["items"] == []
    billing = cat["business"]["billing"]
    assert billing["attached"] is False
    assert billing["ninth_complement"] is False


def test_proof_day_ttl_does_not_move_policy_hash():
    lock = default_lockfile()
    assert lock.grant_ttl_seconds is None
    assert lock.policy_hash == "79f359756ac2139053260c06ca6a09e18113059b0ba7d0d67f6b8956e47e98ff"
    out = run_proof_day("ttl-271")
    assert out["grant_ttl_seconds"] == 5400
    assert out["grant_ttl_outside_digest"] is True
    assert out["live_pin_ok"] is False
    assert out["signed_l1"] is False


def test_continuity_rehearsal_is_seat_b_absent():
    cat = load_catalog()
    rehearsal = cat["expert_review"]["success"]["continuity"]["rehearsal"]
    assert rehearsal["seat_missing"] == "seat_b"
    assert rehearsal["write_lands"] is False
    assert rehearsal["sealed_deny"] is True
    html = Path("institute/app.html").read_text(encoding="utf-8")
    assert 'id="app-continuity-btn"' in html


def test_catalog_refuses_271_fiction():
    cat = load_catalog()
    leak = copy.deepcopy(cat)
    for col in leak["plane_interface"]["included_and_upsells"]["first_glance"]["columns"]:
        if col["id"] == "included_with_l1":
            col["items"].append("Estate — same plane: other uses")
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(leak)
    assert exc.value.reason_code == "CATALOG_PLANE"

    pending = copy.deepcopy(cat)
    pending["plane_interface"]["pending_bind"]["count"] = 1
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(pending)
    assert exc2.value.reason_code == "CATALOG_PLANE"

    named = copy.deepcopy(cat)
    named["plane_interface"]["pending_bind"]["named_pair"] = True
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(named)
    assert exc3.value.reason_code == "CATALOG_PLANE"

    wells = copy.deepcopy(cat)
    wells["plane_interface"]["pending_bind"]["seat_a"] = "invented"
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(wells)
    assert exc4.value.reason_code == "CATALOG_PLANE"

    freeze = copy.deepcopy(cat)
    freeze["plane_interface"]["freeze_console"]["live"] = True
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(freeze)
    assert exc5.value.reason_code == "CATALOG_PLANE"

    closed = copy.deepcopy(cat)
    closed["plane_interface"]["freeze_console"]["catalog_plane_stays_open"] = False
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(closed)
    assert exc6.value.reason_code == "CATALOG_PLANE"

    worm = copy.deepcopy(cat)
    worm["plane_interface"]["examiner_walk"]["seventeen_a4"] = True
    with pytest.raises(IntegrityError) as exc7:
        validate_catalog(worm)
    assert exc7.value.reason_code == "CATALOG_GOVERNANCE"

    included = copy.deepcopy(cat)
    included["plane_interface"]["examiner_walk"]["demo"]["included"] = True
    with pytest.raises(IntegrityError) as exc8:
        validate_catalog(included)
    assert exc8.value.reason_code == "CATALOG_PLANE"

    live_g = copy.deepcopy(cat)
    live_g["plane_interface"]["view_assignment"]["entra_groups"]["assignment_live"] = True
    with pytest.raises(IntegrityError) as exc9:
        validate_catalog(live_g)
    assert exc9.value.reason_code == "LIVE_PIN_NOT_CLAIMED"

    head = copy.deepcopy(cat)
    head["plane_interface"]["view_assignment"]["entra_groups"]["templates"][0]["named_head"] = True
    with pytest.raises(IntegrityError) as exc10:
        validate_catalog(head)
    assert exc10.value.reason_code == "CATALOG_PLANE"

    express = copy.deepcopy(cat)
    express["plane_interface"]["motions"]["small_client"]["express_sku"] = True
    with pytest.raises(IntegrityError) as exc11:
        validate_catalog(express)
    assert exc11.value.reason_code == "CATALOG_SKU"

    discount = copy.deepcopy(cat)
    discount["plane_interface"]["motions"]["small_client"]["discount_udual"] = True
    with pytest.raises(IntegrityError) as exc12:
        validate_catalog(discount)
    assert exc12.value.reason_code == "CATALOG_SKU"

    sox = copy.deepcopy(cat)
    sox["plane_interface"]["motions"]["large_client"]["sox"] = True
    with pytest.raises(IntegrityError) as exc13:
        validate_catalog(sox)
    assert exc13.value.reason_code == "CATALOG_GOVERNANCE"

    launch = copy.deepcopy(cat)
    launch["plane_interface"]["hostname_rehearsal"]["launch"] = True
    with pytest.raises(IntegrityError) as exc14:
        validate_catalog(launch)
    assert exc14.value.reason_code == "CATALOG_PLANE"

    asuid = copy.deepcopy(cat)
    asuid["plane_interface"]["hostname_rehearsal"]["asuid_added"] = True
    with pytest.raises(IntegrityError) as exc15:
        validate_catalog(asuid)
    assert exc15.value.reason_code == "CATALOG_PLANE"

    patent = copy.deepcopy(cat)
    patent["plane_interface"]["competitive"]["patent"] = True
    with pytest.raises(IntegrityError) as exc16:
        validate_catalog(patent)
    assert exc16.value.reason_code == "CATALOG_PLANE"

    win = copy.deepcopy(cat)
    for row in win["plane_interface"]["competitive"]["rows"]:
        if row["id"] == "bc_workflow":
            row["consume_once"] = True
    with pytest.raises(IntegrityError) as exc17:
        validate_catalog(win)
    assert exc17.value.reason_code == "CATALOG_PLANE"

    motion = copy.deepcopy(cat)
    motion["equations"]["motion"] = "invented"
    with pytest.raises(IntegrityError) as exc18:
        validate_catalog(motion)
    assert exc18.value.reason_code == "CATALOG_EQUATION"

    iface = copy.deepcopy(cat)
    iface["equations"]["interface"] = iface["equations"]["interface"].replace("pending bind", "bind")
    with pytest.raises(IntegrityError) as exc19:
        validate_catalog(iface)
    assert exc19.value.reason_code == "CATALOG_EQUATION"

    ttl = copy.deepcopy(cat)
    ttl["plane_interface"]["grant_ttl"]["proof_day_seconds"] = 90
    with pytest.raises(IntegrityError) as exc20:
        validate_catalog(ttl)
    assert exc20.value.reason_code == "CATALOG_PLANE"

    rehearsal = copy.deepcopy(cat)
    rehearsal["expert_review"]["success"]["continuity"]["rehearsal"]["write_lands"] = True
    with pytest.raises(IntegrityError) as exc21:
        validate_catalog(rehearsal)
    assert exc21.value.reason_code == "CATALOG_REVIEW"

    fourth = copy.deepcopy(cat)
    fourth["plane_interface"]["motions"]["fourth_sku"] = True
    with pytest.raises(IntegrityError) as exc22:
        validate_catalog(fourth)
    assert exc22.value.reason_code == "CATALOG_SKU"
