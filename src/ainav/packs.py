"""Industry packs, module libraries, and local-mothership manifests.

None of these are SKUs. They deepen L1 / P-ADM / U-DUAL on the same plane.
"""

from __future__ import annotations

from typing import Any

from ainav.catalog import (
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
) -> dict[str, Any]:
    cat = load_catalog()
    stack = declared_stack()
    return {
        "kind": "ainav.local_mothership.v1",
        "client_id": client_id,
        "skus": list(skus),
        "industry": list(industry),
        "libraries": list(libraries),
        "allowed_actions": sorted(allowed_actions),
        "modules": modules,
        "microsoft": stack,
        "not_the_product": stack.get("not_the_product"),
        "connections": [item["id"] for item in cat.get("connections", {}).get("items", [])],
        "twin": {"live": False, "label": "SANDBOX"},
        "open_gaps": list(cat["open_gaps"]),
        "live": False,
    }
