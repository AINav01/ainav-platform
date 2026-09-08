"""Honest industry certify. Standard, upsells, modules, libraries, and repositories by industry.

Packs are not SKUs. Industry certify is not launch.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    ALLOWED_SKUS,
    HONEST_INDUSTRY_HREFS,
    HONEST_INDUSTRY_LIBRARY_PAIRS,
    HONEST_INDUSTRY_PACK_COUNT,
    HONEST_INDUSTRY_REFUSE_IDS,
    HONEST_INDUSTRY_REFUSE_TEXT,
    HONEST_INDUSTRY_STANDARD_COUNT,
    HONEST_INDUSTRY_UNPAIRED_LIBS,
    HONEST_INDUSTRY_UNPAIRED_PACKS,
    HONEST_INDUSTRY_UPSELL_COUNT,
    LIBRARY_COUNT,
    MODULE_COUNT,
    REPOSITORY_COUNT,
    load_catalog,
)

KIND = "ainav.honest.industry.v1"


def _as_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise IntegrityError(f"{label} must be an object", reason_code="CATALOG_SHAPE")
    return value


def validate_honest_industry(catalog: dict[str, Any]) -> None:
    body = catalog.get("industry_certify")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest industry certify", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest industry kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_admit_plane",
        "cms",
        "live",
        "live_pin_ok",
        "launch",
        "wired",
        "claimed",
        "certified",
        "packs_are_skus",
        "libraries_are_skus",
        "repositories_are_skus",
        "named_vertical_is_sku",
        "industry_certified_launch",
        "certify_is_launch",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest industry cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest industry stays honest", reason_code="CATALOG_REVIEW")
    if body.get("packs_are_skus") is not False:
        raise IntegrityError("packs are not SKUs", reason_code="CATALOG_REVIEW")
    if body.get("industry_certified_launch") is not False:
        raise IntegrityError("industry certify is not launch", reason_code="CATALOG_REVIEW")
    if body.get("complete") is not True:
        raise IntegrityError("honest industry inventory stays complete", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#packs":
        raise IntegrityError("honest industry sits on #packs", reason_code="CATALOG_REVIEW")
    rows = body.get("rows") or []
    if not isinstance(rows, list) or len(rows) != HONEST_INDUSTRY_PACK_COUNT:
        raise IntegrityError("honest industry rows stay the twenty-six desks", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in rows):
        raise IntegrityError("honest industry rows stay objects", reason_code="CATALOG_REVIEW")
    packs = [item for item in (catalog.get("industry_packs") or []) if isinstance(item, dict)]
    if [item.get("id") for item in rows] != [item.get("id") for item in packs]:
        raise IntegrityError("honest industry rows stay catalog pack order", reason_code="CATALOG_REVIEW")
    computed = certify_industry(catalog)
    if [item.get("id") for item in rows] != [item.get("id") for item in computed]:
        raise IntegrityError("honest industry rows stay computed certify", reason_code="CATALOG_REVIEW")
    for row, want in zip(rows, computed, strict=True):
        if row.get("class") != want["class"] or row.get("requires_sku") != want["requires_sku"]:
            raise IntegrityError("honest industry class stays catalog law", reason_code="CATALOG_REVIEW")
        if list(row.get("modules") or []) != list(want["modules"]):
            raise IntegrityError("honest industry modules stay catalog law", reason_code="CATALOG_REVIEW")
        if list(row.get("libraries") or []) != list(want["libraries"]):
            raise IntegrityError("honest industry libraries stay catalog law", reason_code="CATALOG_REVIEW")
        if row.get("sku") is True or row.get("live") is True or row.get("seat") is True:
            raise IntegrityError("industry desks are not SKUs or seats", reason_code="CATALOG_REVIEW")
        if row.get("href") != "#packs":
            raise IntegrityError("honest industry hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    standard = [item for item in rows if item.get("class") == "standard"]
    upsell = [item for item in rows if item.get("class") == "upsell"]
    if len(standard) != HONEST_INDUSTRY_STANDARD_COUNT or len(upsell) != HONEST_INDUSTRY_UPSELL_COUNT:
        raise IntegrityError("honest industry keeps eight standard and eighteen upsell", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_INDUSTRY_REFUSE_IDS):
        raise IntegrityError("honest industry refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_INDUSTRY_REFUSE_TEXT[key] for key in HONEST_INDUSTRY_REFUSE_IDS}:
        raise IntegrityError("honest industry refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_INDUSTRY_HREFS[key] for key in HONEST_INDUSTRY_REFUSE_IDS}:
        raise IntegrityError("honest industry refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest industry refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    modules = [item.get("id") for item in (catalog.get("modules") or []) if isinstance(item, dict)]
    libraries = [item.get("id") for item in (catalog.get("libraries") or []) if isinstance(item, dict)]
    repositories = [item.get("id") for item in (catalog.get("repositories") or []) if isinstance(item, dict)]
    if len(modules) != MODULE_COUNT:
        raise IntegrityError("honest industry keeps thirty modules", reason_code="CATALOG_REVIEW")
    if len(libraries) != LIBRARY_COUNT:
        raise IntegrityError("honest industry keeps twenty-three libraries", reason_code="CATALOG_REVIEW")
    if len(repositories) != REPOSITORY_COUNT:
        raise IntegrityError("honest industry keeps eleven repositories", reason_code="CATALOG_REVIEW")
    if list(body.get("modules") or []) != modules:
        raise IntegrityError("honest industry module inventory stays catalog law", reason_code="CATALOG_REVIEW")
    if list(body.get("libraries") or []) != libraries:
        raise IntegrityError("honest industry library inventory stays catalog law", reason_code="CATALOG_REVIEW")
    if list(body.get("repositories") or []) != repositories:
        raise IntegrityError("honest industry repository inventory stays catalog law", reason_code="CATALOG_REVIEW")
    unpaired_libs = set(libraries) - {lib for libs in HONEST_INDUSTRY_LIBRARY_PAIRS.values() for lib in libs}
    if unpaired_libs != set(HONEST_INDUSTRY_UNPAIRED_LIBS):
        raise IntegrityError("honest industry unpaired libraries stay catalog law", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest industry" not in note:
        raise IntegrityError("honest industry note keeps honest industry", reason_code="CATALOG_REVIEW")
    if "packs are not skus" not in note:
        raise IntegrityError("honest industry note keeps packs are not SKUs", reason_code="CATALOG_REVIEW")
    if "industry certify is not launch" not in note:
        raise IntegrityError("honest industry note keeps industry certify is not launch", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "standard" not in lede or "upsell" not in lede:
        raise IntegrityError("honest industry lede keeps standard and upsell", reason_code="CATALOG_REVIEW")
    if "industry certify is not launch" not in lede:
        raise IntegrityError("honest industry lede keeps industry certify is not launch", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest industry" not in site:
        raise IntegrityError("honest industry site keeps honest industry", reason_code="CATALOG_REVIEW")
    if "#packs" not in site:
        raise IntegrityError("honest industry site keeps #packs", reason_code="CATALOG_REVIEW")
    if "industry certify is not launch" not in site:
        raise IntegrityError("honest industry site keeps industry certify is not launch", reason_code="CATALOG_REVIEW")
    if "not a /industry route" not in site:
        raise IntegrityError("honest industry site keeps not a /industry route", reason_code="CATALOG_REVIEW")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    if operating.get("operator") != "cursor.cloud_agent":
        raise IntegrityError("recorded operator stays cursor.cloud_agent", reason_code="CATALOG_REVIEW")
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    owner = operating.get("owner_principal")
    if playbook.get("actor") != owner:
        raise IntegrityError("industry playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat industry certify as launch", reason_code="CATALOG_REVIEW")


def certify_industry(catalog: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Walk every industry desk. Packs are not SKUs. Empty library is honest."""
    cat = catalog or load_catalog()
    packs = [item for item in (cat.get("industry_packs") or []) if isinstance(item, dict)]
    modules = {item.get("id") for item in (cat.get("modules") or []) if isinstance(item, dict)}
    libraries = {item.get("id"): item for item in (cat.get("libraries") or []) if isinstance(item, dict)}
    if len(packs) != HONEST_INDUSTRY_PACK_COUNT:
        raise IntegrityError("industry certify keeps twenty-six desks", reason_code="CATALOG_REVIEW")
    rows: list[dict[str, Any]] = []
    for pack in packs:
        pack_id = str(pack.get("id") or "")
        if pack_id not in HONEST_INDUSTRY_LIBRARY_PAIRS:
            raise IntegrityError(f"industry {pack_id} missing library pair", reason_code="CATALOG_REVIEW")
        sku = pack.get("requires_sku")
        if sku not in ALLOWED_SKUS:
            raise IntegrityError(f"industry {pack_id} has invented SKU", reason_code="CATALOG_SKU")
        if pack.get("sku") is True or pack.get("id") in ALLOWED_SKUS:
            raise IntegrityError("industry pack cannot be a SKU", reason_code="CATALOG_SKU")
        pack_modules = list(pack.get("modules") or [])
        for mid in pack_modules:
            if mid not in modules:
                raise IntegrityError(f"industry {pack_id} references unknown module {mid}")
        paired = list(HONEST_INDUSTRY_LIBRARY_PAIRS[pack_id])
        if pack_id in HONEST_INDUSTRY_UNPAIRED_PACKS and paired:
            raise IntegrityError(f"industry {pack_id} stays unpaired", reason_code="CATALOG_REVIEW")
        if pack_id not in HONEST_INDUSTRY_UNPAIRED_PACKS and not paired:
            raise IntegrityError(f"industry {pack_id} missing paired library", reason_code="CATALOG_REVIEW")
        for lib_id in paired:
            lib = libraries.get(lib_id)
            if not isinstance(lib, dict):
                raise IntegrityError(f"industry {pack_id} pairs unknown library {lib_id}")
            if lib.get("requires_sku") != sku:
                raise IntegrityError(f"industry {pack_id} library SKU must match", reason_code="CATALOG_SKU")
            if lib.get("sku") is True:
                raise IntegrityError("library cannot be a SKU", reason_code="CATALOG_SKU")
        klass = "standard" if pack.get("included_in_sku") is True else "upsell"
        rows.append(
            {
                "id": pack_id,
                "name": pack.get("name"),
                "class": klass,
                "requires_sku": sku,
                "modules": pack_modules,
                "libraries": paired,
                "repositories": "shared",
                "included": bool(pack.get("included_in_sku")),
                "href": "#packs",
                "sku": False,
                "seat": False,
                "live": False,
            }
        )
    return rows


