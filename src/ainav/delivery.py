"""Integrated delivery OS: master + cloud + local on one Job C ledger.

Not a second product. Not LIVE_PIN_OK. Catalog wins.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import ALLOWED_SKUS, load_catalog
from ainav.errors import LivePinError, ProvisionError


def validate_delivery(catalog: dict[str, Any]) -> None:
    hosts = catalog.get("motherships") or {}
    if list(hosts.get("hosts") or []) != ["master", "cloud", "local"]:
        raise IntegrityError("motherships must be master, cloud, local", reason_code="CATALOG_DELIVERY")
    if hosts.get("shared_ledger") is not True:
        raise IntegrityError("cloud and local must share one consume ledger", reason_code="CATALOG_DELIVERY")
    if (hosts.get("master") or {}).get("writes_client_sor") is True:
        raise IntegrityError("master cannot write client SoR", reason_code="CATALOG_DELIVERY")
    for host in ("master", "cloud", "local"):
        body = hosts.get(host) or {}
        if body.get("live") is True:
            raise IntegrityError(f"{host} mothership cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    delivery = catalog.get("delivery") or {}
    if delivery.get("shared_ledger") is not True:
        raise IntegrityError("delivery pair requires a shared ledger", reason_code="CATALOG_DELIVERY")
    raci = delivery.get("raci") or {}
    for seat in ("master", "cloud", "local", "buyer", "owner", "operator"):
        if not raci.get(seat):
            raise IntegrityError(f"delivery RACI missing {seat}", reason_code="CATALOG_DELIVERY")
    for repo in catalog.get("repositories") or []:
        if repo.get("id") in ALLOWED_SKUS or repo.get("sku"):
            raise IntegrityError("repository cannot be a SKU", reason_code="CATALOG_SKU")


def doctrine() -> dict[str, Any]:
    cat = load_catalog()
    return {
        "motherships": dict(cat["motherships"]),
        "delivery": dict(cat["delivery"]),
        "repositories": [dict(item) for item in cat.get("repositories") or []],
        "bd": dict(cat["business"].get("bd") or {}),
    }


def raci() -> dict[str, str]:
    return dict(load_catalog()["delivery"]["raci"])


def week_one() -> list[str]:
    return list(load_catalog()["delivery"]["week_one"])


class DeliverySystem:
    """Master issues law. Cloud + local share one consume ledger."""

    live = False

    def __init__(self, *, master: Any = None) -> None:
        from ainav.mothership import MasterMothership

        self.master = master or MasterMothership()
        self.pairs: dict[str, Any] = {}

    def provision_pair(
        self,
        client_id: str,
        *,
        packs: tuple[str, ...] = ("L1",),
        industry: tuple[str, ...] | None = None,
        libraries: tuple[str, ...] | None = None,
        kit_pass: bool = False,
    ) -> dict[str, Any]:
        from ainav.mothership import CloudMothership

        spec = load_catalog()["provisioning"]["standard_pair"]
        pair = self.master.provision_pair(
            client_id,
            packs=packs,
            industry=industry if industry is not None else tuple(spec["industry"]),
            libraries=libraries if libraries is not None else tuple(spec.get("libraries") or ()),
            kit_pass=kit_pass,
        )
        local = pair["local"]
        cloud = pair["cloud"]
        if local.lockfile.digest() != cloud.lockfile.digest():
            raise ProvisionError("pair lockfiles must match", reason_code="LOCKFILE_HASH_MISMATCH")
        if local.client.store is not cloud.client.store:
            raise ProvisionError("pair must share one consume ledger", reason_code="SHARED_LEDGER")
        if isinstance(cloud, CloudMothership) is False:
            raise ProvisionError("cloud host required", reason_code="HOST_MODE")
        self.pairs[client_id] = pair
        return pair

    def snapshot(self, client_id: str) -> dict[str, Any]:
        pair = self.pairs.get(client_id)
        if pair is None:
            raise ProvisionError(f"no delivery pair for {client_id}", reason_code="DELIVERY")
        local = pair["local"]
        cloud = pair["cloud"]
        return {
            "kind": "ainav.delivery.v1",
            "client_id": client_id,
            "live": False,
            "live_pin_ok": False,
            "shared_ledger": True,
            "lockfile_digest": local.lockfile.digest(),
            "hosts": {
                "master": self.master.company_surface(),
                "cloud": cloud.manifest(),
                "local": local.manifest(),
            },
            "raci": raci(),
            "week_one": week_one(),
            "bd": doctrine()["bd"],
            "repositories": doctrine()["repositories"],
        }

    def runbook(self, client_id: str) -> dict[str, Any]:
        body = load_catalog()["business"]["delivery"]
        return {
            "client_id": client_id,
            "master": body["master"],
            "cloud": body["cloud"],
            "local": body["local"],
            "steps": list(body["steps"]),
            "week_one": week_one(),
            "raci": raci(),
            "live": False,
        }

    def claim_live_pin(self) -> None:
        raise LivePinError(
            "Delivery cannot mark LIVE_PIN_OK. G1/G10 are open.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )


def public_delivery() -> dict[str, Any]:
    cat = load_catalog()
    return {
        "kind": "ainav.institute.delivery.v1",
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "hosts": list(cat["motherships"]["hosts"]),
        "law": cat["motherships"]["law"],
        "shared_ledger": True,
        "raci": raci(),
        "week_one": week_one(),
        "bd": dict(cat["business"].get("bd") or {}),
        "repositories": [item["id"] for item in cat.get("repositories") or []],
        "live": False,
        "live_pin_ok": False,
    }
