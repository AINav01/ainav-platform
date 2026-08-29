import pytest

from ainav.catalog import load_catalog, validate_catalog
from ainav.errors import ProvisionError
from ainav.mothership import MasterMothership
from ainav.packs import book_service
from ainav.provision import provision_l1, provision_l1_padm, provision_l1_with_udual
from ainav.runbooks import all_runbooks


def test_still_exactly_three_skus():
    assert {item["id"] for item in load_catalog()["skus"]} == {"L1", "P-ADM", "U-DUAL"}
    validate_catalog(load_catalog())


def test_l1_wedge_does_not_include_payables_until_pack():
    local = provision_l1("acme")
    assert "bc.general_journal.post" in local.allowed_actions
    assert "bc.payment_journal.post" not in local.allowed_actions
    local.attach_industry("industry.payables")
    assert "bc.payment_journal.post" in local.allowed_actions
    out = local.run_and_apply(
        {
            "action_class": "bc.payment_journal.post",
            "payload": {"account": "22100", "amount": "25.00", "memo": "payables upsell"},
            "proposal_id": "prp-ap",
            "sor_target": "bc.sandbox",
            "policy_id": "dual-admit-v1",
        },
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert out["record_type"] == "effect_applied"
    assert out["apply_result"]["live"] is False


def test_udual_invoice_is_pack_gated():
    local = provision_l1_with_udual("acme")
    assert "d365.quote.discount_override" in local.allowed_actions
    assert "d365.invoice.post" not in local.allowed_actions
    local.attach_industry("industry.invoice_desk")
    out = local.run_and_apply(
        {
            "action_class": "d365.invoice.post",
            "payload": {"invoice": "INV-1", "amount": "100.00"},
            "proposal_id": "prp-inv",
            "sor_target": "d365.sales.sandbox",
            "policy_id": "dual-admit-v1",
        },
        seat_a="oid-1",
        seat_b="oid-2",
    )
    assert out["record_type"] == "effect_applied"


def test_padm_keep_library_is_not_a_sku():
    local = provision_l1_padm("acme")
    lib = local.attach_library("lib.padm.siem")
    assert lib["requires_sku"] == "P-ADM"
    assert "lib.padm.siem" in local.libraries
    ids = {item["id"] for item in load_catalog()["repositories"]}
    assert {"repo.finance", "repo.brief", "repo.review"} <= ids
    booked = book_service("ffs.pack_seating", skus=("L1",))
    assert booked["billed"] is True
    assert booked["sku"] is None


def test_runbooks_cover_new_desks():
    body = all_runbooks()
    ids = {item["id"] for item in body["items"]}
    assert "industry.payables" in ids
    assert "industry.bank" in ids
    assert "industry.invoice_desk" in ids
    assert "industry.credit" in ids
    assert all(item["sku"] is False for item in body["items"])


def test_invoice_desk_requires_udual():
    local = MasterMothership().provision("x", packs=("L1",))
    with pytest.raises(ProvisionError) as exc:
        local.attach_industry("industry.invoice_desk")
    assert exc.value.reason_code == "PACK_SCOPE"