def run_industry_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree inventory certify. No live HTTP. Never launch. Never LIVE_PIN_OK."""
    cat = catalog or load_catalog()
    validate_honest_industry(cat)
    rows = certify_industry(cat)
    repos = [item for item in (cat.get("repositories") or []) if isinstance(item, dict)]
    if any(item.get("sku") is True or item.get("live") is True for item in repos):
        raise IntegrityError("repositories are not SKUs and are not live", reason_code="CATALOG_SKU")
    if any(item.get("id") in ALLOWED_SKUS for item in repos):
        raise IntegrityError("repository cannot be a SKU", reason_code="CATALOG_SKU")
    return {
        "kind": KIND,
        "packs": len(rows),
        "standard": sum(1 for item in rows if item["class"] == "standard"),
        "upsell": sum(1 for item in rows if item["class"] == "upsell"),
        "modules": len(cat.get("modules") or []),
        "libraries": len(cat.get("libraries") or []),
        "repositories": len(repos),
        "unpaired_packs": sorted(HONEST_INDUSTRY_UNPAIRED_PACKS),
        "unpaired_libraries": sorted(HONEST_INDUSTRY_UNPAIRED_LIBS),
        "launch": False,
        "industry_certified_launch": False,
        "packs_are_skus": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["industry_certify"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_industry_certification()
    return {
        "kind": KIND,
        "entity": load_catalog()["entity"]["legal"],
        "institute": load_catalog()["entity"]["institute"],
        "product": body["product"],
        "is_sku": False,
        "fourth_sku": False,
        "is_connection": False,
        "is_admit_plane": False,
        "live": False,
        "live_pin_ok": False,
        "wired": False,
        "certified": False,
        "complete": True,
        "honest": True,
        "packs_are_skus": False,
        "libraries_are_skus": False,
        "repositories_are_skus": False,
        "named_vertical_is_sku": False,
        "industry_certified_launch": False,
        "certify_is_launch": False,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "href": "#packs",
        "rows": [dict(item) for item in body.get("rows") or []],
        "modules": list(body.get("modules") or []),
        "libraries": list(body.get("libraries") or []),
        "repositories": list(body.get("repositories") or []),
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat an industry pack as a SKU.",
            "Treat a library as a SKU.",
            "Treat a repository as a SKU.",
            "Treat a named vertical as a SKU.",
            "Treat industry certify as launch.",
        ],
    }
