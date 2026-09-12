"""Honest path. Recorded. An industry is not a named client.

A shared sandbox is not production. Hours are not a SKU.
Rollback is not LIVE_PIN_OK. A redeploy is not launch.
Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_PATH_FACT_IDS,
    HONEST_PATH_HREFS,
    HONEST_PATH_REFUSE_IDS,
    HONEST_PATH_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.path.v1"
COMPLEMENT_COUNT = 8


def validate_honest_path(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_path")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest path", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest path kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "industry_is_named_client",
        "shared_sandbox_is_production",
        "hours_is_sku",
        "rollback_is_live_pin",
        "redeploy_is_launch",
        "cms",
        "host",
        "is_host",
        "apex",
        "closes_dual_admit",
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
                "honest path cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest path stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest path stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest path stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#path":
        raise IntegrityError("honest path sits on #path", reason_code="CATALOG_REVIEW")
    if body.get("industry_is_named_client") is not False:
        raise IntegrityError("an industry is not a named client", reason_code="CATALOG_REVIEW")
    if body.get("shared_sandbox_is_production") is not False:
        raise IntegrityError("a shared sandbox is not production", reason_code="CATALOG_REVIEW")
    if body.get("hours_is_sku") is not False:
        raise IntegrityError("hours are not a SKU", reason_code="CATALOG_REVIEW")
    if body.get("rollback_is_live_pin") is not False:
        raise IntegrityError("rollback is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    if body.get("redeploy_is_launch") is not False:
        raise IntegrityError("a redeploy is not launch", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_PATH_FACT_IDS):
        raise IntegrityError("honest path stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest path facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_PATH_FACT_IDS):
        raise IntegrityError("honest path facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest path facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_PATH_REFUSE_IDS):
        raise IntegrityError("honest path refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_PATH_REFUSE_TEXT[key] for key in HONEST_PATH_REFUSE_IDS}:
        raise IntegrityError("honest path refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_PATH_HREFS[key] for key in HONEST_PATH_REFUSE_IDS}:
        raise IntegrityError("honest path refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest path refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest path" not in note:
        raise IntegrityError("honest path note keeps honest path", reason_code="CATALOG_REVIEW")
    if "an industry is not a named client" not in note:
        raise IntegrityError("honest path note keeps an industry is not a named client", reason_code="CATALOG_REVIEW")
    if "a shared sandbox is not production" not in note:
        raise IntegrityError("honest path note keeps a shared sandbox is not production", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "an industry is not a named client" not in lede:
        raise IntegrityError("honest path lede keeps an industry is not a named client", reason_code="CATALOG_REVIEW")
    if "hours are not a sku" not in lede:
        raise IntegrityError("honest path lede keeps hours are not a SKU", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest path" not in site:
        raise IntegrityError("honest path site keeps honest path", reason_code="CATALOG_REVIEW")
    if "not a /path route" not in site:
        raise IntegrityError("honest path site keeps not a /path route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest path site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest path is not a complement", reason_code="CATALOG_REVIEW")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("path playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot invent a named client", reason_code="CATALOG_REVIEW")


def run_path_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded probe. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_path(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest path", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "industry_is_named_client": False,
        "shared_sandbox_is_production": False,
        "hours_is_sku": False,
        "rollback_is_live_pin": False,
        "redeploy_is_launch": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_path"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_path_certification()
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
        "is_job_c": False,
        "is_seat": False,
        "industry_is_named_client": False,
        "shared_sandbox_is_production": False,
        "hours_is_sku": False,
        "rollback_is_live_pin": False,
        "redeploy_is_launch": False,
        "created": False,
        "live": False,
        "live_pin_ok": False,
        "wired": False,
        "certified": False,
        "considered": True,
        "recorded": True,
        "honest": True,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "href": "#path",
        "facts": [dict(item) for item in body.get("facts") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat an industry as a named client.",
            "Treat a shared sandbox as production.",
            "Treat hours as a SKU.",
            "Treat rollback as LIVE_PIN_OK.",
            "Treat a redeploy as launch.",
        ],
    }
