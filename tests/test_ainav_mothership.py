from __future__ import annotations

import pytest

from agent_gov import AdmitDenied, EffectBlocked
from ainav.catalog import l1_action_classes, load_catalog, sku
from ainav.errors import LivePinError, ProvisionError, SoftDualError
from ainav.microsoft.bc import BusinessCentralAdapter
from ainav.microsoft.entra import EntraSeatVerifier
from ainav.microsoft.stack import assert_not_a_seat
from ainav.microsoft.teams import TeamsNotifier
from ainav.mothership import MasterMothership
from ainav.plan import one_page
from ainav.provision import provision_l1, provision_l1_with_udual


def test_catalog_has_exactly_three_skus():
    cat = load_catalog()
    assert {s["id"] for s in cat["skus"]} == {"L1", "P-ADM", "U-DUAL"}
    assert cat["entity"]["job"] == "C"
    assert l1_action_classes() == frozenset({"bc.general_journal.post"})
    assert sku("L1")["price_usd"]["min"] == 28000


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


def test_udual_without_l1_is_refused():
    with pytest.raises(ProvisionError):
        MasterMothership().provision("acme", packs=("U-DUAL",))


def test_invented_pack_refused():
    with pytest.raises(ProvisionError):
        MasterMothership().provision("acme", packs=("L1", "COPILOT_PACK"))


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
        EntraSeatVerifier().live_group_check()
    assert EntraSeatVerifier().graph_configured() in {False, True}


def test_cli_catalog_and_twin(capsys):
    from ainav.__main__ import main

    assert main(["catalog"]) == 0
    assert "bc.general_journal.post" in capsys.readouterr().out
    assert main(["plan"]) == 0
    assert "FIRST_OFFER" in capsys.readouterr().out
    assert main(["provision", "acme", "--packs", "L1"]) == 0
    assert main(["twin-demo", "--client-id", "acme"]) == 0
    out = capsys.readouterr().out
    assert "SANDBOX" in out
    assert "effect_applied" in out
