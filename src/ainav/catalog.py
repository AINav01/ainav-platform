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
    for sku in catalog["skus"]:
        if sku["id"] == "U-DUAL":
            never = set(sku.get("never_free_with") or [])
            if "P-ADM" not in never:
                raise IntegrityError("U-DUAL must never be free with P-ADM")
    for module in catalog.get("modules", []):
        if module.get("sku") not in ALLOWED_SKUS:
            raise IntegrityError(f"module {module.get('id')} has invented SKU")


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
