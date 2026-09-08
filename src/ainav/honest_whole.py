"""Honest whole. Business, build, and website on one board.

The stitch is not a SKU. A 10/10 review is not launch.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_WHOLE_HREFS,
    HONEST_WHOLE_LANE_HREFS,
    HONEST_WHOLE_LANE_IDS,
    HONEST_WHOLE_REFUSE_IDS,
    HONEST_WHOLE_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.whole.v1"


def validate_honest_whole(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_whole")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest whole", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest whole kind stays catalog law", reason_code="CATALOG_REVIEW")
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
        "whole_is_launch",
        "ten_is_launch",
        "stitch_is_sku",
        "website_is_apex",
        "ci_is_launch",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest whole cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest whole stays honest", reason_code="CATALOG_REVIEW")
    if body.get("complete") is not True:
        raise IntegrityError("honest whole inventory stays complete", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#whole":
        raise IntegrityError("honest whole sits on #whole", reason_code="CATALOG_REVIEW")
    if body.get("whole_is_launch") is not False:
        raise IntegrityError("the whole firm is not launch", reason_code="CATALOG_REVIEW")
    if body.get("ten_is_launch") is not False:
        raise IntegrityError("a 10/10 review is not launch", reason_code="CATALOG_REVIEW")
    if body.get("stitch_is_sku") is not False:
        raise IntegrityError("the stitch is not a SKU", reason_code="CATALOG_REVIEW")
    lanes = body.get("lanes") or []
    if not isinstance(lanes, list) or len(lanes) != len(HONEST_WHOLE_LANE_IDS):
        raise IntegrityError("honest whole stays seven lanes", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in lanes):
        raise IntegrityError("honest whole lanes stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in lanes] != list(HONEST_WHOLE_LANE_IDS):
        raise IntegrityError("honest whole lanes stay catalog law", reason_code="CATALOG_REVIEW")
    hrefs = {item.get("id"): item.get("href") for item in lanes}
    if hrefs != dict(HONEST_WHOLE_LANE_HREFS):
        raise IntegrityError("honest whole lane hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("seat") is True or item.get("live") is True for item in lanes):
        raise IntegrityError("honest whole lanes are not SKUs or seats", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_WHOLE_REFUSE_IDS):
        raise IntegrityError("honest whole refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_WHOLE_REFUSE_TEXT[key] for key in HONEST_WHOLE_REFUSE_IDS}:
        raise IntegrityError("honest whole refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_WHOLE_HREFS[key] for key in HONEST_WHOLE_REFUSE_IDS}:
        raise IntegrityError("honest whole refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest whole refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest whole" not in note:
        raise IntegrityError("honest whole note keeps honest whole", reason_code="CATALOG_REVIEW")
    if "10/10 review is not launch" not in note and "a 10/10 review is not launch" not in note:
        raise IntegrityError("honest whole note keeps 10/10 review is not launch", reason_code="CATALOG_REVIEW")
    if "the whole firm is not launch" not in note:
        raise IntegrityError("honest whole note keeps the whole firm is not launch", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "business, build, and website" not in lede:
        raise IntegrityError("honest whole lede keeps business, build, and website", reason_code="CATALOG_REVIEW")
    if "the whole firm is not launch" not in lede:
        raise IntegrityError("honest whole lede keeps the whole firm is not launch", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest whole" not in site:
        raise IntegrityError("honest whole site keeps honest whole", reason_code="CATALOG_REVIEW")
    if "not a /whole route" not in site:
        raise IntegrityError("honest whole site keeps not a /whole route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest whole site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("whole playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot mark the whole firm launch", reason_code="CATALOG_REVIEW")


def run_whole_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree stitch. No live HTTP. Never launch. Never LIVE_PIN_OK."""
    cat = catalog or load_catalog()
    validate_honest_whole(cat)
    from ainav.industry_certify import run_industry_certification
    from ainav.microsoft.institute_publish import publish_institute
    from ainav.microsoft.readiness import run_twin_certification

    industry = run_industry_certification(cat)
    ready = run_twin_certification(cat)
    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    if industry.get("packs") != 26 or ready.get("launch") is True:
        raise IntegrityError("honest whole keeps industry certified and launch open", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "lanes": len(HONEST_WHOLE_LANE_IDS),
        "write": True,
        "skus": True,
        "industry": True,
        "build": True,
        "business": True,
        "website": True,
        "launch": False,
        "whole_is_launch": False,
        "ten_is_launch": False,
        "stitch_is_sku": False,
        "website_is_apex": False,
        "ci_is_launch": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "institute_publish": held.get("reason"),
        "industry_packs": industry.get("packs"),
        "readiness_launch": False,
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_whole"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_whole_certification()
    cat = load_catalog()
    return {
        "kind": KIND,
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
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
        "whole_is_launch": False,
        "ten_is_launch": False,
        "stitch_is_sku": False,
        "website_is_apex": False,
        "ci_is_launch": False,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "href": "#whole",
        "lanes": [dict(item) for item in body.get("lanes") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat the whole firm as launch.",
            "Treat a 10/10 review as launch.",
            "Treat the stitch as a SKU.",
            "Treat the twin as the Institute apex.",
            "Treat a green check as launch.",
        ],
    }
