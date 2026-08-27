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

    padm_only = LocalMothership("padm-only", packs=("P-ADM",))
    with pytest.raises(ProvisionError):
        padm_only.attach_pack("U-DUAL")
    with pytest.raises(ProvisionError):
        padm_only.attach_industry("industry.treasury")
    account.local.attach_industry("industry.treasury")


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
