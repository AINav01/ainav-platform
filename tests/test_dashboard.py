from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import (
    dashboard_html,
    dashboard_markdown,
    public_dashboard,
    write_dashboard,
)


def test_dashboard_is_honest_and_not_a_sku():
    body = public_dashboard()
    assert body["kind"] == "ainav.plane.interface.v1"
    assert body["sku"] is False
    assert body["live"] is False
    assert body["certified"] is False
    assert body["real_time_claimed"] is False
    assert body["forecast"] is False
    assert body["recorded"] is False
    assert body["invited"] == "Cynthia Hodnett"
    assert {item["id"] for item in body["levels"]} >= {
        "owner",
        "board",
        "seat_a",
        "seat_b",
        "remote",
        "agent",
    }
    assert body["access"]["same_plane"] is True
    assert body["access"]["second_remote_plane"] is False
    assert body["access"]["vpn_sku"] is False
    tiles = {item["id"]: item for item in body["tiles"]}
    assert tiles["recognized_revenue"]["value"] == "$0"
    assert tiles["named_customers"]["value"] == "0"
    assert tiles["signed_l1"]["value"] == "0"
    assert tiles["plane_state"]["tone"] == "ready"
    assert tiles["recognized_revenue"]["tone"] == "hold"
    assert "claimed=false" in tiles["compliance_maps"]["value"]
    assert {item["role"] for item in body["cascade"]} >= {"oversee", "admit", "not_a_seat"}
    assert {item["id"] for item in body["views"]} >= {
        "owner",
        "seats",
        "examiner",
        "remote",
        "provision",
        "records",
        "client",
    }
    assert {item["id"] for item in body["write_path"]} >= {"draft", "seat_a", "seat_b", "keep"}
    assert all(item["claimed"] is False for item in body["lines_of_defense"])
    assert all(item["live"] is False for item in body["coverage"])
    assert body["ledger"]["pending_binds"] == 0
    assert body["clock"]["live_clock_claimed"] is False
    assert body["clock"]["pending_binds"] == 0
    assert body["rehearsal"]["live"] is False
    assert body["rehearsal"]["writes_sor"] is False
    assert body["rehearsal"]["wedge"] == "bc.general_journal.post"
    assert body["rehearsal"]["named_humans"] is False
    assert body["zero_trust"]["identify_is_not_admit"] is True
    assert body["zero_trust"]["ztna_sku"] is False
    assert {item["id"] for item in body["authorizations"]} >= {"identify", "seat", "bind", "revoke"}
    assert all(item["standing"] is False for item in body["authorizations"])
    assert body["provisioning"]["u_dual_never_free"] is True
    assert body["provisioning"]["attached"] == {"L1": 0, "P-ADM": 0, "U-DUAL": 0}
    assert body["client_dashboard"]["sku"] is False
    assert body["client_dashboard"]["upsell"] is False
    assert body["client_dashboard"]["included_with"] == "L1"
    assert body["provision_bands"]["sku"] is False
    band_ids = {item["id"]: item for item in body["provision_bands"]["items"]}
    assert band_ids["provision.standard"]["sku"] is False
    assert band_ids["provision.standard"]["upsell"] is False
    assert band_ids["provision.advanced"]["sku"] is False
    assert band_ids["provision.advanced"]["upsell"] is True
    assert any(item["id"] == "industry.control_plane" for item in body["provision_bands"]["included_l1"])
    assert any(item["id"] == "lib.l1.wedge" for item in body["provision_bands"]["included_l1"])
    assert any(item["id"] == "industry.payables" for item in body["provision_bands"]["priced_l1"])
    assert all(not item["attaches_udual"] for item in body["provision_bands"]["priced_hours"])
    assert body["client_dashboard"]["same_as"] == "dashboard"
    assert body["dashboard"]["same_as"] == "client_dashboard"
    assert body["provision_bands"]["week_one"] == "provisioning.standard_l1"
    assert "included with" in (body["provision_bands"].get("attach_means") or "").lower()
    treasury = next(item for item in body["provision_bands"]["included_l1"] if item["id"] == "industry.treasury")
    assert treasury["attach"] == "included with L1"
    sales = next(item for item in body["provision_bands"]["included_udual"] if item["id"] == "industry.sales")
    assert sales["attach"] == "included with U-DUAL"
    assert sales["band"] == "advanced · with U-DUAL"
    assert treasury["band"] == "standard"
    assert all(
        item["attach"] != "included"
        for item in body["provision_bands"]["included_udual"]
    )
    assert all(
        item["band"] != "advanced"
        for item in body["provision_bands"]["included_udual"]
    )
    assert "with u-dual" in (body["provision_bands"].get("desk_band_means") or "").lower()
    assert all(item["seat"] is False and item["keep"] is False for item in body["communications"])
    assert all(item["certified"] is False for item in body["records"])
    assert all(item["claimed"] is False for item in body["compliance_matrix"])
    tiles = {item["id"]: item for item in body["tiles"]}
    assert tiles["standing_grants"]["value"] == "0"
    assert tiles["provisioned_skus"]["value"] == "0 / 0 / 0"
    assert {item["id"] for item in body["attention"]} >= {"pending", "production", "sandbox_first"}
    assert all(str(item["value"]) == "0" for item in body["attention"] if item["id"] in {"pending", "production"})
    assert {item["id"] for item in body["exceptions"]} >= {"same_seat", "agent_click", "freeze", "replay"}
    assert all(item["live"] is False for item in body["exceptions"])
    admit_yes = {item["id"] for item in body["duties"] if item["admit"] is True}
    assert admit_yes == {"seat_a", "seat_b"}
    agent = next(item for item in body["duties"] if item["id"] == "agent")
    assert agent["admit"] is False
    assert agent["draft"] is False
    md = dashboard_markdown()
    assert "humans sit from the top" in md.lower()
    assert "client executive dashboard" in md.lower()
    assert "standard included" in md.lower() or "included seating" in md.lower()
    assert "upsell band" in md.lower()
    assert "not a sku" in md.lower()
    assert "$0" in md
    assert "same entra" in md.lower() or "same plane" in md.lower()
    assert "throughout the client organization" in md.lower()
    assert "seating cascade" in md.lower()
    html = dashboard_html()
    assert "Executive control-plane dashboard" in html
    assert "OPEN" in html
    assert "Throughout the client organization" in html
    assert "Department AI is not a seat" in html
    assert "data-tone=" in html
    assert "Seating cascade" in html
    assert "Write path" in html
    assert "Hierarchical views" in html
    assert "Three lines of defense" in html
    assert "Duty matrix" in html
    assert "Walkable rehearsal" in html
    assert "Attention board" in html
    assert "Exception paths" in html
    assert "Zero-standing access" in html
    assert "Authorization lifecycle" in html
    assert "Provisioning" in html
    assert "Client executive dashboard" in html
    assert "included with l1" in html.lower()
    assert "upsell band" in html.lower()
    assert "Inter-communication" in html
    assert "Record keeping" in html
    assert "compliance matrix" in html.lower()
    assert "bc.general_journal.post" in html
    assert "live clock claimed=false" in html
    path = write_dashboard()
    assert path.exists()
    assert Path("docs/CONTROL_PLANE.md").exists()


