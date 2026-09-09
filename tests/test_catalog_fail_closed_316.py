from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import load_catalog, validate_catalog


def test_graph_writes_revoke_fail_closed_branches():
    cat = load_catalog()
    recorded = copy.deepcopy(cat)
    recorded["microsoft_stack"]["graph"]["owner_recorded"] = ["Grant succeeded. Four Reads Granted."]
    with pytest.raises(IntegrityError):
        catmod._validate_graph_writes_revoked(recorded)
    claimed = copy.deepcopy(cat)
    claimed["microsoft_stack"]["graph"]["from_this_plane"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_graph_writes_revoked(claimed)
    reads = copy.deepcopy(cat)
    reads["microsoft_stack"]["graph"]["four_reads_granted"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_graph_writes_revoked(reads)
    opens = copy.deepcopy(cat)
    opens["investor"]["executive_summary"]["opens"] = "Graph Writes still Granted"
    with pytest.raises(IntegrityError):
        catmod._validate_graph_writes_revoked(opens)
    missing = copy.deepcopy(cat)
    missing["honest_missing"] = list(missing.get("honest_missing") or []) + ["Graph Writes still Granted"]
    with pytest.raises(IntegrityError):
        catmod._validate_graph_writes_revoked(missing)


def test_examiner_walk_cannot_invent_named_record():
    cat = copy.deepcopy(load_catalog())
    demo = cat["plane_interface"]["examiner_walk"]["demo"]
    demo["record_id"] = "named.human.record"
    demo["included"] = False
    demo["leaf"] = "named"
    demo["root"] = "owner"
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_launch_day_map_cannot_mark_live_pin():
    cat = copy.deepcopy(load_catalog())
    run = cat["expert_review"]["success"]["operating_company"]["microsoft_run"]
    for item in run.get("day_map") or []:
        if item.get("id") == "launch":
            item["note"] = "Launch day is ready."
            break
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_included_pack_cannot_carry_attach_price():
    cat = copy.deepcopy(load_catalog())
    for pack in cat.get("industry_packs") or []:
        if pack.get("included_in_sku") is True:
            pack["attach_usd"] = {"min": 1000, "max": 2000}
            break
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_view_assignment_must_cover_org_chart():
    cat = copy.deepcopy(load_catalog())
    matrix = cat["plane_interface"]["view_assignment"]["matrix"]
    cat["plane_interface"]["view_assignment"]["matrix"] = list(matrix)[:-1]
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_other_uses_module_must_stay_on_sku():
    cat = copy.deepcopy(load_catalog())
    for module in cat.get("modules") or []:
        if module.get("id") == "bc.general_journal.post":
            module["sku"] = "P-ADM"
            break
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_client_dashboard_needs_executive_board():
    cat = copy.deepcopy(load_catalog())
    cat["plane_interface"]["client_dashboard"]["executive_board"] = ["not-a-board"]
    with pytest.raises(IntegrityError):
        catmod._validate_plane_interface(cat)


def test_dashboard_write_rail_must_match_public_rail():
    cat = copy.deepcopy(load_catalog())
    glance = cat["plane_interface"]["dashboard"]["first_glance"]
    glance["write_rail"] = list(glance.get("write_rail") or [])[:-1]
    with pytest.raises(IntegrityError):
        catmod._validate_plane_interface(cat)


def test_integrate_steps_need_https_and_no_app_id():
    cat = load_catalog()
    https = copy.deepcopy(cat)
    items = https["plane_interface"]["floor"]["integrate"]["items"]
    gates = https["owner_gates"]
    items[0]["url"] = "http://example.com"
    gates[0]["url"] = "http://example.com"
    with pytest.raises(IntegrityError):
        catmod._validate_plane_interface(https)
    app_id = copy.deepcopy(cat)
    items = app_id["plane_interface"]["floor"]["integrate"]["items"]
    gates = app_id["owner_gates"]
    items[0]["url"] = "https://entra.microsoft.com/?entra_client_id=2ad041b8"
    gates[0]["url"] = "https://entra.microsoft.com/?entra_client_id=2ad041b8"
    with pytest.raises(IntegrityError):
        catmod._validate_plane_interface(app_id)


def test_first_principles_keep_honest_ten_stems():
    cat = load_catalog()
    principles = list(cat["expert_review"]["first_principles"])
    gold = [item.replace("Gold 99.9 is not LIVE_PIN_OK.", "Gold stays a target.") for item in principles]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(gold)
    seated = [
        item.replace("A quality check is not a seated second human.", "Quality is recorded.")
        for item in principles
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(seated)


def test_first_principles_keep_honest_protect_stems():
    cat = load_catalog()
    principles = list(cat["expert_review"]["first_principles"])
    patent = [item.replace("An IP board is not a patent.", "Protect is recorded.") for item in principles]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(patent)
    assign = [
        item.replace("An L1 license is not an assignment of Job C.", "License is recorded.")
        for item in principles
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(assign)


def test_industry_pack_cannot_be_a_sku():
    cat = copy.deepcopy(load_catalog())
    cat["industry_packs"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_upsells(cat)


def test_other_uses_desk_must_stay_on_sku():
    cat = copy.deepcopy(load_catalog())
    for module in cat.get("modules") or []:
        if module.get("id") == "d365.invoice.post":
            module["sku"] = "L1"
            break
    with pytest.raises(IntegrityError):
        catmod._validate_plane_interface(cat)


def test_examiner_walk_else_branch_via_plane():
    cat = copy.deepcopy(load_catalog())
    demo = cat["plane_interface"]["examiner_walk"]["demo"]
    demo["record_id"] = ""
    demo["included"] = True
    demo["leaf"] = ""
    demo["root"] = ""
    with pytest.raises(IntegrityError):
        catmod._validate_plane_interface(cat)
