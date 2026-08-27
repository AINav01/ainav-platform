from __future__ import annotations

import pytest

from ainav.business import public_business
from ainav.errors import ProvisionError
from ainav.ops import EXITS, ClientAccount


def test_pass_kit_runs_the_twin_proof():
    account = ClientAccount("kit-acme")
    account.sell_l1()
    account.start_kit()
    report = account.pass_kit()
    assert report["passed"] is True
    assert report["signed_l1"] is False
    assert account.local.bc.twin.journals
    assert account.seats["roles"]["seat_a"] == "treasury_approver"
    quotes = [item for item in account.ledger.entries if item["kind"] == "quote"]
    invoices = [item for item in account.ledger.entries if item["kind"] == "invoice"]
    assert quotes[0]["sku"] == "L1"
    assert invoices[0]["recognized"] is False


def test_lost_kit_fail_churn_and_renew():
    lost = ClientAccount("no-fit")
    lost.lose()
    assert lost.stage == "LOST"
    with pytest.raises(ProvisionError):
        lost.sell_l1()
    account = ClientAccount("renew-acme")
    account.sell_l1()
    account.start_kit()
    account.pass_kit()
    account.attach_padm()
    renewed = account.renew("P-ADM")
    assert renewed["term"] == 2
    assert renewed["recognized"] is False
    account.offer_udual()
    account.attach_udual()
    account.renew("U-DUAL")
    assert account.terms["U-DUAL"] == 2
    account.churn()
    assert account.stage == "CHURN"
    assert account.coverage_active is False
    with pytest.raises(ProvisionError) as exc:
        account.renew("P-ADM")
    assert exc.value.reason_code == "CHURN"
    assert "LOST" in EXITS


def test_public_business_names_the_missing():
    body = public_business()
    assert body["live"] is False
    assert body["acceptance_kit"]["signed_l1"] is False
    assert "kit.bc.journal" in body["acceptance_kit"]["cases"]
    assert any("Recognized revenue" in item for item in body["honest_missing"])
    assert body["proof_day"]["minutes"] == 90
    assert body["proof_day"]["signed_l1"] is False
    assert body["buyer"]["contact_email"] is None
    assert body["next_pin"]["id"] == "bc.microsoft.sandbox"
    assert body["icp"]["named_customers"] == []
    assert body["programs_order"][0] == "microsoft.founders_hub"
