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
    assert body["recorded"] is True
    assert body["agreed"] is True
    assert body["email"] == "chodnett@ainav.institute"
    assert body["entra_oid"] is None
    assert body["seat_clicked"] is False
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
    board = body["client_dashboard"]["executive_board"]
    assert board["sku"] is False
    assert board["upsell"] is False
    assert board["included_with"] == "L1"
    assert board["default_view"] == "client"
    assert [item["id"] for item in board["sections"]] == [
        "write_rail",
        "attention",
        "seats",
        "keep",
        "offer",
    ]
    assert "seats_recorded" in board["seat_tile_ids"]
    assert "second_record" in board["keep_tile_ids"]
    assert "signed_l1" in board["tile_ids"]
    assert body["dashboard"]["same_as"] == "client_dashboard"
    dash_glance = body["dashboard"]["first_glance"]
    assert dash_glance["uses"] == "write_rail"
    assert [item["id"] for item in dash_glance["write_rail"]] == ["seat_a", "seat_b", "hash", "write"]
    assert "one dashboard" in dash_glance["lede"].lower()
    assert body["provision_bands"]["week_one"] == "provisioning.standard_l1"
    assert body["must_have"]["mandated"] is False
    assert body["must_have"]["certified"] is False
    assert body["must_have"]["sku"] is False
    assert "write surface" in body["must_have"]["why"].lower()
    assert "unauthorized general-journal" in body["must_have"]["incident"].lower()
    assert "must-have" in (body.get("floor") or {}).get("lede", "").lower()
    assert "already have" in (body.get("floor") or {}).get("lede", "").lower()
    assert "gate" in (body.get("floor") or {}).get("lede", "").lower()
    assert "one dashboard" in (body.get("floor") or {}).get("lede", "").lower()
    assert "business central" in (body.get("floor") or {}).get("already_have", "").lower()
    assert "gate" in (body.get("floor") or {}).get("still_lack", "").lower()
    assert set((body.get("must_have") or {}).get("for") or {}) >= {"owner", "board", "examiner"}
    assert {item["id"] for item in (body.get("floor") or {}).get("not_the_gate") or []} >= {
        "vendor_native",
        "teams",
        "pim",
        "copilot",
    }
    assert "sealed DecisionRecord" in ((body.get("floor") or {}).get("proof_close") or {}).get("walk_out") or []
    assert {item["id"] for item in (body.get("floor") or {}).get("scopes") or []} >= {
        "week_one",
        "included_seating",
        "advanced",
    }
    assert "included with" in (body["provision_bands"].get("attach_means") or "").lower()
    offer = body["included_and_upsells"]
    assert offer["sku"] is False
    assert offer["fourth_sku"] is False
    assert offer["included_means_free"] is False
    assert offer["u_dual_never_free"] is True
    assert offer["hours_never_attach_udual"] is True
    assert [item["id"] for item in offer["first_glance"]["columns"]] == [
        "included_with_l1",
        "upsell_band",
    ]
    assert offer["first_glance"]["columns"][0]["upsell"] is False
    assert offer["first_glance"]["columns"][1]["upsell"] is True
    assert offer["attach_means"] == body["provision_bands"]["attach_means"]
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
    assert {item["id"] for item in body["attention"]} >= {"must_have", "pending", "production", "sandbox_first"}
    assert "write surface" in tiles["must_have"]["note"].lower()
    assert all(str(item["value"]) == "0" for item in body["attention"] if item["id"] in {"pending", "production"})
    assert {item["id"] for item in body["exceptions"]} >= {"same_seat", "agent_click", "freeze", "replay"}
    assert all(item["live"] is False for item in body["exceptions"])
    admit_yes = {item["id"] for item in body["duties"] if item["admit"] is True}
    assert admit_yes == {"seat_a", "seat_b"}
    agent = next(item for item in body["duties"] if item["id"] == "agent")
    assert agent["admit"] is False
    assert agent["draft"] is False
    md = dashboard_markdown()
    assert "why a client must have this" in md.lower()
    assert "write rail" in md.lower()
    assert "one dashboard" in md.lower()
    assert "already have" in md.lower()
    assert "must-have for owner, board, examiner" in md.lower()
    assert "not the gate" in md.lower()
    assert "success program" in md.lower()
    assert "they win when" in md.lower()
    assert "walk away" in md.lower()
    assert "objection cards" in md.lower()
    assert "ciso posture" in md.lower()
    assert "seat b meaning" in md.lower()
    assert "one seat missing" in md.lower()
    assert body["success"]["live_pin_ok"] is False
    assert body["success"]["seat_b"]["mailbox"] == "chodnett@ainav.institute"
    assert "walk-away" in (body.get("success_equation") or "")
    assert "walk out" in md.lower()
    assert "what no does" in md.lower()
    assert "the product is the admit plane" in md.lower()
    assert "the sale is the ninety-minute proof" in md.lower()
    assert "who may admit, freeze, keep" in md.lower()
    assert "lab oids are not two named" in md.lower()
    assert "disclaimer, attestation, and protection" in md.lower()
    assert "cannot weaken job c" in md.lower()
    assert "not a signature" in md.lower()
    assert "institutional memory" in md.lower()
    assert "two records and a keep" in md.lower()
    assert "not a time machine" in md.lower()
    assert "complete the stack" in md.lower()
    assert "cannot create users" in md.lower()
    assert "admin.microsoft.com" in md
    assert "humans sit from the top" in md.lower()
    assert "client executive dashboard" in md.lower()
    assert "standard included" in md.lower() or "included seating" in md.lower()
    assert "upsell band" in md.lower()
    assert "sit the plane" in md.lower()
    assert "not a gift" in md.lower() or "included with l1 · upsell band" in md.lower()
    assert "not a sku" in md.lower()
    assert "$0" in md
    assert "same entra" in md.lower() or "same plane" in md.lower()
    assert "throughout the client organization" in md.lower()
    assert "seating cascade" in md.lower()
    html = dashboard_html()
    assert "Write rail — one dashboard" in html
    assert "Seat A" in html
    assert "Then the write" in html
    assert "Success program — bake-off" in html
    assert "They win when" in html
    assert "We win when" in html
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
    assert "Included with L1 · upsell band" in html
    assert "Executive board — sit the plane" in html
    assert "sit the plane" in html.lower()
    assert "not a gift" in html.lower()
    assert "fourth sku" in html.lower()
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
    offer_sku = copy.deepcopy(cat)
    offer_sku["plane_interface"]["included_and_upsells"]["sku"] = True
    with pytest.raises(IntegrityError) as offer_exc:
        validate_catalog(offer_sku)
    assert offer_exc.value.reason_code == "CATALOG_SKU"
    offer_free = copy.deepcopy(cat)
    offer_free["plane_interface"]["included_and_upsells"]["included_means_free"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(offer_free)
    offer_fourth = copy.deepcopy(cat)
    offer_fourth["plane_interface"]["included_and_upsells"]["fourth_sku"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(offer_fourth)
    offer_col = copy.deepcopy(cat)
    offer_col["plane_interface"]["included_and_upsells"]["first_glance"]["columns"][0]["upsell"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(offer_col)
    board_sku = copy.deepcopy(cat)
    board_sku["plane_interface"]["client_dashboard"]["executive_board"]["sku"] = True
    with pytest.raises(IntegrityError) as board_exc:
        validate_catalog(board_sku)
    assert board_exc.value.reason_code == "CATALOG_SKU"
    board_view = copy.deepcopy(cat)
    board_view["plane_interface"]["client_dashboard"]["executive_board"]["default_view"] = "entire"
    with pytest.raises(IntegrityError):
        validate_catalog(board_view)
    two_dash = copy.deepcopy(cat)
    two_dash["plane_interface"]["client_dashboard"]["same_as"] = "another_dashboard"
    with pytest.raises(IntegrityError):
        validate_catalog(two_dash)
    no_lede = copy.deepcopy(cat)
    no_lede["plane_interface"]["floor"]["lede"] = "two dashboards"
    with pytest.raises(IntegrityError):
        validate_catalog(no_lede)
    mandated = copy.deepcopy(cat)
    mandated["plane_interface"]["floor"]["must_have"]["mandated"] = True
    with pytest.raises(IntegrityError) as must_exc:
        validate_catalog(mandated)
    assert must_exc.value.reason_code == "CATALOG_GOVERNANCE"
    no_must = copy.deepcopy(cat)
    no_must["plane_interface"]["floor"]["lede"] = "One dashboard included with L1 — not an upsell."
    with pytest.raises(IntegrityError):
        validate_catalog(no_must)
    why = copy.deepcopy(cat)
    why["plane_interface"]["floor"]["must_have"]["why"] = "invented mandate"
    with pytest.raises(IntegrityError):
        validate_catalog(why)
    incident = copy.deepcopy(cat)
    incident["plane_interface"]["floor"]["must_have"]["incident"] = "invented inbox"
    with pytest.raises(IntegrityError):
        validate_catalog(incident)
    job = copy.deepcopy(cat)
    job["plane_interface"]["floor"]["must_have"]["job_c_plain"] = "action_hash jargon"
    with pytest.raises(IntegrityError):
        validate_catalog(job)
    eq = copy.deepcopy(cat)
    eq["equations"]["interface"] = cat["equations"]["interface"].replace("must-have × ", "")
    with pytest.raises(IntegrityError):
        validate_catalog(eq)
    refuse = copy.deepcopy(cat)
    refuse["plane_interface"]["refuse"] = [
        item for item in cat["plane_interface"]["refuse"] if "must-have" not in str(item).lower()
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(refuse)
    attn = copy.deepcopy(cat)
    attn["plane_interface"]["attention"] = [
        item for item in cat["plane_interface"]["attention"] if item.get("id") != "must_have"
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(attn)
    no_have = copy.deepcopy(cat)
    no_have["plane_interface"]["floor"]["already_have"] = "they have Copilot"
    with pytest.raises(IntegrityError):
        validate_catalog(no_have)
    no_gate = copy.deepcopy(cat)
    no_gate["plane_interface"]["floor"]["still_lack"] = "they lack a dashboard"
    with pytest.raises(IntegrityError):
        validate_catalog(no_gate)
    audience = copy.deepcopy(cat)
    audience["plane_interface"]["floor"]["must_have"]["for"]["board"] = "invented mandate"
    with pytest.raises(IntegrityError):
        validate_catalog(audience)
    no_teams = copy.deepcopy(cat)
    no_teams["plane_interface"]["floor"]["not_the_gate"] = [
        item for item in cat["plane_interface"]["floor"]["not_the_gate"] if item.get("id") != "teams"
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(no_teams)
    bad_walk = copy.deepcopy(cat)
    bad_walk["plane_interface"]["floor"]["proof_close"]["walk_out"] = ["invented certificate"]
    with pytest.raises(IntegrityError):
        validate_catalog(bad_walk)
    company_first = copy.deepcopy(cat)
    company_first["plane_interface"]["floor"]["page"]["product_first"] = False
    with pytest.raises(IntegrityError):
        validate_catalog(company_first)
    twin_ms = copy.deepcopy(cat)
    twin_ms["plane_interface"]["floor"]["page"]["twin_is"] = "Microsoft is the product"
    with pytest.raises(IntegrityError):
        validate_catalog(twin_ms)
    bad_sale = copy.deepcopy(cat)
    bad_sale["plane_interface"]["floor"]["page"]["sale"] = "invented six-month RFP"
    with pytest.raises(IntegrityError):
        validate_catalog(bad_sale)
    bad_path = copy.deepcopy(cat)
    bad_path["plane_interface"]["floor"]["page"]["product_path"] = ["opportunity", "org"]
    with pytest.raises(IntegrityError):
        validate_catalog(bad_path)
    no_admit = copy.deepcopy(cat)
    no_admit["plane_interface"]["floor"]["accountable"]["items"] = [
        item
        for item in cat["plane_interface"]["floor"]["accountable"]["items"]
        if item.get("id") != "admit"
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(no_admit)
    bad_keep = copy.deepcopy(cat)
    bad_keep["plane_interface"]["floor"]["accountable"]["items"][2]["note"] = "invented filing"
    with pytest.raises(IntegrityError):
        validate_catalog(bad_keep)
    lab_as_seat = copy.deepcopy(cat)
    lab_as_seat["plane_interface"]["floor"]["accountable"]["items"][3]["note"] = "lab oids are the seats"
    with pytest.raises(IntegrityError):
        validate_catalog(lab_as_seat)
    no_duty = copy.deepcopy(cat)
    no_duty["plane_interface"]["floor"]["accountable"]["lede"] = "invented RACI"
    with pytest.raises(IntegrityError):
        validate_catalog(no_duty)
    bad_admit = copy.deepcopy(cat)
    bad_admit["plane_interface"]["floor"]["accountable"]["items"][0]["note"] = "anyone may admit"
    with pytest.raises(IntegrityError):
        validate_catalog(bad_admit)
    owner_seat = copy.deepcopy(cat)
    owner_seat["plane_interface"]["floor"]["accountable"]["items"][1]["note"] = "owner clicks both admits"
    with pytest.raises(IntegrityError):
        validate_catalog(owner_seat)
    drop_attest = copy.deepcopy(cat)
    drop_attest["plane_interface"]["floor"]["protect"]["items"] = [
        item
        for item in cat["plane_interface"]["floor"]["protect"]["items"]
        if item.get("id") != "attest"
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(drop_attest)
    mismatch_attest = copy.deepcopy(cat)
    mismatch_attest["plane_interface"]["floor"]["protect"]["items"][1]["note"] = "Signed certificate of dual admit."
    with pytest.raises(IntegrityError):
        validate_catalog(mismatch_attest)
    weaken_policy = copy.deepcopy(cat)
    weaken_policy["plane_interface"]["floor"]["protect"]["items"][2]["note"] = "Host policy. May weaken Job C."
    with pytest.raises(IntegrityError):
        validate_catalog(weaken_policy)
    bad_update = copy.deepcopy(cat)
    bad_update["plane_interface"]["floor"]["protect"]["items"][3]["note"] = "A rebrand is fine."
    with pytest.raises(IntegrityError):
        validate_catalog(bad_update)
    no_disc = copy.deepcopy(cat)
    no_disc["plane_interface"]["floor"]["protect"]["lede"] = "this page is a certificate"
    with pytest.raises(IntegrityError):
        validate_catalog(no_disc)
    unsigned = copy.deepcopy(cat)
    unsigned["plane_interface"]["floor"]["protect"]["items"][0]["note"] = "this tree certifies"
    with pytest.raises(IntegrityError):
        validate_catalog(unsigned)
    no_protect_refuse = copy.deepcopy(cat)
    no_protect_refuse["plane_interface"]["refuse"] = [
        item
        for item in cat["plane_interface"]["refuse"]
        if "update weakens job c" not in str(item).lower()
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(no_protect_refuse)
    no_cert_refuse = copy.deepcopy(cat)
    no_cert_refuse["plane_interface"]["refuse"] = [
        item
        for item in cat["plane_interface"]["refuse"]
        if "this page as a certificate" not in str(item).lower()
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(no_cert_refuse)
    drop_memory_first = copy.deepcopy(cat)
    drop_memory_first["plane_interface"]["floor"]["memory"]["items"] = [
        item
        for item in cat["plane_interface"]["floor"]["memory"]["items"]
        if item.get("id") != "first"
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(drop_memory_first)
    mismatch_memory_first = copy.deepcopy(cat)
    mismatch_memory_first["plane_interface"]["floor"]["memory"]["items"][0]["note"] = "invented ledger"
    with pytest.raises(IntegrityError):
        validate_catalog(mismatch_memory_first)
    mismatch_memory_keep = copy.deepcopy(cat)
    mismatch_memory_keep["plane_interface"]["floor"]["memory"]["items"][1]["note"] = "a chat is the keep"
    with pytest.raises(IntegrityError):
        validate_catalog(mismatch_memory_keep)
    mismatch_memory_reset = copy.deepcopy(cat)
    mismatch_memory_reset["plane_interface"]["floor"]["memory"]["items"][2]["note"] = "reset wipes production"
    with pytest.raises(IntegrityError):
        validate_catalog(mismatch_memory_reset)
    time_machine = copy.deepcopy(cat)
    time_machine["plane_interface"]["floor"]["memory"]["items"][3]["note"] = "silent undo"
    with pytest.raises(IntegrityError):
        validate_catalog(time_machine)
    no_memory_lede = copy.deepcopy(cat)
    no_memory_lede["plane_interface"]["floor"]["memory"]["lede"] = "invented archive"
    with pytest.raises(IntegrityError):
        validate_catalog(no_memory_lede)
    no_mailbox_refuse = copy.deepcopy(cat)
    no_mailbox_refuse["plane_interface"]["refuse"] = [
        item
        for item in cat["plane_interface"]["refuse"]
        if "mailbox as the second record" not in str(item).lower()
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(no_mailbox_refuse)
    drop_integrate = copy.deepcopy(cat)
    drop_integrate["plane_interface"]["floor"]["integrate"]["items"] = [
        item
        for item in cat["plane_interface"]["floor"]["integrate"]["items"]
        if item.get("id") != "invite.seat_b"
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(drop_integrate)
    drift_integrate = copy.deepcopy(cat)
    drift_integrate["plane_interface"]["floor"]["integrate"]["items"][0]["url"] = "https://example.com"
    with pytest.raises(IntegrityError):
        validate_catalog(drift_integrate)
    no_new_app_refuse = copy.deepcopy(cat)
    no_new_app_refuse["plane_interface"]["refuse"] = [
        item
        for item in cat["plane_interface"]["refuse"]
        if "new entra app" not in str(item).lower()
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(no_new_app_refuse)
    no_lab_refuse = copy.deepcopy(cat)
    no_lab_refuse["plane_interface"]["refuse"] = [
        item for item in cat["plane_interface"]["refuse"] if "lab oids" not in str(item).lower()
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(no_lab_refuse)
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
    assert 'id="plane-write-rail"' in floor
    assert 'id="plane-dash-lede"' in floor
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
    assert 'id="plane-page-first"' in floor
    assert "ninety-minute proof" in floor
    assert "seat A · seat B" in floor
    assert "owner / board request" in floor
    assert "not a certificate" in floor
    assert "cannot weaken Job C" in floor
    assert "last sealed keep" in floor
    assert "not a time machine" in floor
    assert "owner clicks" in floor
    assert "same Entra app" in floor
    assert 'id="plane-authorizations"' in floor
    assert 'id="plane-provision"' in floor
    assert 'id="plane-records"' in floor
    assert 'id="plane-bands"' in floor
    assert 'id="plane-desks"' in floor
    assert 'id="plane-week-one"' in floor
    assert 'id="plane-scopes"' in floor
    assert 'data-view-tab="client"' in floor
    assert 'data-view-tab="provision"' in floor
    assert 'data-view-tab="records"' in floor
    assert 'data-view-tab="client"' in floor
    assert "data-rehearse" in js or "runRehearsal" in js
    assert "Cannot: " in js
    on_disk = json.loads(Path("institute/control-plane.json").read_text(encoding="utf-8"))
    assert on_disk == public_dashboard()
