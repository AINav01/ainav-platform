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
    assert body["contacts"]["invited"]["number_two"] is True
    assert body["contacts"]["invited"]["all_aspects"] is False
    assert body["contacts"]["invited"]["officer"] is False
    two = body["number_two"]
    assert two["role"] == "number_two"
    assert two["scope"] == "other_aspects"
    assert two["all_aspects"] is False
    assert two["officer"] is False
    assert two["seated"] is False
    assert two["seat_clicked"] is False
    assert two["entra_oid"] is None
    assert two["mailbox"] == "chodnett@ainav.institute"
    licenses = body["contacts"]["invited"]["licenses"]
    assert licenses["kind"] == "ainav.invite.licenses.v1"
    assert licenses["e7"] is True
    assert licenses["teams_premium"] is True
    assert licenses["fallback_stays_on_owner"] is True
    assert licenses["from_this_plane"] is False
    assert licenses["seat"] is False
    assert licenses["second_unique_human"] is False
    assert [item["id"] for item in body["departments"]] == list(REQUIRED_DEPT_IDS)
    assert body["sku"] is False
    statuses = {item["id"]: item["status"] for item in body["departments"]}
    assert statuses["dept.treasury"] == "running_sandbox"
    assert statuses["dept.identity"] == "running_sandbox"
    assert statuses["dept.sales"] == "licensed_not_wired"
    assert statuses["dept.people"] == "licensed_not_wired"
    assert statuses["dept.institute"] == "azure_hosted_not_custom"
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
    assert any("second unique human" in gate.lower() for gate in report["human_gates"])
    assert any("chodnett@ainav.institute" in gate for gate in report["human_gates"])
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
    gmail = copy.deepcopy(cat)
    gmail["organization"]["contacts"]["invited"]["email"] = "cynthia@gmail.com"
    with pytest.raises(IntegrityError) as exc_gmail:
        validate_catalog(gmail)
    assert exc_gmail.value.reason_code == "ORG_SECOND_OFFICER"
    oid = copy.deepcopy(cat)
    oid["organization"]["contacts"]["invited"]["entra_oid"] = "00000000-0000-0000-0000-000000000001"
    with pytest.raises(IntegrityError) as exc_oid:
        validate_catalog(oid)
    assert exc_oid.value.reason_code == "ORG_SECOND_OFFICER"
    paid = copy.deepcopy(cat)
    paid["organization"]["contacts"]["invited"]["licenses"]["seat"] = True
    with pytest.raises(IntegrityError) as exc_lic:
        validate_catalog(paid)
    assert exc_lic.value.reason_code == "ORG_SECOND_OFFICER"
    missing_e7 = copy.deepcopy(cat)
    missing_e7["organization"]["contacts"]["invited"]["licenses"]["e7"] = False
    with pytest.raises(IntegrityError) as exc_e7:
        validate_catalog(missing_e7)
    assert exc_e7.value.reason_code == "ORG_SECOND_OFFICER"
    clicked = copy.deepcopy(cat)
    clicked["organization"]["contacts"]["invited"]["seat_clicked"] = True
    with pytest.raises(IntegrityError) as exc_click:
        validate_catalog(clicked)
    assert exc_click.value.reason_code == "ORG_SECOND_OFFICER"
    equity = copy.deepcopy(cat)
    equity["organization"]["contacts"]["invited"]["equity"] = True
    with pytest.raises(IntegrityError) as exc_eq:
        validate_catalog(equity)
    assert exc_eq.value.reason_code == "ORG_SECOND_OFFICER"
    officer = copy.deepcopy(cat)
    officer["organization"]["contacts"]["invited"]["officer"] = True
    with pytest.raises(IntegrityError) as exc_off:
        validate_catalog(officer)
    assert exc_off.value.reason_code == "ORG_SECOND_OFFICER"
    all_aspects = copy.deepcopy(cat)
    all_aspects["organization"]["number_two"]["all_aspects"] = True
    with pytest.raises(IntegrityError) as exc_all:
        validate_catalog(all_aspects)
    assert exc_all.value.reason_code == "ORG_SECOND_OFFICER"
    nameless = copy.deepcopy(cat)
    nameless["organization"]["contacts"]["invited"]["name"] = ""
    with pytest.raises(IntegrityError) as exc_name:
        validate_catalog(nameless)
    assert exc_name.value.reason_code == "CATALOG_ORG"
    no_agree = copy.deepcopy(cat)
    no_agree["organization"]["contacts"]["invited"]["agreed"] = False
    with pytest.raises(IntegrityError) as exc_agree:
        validate_catalog(no_agree)
    assert exc_agree.value.reason_code == "ORG_SECOND_OFFICER"
    wrong_name = copy.deepcopy(cat)
    wrong_name["organization"]["contacts"]["invited"]["name"] = "Invented Person"
    with pytest.raises(IntegrityError) as exc_wrong:
        validate_catalog(wrong_name)
    assert exc_wrong.value.reason_code == "ORG_SECOND_OFFICER"
    email_only = copy.deepcopy(cat)
    email_only["organization"]["contacts"]["invited"]["recorded"] = False
    email_only["organization"]["contacts"]["invited"]["agreed"] = False
    email_only["organization"]["contacts"]["invited"]["email"] = "invented@ainav.institute"
    with pytest.raises(IntegrityError) as exc_mail:
        validate_catalog(email_only)
    assert exc_mail.value.reason_code == "ORG_SECOND_OFFICER"
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
