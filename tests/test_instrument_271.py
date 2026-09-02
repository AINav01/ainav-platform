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
    assert cat["entity"]["release"] == "2.74.0"
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
    assert walk["demo"]["lab"] is True
    assert walk["demo"]["record_id"] == "lab.demo.inclusion"
    assert walk["demo"]["included"] is True
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
    included["plane_interface"]["examiner_walk"]["demo"]["included"] = False
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

    drawer = copy.deepcopy(cat)
    for col in drawer["plane_interface"]["included_and_upsells"]["first_glance"]["columns"]:
        if col["id"] == "included_with_l1":
            col["items"] = [item for item in col["items"] if "encyclopedia" not in item.lower()]
    with pytest.raises(IntegrityError) as exc23:
        validate_catalog(drawer)
    assert exc23.value.reason_code == "CATALOG_PLANE"

    shows = copy.deepcopy(cat)
    shows["plane_interface"]["proof_day_floor"]["client_shows"] = [
        item for item in shows["plane_interface"]["proof_day_floor"]["client_shows"] if item != "pending_bind"
    ]
    with pytest.raises(IntegrityError) as exc24:
        validate_catalog(shows)
    assert exc24.value.reason_code == "CATALOG_PLANE"

    exam = copy.deepcopy(cat)
    exam["plane_interface"]["proof_day_floor"]["examiner_shows"] = ["estate", "audit"]
    with pytest.raises(IntegrityError) as exc25:
        validate_catalog(exam)
    assert exc25.value.reason_code == "CATALOG_PLANE"

    owner = copy.deepcopy(cat)
    owner["plane_interface"]["proof_day_floor"]["owner_shows"] = ["govern", "estate", "audit"]
    with pytest.raises(IntegrityError) as exc26:
        validate_catalog(owner)
    assert exc26.value.reason_code == "CATALOG_PLANE"

    cont = copy.deepcopy(cat)
    cont["plane_interface"]["proof_day_floor"]["seats_shows"] = []
    cont["plane_interface"]["proof_day_floor"]["entire_shows"] = ["board", "govern", "estate", "audit"]
    with pytest.raises(IntegrityError) as exc27:
        validate_catalog(cont)
    assert exc27.value.reason_code == "CATALOG_PLANE"

    missing_p = copy.deepcopy(cat)
    missing_p["plane_interface"]["pending_bind"] = True
    with pytest.raises(IntegrityError) as exc28:
        validate_catalog(missing_p)
    assert exc28.value.reason_code == "CATALOG_PLANE"

    live_p = copy.deepcopy(cat)
    live_p["plane_interface"]["pending_bind"]["live"] = True
    with pytest.raises(IntegrityError) as exc29:
        validate_catalog(live_p)
    assert exc29.value.reason_code == "CATALOG_PLANE"

    wedge = copy.deepcopy(cat)
    wedge["plane_interface"]["pending_bind"]["action_class"] = "invented.write"
    with pytest.raises(IntegrityError) as exc30:
        validate_catalog(wedge)
    assert exc30.value.reason_code == "CATALOG_PLANE"

    refuse = copy.deepcopy(cat)
    refuse["plane_interface"]["pending_bind"]["refuse"] = False
    with pytest.raises(IntegrityError) as exc31:
        validate_catalog(refuse)
    assert exc31.value.reason_code == "CATALOG_PLANE"

    no_freeze = copy.deepcopy(cat)
    no_freeze["plane_interface"]["freeze_console"] = True
    with pytest.raises(IntegrityError) as exc32:
        validate_catalog(no_freeze)
    assert exc32.value.reason_code == "CATALOG_PLANE"

    verb = copy.deepcopy(cat)
    verb["plane_interface"]["freeze_console"]["verb"] = "execute"
    with pytest.raises(IntegrityError) as exc33:
        validate_catalog(verb)
    assert exc33.value.reason_code == "CATALOG_PLANE"

    local = copy.deepcopy(cat)
    local["plane_interface"]["freeze_console"]["local_to_browser"] = False
    with pytest.raises(IntegrityError) as exc34:
        validate_catalog(local)
    assert exc34.value.reason_code == "CATALOG_PLANE"

    infer = copy.deepcopy(cat)
    infer["plane_interface"]["freeze_console"]["consequence_does_not"] = False
    with pytest.raises(IntegrityError) as exc35:
        validate_catalog(infer)
    assert exc35.value.reason_code == "CATALOG_PLANE"

    no_walk = copy.deepcopy(cat)
    no_walk["plane_interface"]["examiner_walk"] = True
    with pytest.raises(IntegrityError) as exc36:
        validate_catalog(no_walk)
    assert exc36.value.reason_code == "CATALOG_PLANE"

    walk_sku = copy.deepcopy(cat)
    walk_sku["plane_interface"]["examiner_walk"]["sku"] = True
    with pytest.raises(IntegrityError) as exc37:
        validate_catalog(walk_sku)
    assert exc37.value.reason_code == "CATALOG_PLANE"

    ro = copy.deepcopy(cat)
    ro["plane_interface"]["examiner_walk"]["read_only"] = False
    with pytest.raises(IntegrityError) as exc38:
        validate_catalog(ro)
    assert exc38.value.reason_code == "CATALOG_PLANE"

    named_r = copy.deepcopy(cat)
    named_r["plane_interface"]["examiner_walk"]["named_records"] = 1
    with pytest.raises(IntegrityError) as exc39:
        validate_catalog(named_r)
    assert exc39.value.reason_code == "CATALOG_PLANE"

    invent = copy.deepcopy(cat)
    invent["plane_interface"]["examiner_walk"]["demo"]["record_id"] = "invented"
    with pytest.raises(IntegrityError) as exc40:
        validate_catalog(invent)
    assert exc40.value.reason_code == "CATALOG_PLANE"

    no_g = copy.deepcopy(cat)
    no_g["plane_interface"]["view_assignment"]["entra_groups"] = True
    with pytest.raises(IntegrityError) as exc41:
        validate_catalog(no_g)
    assert exc41.value.reason_code == "CATALOG_PLANE"

    heads = copy.deepcopy(cat)
    heads["plane_interface"]["view_assignment"]["entra_groups"]["named_head"] = True
    with pytest.raises(IntegrityError) as exc42:
        validate_catalog(heads)
    assert exc42.value.reason_code == "CATALOG_PLANE"

    agent = copy.deepcopy(cat)
    agent["plane_interface"]["view_assignment"]["entra_groups"]["cloud_agent_cannot_assign"] = False
    with pytest.raises(IntegrityError) as exc43:
        validate_catalog(agent)
    assert exc43.value.reason_code == "CATALOG_PLANE"

    empty_t = copy.deepcopy(cat)
    empty_t["plane_interface"]["view_assignment"]["entra_groups"]["templates"] = []
    with pytest.raises(IntegrityError) as exc44:
        validate_catalog(empty_t)
    assert exc44.value.reason_code == "CATALOG_PLANE"

    bad_t = copy.deepcopy(cat)
    bad_t["plane_interface"]["view_assignment"]["entra_groups"]["templates"] = ["invented"]
    with pytest.raises(IntegrityError) as exc45:
        validate_catalog(bad_t)
    assert exc45.value.reason_code == "CATALOG_PLANE"

    fields = copy.deepcopy(cat)
    fields["plane_interface"]["view_assignment"]["entra_groups"]["templates"][0]["group"] = ""
    with pytest.raises(IntegrityError) as exc46:
        validate_catalog(fields)
    assert exc46.value.reason_code == "CATALOG_PLANE"

    stem = copy.deepcopy(cat)
    stem["plane_interface"]["view_assignment"]["refuse"] = [
        item
        for item in stem["plane_interface"]["view_assignment"]["refuse"]
        if "entra group" not in item.lower()
    ]
    with pytest.raises(IntegrityError) as exc47:
        validate_catalog(stem)
    assert exc47.value.reason_code == "CATALOG_PLANE"

    no_m = copy.deepcopy(cat)
    no_m["plane_interface"]["motions"] = True
    with pytest.raises(IntegrityError) as exc48:
        validate_catalog(no_m)
    assert exc48.value.reason_code == "CATALOG_PLANE"

    mins = copy.deepcopy(cat)
    mins["plane_interface"]["motions"]["small_client"]["minutes"] = 30
    with pytest.raises(IntegrityError) as exc49:
        validate_catalog(mins)
    assert exc49.value.reason_code == "CATALOG_PLANE"

    price = copy.deepcopy(cat)
    price["plane_interface"]["motions"]["small_client"]["price_usd"]["min"] = 1
    with pytest.raises(IntegrityError) as exc50:
        validate_catalog(price)
    assert exc50.value.reason_code == "CATALOG_PLANE"

    walk_away = copy.deepcopy(cat)
    walk_away["plane_interface"]["motions"]["small_client"]["walk_away_if"] = "cheaper"
    with pytest.raises(IntegrityError) as exc51:
        validate_catalog(walk_away)
    assert exc51.value.reason_code == "CATALOG_PLANE"

    cert = copy.deepcopy(cat)
    cert["plane_interface"]["motions"]["large_client"]["certificate"] = True
    with pytest.raises(IntegrityError) as exc52:
        validate_catalog(cert)
    assert exc52.value.reason_code == "CATALOG_GOVERNANCE"

    three = copy.deepcopy(cat)
    three["plane_interface"]["motions"]["large_client"]["g12_open"] = False
    with pytest.raises(IntegrityError) as exc53:
        validate_catalog(three)
    assert exc53.value.reason_code == "CATALOG_PLANE"

    packet = copy.deepcopy(cat)
    packet["plane_interface"]["motions"]["large_client"]["counsel_ready"]["order_form"] = False
    with pytest.raises(IntegrityError) as exc54:
        validate_catalog(packet)
    assert exc54.value.reason_code == "CATALOG_PLANE"

    no_h = copy.deepcopy(cat)
    no_h["plane_interface"]["hostname_rehearsal"] = True
    with pytest.raises(IntegrityError) as exc55:
        validate_catalog(no_h)
    assert exc55.value.reason_code == "CATALOG_PLANE"

    pages = copy.deepcopy(cat)
    pages["plane_interface"]["hostname_rehearsal"]["pages_is_not_institute"] = False
    with pytest.raises(IntegrityError) as exc56:
        validate_catalog(pages)
    assert exc56.value.reason_code == "CATALOG_PLANE"

    cut = copy.deepcopy(cat)
    cut["plane_interface"]["hostname_rehearsal"]["cutover"] = ["SWA as origin"]
    with pytest.raises(IntegrityError) as exc57:
        validate_catalog(cut)
    assert exc57.value.reason_code == "CATALOG_PLANE"

    no_c = copy.deepcopy(cat)
    no_c["plane_interface"]["competitive"] = True
    with pytest.raises(IntegrityError) as exc58:
        validate_catalog(no_c)
    assert exc58.value.reason_code == "CATALOG_PLANE"

    live_c = copy.deepcopy(cat)
    live_c["plane_interface"]["competitive"]["live"] = True
    with pytest.raises(IntegrityError) as exc59:
        validate_catalog(live_c)
    assert exc59.value.reason_code == "CATALOG_PLANE"

    wins = copy.deepcopy(cat)
    wins["plane_interface"]["competitive"]["we_win_only"] = ["independence"]
    with pytest.raises(IntegrityError) as exc60:
        validate_catalog(wins)
    assert exc60.value.reason_code == "CATALOG_PLANE"

    cols = copy.deepcopy(cat)
    cols["plane_interface"]["competitive"]["columns"] = ["covers_this_vendor"]
    with pytest.raises(IntegrityError) as exc61:
        validate_catalog(cols)
    assert exc61.value.reason_code == "CATALOG_PLANE"

    rows = copy.deepcopy(cat)
    rows["plane_interface"]["competitive"]["rows"] = [
        item for item in rows["plane_interface"]["competitive"]["rows"] if item["id"] != "pim"
    ]
    with pytest.raises(IntegrityError) as exc62:
        validate_catalog(rows)
    assert exc62.value.reason_code == "CATALOG_PLANE"

    job = copy.deepcopy(cat)
    for row in job["plane_interface"]["competitive"]["rows"]:
        if row["id"] == "job_c":
            row["counterparty_ai"] = False
    with pytest.raises(IntegrityError) as exc63:
        validate_catalog(job)
    assert exc63.value.reason_code == "CATALOG_PLANE"

    claim = copy.deepcopy(cat)
    claim["plane_interface"]["competitive"]["note"] = "This is uncopyable."
    with pytest.raises(IntegrityError) as exc64:
        validate_catalog(claim)
    assert exc64.value.reason_code == "CATALOG_PLANE"

    no_r = copy.deepcopy(cat)
    no_r["expert_review"]["success"]["continuity"]["rehearsal"] = {}
    with pytest.raises(IntegrityError) as exc65:
        validate_catalog(no_r)
    assert exc65.value.reason_code == "CATALOG_REVIEW"

    live_r = copy.deepcopy(cat)
    live_r["expert_review"]["success"]["continuity"]["rehearsal"]["live"] = True
    with pytest.raises(IntegrityError) as exc66:
        validate_catalog(live_r)
    assert exc66.value.reason_code == "CATALOG_REVIEW"

    seat = copy.deepcopy(cat)
    seat["expert_review"]["success"]["continuity"]["rehearsal"]["seat_missing"] = "seat_a"
    with pytest.raises(IntegrityError) as exc67:
        validate_catalog(seat)
    assert exc67.value.reason_code == "CATALOG_REVIEW"

    ttl_m = copy.deepcopy(cat)
    ttl_m["proof_day"]["grant_ttl_seconds"] = 90
    with pytest.raises(IntegrityError) as exc68:
        validate_catalog(ttl_m)
    assert exc68.value.reason_code == "CATALOG_PLANE"

    lab = copy.deepcopy(cat)
    lab["proof_day"]["lab_oids_are_not_named_seats"] = False
    with pytest.raises(IntegrityError) as exc69:
        validate_catalog(lab)
    assert exc69.value.reason_code == "CATALOG_PLANE"

    audit_leak = copy.deepcopy(cat)
    for col in audit_leak["plane_interface"]["included_and_upsells"]["first_glance"]["columns"]:
        if col["id"] == "included_with_l1":
            col["items"] = [item for item in col["items"] if "encyclopedia" in item.lower()]
            col["items"].append("Audit — same plane: regulator archive")
    with pytest.raises(IntegrityError) as exc70:
        validate_catalog(audit_leak)
    assert exc70.value.reason_code == "CATALOG_PLANE"
