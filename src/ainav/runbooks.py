"""Industry seating runbooks. Not SKUs. Same admit plane."""

from __future__ import annotations

from typing import Any

from ainav.catalog import industry_pack, load_catalog


def seating_runbook(pack_id: str) -> dict[str, Any]:
    pack = industry_pack(pack_id)
    return {
        "id": pack["id"],
        "name": pack["name"],
        "requires_sku": pack["requires_sku"],
        "modules": list(pack["modules"]),
        "steps": list(pack.get("runbook") or []),
        "sku": False,
        "live": False,
    }


def all_runbooks() -> dict[str, Any]:
    cat = load_catalog()
    return {
        "kind": "ainav.runbooks.v1",
        "items": [seating_runbook(item["id"]) for item in cat["industry_packs"]],
        "live": False,
        "note": "Runbooks deepen seating. They do not mint a SKU.",
    }
