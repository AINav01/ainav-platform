from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog


def test_graph_writes_revoke_fail_closed_branches():
    cat = load_catalog()
    recorded = copy.deepcopy(cat)
    recorded["microsoft_stack"]["graph"]["owner_recorded"] = ["Grant succeeded. Four Reads Granted."]
    with pytest.raises(IntegrityError):
        validate_catalog(recorded)
    claimed = copy.deepcopy(cat)
    claimed["microsoft_stack"]["graph"]["graph_write_claimed"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(claimed)
    reads = copy.deepcopy(cat)
    reads["microsoft_stack"]["graph"]["four_reads_granted"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(reads)
    missing = copy.deepcopy(cat)
    missing["honest_missing"] = list(missing.get("honest_missing") or []) + ["Graph Writes still Granted"]
    with pytest.raises(IntegrityError):
        validate_catalog(missing)


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
    cat["plane_interface"]["client_dashboard"]["executive_board"] = None
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_dashboard_write_rail_must_match_public_rail():
    cat = copy.deepcopy(load_catalog())
    glance = cat["plane_interface"]["dashboard"]["first_glance"]
    glance["write_rail"] = list(glance.get("write_rail") or [])[:-1]
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_integrate_steps_need_https_and_no_app_id():
    cat = load_catalog()
    https = copy.deepcopy(cat)
    items = https["plane_interface"]["floor"]["integrate"]["items"]
    items[0]["url"] = "http://example.com"
    with pytest.raises(IntegrityError):
        validate_catalog(https)
    app_id = copy.deepcopy(cat)
    items = app_id["plane_interface"]["floor"]["integrate"]["items"]
    items[0]["url"] = "https://entra.microsoft.com/?entra_client_id=2ad041b8"
    with pytest.raises(IntegrityError):
        validate_catalog(app_id)
