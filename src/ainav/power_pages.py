"""Honest Power Pages. Considered. Not the Institute host.

Power Pages is not a SKU. Power Pages is not the CMS.
Power Pages does not close US Dataverse.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_POWER_PAGES_FACT_IDS,
    HONEST_POWER_PAGES_HREFS,
    HONEST_POWER_PAGES_REFUSE_IDS,
    HONEST_POWER_PAGES_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.power_pages.v1"
COMPLEMENT_COUNT = 8


def validate_honest_power_pages(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_power_pages")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest Power Pages", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest Power Pages kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "cms",
        "host",
        "is_host",
        "apex",
        "closes_dataverse",
        "wired",
        "claimed",
        "certified",
        "live",
        "live_pin_ok",
        "launch",
        "created",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest Power Pages cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest Power Pages stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest Power Pages stays considered", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#twin":
        raise IntegrityError("honest Power Pages sits on #twin", reason_code="CATALOG_REVIEW")
    if body.get("is_host") is not False:
        raise IntegrityError("Power Pages is not the Institute host", reason_code="CATALOG_REVIEW")
    if body.get("is_sku") is not False:
        raise IntegrityError("Power Pages is not a SKU", reason_code="CATALOG_REVIEW")
    if body.get("cms") is not False:
        raise IntegrityError("Power Pages is not the CMS", reason_code="CATALOG_REVIEW")
    if body.get("closes_dataverse") is not False:
        raise IntegrityError("Power Pages does not close US Dataverse", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_POWER_PAGES_FACT_IDS):
        raise IntegrityError("honest Power Pages stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest Power Pages facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_POWER_PAGES_FACT_IDS):
        raise IntegrityError("honest Power Pages facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("host") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest Power Pages facts are not SKUs or hosts", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_POWER_PAGES_REFUSE_IDS):
        raise IntegrityError("honest Power Pages refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_POWER_PAGES_REFUSE_TEXT[key] for key in HONEST_POWER_PAGES_REFUSE_IDS}:
        raise IntegrityError("honest Power Pages refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_POWER_PAGES_HREFS[key] for key in HONEST_POWER_PAGES_REFUSE_IDS}:
        raise IntegrityError("honest Power Pages refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest Power Pages refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest power pages" not in note:
        raise IntegrityError("honest Power Pages note keeps honest Power Pages", reason_code="CATALOG_REVIEW")
    if "power pages is not the institute host" not in note:
        raise IntegrityError("honest Power Pages note keeps Power Pages is not the Institute host", reason_code="CATALOG_REVIEW")
    if "power pages is not a sku" not in note:
        raise IntegrityError("honest Power Pages note keeps Power Pages is not a SKU", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "dataverse-backed" not in lede and "dataverse backed" not in lede:
        raise IntegrityError("honest Power Pages lede keeps Dataverse-backed", reason_code="CATALOG_REVIEW")
    if "power pages is not the institute host" not in lede:
        raise IntegrityError("honest Power Pages lede keeps Power Pages is not the Institute host", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest power pages" not in site:
        raise IntegrityError("honest Power Pages site keeps honest Power Pages", reason_code="CATALOG_REVIEW")
    if "not a /power-pages route" not in site:
        raise IntegrityError("honest Power Pages site keeps not a /power-pages route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest Power Pages site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = ((catalog.get("connections") or {}).get("complements") or [])
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Power Pages is not a complement", reason_code="CATALOG_REVIEW")
    if any("power" in str(item.get("id") or "").lower() and "page" in str(item.get("id") or "").lower() for item in complements):
        raise IntegrityError("Power Pages is not a complement", reason_code="CATALOG_REVIEW")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("Power Pages playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot create a Power Pages site", reason_code="CATALOG_REVIEW")


def run_power_pages_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree consider. No live HTTP. Never a host. Never a SKU. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_power_pages(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after Power Pages consider", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "is_host": False,
        "is_sku": False,
        "cms": False,
        "closes_dataverse": False,
        "is_complement": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_power_pages"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_power_pages_certification()
    cat = load_catalog()
    return {
        "kind": KIND,
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "product": body["product"],
        "microsoft_product": body.get("microsoft_product"),
        "is_sku": False,
        "fourth_sku": False,
        "is_connection": False,
        "is_complement": False,
        "is_admit_plane": False,
        "cms": False,
        "is_host": False,
        "closes_dataverse": False,
        "created": False,
        "live": False,
        "live_pin_ok": False,
        "wired": False,
        "certified": False,
        "considered": True,
        "honest": True,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "href": "#twin",
        "facts": [dict(item) for item in body.get("facts") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat Power Pages as the Institute host.",
            "Treat Power Pages as a SKU.",
            "Treat Power Pages as the CMS.",
            "Treat Power Pages as the Institute apex.",
            "Treat Power Pages as a Dataverse close.",
        ],
    }
