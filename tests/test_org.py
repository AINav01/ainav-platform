from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.org import REQUIRED_DEPT_IDS, _wired_now, org_report, organization, public_org, validate_organization


def test_organization_is_full_service_and_honest():
    body = organization()
    assert body["full_service"] is True
    assert body["all_wired_claimed"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["second_officer"] is None
    assert body["incorporation_date"] is None
    assert body["contacts"]["second_unique_human"] is False
    assert [item["id"] for item in body["departments"]] == list(REQUIRED_DEPT_IDS)
    assert body["sku"] is False
    statuses = {item["id"]: item["status"] for item in body["departments"]}
    assert statuses["dept.treasury"] == "running_sandbox"
    assert statuses["dept.identity"] == "running_sandbox"
    assert statuses["dept.sales"] == "licensed_not_wired"
    assert statuses["dept.people"] == "licensed_not_wired"
    assert statuses["dept.institute"] == "in_repo_not_public"
    assert statuses["dept.legal"] == "open_gap"
    assert statuses["dept.product"] == "running_code"
    assert statuses["dept.programs"] == "qualify_not_claimed"


def test_org_report_does_not_claim_all_wired():
    report = org_report(probe=False)
    assert report["kind"] == "ainav.org.v1"
    assert report["all_wired_claimed"] is False
    assert report["all_running_claimed"] is False
    assert report["live"] is False
    assert report["probed"] is False
    assert report["health"] is None
    assert "dept.treasury" in report["wired_now"]
    assert "dept.product" in report["wired_now"]
    assert "dept.sales" in report["blocked_now"]
    assert "dept.programs" in report["blocked_now"]
    assert report["programs"]["ready_to_apply"] is False
    assert any("second unique human" in gate for gate in report["human_gates"])
    public = public_org()
    assert "health" not in public
    assert public["all_wired_claimed"] is False


def test_catalog_refuses_invented_officer_and_all_wired():
    cat = load_catalog()
    claimed = copy.deepcopy(cat)
    claimed["organization"]["all_wired_claimed"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(claimed)
    assert exc.value.reason_code == "ORG_NOT_WIRED"
    officer = copy.deepcopy(cat)
    officer["organization"]["second_officer"] = "invented-cfo"
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(officer)
    assert exc2.value.reason_code == "ORG_SECOND_OFFICER"
    dated = copy.deepcopy(cat)
    dated["organization"]["incorporation_date"] = "2026-01-01"
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(dated)
    assert exc3.value.reason_code == "ORG_INCORPORATION"
    sku = copy.deepcopy(cat)
    sku["organization"]["departments"][0]["sku"] = "L1"
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(sku)
    assert exc4.value.reason_code == "CATALOG_SKU"


def test_organization_refuses_live_contacts_and_unknown_systems():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    missing["organization"] = None
    with pytest.raises(IntegrityError) as exc:
        validate_organization(missing)
    assert exc.value.reason_code == "CATALOG_ORG"
    sku = copy.deepcopy(cat)
    sku["organization"]["sku"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(sku)
    assert exc2.value.reason_code == "CATALOG_SKU"
    live = copy.deepcopy(cat)
    live["organization"]["live"] = True
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(live)
    assert exc3.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    contact = copy.deepcopy(cat)
    contact["organization"]["contacts"]["second_unique_human"] = True
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(contact)
    assert exc4.value.reason_code == "ORG_SECOND_OFFICER"
    named = copy.deepcopy(cat)
    named["organization"]["contacts"]["developer"] = "invented@ainav.institute"
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(named)
    assert exc5.value.reason_code == "ORG_SECOND_OFFICER"
    trimmed = copy.deepcopy(cat)
    trimmed["organization"]["departments"] = trimmed["organization"]["departments"][:1]
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(trimmed)
    assert exc6.value.reason_code == "CATALOG_ORG"
    status = copy.deepcopy(cat)
    status["organization"]["departments"][0]["status"] = "invented_live"
    with pytest.raises(IntegrityError) as exc7:
        validate_catalog(status)
    assert exc7.value.reason_code == "CATALOG_ORG"
    prod = copy.deepcopy(cat)
    prod["organization"]["departments"][0]["production"] = True
    with pytest.raises(IntegrityError) as exc8:
        validate_catalog(prod)
    assert exc8.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    system = copy.deepcopy(cat)
    system["organization"]["departments"][0]["systems"] = ["not.a.system"]
    with pytest.raises(IntegrityError) as exc9:
        validate_catalog(system)
    assert exc9.value.reason_code == "CATALOG_ORG"


def test_org_probe_overlays_health_without_claiming_live(monkeypatch):
    monkeypatch.setattr(
        "ainav.microsoft.health.stack_health",
        lambda *, probe=True: {
            "kind": "ainav.connect.v1",
            "live": False,
            "connected": ["bc.premium", "azure.host", "m365.e7"],
            "blocked": ["sales.enterprise", "teams.enterprise"],
        },
    )
    report = org_report(probe=True)
    assert report["probed"] is True
    assert report["live"] is False
    assert report["all_wired_claimed"] is False
    by_id = {item["id"]: item for item in report["departments"]}
    assert by_id["dept.treasury"]["wired_now"] is True
    assert "bc.premium" in by_id["dept.treasury"]["systems_connected"]
    assert by_id["dept.sales"]["wired_now"] is False
    assert "sales.enterprise" in by_id["dept.sales"]["systems_blocked"]
    assert by_id["dept.institute"]["wired_now"] is False
    assert _wired_now({"status": "running_sandbox", "systems": ["bc.premium"]}, {"bc.premium"}) is True
    assert _wired_now({"status": "running_sandbox", "systems": ["bc.premium"]}, set()) is False
    assert _wired_now({"status": "running_code", "systems": ["repo.agent_gov"]}, {"bc.premium"}) is True
    assert _wired_now({"status": "in_repo_not_public", "systems": ["azure.host"]}, {"azure.host"}) is False


def test_cli_org_and_institute_section(capsys):
    from ainav.__main__ import main

    assert main(["org"]) == 0
    out = capsys.readouterr().out
    assert "dept.treasury" in out
    assert "all_wired_claimed" in out
    assert "nvidia.inception" in out
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert 'href="#org"' in html
    assert 'id="org"' in html
    assert "two unique contacts" in html
    assert "Second unique human" in html
