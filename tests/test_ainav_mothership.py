from __future__ import annotations

import copy

import pytest

from agent_gov import AdmitDenied, EffectBlocked
from agent_gov.errors import IntegrityError
from ainav.catalog import l1_action_classes, load_catalog, sku, wedge_action_classes
from ainav.errors import IPError, LivePinError, ProvisionError, SoftDualError
from ainav.catalog import validate_catalog
from ainav.microsoft.azure import AzureHost
from ainav.microsoft.bc import BusinessCentralAdapter
from ainav.microsoft.compliance import ComplianceSink
from ainav.microsoft.entra import EntraSeatVerifier
from ainav.microsoft.sales import SalesEnterpriseAdapter
from ainav.microsoft.stack import assert_not_a_seat
from ainav.microsoft.teams import TeamsNotifier
from ainav.mothership import MasterMothership
from ainav.plan import one_page
from ainav.provision import provision_l1, provision_l1_padm, provision_l1_with_udual


def test_catalog_has_exactly_three_skus():
    cat = load_catalog()
    assert {s["id"] for s in cat["skus"]} == {"L1", "P-ADM", "U-DUAL"}
    assert cat["entity"]["job"] == "C"
    assert cat["operating"]["sole_owner"] is True
    assert cat["operating"]["owner_principal"] == "James Hodnett"
    assert cat["operating"]["operator_is_seat"] is False
    assert cat["operating"]["agent_is_not_dual"] is True
    assert wedge_action_classes("L1") == frozenset({"bc.general_journal.post"})
    assert "bc.general_journal.post" in l1_action_classes()
    assert "bc.payment_journal.post" in l1_action_classes()
    assert sku("L1")["price_usd"]["min"] == 28000


def test_operating_model_refuses_agent_as_seat():
    cat = copy.deepcopy(load_catalog())
    cat["operating"]["operator_is_seat"] = True
    with pytest.raises(IntegrityError, match="operator cannot be a dual seat"):
        validate_catalog(cat)


def test_plan_is_generated_from_catalog():
    text = one_page()
    assert "AINav, Inc." in text
    assert "U-DUAL" in text
    assert "never free" in text.lower() or "Never free" in text or "never free with" in text
    assert "LIVE_PIN_OK" in text
    assert "Teams" in text


