"""Business operations on the commercial spine. Catalog wins.

Happy path: QUALIFY → L1_SOLD → KIT_IN_PROGRESS → KIT_PASS → P_ADM_ATTACH
            → U_DUAL_OFFER → U_DUAL_ATTACH
Exits: LOST, KIT_FAIL, CHURN.

The Acceptance Kit is a twin proof, not a boolean. This plane cannot
mark LIVE_PIN_OK or signed L1. Quotes and invoices are catalog-list
artifacts, not recognized revenue.
"""

from __future__ import annotations

from typing import Any

from ainav.catalog import ALLOWED_SKUS, acceptance_kit, operations, sku
from ainav.errors import LivePinError, ProvisionError
from ainav.mothership import LocalMothership, MasterMothership
from ainav.packs import book_service


STAGES = tuple(operations()["stages"])
EXITS = tuple(operations().get("exits") or ())


class CommercialLedger:
    """AINav, Inc. quote/invoice book. Not a client SoR. Not revenue."""

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def quote(self, client_id: str, sku_id: str) -> dict[str, Any]:
        price = sku(sku_id)["price_usd"]
        entry = {
            "kind": "quote",
            "client_id": client_id,
            "sku": sku_id,
            "min": price["min"],
            "max": price["max"],
            "recognized": False,
            "live": False,
        }
        self.entries.append(entry)
        return dict(entry)

    def invoice(self, client_id: str, sku_id: str) -> dict[str, Any]:
        price = sku(sku_id)["price_usd"]
        entry = {
            "kind": "invoice",
            "client_id": client_id,
            "sku": sku_id,
            "min": price["min"],
            "max": price["max"],
            "recognized": False,
            "live": False,
            "note": "catalog list — not recognized revenue",
        }
        self.entries.append(entry)
        return dict(entry)


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
        self.kit_runs: list[dict[str, Any]] = []
        self.services: list[dict[str, Any]] = []
        self.local: LocalMothership | None = None
        self.cloud: LocalMothership | None = None
        self.coverage_active = False
        self.terms: dict[str, int] = {}
        self.ledger = CommercialLedger()
        kit = acceptance_kit()
        self.seats = {
            "seat_a": kit["seats"]["seat_a"]["lab"],
            "seat_b": kit["seats"]["seat_b"]["lab"],
            "roles": {
                "seat_a": kit["seats"]["seat_a"]["role"],
                "seat_b": kit["seats"]["seat_b"]["role"],
            },
        }

    def lose(self) -> None:
        if self.stage != "QUALIFY":
            raise ProvisionError("only a QUALIFY account can be marked LOST")
        self.stage = "LOST"

    def sell_l1(self) -> LocalMothership:
        if self.stage != "QUALIFY":
            raise ProvisionError(f"cannot sell L1 from {self.stage}")
        self.ledger.quote(self.client_id, "L1")
        spec = self.master.catalog["provisioning"]["standard_pair"]
        pair = self.master.provision_pair(
            self.client_id,
            packs=tuple(spec["skus"]),
            industry=tuple(spec["industry"]),
            libraries=tuple(spec.get("libraries") or ()),
        )
        self.local = pair["local"]
        self.cloud = pair["cloud"]
        self.sold.append("L1")
        self.stage = "L1_SOLD"
        self.ledger.invoice(self.client_id, "L1")
        return self.local

    def start_kit(self) -> None:
        if self.stage != "L1_SOLD":
            raise ProvisionError("Acceptance Kit starts after L1 is sold")
        self.stage = "KIT_IN_PROGRESS"

    def run_kit(self) -> dict[str, Any]:
        if self.stage != "KIT_IN_PROGRESS":
            raise ProvisionError("kit run requires KIT_IN_PROGRESS")
        local = self._require_local()
        kit = acceptance_kit()
        results: list[dict[str, Any]] = []
        passed = True
        for index, case in enumerate(kit["cases"]):
            action = dict(case["action"])
            action["proposal_id"] = f"prp-kit-{self.client_id}-{len(self.kit_runs)}-{index}"
            try:
                out = local.run_and_apply(
                    action,
                    seat_a=self.seats["seat_a"],
                    seat_b=self.seats["seat_b"],
                )
                ok = out.get("record_type") == case.get("expect")
            except Exception as exc:  # kit is fail-closed
                out = {"record_type": type(exc).__name__, "reason": str(exc)}
                ok = False
            passed = passed and ok
            results.append({"id": case["id"], "ok": ok, "effect": out.get("record_type")})
        report = {"passed": passed, "results": results, "live": False, "signed_l1": False}
        self.kit_runs.append(report)
        if not passed:
            self.stage = "KIT_FAIL"
        return report

    def pass_kit(self) -> dict[str, Any]:
        if self.stage != "KIT_IN_PROGRESS":
            raise ProvisionError("kit PASS requires KIT_IN_PROGRESS")
        report = self.run_kit()
        if not report["passed"]:
            raise ProvisionError("Acceptance Kit failed on the twin", reason_code="KIT_FAIL")
        self.kit_pass = True
        self.stage = "KIT_PASS"
        if self.local is not None:
            self.local.kit_pass = True
        if self.cloud is not None:
            self.cloud.kit_pass = True
        return report

    def attach_padm(self) -> LocalMothership:
        if not self.kit_pass or self.stage != "KIT_PASS":
            raise ProvisionError("P-ADM attaches only after kit PASS", reason_code="ATTACH_GATE")
        local = self._require_local()
        local.attach_pack("P-ADM")
        if self.cloud is not None:
            self.cloud.attach_pack("P-ADM")
        self.sold.append("P-ADM")
        self.terms["P-ADM"] = 1
        self.coverage_active = True
        self.stage = "P_ADM_ATTACH"
        self.ledger.invoice(self.client_id, "P-ADM")
        return local

    def offer_udual(self) -> None:
        if not self.kit_pass:
            raise ProvisionError("U-DUAL is offered after kit PASS", reason_code="ATTACH_GATE")
        if self.stage not in {"KIT_PASS", "P_ADM_ATTACH"}:
            raise ProvisionError("U-DUAL is offered after kit PASS")
        self.stage = "U_DUAL_OFFER"

    def attach_udual(self, *, bundled_free: bool = False) -> LocalMothership:
        if bundled_free:
            raise ProvisionError(
                "U-DUAL is never free with P-ADM or U-SOR",
                reason_code="UDUAL_NOT_FREE",
            )
        if not self.kit_pass:
            raise ProvisionError("U-DUAL attaches only after kit PASS", reason_code="ATTACH_GATE")
        if "L1" not in self.sold:
            raise ProvisionError("U-DUAL requires L1", reason_code="PACK_SCOPE")
        if self.stage not in {"KIT_PASS", "P_ADM_ATTACH", "U_DUAL_OFFER"}:
            raise ProvisionError(f"cannot attach U-DUAL from {self.stage}")
        local = self._require_local()
        local.attach_pack("U-DUAL")
        local.attach_industry("industry.sales")
        if self.cloud is not None:
            self.cloud.attach_pack("U-DUAL")
            self.cloud.attach_industry("industry.sales")
        self.sold.append("U-DUAL")
        self.terms["U-DUAL"] = 1
        self.stage = "U_DUAL_ATTACH"
        self.ledger.invoice(self.client_id, "U-DUAL")
        return local

    def renew(self, sku_id: str) -> dict[str, Any]:
        if sku_id not in {"P-ADM", "U-DUAL"}:
            raise ProvisionError("only P-ADM and U-DUAL renew", reason_code="CATALOG_SKU")
        if sku_id not in self.sold:
            raise ProvisionError(f"{sku_id} is not attached", reason_code="PACK_SCOPE")
        if not self.coverage_active and sku_id == "P-ADM":
            raise ProvisionError("churned coverage cannot renew", reason_code="CHURN")
        self.terms[sku_id] = int(self.terms.get(sku_id) or 1) + 1
        self.ledger.invoice(self.client_id, sku_id)
        return {"sku": sku_id, "term": self.terms[sku_id], "recognized": False, "live": False}

    def churn(self) -> None:
        if self.stage not in {"P_ADM_ATTACH", "U_DUAL_OFFER", "U_DUAL_ATTACH"}:
            raise ProvisionError("churn is only after a keep/deepen attach")
        self.coverage_active = False
        self.stage = "CHURN"

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
            "kit_runs": list(self.kit_runs),
            "seats": dict(self.seats),
            "coverage_active": self.coverage_active,
            "terms": dict(self.terms),
            "commercial": list(self.ledger.entries),
            "live": False,
            "live_pin_ok": False,
            "signed_l1": False,
            "services": list(self.services),
            "industry": list(self.local.industry) if self.local else [],
            "libraries": list(self.local.libraries) if self.local else [],
            "hosts": {
                "local": self.local.host_mode if self.local else None,
                "cloud": self.cloud.host_mode if self.cloud else None,
            },
        }

    def _require_local(self) -> LocalMothership:
        if self.local is None:
            raise ProvisionError("no local mothership")
        return self.local
