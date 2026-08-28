from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.buyer import buyer_page, icp_profile, proof_day_brief
from ainav.catalog import load_catalog, validate_catalog
from ainav.errors import LivePinError, ProvisionError
from ainav.next_pin import next_pin_spec, pin_from_twin, refuse_production, sandbox_envelope, send_sandbox
from ainav.proof_day import claim_live_pin, claim_signed_l1, run_proof_day, runbook


def test_proof_day_seals_journal_and_export():
    result = run_proof_day("lab-proof")
    assert result["minutes"] == 90
    assert result["effect"] == "effect_applied"
    assert result["sealed"] is True
    assert result["signed_l1"] is False
    assert result["live"] is False
    assert result["live_pin_ok"] is False
    assert result["seats"]["seat_a"]["role"] == "treasury_approver"
    assert result["seats"]["seat_b"]["role"] == "treasury_controller"
    assert result["seats"]["seat_a"]["lab"] != result["seats"]["seat_b"]["lab"]
    assert result["export"]["count"] >= 1
    assert result["export"]["merkle_root"]
    assert result["next_pin"]["environment"] == "bc.microsoft.sandbox"
    assert result["next_pin"]["sent"] is False
    assert result["next_pin"]["live"] is False
    assert "sealed DecisionRecord" in result["walk_out"]
    assert runbook()[0].startswith("Confirm two existing")


def test_proof_day_cannot_close_g13_or_live():
    with pytest.raises(ProvisionError) as exc:
        claim_signed_l1()
    assert exc.value.reason_code == "SIGNED_L1_OPEN"
    with pytest.raises(LivePinError):
        claim_live_pin()


def test_next_pin_is_intended_sandbox_only():
    env = sandbox_envelope(
        {
            "action_class": "bc.general_journal.post",
            "payload": {"account": "1000", "amount": "1.00"},
            "sor_target": "bc.microsoft.sandbox",
        }
    )
    assert env["sent"] is False
    assert env["production"] is False
    assert env["live_pin_ok"] is False
    assert env["intended"]["sent"] is False
    assert "sandbox" in env["intended"]["url"]
    with pytest.raises(LivePinError):
        refuse_production("bc.production")
    with pytest.raises(LivePinError):
        send_sandbox(env)
    with pytest.raises(ProvisionError):
        pin_from_twin(type("Empty", (), {"bc": type("B", (), {"twin": type("T", (), {"journals": []})()})()})())
    with pytest.raises(ProvisionError):
        sandbox_envelope({"sor_target": "bc.other"})
    assert next_pin_spec()["id"] == "bc.microsoft.sandbox"
    with pytest.raises(ProvisionError):
        run_proof_day("   ")


def test_buyer_page_has_no_inbox_or_named_customer():
    page = buyer_page()
    assert page["contact_email"] is None
    assert page["mailto"] is None
    assert page["icp"]["named_customers"] == []
    assert "journal" in page["write_that_must_not_happen"].lower()
    assert page["seats"] == ["treasury_approver", "treasury_controller"]
    brief = proof_day_brief()
    assert brief["forwardable"] is True
    assert brief["named_customer"] is None
    assert brief["mailto"] is None
    with pytest.raises(ProvisionError) as exc:
        proof_day_brief(for_controller="Acme")
    assert exc.value.reason_code == "ICP_NAMED"
    profile = icp_profile()
    assert profile["do_not_invent_names"] is True


def test_catalog_rejects_named_customer_and_live_next_pin():
    cat = load_catalog()
    named = copy.deepcopy(cat)
    named["icp"]["named_customers"] = ["Invented Corp"]
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(named)
    assert exc.value.reason_code == "ICP_NAMED"
    live = copy.deepcopy(cat)
    live["next_pin"]["live"] = True
    with pytest.raises(IntegrityError) as exc2:
        validate_catalog(live)
    assert exc2.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    inbox = copy.deepcopy(cat)
    inbox["buyer"]["contact_email"] = "sales@example.com"
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(inbox)
    assert exc3.value.reason_code == "BUYER_INBOX"


def test_institute_buyer_page_is_forwardable():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert 'id="buyer"' in html
    assert 'href="#buyer"' in html
    assert "Ask for a proof day" in html
    assert "href=\"mailto:" not in html
    assert "href='mailto:" not in html
    assert "ainav-proof-day-brief.json" in Path("institute/site.js").read_text(encoding="utf-8")
    buyer = json.loads(Path("institute/buyer.json").read_text(encoding="utf-8"))
    assert buyer == buyer_page()
    assert buyer["contact_email"] is None


def test_cli_proof_day_buyer_and_next_pin(capsys):
    from ainav.__main__ import main

    assert main(["proof-day"]) == 0
    out = capsys.readouterr().out
    assert "effect_applied" in out
    assert "bc.microsoft.sandbox" in out
    assert main(["buyer"]) == 0
    buyer = capsys.readouterr().out
    assert "treasury_approver" in buyer
    assert main(["brief"]) == 0
    brief = capsys.readouterr().out
    assert "ainav.proof_day.brief.v1" in brief
    assert main(["next-pin"]) == 0
    nxt = capsys.readouterr().out
    assert '"sent":false' in nxt
