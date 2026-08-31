from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.microsoft.connections import COMPLEMENT_IDS
from ainav.institute_status import public_status


def test_public_status_is_sandbox_and_unclaimed():
    body = public_status()
    assert body["kind"] == "ainav.institute.status.v1"
    assert body["live"] is False
    assert body["bc"]["wedge"] == "bc.general_journal.post"
    assert body["bc"]["sandbox_document"] == "AINAV-L1"
    assert body["sales"]["instances"] == 0
    assert body["custom_domain_claimed"] is False
    assert body["launch_ready"] is False
    assert body["agent_tools"]["is_admit_plane"] is False
    assert body["agent_tools"]["cloud_agent_can_approve"] is False
    assert "workiq.user" in body["agent_tools"]["leave_available"]
    assert "dataverse.mcp" in body["agent_tools"]["block_until_dual"]


def test_public_status_fabric_and_complements_stay_honest():
    body = public_status()
    assert body["fabric"]["live"] is False
    assert "Microsoft is identity" in body["fabric"]["not_the_product"]
    assert "Microsoft 365 Copilot" in body["fabric"]["e7_not_the_product"]
    path_ids = [item["id"] for item in body["fabric"]["path"]]
    assert path_ids == [
        "azure.host",
        "m365.e7",
        "admit",
        "bc.premium",
        "sales.enterprise",
        "teams.enterprise",
        "teams.premium",
    ]
    assert [item["id"] for item in body["complements"]] == list(COMPLEMENT_IDS)
    assert "cloudflare.dns" not in path_ids
    assert body["e7_cloudflare"]["id"] == "cloudflare.dns"
    assert body["e7_cloudflare"]["full"] is True
    assert body["e7_cloudflare"]["complement"] is False
    assert body["e7_cloudflare"]["is_admit_plane"] is False
    assert body["e7_cloudflare"]["live_pin_ok"] is False
    assert body["engineering"]["gold_ci"]["exists"] is True
    assert body["engineering"]["sku"] is False
    assert body["engineering"]["live_pin_ok"] is False
    assert body["engineering"]["launch"] is False
    assert all(item["wired"] is False and item["live"] is False for item in body["complements"])
    pim = next(item for item in body["complements"] if item["id"] == "entra.pim")
    assert "not dual admit" in pim["note"]
    sentinel = next(item for item in body["complements"] if item["id"] == "sentinel.siem")
    assert "not a Sentinel workspace" in sentinel["note"]


def test_public_status_opportunity_is_catalog_list_not_revenue():
    body = public_status()
    opp = body["opportunity"]
    assert opp["recognized_revenue"] is None
    assert opp["named_customers"] == []
    assert opp["signed_l1"] == 0
    assert opp["attached"] == {"L1": 0, "P-ADM": 0, "U-DUAL": 0}
    assert opp["list"]["L1"]["min"] == 28000
    assert opp["year_one_list_if_all_three"]["min"] == 88000
    assert opp["year_one_list_if_all_three"]["max"] == 135000
    assert "Not recognized revenue" in opp["year_one_list_if_all_three"]["note"]


def test_sandbox_evidence_cannot_claim_production():
    cat = copy.deepcopy(load_catalog())
    cat["sandbox_evidence"]["production"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cat)
    assert exc.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    signed = copy.deepcopy(load_catalog())
    signed["sandbox_evidence"]["signed_l1"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(signed)
    assert exc2.value.reason_code == "SIGNED_L1_OPEN"
