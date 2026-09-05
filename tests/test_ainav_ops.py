from __future__ import annotations

import pytest

from ainav.errors import LivePinError, ProvisionError
from ainav.ops import ClientAccount, STAGES
from ainav.packs import book_service, require_library


def test_operations_stages_are_catalog_law():
    assert STAGES[0] == "QUALIFY"
    assert STAGES[-1] == "U_DUAL_ATTACH"


def test_spine_l1_kit_padm_paid_udual():
    account = ClientAccount("northwind")
    local = account.sell_l1()
    assert local.industry == ("industry.treasury",)
    account.start_kit()
    account.pass_kit()
    kit = account.book("ffs.acceptance_kit")
    assert kit["billed"] is False
    assert kit["sku"] is None
    assist = account.book("ffs.integration_assist")
    assert assist["billed"] is True
    assert assist["sku"] is None
    account.attach_padm()
    account.offer_udual()
    account.attach_udual()
    snap = account.snapshot()
    assert snap["sold"] == ["L1", "P-ADM", "U-DUAL"]
    assert snap["live_pin_ok"] is False
    assert snap["signed_l1"] is False
    assert "d365.order.submit" in account.local.allowed_actions


def test_padm_before_kit_pass_is_refused():
    account = ClientAccount("blocked")
    account.sell_l1()
    with pytest.raises(ProvisionError) as exc:
        account.attach_padm()
    assert exc.value.reason_code == "ATTACH_GATE"


def test_udual_never_free_with_padm():
    account = ClientAccount("bundle")
    account.sell_l1()
    account.start_kit()
    account.pass_kit()
    account.attach_padm()
    with pytest.raises(ProvisionError) as exc:
        account.attach_udual(bundled_free=True)
    assert exc.value.reason_code == "UDUAL_NOT_FREE"


def test_ops_gates_are_fail_closed():
    account = ClientAccount("gates")
    with pytest.raises(ProvisionError):
        account.start_kit()
    account.sell_l1()
    with pytest.raises(ProvisionError):
        account.sell_l1()
    with pytest.raises(ProvisionError):
        account.pass_kit()
    with pytest.raises(ProvisionError):
        account.offer_udual()
    account.start_kit()
    account.pass_kit()
    from ainav.mothership import LocalMothership

    with pytest.raises(ProvisionError) as padm:
        LocalMothership("padm-only", packs=("P-ADM",))
    assert padm.value.reason_code == "PACK_SCOPE"
    l1_only = LocalMothership("l1-only", packs=("L1",))
    with pytest.raises(ProvisionError) as udual:
        l1_only.attach_pack("U-DUAL")
    assert udual.value.reason_code == "ATTACH_GATE"
    with pytest.raises(ProvisionError):
        l1_only.attach_industry("industry.sales")
    account.local.attach_industry("industry.treasury")


def test_ops_exits_and_stage_gates_are_fail_closed():
    qualify = ClientAccount("qualify-only")
    with pytest.raises(ProvisionError):
        qualify.churn()
    with pytest.raises(ProvisionError):
        qualify.run_kit()
    with pytest.raises(ProvisionError):
        qualify.attach_udual()
    with pytest.raises(ProvisionError):
        qualify.renew("L1")
    sold = ClientAccount("sold-only")
    sold.sell_l1()
    with pytest.raises(ProvisionError):
        sold.lose()
    with pytest.raises(ProvisionError):
        sold.run_kit()
    with pytest.raises(ProvisionError):
        sold.renew("P-ADM")
    with pytest.raises(ProvisionError):
        sold.churn()
    sold.start_kit()
    report = sold.run_kit()
    assert report["passed"] is True
    assert report["live"] is False
    fail_kit = ClientAccount("kit-fail")
    fail_kit.sell_l1()
    fail_kit.start_kit()
    fail_kit.seats["seat_b"] = fail_kit.seats["seat_a"]
    failed = fail_kit.run_kit()
    assert failed["passed"] is False
    assert fail_kit.stage == "KIT_FAIL"
    with pytest.raises(ProvisionError):
        fail_kit.attach_udual()
    same_pass = ClientAccount("kit-fail-pass")
    same_pass.sell_l1()
    same_pass.start_kit()
    same_pass.seats["seat_b"] = same_pass.seats["seat_a"]
    with pytest.raises(ProvisionError) as kit_fail:
        same_pass.pass_kit()
    assert kit_fail.value.reason_code == "KIT_FAIL"
    orphan = ClientAccount("no-local")
    orphan.stage = "KIT_IN_PROGRESS"
    with pytest.raises(ProvisionError):
        orphan.run_kit()


def test_cannot_mark_open_gaps():
    account = ClientAccount("gaps")
    account.sell_l1()
    with pytest.raises(LivePinError):
        account.claim_live_pin()
    with pytest.raises(ProvisionError) as exc:
        account.claim_signed_l1()
    assert exc.value.reason_code == "SIGNED_L1_OPEN"


def test_ffs_cannot_mint_a_sku():
    booked = book_service("ffs.replay_workshop", skus=("L1",))
    assert booked["sku"] is None
    assert booked["billed"] is True
    with pytest.raises(ProvisionError):
        ClientAccount("  ")
    early = ClientAccount("early")
    with pytest.raises(ProvisionError):
        early.book("ffs.integration_assist")
    require_library("lib.l1.wedge", skus=("L1",))
    with pytest.raises(ProvisionError):
        require_library("lib.udual.sales", skus=("L1",))
    with pytest.raises(ProvisionError):
        book_service("ffs.acceptance_kit", skus=())
    local_booked = ClientAccount("svc").sell_l1().book_service("ffs.acceptance_kit")
    assert local_booked["billed"] is False
