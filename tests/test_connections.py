from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.errors import LivePinError, SoftDualError
from ainav.microsoft.azure import AzureHost
from ainav.microsoft.connections import REQUIRED_IDS, StackPlane, spec, stack_json
from ainav.microsoft.teams import TeamsNotifier
from ainav.mothership import MasterMothership
from ainav.provision import provision_l1, provision_l1_padm, provision_l1_with_udual


def test_catalog_has_six_microsoft_connections():
    cat = load_catalog()
    ids = [item["id"] for item in cat["connections"]["items"]]
    assert ids == list(REQUIRED_IDS)
    assert cat["connections"]["live"] is False
    assert "Agent 365" in cat["microsoft_stack"]["e7_not_the_product"]


def test_stack_json_is_sandbox_public_artifact():
    body = stack_json()
    assert body["live"] is False
    assert body["kind"] == "ainav.institute.stack.v1"
    assert [item["id"] for item in body["connections"]] == list(REQUIRED_IDS)
    assert all(item["mode"] == "sandbox" for item in body["connections"])
    assert body["walk"]["path"][0]["url"] == "https://dash.cloudflare.com"
    assert "create users" in " ".join(body["walk"]["cannot"])
    on_disk = json.loads(Path("institute/stack.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_l1_effect_notifies_both_teams_and_binds_bc():
    local = provision_l1("acme")
    out = local.run_and_apply(
        {
            "action_class": "bc.general_journal.post",
            "payload": {"account": "1000", "amount": "10.00"},
            "proposal_id": "prp-stack-l1",
            "sor_target": "bc.sandbox",
            "policy_id": "dual-admit-v1",
        },
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert out["record_type"] == "effect_applied"
    assert local.last_sor_connection == "bc.premium"
    assert [item["connection"] for item in local.teams.sent] == [
        "teams.enterprise",
        "teams.premium",
    ]
    assert all(item["sent"] is False and item["live"] is False for item in local.teams.sent)
    assert local.teams.sent[1]["protection"] == "premium"


def test_udual_effect_binds_sales_and_padm_exports_e7():
    local = provision_l1_with_udual("acme")
    out = local.run_and_apply(
        {
            "action_class": "d365.order.submit",
            "payload": {"order": "SO-1"},
            "proposal_id": "prp-stack-sales",
            "sor_target": "d365.sales.sandbox",
            "policy_id": "dual-admit-v1",
        },
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert local.last_sor_connection == "sales.enterprise"
    padm = provision_l1_padm("acme-padm")
    padm.run_and_apply(
        {
            "action_class": "bc.general_journal.post",
            "payload": {"account": "2000", "amount": "1.00"},
            "proposal_id": "prp-e7",
            "sor_target": "bc.sandbox",
            "policy_id": "dual-admit-v1",
        },
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert padm.compliance.exported
    assert padm.compliance.exported[0]["connection"] == "m365.e7"
    assert padm.compliance.exported[0]["live"] is False


def test_company_and_institute_azure_plans_are_not_live():
    master = MasterMothership()
    surface = master.company_surface()
    assert surface["live"] is False
    assert surface["operating"]["owner_principal"] == "James Hodnett"
    assert surface["operating"]["operator_is_seat"] is False
    assert surface["azure"]["live"] is False
    assert surface["institute_plan"]["sent"] is False
    assert "institute" in surface["institute_plan"]["payload"]["appLocation"]
    with pytest.raises(LivePinError):
        master.host.deploy_institute()
    with pytest.raises(LivePinError):
        StackPlane().live_connect("bc.premium")


def test_teams_unknown_connection_and_seat_still_refused():
    with pytest.raises(SoftDualError):
        TeamsNotifier().notify({"request_id": "x"}, connection_id="copilot")
    with pytest.raises(SoftDualError):
        TeamsNotifier().notify({"as_seat": True}, connection_id="teams.enterprise")


def test_catalog_rejects_live_or_reordered_connections():
    cat = load_catalog()
    live = copy.deepcopy(cat)
    live["connections"]["live"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(live)
    assert exc.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    missing = copy.deepcopy(cat)
    missing["connections"]["items"] = missing["connections"]["items"][1:]
    with pytest.raises(IntegrityError):
        validate_catalog(missing)
    gone = copy.deepcopy(cat)
    gone["connections"] = None
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(gone)
    assert exc2.value.reason_code == "CATALOG_CONNECTION"
    copilot = copy.deepcopy(cat)
    copilot["connections"]["items"][0]["product"] = "Microsoft 365 Copilot"
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(copilot)
    assert exc3.value.reason_code == "MICROSOFT_PRODUCT"
    surface = copy.deepcopy(cat)
    surface["connections"]["items"][0]["surfaces"] = ["invented"]
    with pytest.raises(IntegrityError) as exc4:
        validate_catalog(surface)
    assert exc4.value.reason_code == "CATALOG_CONNECTION"
    comps = copy.deepcopy(cat)
    comps["connections"]["complements"] = comps["connections"]["complements"][1:]
    with pytest.raises(IntegrityError) as exc5:
        validate_catalog(comps)
    assert exc5.value.reason_code == "CATALOG_CONNECTION"
    agent = copy.deepcopy(cat)
    agent["connections"]["complements"][0]["product"] = "Agent 365"
    with pytest.raises(IntegrityError) as exc6:
        validate_catalog(agent)
    assert exc6.value.reason_code == "MICROSOFT_PRODUCT"
    with pytest.raises(IntegrityError) as exc7:
        spec("copilot.as.seat")
    assert exc7.value.reason_code == "CATALOG_CONNECTION"


def test_stack_plane_after_effect_ignores_non_applied():
    from ainav.microsoft.connections import StackPlane

    assert StackPlane().after_effect(object(), {"record_type": "effect_apply_failed"}) == []


def test_institute_site_and_swa_config():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "Microsoft Azure" in html
    assert "Microsoft 365 E7" in html
    assert "Teams Enterprise" in html
    assert "Teams Premium" in html
    assert "Business Central Premium" in html
    assert "Sales Enterprise" in html
    assert "stack.json" in Path("institute/site.js").read_text(encoding="utf-8")
    assert "complement-cards" in html
    assert "Microsoft fabric" in html
    swa = json.loads(Path("institute/staticwebapp.config.json").read_text(encoding="utf-8"))
    assert swa["navigationFallback"]["rewrite"] == "/index.html"
    assert spec("azure.host")["role"] == "hosting"
    assert AzureHost().plan_institute()["live"] is False


def test_cli_connections_and_stack_demo(capsys):
    from ainav.__main__ import main

    assert main(["connections"]) == 0
    out = capsys.readouterr().out
    assert "azure.host" in out
    assert "AINAV.Institute" in out
    assert main(["stack-demo", "--client-id", "stack-acme"]) == 0
    demo = capsys.readouterr().out
    assert "bc.premium" in demo
    assert "teams.premium" in demo
