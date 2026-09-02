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
    elevator = body.get("elevator") or {}
    if "control plane" not in str(elevator.get("ten") or "").lower():
        raise IntegrityError("business elevator ten is the control-plane one-liner", reason_code="CATALOG_BUSINESS")
    if "ninety" not in str(elevator.get("thirty") or "").lower() or "l1" not in str(elevator.get("thirty") or "").lower():
        raise IntegrityError("business elevator thirty is the ninety-minute L1 proof", reason_code="CATALOG_BUSINESS")
    if "walk away" not in str(elevator.get("ask") or "").lower():
        raise IntegrityError("business elevator ask is ninety minutes or walk away", reason_code="CATALOG_BUSINESS")
    if "gate in front of the write" not in str(body.get("why_client") or "").lower():
        raise IntegrityError("why_client is the missing gate", reason_code="CATALOG_BUSINESS")
    if "priced round" not in str(body.get("why_investor") or "").lower():
        raise IntegrityError("why_investor stays not a priced round", reason_code="CATALOG_BUSINESS")
    if "failsafe" not in str(body.get("thesis") or "").lower():
        raise IntegrityError("business thesis keeps the failsafe", reason_code="CATALOG_BUSINESS")
    if model.get("estate") != "same plane":
        raise IntegrityError("other uses stay on the same plane", reason_code="CATALOG_SKU")
    if model.get("audit") != "same plane":
        raise IntegrityError("audit stays on the same plane", reason_code="CATALOG_SKU")
    if model.get("regulated") != "room 1 books, room 2 refuse":
        raise IntegrityError("regulated is Room 1 books, Room 2 refuse", reason_code="CATALOG_BUSINESS")


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
            "cloud": body.get("cloud"),
            "last_sor_connection": account.local.last_sor_connection if account.local else None,
            "hosts": {
                "local": account.local.host_mode if account.local else None,
                "cloud": account.cloud.host_mode if account.cloud else None,
            },
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
        for host in (account.local, account.cloud):
            if host is None:
                continue
            host.attach_industry("industry.controller")
            host.attach_industry("industry.quote_desk")
            host.attach_library("lib.kit.evidence")
        self.store_kit_evidence(account)
        return account


def public_business() -> dict[str, Any]:
    cat = load_catalog()
    return {
        "kind": "ainav.institute.business.v1",
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "thesis": cat["business"]["thesis"],
        "elevator": dict(cat["business"].get("elevator") or {}),
        "why_client": cat["business"].get("why_client"),
        "why_investor": cat["business"].get("why_investor"),
        "estate_equation": cat["equations"].get("estate"),
        "audit_equation": cat["equations"].get("audit"),
        "model": cat["business"]["model"],
        "sales": cat["business"]["sales"],
        "delivery": cat["business"]["delivery"],
        "economics": cat["business"]["economics"],
        "acceptance_kit": {
            "requires_sku": "L1",
            "cases": [case["id"] for case in cat["acceptance_kit"]["cases"]],
            "signed_l1": False,
        },
        "proof_day": {
            "minutes": cat["proof_day"]["minutes"],
            "cli": cat["proof_day"]["cli"],
            "signed_l1": False,
            "live": False,
        },
        "buyer": {
            "write_that_must_not_happen": cat["buyer"]["write_that_must_not_happen"],
            "seats": list(cat["buyer"]["seats"]),
            "door": cat["buyer"]["door"],
            "contact_email": None,
        },
        "delivery": {
            "hosts": list(cat["motherships"]["hosts"]),
            "law": cat["motherships"]["law"],
            "shared_ledger": True,
            "raci": dict(cat["delivery"]["raci"]),
            "week_one": list(cat["delivery"]["week_one"]),
        },
        "next_pin": {
            "id": cat["next_pin"]["id"],
            "sent": False,
            "live": False,
            "live_pin_ok": False,
        },
        "icp": {
            "erp": cat["icp"]["erp"],
            "identity": cat["icp"]["identity"],
            "control": cat["icp"]["control"],
            "named_customers": [],
        },
        "organization": {
            "full_service": True,
            "all_wired_claimed": False,
            "second_officer": None,
            "departments": [
                {"id": item["id"], "name": item["name"], "status": item["status"]}
                for item in cat["organization"]["departments"]
            ],
        },
        "programs_order": list(cat["programs"]["application_order"]),
        "honest_missing": honest_missing(),
        "open_gaps": list(cat["open_gaps"]),
        "live": False,
    }


def public_business_plane() -> dict[str, Any]:
    """Application business workspace. Catalog list. Not a forecast."""
    from ainav.finance import model as finance_model

    cat = load_catalog()
    fin = finance_model()
    success = cat["expert_review"]["success"]
    invited = cat["organization"]["contacts"]["invited"]
    all_three = next(row for row in fin["scenarios"] if row["id"] == "all_three")
    return {
        "kind": "ainav.institute.business_plane.v1",
        "sku": False,
        "cms": False,
        "live": False,
        "live_pin_ok": False,
        "priced_round": False,
        "forecast": False,
        "recognized_revenue": 0,
        "signed_l1": 0,
        "named_customers": 0,
        "billing_provider": False,
        "walk_away_recorded": False,
        "release": cat["entity"]["release"],
        "legal": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "thesis": (
            "The business succeeds when a named controller walks away from the licensed "
            "substitute and buys L1. If-then catalog list is not a forecast. Not a priced round. "
            "Not LIVE_PIN_OK."
        ),
        "commercial": cat["equations"]["commercial"],
        "included_and_upsells": dict(cat["plane_interface"].get("included_and_upsells") or {}),
        "elevator": dict(cat["business"].get("elevator") or {}),
        "why_client": cat["business"].get("why_client"),
        "why_investor": cat["business"].get("why_investor"),
        "estate": dict(cat["plane_interface"].get("estate") or {}),
        "estate_equation": cat["equations"].get("estate"),
        "audit": dict(cat["plane_interface"].get("audit") or {}),
        "audit_equation": cat["equations"].get("audit"),
        "lab_pin": cat["equations"]["lab_pin"],
        "close": {
            "named_dual_seats": False,
            "proof_day_sold": False,
            "signed_l1": False,
            "p_adm_attached": 0,
            "closed": False,
            "note": "Mailbox recorded is not dual admit. Controllers buy the commercial equation. LIVE_PIN_OK is the lab pin.",
        },
        "year_one_all_three": {
            "min": all_three["min"],
            "max": all_three["max"],
            "forecast": False,
            "note": "Catalog list if one controller buys all three SKUs. Not booked.",
        },
        "path": [dict(item) for item in cat["plane_interface"]["provisioning"]["path"]],
        "scenarios": fin["scenarios"],
        "bake_off": dict(success["bake_off"]),
        "qualify": dict(success["qualify"]),
        "objections": [dict(item) for item in success["objections"]],
        "seat_b": {
            "name": invited["name"],
            "mailbox": invited.get("email"),
            "entra_oid": None,
            "seat_clicked": False,
            "officer": False,
            "equity": False,
            "second_unique_human": False,
            "number_two": True,
            "all_aspects": False,
        },
        "number_two": dict(cat["organization"]["number_two"]),
        "honest_missing": honest_missing(),
        "refuse": [
            "priced round",
            "forecast ARR",
            "recognized revenue",
            "invented walk-away",
            "LIVE_PIN_OK",
        ],
    }