def test_plane_interface_validators_refuse_fiction():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    del missing["plane_interface"]
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(missing)
    assert exc.value.reason_code == "CATALOG_PLANE"
    live = copy.deepcopy(cat)
    live["plane_interface"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)
    sku = copy.deepcopy(cat)
    sku["plane_interface"]["sku"] = True
    with pytest.raises(IntegrityError) as sku_exc:
        validate_catalog(sku)
    assert sku_exc.value.reason_code == "CATALOG_SKU"
    vpn = copy.deepcopy(cat)
    vpn["plane_interface"]["access"]["vpn_sku"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(vpn)
    remote = copy.deepcopy(cat)
    remote["plane_interface"]["access"]["second_remote_plane"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(remote)
    live_clock = copy.deepcopy(cat)
    live_clock["plane_interface"]["clock"]["live_clock_claimed"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live_clock)
    live_reh = copy.deepcopy(cat)
    live_reh["plane_interface"]["rehearsal"]["writes_sor"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live_reh)
    named = copy.deepcopy(cat)
    named["plane_interface"]["rehearsal"]["named_humans"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(named)
    ztna = copy.deepcopy(cat)
    ztna["plane_interface"]["zero_trust"]["ztna_sku"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(ztna)
    free = copy.deepcopy(cat)
    free["plane_interface"]["provisioning"]["u_dual_never_free"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(free)
    dash_sku = copy.deepcopy(cat)
    dash_sku["plane_interface"]["client_dashboard"]["sku"] = True
    with pytest.raises(IntegrityError) as dash_exc:
        validate_catalog(dash_sku)
    assert dash_exc.value.reason_code == "CATALOG_SKU"
    dash_upsell = copy.deepcopy(cat)
    dash_upsell["plane_interface"]["client_dashboard"]["upsell"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(dash_upsell)
    std_sku = copy.deepcopy(cat)
    std_sku["plane_interface"]["provision_bands"]["items"][0]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(std_sku)
    std_upsell = copy.deepcopy(cat)
    std_upsell["plane_interface"]["provision_bands"]["items"][0]["upsell"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(std_upsell)
    adv_sku = copy.deepcopy(cat)
    adv_sku["plane_interface"]["provision_bands"]["items"][1]["sku"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(adv_sku)
    adv_not_upsell = copy.deepcopy(cat)
    adv_not_upsell["plane_interface"]["provision_bands"]["items"][1]["upsell"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(adv_not_upsell)
    free_hours = copy.deepcopy(cat)
    free_hours["plane_interface"]["provision_bands"]["items"][1]["hours_never_attach_udual"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(free_hours)
    two_dash = copy.deepcopy(cat)
    two_dash["plane_interface"]["client_dashboard"]["same_as"] = "another_dashboard"
    with pytest.raises(IntegrityError):
        validate_catalog(two_dash)
    chat = copy.deepcopy(cat)
    chat["plane_interface"]["communications"][0]["seat"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(chat)


def test_institute_control_plane_matches_catalog():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert 'id="control-plane"' in html
    assert "Human control plane" in html
    assert 'id="plane-tiles"' in html
    assert 'id="plane-hierarchy"' in html
    assert 'id="plane-depts"' in html
    assert 'id="plane-maps"' in html
    assert 'id="plane-access-rules"' in html
    assert 'id="plane-cascade"' in html
    assert 'id="plane-strip"' in html
    assert "control-plane.html" in html
    assert "control-plane.json" in js
    assert "plane-depts" in js
    assert "plane-maps" in js
    floor = Path("institute/control-plane.html").read_text(encoding="utf-8")
    assert "Executive control-plane dashboard" in floor
    assert 'id="plane-tiles"' in floor
    assert 'id="plane-cascade"' in floor
    assert 'data-keep="short"' in floor
    assert 'id="plane-path"' in floor
    assert 'id="plane-view-tabs"' in floor
    assert 'id="plane-lod"' in floor
    assert 'id="plane-coverage"' in floor
    assert 'id="plane-console"' in floor
    assert 'id="plane-rehearsal"' in floor
    assert 'id="plane-duties"' in floor
    assert 'id="plane-attention"' in floor
    assert 'id="plane-exceptions"' in floor
    assert 'id="plane-inspector"' in floor
    assert 'id="plane-authorizations"' in floor
    assert 'id="plane-provision"' in floor
    assert 'id="plane-records"' in floor
    assert 'id="plane-bands"' in floor
    assert 'id="plane-desks"' in floor
    assert 'id="plane-week-one"' in floor
    assert 'data-view-tab="provision"' in floor
    assert 'data-view-tab="records"' in floor
    assert 'data-view-tab="client"' in floor
    assert "data-rehearse" in js or "runRehearsal" in js
    assert "Cannot: " in js
    on_disk = json.loads(Path("institute/control-plane.json").read_text(encoding="utf-8"))
    assert on_disk == public_dashboard()
