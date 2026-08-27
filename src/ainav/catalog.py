"""Commercial catalog. Source of truth for SKUs. No invented products."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any

from agent_gov.errors import IntegrityError

ALLOWED_SKUS = frozenset({"L1", "P-ADM", "U-DUAL"})


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    raw = files("ainav.data").joinpath("catalog.json").read_text(encoding="utf-8")
    catalog = json.loads(raw)
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog: dict[str, Any]) -> None:
    if catalog.get("schema_version") != "ainav.catalog.v1":
        raise IntegrityError("unsupported catalog schema", reason_code="CATALOG_SCHEMA")
    if catalog.get("entity", {}).get("job") != "C":
        raise IntegrityError("catalog job must be C", reason_code="CATALOG_JOB")
    skus = {item["id"] for item in catalog.get("skus", [])}
    if skus != ALLOWED_SKUS:
        raise IntegrityError(
            f"catalog SKUs must be exactly {sorted(ALLOWED_SKUS)}",
            reason_code="CATALOG_SKU",
        )
    for sku_item in catalog["skus"]:
        if sku_item["id"] == "U-DUAL":
            never = set(sku_item.get("never_free_with") or [])
            if "P-ADM" not in never:
                raise IntegrityError("U-DUAL must never be free with P-ADM")
    module_ids: set[str] = set()
    for module in catalog.get("modules", []):
        if module.get("sku") not in ALLOWED_SKUS:
            raise IntegrityError(f"module {module.get('id')} has invented SKU")
        module_ids.add(module["id"])
    _validate_named_sets(catalog.get("industry_packs", []), module_ids, "industry pack")
    _validate_named_sets(catalog.get("libraries", []), module_ids, "library")
    for svc in catalog.get("fee_for_service", []):
        if svc.get("id") in ALLOWED_SKUS or svc.get("sku"):
            raise IntegrityError("fee-for-service is not a SKU", reason_code="CATALOG_SKU")
        included = svc.get("included_in")
        if included and included not in ALLOWED_SKUS:
            raise IntegrityError(
                f"fee-for-service {svc.get('id')} included_in invented SKU",
                reason_code="CATALOG_SKU",
            )
    from ainav.business import validate_business
    from ainav.ip import validate_ip_doctrine
    from ainav.microsoft.connections import validate_connections
    from ainav.programs import validate_programs

    validate_ip_doctrine(catalog)
    validate_programs(catalog)
    validate_connections(catalog)
    validate_business(catalog)


def _validate_named_sets(items: list[dict[str, Any]], module_ids: set[str], kind: str) -> None:
    for item in items:
        ident = item.get("id")
        if ident in ALLOWED_SKUS:
            raise IntegrityError(f"{kind} cannot be a SKU", reason_code="CATALOG_SKU")
        required = item.get("requires_sku")
        if required not in ALLOWED_SKUS:
            raise IntegrityError(f"{kind} {ident} has invented SKU", reason_code="CATALOG_SKU")
        for mid in item.get("modules", []):
            if mid not in module_ids:
                raise IntegrityError(f"{kind} {ident} references unknown module {mid}")


def sku(sku_id: str) -> dict[str, Any]:
    for item in load_catalog()["skus"]:
        if item["id"] == sku_id:
            return dict(item)
    raise IntegrityError(f"unknown SKU {sku_id}", reason_code="CATALOG_SKU")


def modules_for(sku_id: str) -> list[dict[str, Any]]:
    sku(sku_id)
    return [dict(m) for m in load_catalog()["modules"] if m["sku"] == sku_id]


def action_classes_for(sku_id: str) -> frozenset[str]:
    return frozenset(m["id"] for m in modules_for(sku_id) if m.get("kind") == "action")


def l1_action_classes() -> frozenset[str]:
    return action_classes_for("L1")


def udual_action_classes() -> frozenset[str]:
    return action_classes_for("U-DUAL")


def industry_pack(pack_id: str) -> dict[str, Any]:
    for item in load_catalog().get("industry_packs", []):
        if item["id"] == pack_id:
            return dict(item)
    raise IntegrityError(f"unknown industry pack {pack_id}", reason_code="CATALOG_PACK")


def library(library_id: str) -> dict[str, Any]:
    for item in load_catalog().get("libraries", []):
        if item["id"] == library_id:
            return dict(item)
    raise IntegrityError(f"unknown library {library_id}", reason_code="CATALOG_LIB")


def fee_for_service(service_id: str) -> dict[str, Any]:
    for item in load_catalog().get("fee_for_service", []):
        if item["id"] == service_id:
            return dict(item)
    raise IntegrityError(f"unknown fee-for-service {service_id}", reason_code="CATALOG_FFS")


def operations() -> dict[str, Any]:
    return dict(load_catalog()["operations"])


def microsoft_stack() -> dict[str, Any]:
    return dict(load_catalog()["microsoft_stack"])
