from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.org import REQUIRED_DEPT_IDS, org_report, organization, public_org


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
