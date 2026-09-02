from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav.business import KitEvidence, OperatingCompany, doctrine
from ainav.catalog import load_catalog, validate_catalog
from ainav.errors import LivePinError, ProvisionError
from ainav.microsoft.azure import AzureHost
from ainav.microsoft.connections import COMPLEMENT_IDS


def test_business_model_stays_three_skus():
    body = doctrine()
    assert body["model"]["prove"] == "L1"
    assert body["model"]["keep"] == "P-ADM"
    assert body["model"]["deepen"] == "U-DUAL"
    assert body["economics"]["recognized_revenue_claimed"] is False
    assert "control plane" in body["elevator"]["ten"].lower()
    assert "ninety" in body["elevator"]["thirty"].lower()
    assert "gate in front of the write" in body["why_client"].lower()
    assert "priced round" in body["why_investor"].lower()
    assert body["model"]["estate"] == "same plane"
    assert body["model"]["audit"] == "same plane"
    assert body["model"]["regulated"] == "room 1 books, room 2 refuse"
    assert "failsafe" in body["thesis"].lower()


def test_operating_company_runs_the_spine():
    company = OperatingCompany()
    won = company.run_standard_engagement("acme")
    company.qualify("prospect")
    snap = company.management_snapshot()
    assert snap["live"] is False
    assert snap["economics"]["recognized_revenue"] is None
    assert snap["economics"]["contracted_catalog_min"] == 28000 + 40000 + 20000
    assert won.stage == "U_DUAL_ATTACH"
    assert "industry.controller" in won.local.industry
    assert "industry.quote_desk" in won.local.industry
    assert company.evidence.stored[0]["connection"] == "sharepoint.kit"
    runbook = company.delivery_runbook(won)
    assert "refuse live pin" in runbook["steps"]
    stages = {item["stage"] for item in snap["pipeline"]}
    assert "QUALIFY" in stages
    assert "U_DUAL_ATTACH" in stages


def test_kit_evidence_and_complements_are_sandbox():
    with pytest.raises(LivePinError):
        KitEvidence().live_upload()
    host = AzureHost()
    assert host.plan_keyvault()["connection"] == "azure.keyvault"
    assert host.plan_monitor()["sent"] is False
    cat = load_catalog()
    assert [item["id"] for item in cat["connections"]["complements"]] == list(COMPLEMENT_IDS)


def test_catalog_rejects_claimed_revenue():
    cat = load_catalog()
    broken = copy.deepcopy(cat)
    broken["business"]["economics"]["recognized_revenue_claimed"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(broken)
    assert exc.value.reason_code == "REVENUE_NOT_CLAIMED"


def test_catalog_rejects_audit_as_sku_and_room_2_as_buy():
    cat = load_catalog()
    audit_sku = copy.deepcopy(cat)
    audit_sku["business"]["model"]["audit"] = "fourth sku"
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(audit_sku)
    assert exc.value.reason_code == "CATALOG_SKU"
    room2 = copy.deepcopy(cat)
    room2["business"]["model"]["regulated"] = "lead with mint"
    with pytest.raises(IntegrityError) as room_exc:
        validate_catalog(room2)
    assert room_exc.value.reason_code == "CATALOG_BUSINESS"


def test_kit_evidence_refuses_before_pass():
    company = OperatingCompany()
    account = company.qualify("early")
    with pytest.raises(ProvisionError):
        company.store_kit_evidence(account)


def test_cli_company_demo(capsys):
    from ainav.__main__ import main

    assert main(["company-demo"]) == 0
    out = capsys.readouterr().out
    assert "sharepoint.kit" in out
    assert "industry.controller" in out
    assert "recognized_revenue" in out
