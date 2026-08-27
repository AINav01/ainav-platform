"""AINav, Inc. operating company. Catalog wins. Not a second product.

Pipeline, delivery, services, and management snapshots run on the same
Job C spine. Catalog list prices are not recognized revenue.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import ALLOWED_SKUS, honest_missing, load_catalog, sku
from ainav.errors import LivePinError, ProvisionError


def validate_business(catalog: dict[str, Any]) -> None:
    body = catalog.get("business")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing business doctrine", reason_code="CATALOG_BUSINESS")
    model = body.get("model") or {}
    if model.get("prove") != "L1" or model.get("keep") != "P-ADM" or model.get("deepen") != "U-DUAL":
        raise IntegrityError("business model cannot invent SKUs", reason_code="CATALOG_SKU")
    if body.get("economics", {}).get("recognized_revenue_claimed") is True:
        raise IntegrityError("recognized revenue cannot be claimed here", reason_code="REVENUE_NOT_CLAIMED")


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["business"])


class KitEvidence:
    """SharePoint sandbox for Acceptance Kit evidence. Not dual and not live."""

    live = False
    connection_id = "sharepoint.kit"

    def __init__(self) -> None:
        self.stored: list[dict[str, Any]] = []

    def store(self, envelope: dict[str, Any]) -> dict[str, Any]:
        from ainav.microsoft.connections import intended_request

        record = {
            "connection": self.connection_id,
            "live": False,
            "sent": False,
            "envelope": dict(envelope),
            "intended": intended_request(
                self.connection_id,
                method="PUT",
                path="/{site}/drive/root:/kit/{request_id}.json:/content",
                payload={"live": False, "kind": "ainav.kit.evidence"},
            ),
        }
        self.stored.append(record)
        return {"stored": True, "connection": self.connection_id, "live": False, "seq": len(self.stored)}

    def live_upload(self) -> None:
        raise LivePinError(
            "SharePoint live kit upload is not claimed. G1 LIVE_PIN_OK is open.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )


class OperatingCompany:
    """Master-side company OS: sales, delivery, services, management."""

    live = False

    def __init__(self, *, master: Any = None) -> None:
        from ainav.mothership import MasterMothership

        self.master = master or MasterMothership()
        self.accounts: dict[str, Any] = {}
        self.evidence = KitEvidence()

    def qualify(self, client_id: str) -> Any:
        from ainav.ops import ClientAccount

        if client_id in self.accounts:
            return self.accounts[client_id]
        account = ClientAccount(client_id, master=self.master)
        self.accounts[client_id] = account
        return account

    def pipeline(self) -> list[dict[str, Any]]:
        return [account.snapshot() for account in self.accounts.values()]

    def economics(self) -> dict[str, Any]:
        contracted_min = 0
        contracted_max = 0
        ffs_day_rate = 0
        for account in self.accounts.values():
            for sku_id in account.sold:
                price = sku(sku_id)["price_usd"]
                contracted_min += int(price["min"])
                contracted_max += int(price["max"])
            for booked in account.services:
                if booked.get("billed"):
                    ffs_day_rate += int(booked.get("rate_usd_per_day") or 0)
        return {
            "contracted_catalog_min": contracted_min,
            "contracted_catalog_max": contracted_max,
            "ffs_booked_day_rate": ffs_day_rate,
            "recognized_revenue": None,
            "live": False,
            "note": doctrine()["economics"]["note"],
        }

    def kit_board(self) -> list[dict[str, Any]]:
        return [
            account.snapshot()
            for account in self.accounts.values()
            if account.stage in {"KIT_IN_PROGRESS", "KIT_PASS"}
        ]

    def store_kit_evidence(self, account: Any) -> dict[str, Any]:
        if not account.kit_pass:
            raise ProvisionError("kit evidence stores only after kit PASS", reason_code="ATTACH_GATE")
        return self.evidence.store(account.snapshot())

    def delivery_runbook(self, account: Any) -> dict[str, Any]:
        body = doctrine()["delivery"]
        return {
            "client_id": account.client_id,
            "stage": account.stage,
            "master": body["master"],
            "local": body["local"],
            "steps": list(body["steps"]),
            "last_sor_connection": account.local.last_sor_connection if account.local else None,
            "live": False,
        }

    def management_snapshot(self) -> dict[str, Any]:
        body = doctrine()
        stages = Counter(account.stage for account in self.accounts.values())
        return {
            "entity": "AINav, Inc.",
            "thesis": body["thesis"],
            "model": body["model"],
            "cadence": list(body["management"]["cadence"]),
            "cannot_mark": list(body["management"]["cannot_mark"]),
            "pipeline": self.pipeline(),
            "stages": dict(stages),
            "kit_board": self.kit_board(),
            "economics": self.economics(),
            "skus": sorted(ALLOWED_SKUS),
            "stack": self.master.stack.describe(),
            "live": False,
            "open_gaps": list(load_catalog()["open_gaps"]),
            "honest_missing": honest_missing(),
        }

    def run_standard_engagement(self, client_id: str) -> Any:
        """Lab path through the commercial spine. Not a live pin."""
        account = self.qualify(client_id)
        account.sell_l1()
        account.start_kit()
        account.pass_kit()
        account.book("ffs.acceptance_kit")
        account.book("ffs.integration_assist")
        account.attach_padm()
        account.offer_udual()
        account.attach_udual()
        account.local.attach_industry("industry.controller")
        account.local.attach_industry("industry.quote_desk")
        account.local.attach_library("lib.kit.evidence")
        self.store_kit_evidence(account)
        return account


def public_business() -> dict[str, Any]:
    cat = load_catalog()
    return {
        "kind": "ainav.institute.business.v1",
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "thesis": cat["business"]["thesis"],
        "model": cat["business"]["model"],
        "sales": cat["business"]["sales"],
        "delivery": cat["business"]["delivery"],
        "economics": cat["business"]["economics"],
        "acceptance_kit": {
            "requires_sku": "L1",
            "cases": [case["id"] for case in cat["acceptance_kit"]["cases"]],
            "signed_l1": False,
        },
        "honest_missing": honest_missing(),
        "open_gaps": list(cat["open_gaps"]),
        "live": False,
    }
