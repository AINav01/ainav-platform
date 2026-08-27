"""Business operations on the commercial spine. Catalog wins.

Stages: QUALIFY → L1_SOLD → KIT_IN_PROGRESS → KIT_PASS → P_ADM_ATTACH
        → U_DUAL_OFFER → U_DUAL_ATTACH

This plane cannot mark LIVE_PIN_OK or signed L1.
"""

from __future__ import annotations

from typing import Any

from ainav.catalog import ALLOWED_SKUS, operations
from ainav.errors import LivePinError, ProvisionError
from ainav.mothership import LocalMothership, MasterMothership
from ainav.packs import book_service


STAGES = tuple(operations()["stages"])


class ClientAccount:
    """One client on the Job C commercial spine. Not a second product."""

    def __init__(self, client_id: str, *, master: MasterMothership | None = None) -> None:
        if not client_id.strip():
            raise ProvisionError("client_id is required")
        self.client_id = client_id
        self.master = master or MasterMothership()
        self.stage = "QUALIFY"
        self.sold: list[str] = []
        self.kit_pass = False
        self.services: list[dict[str, Any]] = []
        self.local: LocalMothership | None = None

    def sell_l1(self) -> LocalMothership:
        if self.stage != "QUALIFY":
            raise ProvisionError(f"cannot sell L1 from {self.stage}")
        self.local = self.master.standard_l1_pack(self.client_id)
        self.sold.append("L1")
        self.stage = "L1_SOLD"
        return self.local

    def start_kit(self) -> None:
        if self.stage != "L1_SOLD":
            raise ProvisionError("Acceptance Kit starts after L1 is sold")
        self.stage = "KIT_IN_PROGRESS"

    def pass_kit(self) -> None:
        if self.stage != "KIT_IN_PROGRESS":
            raise ProvisionError("kit PASS requires KIT_IN_PROGRESS")
        self.kit_pass = True
        self.stage = "KIT_PASS"

    def attach_padm(self) -> LocalMothership:
        if not self.kit_pass or self.stage != "KIT_PASS":
            raise ProvisionError("P-ADM attaches only after kit PASS", reason_code="ATTACH_GATE")
        local = self._require_local()
        local.attach_pack("P-ADM")
        self.sold.append("P-ADM")
        self.stage = "P_ADM_ATTACH"
        return local

    def offer_udual(self) -> None:
        if self.stage not in {"KIT_PASS", "P_ADM_ATTACH"}:
            raise ProvisionError("U-DUAL is offered after kit PASS")
        self.stage = "U_DUAL_OFFER"

    def attach_udual(self, *, bundled_free: bool = False) -> LocalMothership:
        if bundled_free:
            raise ProvisionError(
                "U-DUAL is never free with P-ADM or U-SOR",
                reason_code="UDUAL_NOT_FREE",
            )
        if "L1" not in self.sold:
            raise ProvisionError("U-DUAL requires L1", reason_code="PACK_SCOPE")
        if self.stage not in {"KIT_PASS", "P_ADM_ATTACH", "U_DUAL_OFFER"}:
            raise ProvisionError(f"cannot attach U-DUAL from {self.stage}")
        local = self._require_local()
        local.attach_pack("U-DUAL")
        local.attach_industry("industry.sales")
        self.sold.append("U-DUAL")
        self.stage = "U_DUAL_ATTACH"
        return local

    def book(self, service_id: str) -> dict[str, Any]:
        if "L1" not in self.sold:
            raise ProvisionError("services book after L1")
        booked = book_service(service_id, skus=tuple(self.sold))
        if booked.get("sku") in ALLOWED_SKUS:
            raise ProvisionError("fee-for-service cannot mint a SKU", reason_code="CATALOG_SKU")
        self.services.append(booked)
        return booked

    def claim_live_pin(self) -> None:
        raise LivePinError(
            "LIVE_PIN_OK cannot be marked from this plane. G1/G10 are open.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )

    def claim_signed_l1(self) -> None:
        raise ProvisionError(
            "Signed L1 is G13 and is not marked from this plane.",
            reason_code="SIGNED_L1_OPEN",
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "client_id": self.client_id,
            "stage": self.stage,
            "sold": list(self.sold),
            "kit_pass": self.kit_pass,
            "live": False,
            "live_pin_ok": False,
            "signed_l1": False,
            "services": list(self.services),
        }

    def _require_local(self) -> LocalMothership:
        if self.local is None:
            raise ProvisionError("no local mothership")
        return self.local
