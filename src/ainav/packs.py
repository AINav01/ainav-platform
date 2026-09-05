"""Industry packs, module libraries, and local-mothership manifests.

None of these are SKUs. They deepen L1 / P-ADM / U-DUAL on the same plane.
"""

from __future__ import annotations

from typing import Any

from ainav.catalog import (
    attach_band,
    fee_for_service,
    industry_pack,
    library,
    load_catalog,
)
from ainav.errors import ProvisionError
from ainav.microsoft.stack import declared_stack


def require_industry(pack_id: str, *, skus: tuple[str, ...]) -> dict[str, Any]:
    pack = industry_pack(pack_id)
    if pack["requires_sku"] not in skus:
        raise ProvisionError(
            f"{pack_id} requires paid SKU {pack['requires_sku']}",
            reason_code="PACK_SCOPE",
        )
    return pack


def require_library(library_id: str, *, skus: tuple[str, ...]) -> dict[str, Any]:
    lib = library(library_id)
    if lib["requires_sku"] not in skus:
        raise ProvisionError(
            f"{library_id} requires paid SKU {lib['requires_sku']}",
            reason_code="PACK_SCOPE",
        )
    return lib


def book_service(service_id: str, *, skus: tuple[str, ...]) -> dict[str, Any]:
    """Fee-for-service hours. Never a SKU. Never attaches U-DUAL."""
    svc = fee_for_service(service_id)
    included = svc.get("included_in")
    if included and included in skus:
        return {
            "id": service_id,
            "name": svc.get("name"),
            "billed": False,
            "sku": None,
            "note": svc.get("note"),
        }
    if svc.get("billable"):
        if svc.get("requires_l1") is not False and "L1" not in skus:
            raise ProvisionError(
                "billable fee-for-service books only after L1",
                reason_code="FFS_SCOPE",
            )
        if svc.get("attaches_udual") is True:
            raise ProvisionError("fee-for-service cannot attach U-DUAL", reason_code="UDUAL_NOT_FREE")
        return {
            "id": service_id,
            "name": svc.get("name"),
            "billed": True,
            "sku": None,
            "rate_usd_per_day": svc.get("rate_usd_per_day"),
            "note": svc.get("note"),
        }
    raise ProvisionError(f"{service_id} is not bookable on {skus!r}", reason_code="FFS_SCOPE")


def pack_manifest(
    *,
    client_id: str,
    skus: tuple[str, ...],
    industry: tuple[str, ...],
    allowed_actions: frozenset[str] | set[str],
    modules: list[dict[str, Any]],
    libraries: tuple[str, ...] = (),
    host_mode: str = "local",
    lockfile_digest: str | None = None,
) -> dict[str, Any]:
    cat = load_catalog()
    stack = declared_stack()
    kind = {
        "local": "ainav.local_mothership.v1",
        "cloud": "ainav.cloud_mothership.v1",
        "master": "ainav.master_mothership.v1",
    }.get(host_mode, "ainav.local_mothership.v1")
    return {
        "kind": kind,
        "host_mode": host_mode,
        "client_id": client_id,
        "skus": list(skus),
        "industry": list(industry),
        "libraries": list(libraries),
        "allowed_actions": sorted(allowed_actions),
        "modules": modules,
        "lockfile_digest": lockfile_digest,
        "shared_ledger": bool(cat.get("motherships", {}).get("shared_ledger")),
        "microsoft": stack,
        "not_the_product": stack.get("not_the_product"),
        "connections": [item["id"] for item in cat.get("connections", {}).get("items", [])],
        "twin": {"live": False, "label": "SANDBOX"},
        "open_gaps": list(cat["open_gaps"]),
        "live": False,
    }


def public_packs() -> dict[str, Any]:
    """Institute catalog-list. Packs, libraries, FFS, and repos are not SKUs."""
    cat = load_catalog()
    return {
        "kind": "ainav.institute.packs.v1",
        "sku": False,
        "live": False,
        "live_pin_ok": False,
        "note": "Industry desks, libraries, fee-for-service hours, and repositories are not SKUs.",
        "industry": [
            {
                "id": pack["id"],
                "name": pack["name"],
                "requires_sku": pack["requires_sku"],
                "modules": list(pack.get("modules") or []),
                "included": bool(pack.get("included_in_sku")),
                "min": attach_band(pack)[0],
                "max": attach_band(pack)[1],
                "ala_carte": bool(pack.get("ala_carte")),
                "note": pack.get("note"),
                "sku": False,
            }
            for pack in cat.get("industry_packs") or []
        ],
        "libraries": [
            {
                "id": lib["id"],
                "requires_sku": lib["requires_sku"],
                "modules": list(lib.get("modules") or []),
                "note": lib.get("note"),
                "sku": False,
            }
            for lib in cat.get("libraries") or []
        ],
        "fee_for_service": [
            {
                "id": svc["id"],
                "name": svc.get("name"),
                "billable": bool(svc.get("billable")),
                "rate_usd_per_day": svc.get("rate_usd_per_day"),
                "requires_l1": bool(svc.get("requires_l1")),
                "attaches_udual": False,
                "note": svc.get("note"),
                "sku": False,
            }
            for svc in cat.get("fee_for_service") or []
        ],
        "repositories": [
            {
                "id": repo["id"],
                "path": repo.get("path"),
                "note": repo.get("note"),
                "sku": False,
                "live": False,
            }
            for repo in cat.get("repositories") or []
        ],
    }