def test_standard_l1_twin_journal():
    local = provision_l1("acme")
    out = local.run_and_apply(
        {
            "action_class": "bc.general_journal.post",
            "payload": {"account": "1000", "amount": "10.00"},
            "proposal_id": "prp-l1",
            "sor_target": "bc.sandbox",
            "policy_id": "dual-admit-v1",
        },
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert out["record_type"] == "effect_applied"
    assert out["apply_result"]["live"] is False
    assert out["apply_result"]["label"] == "SANDBOX"
    assert local.bc.twin.journals[0]["action_hash"] == out["action_hash"]
    audit = local.audit()
    assert audit["live"] is False
    assert audit["client_id"] == "acme"


def test_l1_refuses_udual_action():
    local = provision_l1("acme")
    with pytest.raises(ProvisionError) as exc:
        local.run_and_apply(
            {
                "action_class": "d365.quote.discount_override",
                "payload": {"discount": "40"},
                "proposal_id": "prp-no",
                "policy_id": "dual-admit-v1",
            },
            seat_a="oid-1",
            seat_b="oid-2",
        )
    assert exc.value.reason_code == "PACK_SCOPE"


def test_paid_udual_pack_allows_sales_action():
    local = provision_l1_with_udual("acme")
    assert "d365.quote.discount_override" in local.allowed_actions
    assert "bc.general_journal.post" in local.allowed_actions
    out = local.run_and_apply(
        {
            "action_class": "d365.quote.discount_override",
            "payload": {"discount": "15"},
            "proposal_id": "prp-sales",
            "sor_target": "d365.sales.sandbox",
            "policy_id": "dual-admit-v1",
        },
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert out["record_type"] == "effect_applied"
    assert out["apply_result"]["live"] is False
    assert local.sales.twin.writes[0]["action_class"] == "d365.quote.discount_override"
    assert "industry.sales" in local.industry


def test_udual_without_l1_is_refused():
    with pytest.raises(ProvisionError):
        MasterMothership().provision("acme", packs=("U-DUAL",))


def test_invented_pack_refused():
    with pytest.raises(ProvisionError):
        MasterMothership().provision("acme", packs=("L1", "NOT_A_SKU"))
    with pytest.raises(IPError) as exc:
        MasterMothership().provision("acme", packs=("L1", "COPILOT_PACK"))
    assert exc.value.reason_code == "MICROSOFT_PRODUCT"


def test_teams_is_not_a_seat():
    with pytest.raises(SoftDualError):
        assert_not_a_seat("teams:general")
    verifier = EntraSeatVerifier()
    with pytest.raises(SoftDualError):
        verifier.verify("teams:approvals", "seat_b")
    with pytest.raises(AdmitDenied):
        verifier.verify("not-an-oid", "seat_a")
    assert verifier.verify("oid-1", "seat_a") == "oid-1"
    notifier = TeamsNotifier()
    with pytest.raises(SoftDualError):
        notifier.notify({"as_seat": True})
    notifier.notify({"request_id": "req_x"})
    assert notifier.sent[0]["as_seat"] is False


def test_live_bc_and_entra_graph_are_not_claimed():
    with pytest.raises(LivePinError):
        BusinessCentralAdapter(live=True)
    with pytest.raises(LivePinError):
        SalesEnterpriseAdapter(live=True)
    with pytest.raises(LivePinError):
        AzureHost(live=True)
    with pytest.raises(LivePinError):
        AzureHost().deploy_master()
    with pytest.raises(LivePinError):
        EntraSeatVerifier().live_group_check()
    sink = ComplianceSink()
    with pytest.raises(LivePinError):
        sink.live_purview()
    with pytest.raises(LivePinError):
        sink.live_sentinel()
    assert EntraSeatVerifier().graph_configured() in {False, True}
    posted = BusinessCentralAdapter().apply(
        {
            "record_type": "admit_ok",
            "proposal": {"action_class": "bc.general_journal.post", "sor_target": "bc.sandbox"},
        }
    )
    assert posted["live"] is False
    sold = SalesEnterpriseAdapter().apply(
        {
            "record_type": "admit_ok",
            "proposal": {
                "action_class": "d365.quote.discount_override",
                "sor_target": "d365.sales.sandbox",
            },
        }
    )
    assert sold["live"] is False
    oid = EntraSeatVerifier().verify("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", "seat_a")
    assert oid.startswith("aaaaaaaa")
    TeamsNotifier().refuse_seat("oid-1")


def test_industry_sales_requires_udual():
    local = provision_l1("acme")
    with pytest.raises(ProvisionError) as exc:
        local.attach_industry("industry.sales")
    assert exc.value.reason_code == "PACK_SCOPE"


def test_padm_export_and_standard_manifest():
    local = provision_l1_padm("acme")
    exported = local.export_audit()
    assert exported["live"] is False
    manifest = local.manifest()
    assert manifest["kind"] == "ainav.local_mothership.v1"
    assert manifest["live"] is False
    assert "P-ADM" in manifest["skus"]
    with pytest.raises(ProvisionError):
        provision_l1("other").export_audit()


def test_catalog_rejects_invented_industry_sku():
    cat = load_catalog()
    broken = {
        **cat,
        "industry_packs": [
            {
                "id": "industry.fake",
                "requires_sku": "COPILOT_PACK",
                "modules": ["bc.general_journal.post"],
            }
        ],
    }
    with pytest.raises(IntegrityError):
        validate_catalog(broken)


def test_twins_refuse_wrong_action():
    from ainav.twin import BusinessCentralTwin, SalesEnterpriseTwin, SandboxRouter

    bc = BusinessCentralTwin()
    with pytest.raises(EffectBlocked):
        bc.post_journal(
            {"record_type": "admit_ok", "proposal": {"action_class": "d365.order.submit"}}
        )
    with pytest.raises(EffectBlocked):
        bc.post_journal(
            {
                "record_type": "effect_applied",
                "proposal": {"action_class": "bc.general_journal.post"},
            }
        )
    sales = SalesEnterpriseTwin()
    with pytest.raises(EffectBlocked):
        sales.apply(
            {
                "record_type": "admit_ok",
                "proposal": {"action_class": "bc.general_journal.post"},
            }
        )
    with pytest.raises(EffectBlocked):
        SandboxRouter().apply(
            {"record_type": "admit_ok", "proposal": {"action_class": "unknown.x"}}
        )


def test_empty_client_and_invented_attach():
    with pytest.raises(ProvisionError):
        MasterMothership().provision("  ")
    local = provision_l1("acme")
    with pytest.raises(IPError):
        local.attach_pack("COPILOT_PACK")
    with pytest.raises(ProvisionError):
        local.attach_pack("NOT_A_SKU")
    local.attach_pack("L1")
    assert local.bc.live is False
    assert MasterMothership().host.describe()["live"] is False
    assert MasterMothership().issue_lockfile() is not None


def test_cli_catalog_and_twin(capsys):
    from ainav.__main__ import main

    assert main(["catalog"]) == 0
    assert "bc.general_journal.post" in capsys.readouterr().out
    assert main(["plan"]) == 0
    out = capsys.readouterr().out
    assert "FIRST_OFFER" in out
    assert "IP and competitor" in out
    assert main(["ip"]) == 0
    assert "AINav, Inc." in capsys.readouterr().out
    assert main(["org"]) == 0
    org_out = capsys.readouterr().out
    assert "dept.treasury" in org_out
    assert "all_wired_claimed" in org_out
    assert main(["programs"]) == 0
    programs_out = capsys.readouterr().out
    assert "nvidia.inception" in programs_out
    assert "qualify_not_claimed" in programs_out
    assert main(["pitch"]) == 0
    assert "bc.general_journal.post" in capsys.readouterr().out
    assert main(["provision", "acme", "--packs", "L1"]) == 0
    assert main(["twin-demo", "--client-id", "acme"]) == 0
    out = capsys.readouterr().out
    assert "SANDBOX" in out
    assert "effect_applied" in out
    assert main(["ops-demo", "--client-id", "ops-acme"]) == 0
    ops_out = capsys.readouterr().out
    assert "U_DUAL_ATTACH" in ops_out
    assert "d365.quote.discount_override" in ops_out
    assert main(["manifest", "acme", "--packs", "L1"]) == 0
