"""Honest production. Recorded. A production sim is not production.

Fixing all is not this plane. Rehearsed elements are not live.
Making all much better is not launch. A rehearsal is not LIVE_PIN_OK.
Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_PRODUCTION_FACT_IDS,
    HONEST_PRODUCTION_HREFS,
    HONEST_PRODUCTION_REFUSE_IDS,
    HONEST_PRODUCTION_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.production.v1"
COMPLEMENT_COUNT = 8


def validate_honest_production(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_production")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest production", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest production kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "production_sim_is_production",
        "fix_all_is_this_plane",
        "elements_are_live",
        "better_is_launch",
        "rehearsal_is_live_pin",
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
                "honest production cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest production stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest production stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest production stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#firm":
        raise IntegrityError("honest production sits on #firm", reason_code="CATALOG_REVIEW")
    if body.get("production_sim_is_production") is not False:
        raise IntegrityError("a production sim is not production", reason_code="CATALOG_REVIEW")
    if body.get("fix_all_is_this_plane") is not False:
        raise IntegrityError("fixing all is not this plane", reason_code="CATALOG_REVIEW")
    if body.get("elements_are_live") is not False:
        raise IntegrityError("rehearsed elements are not live", reason_code="CATALOG_REVIEW")
    if body.get("better_is_launch") is not False:
        raise IntegrityError("making all much better is not launch", reason_code="CATALOG_REVIEW")
    if body.get("rehearsal_is_live_pin") is not False:
        raise IntegrityError("a rehearsal is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_PRODUCTION_FACT_IDS):
        raise IntegrityError("honest production stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest production facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_PRODUCTION_FACT_IDS):
        raise IntegrityError("honest production facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest production facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_PRODUCTION_REFUSE_IDS):
        raise IntegrityError("honest production refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_PRODUCTION_REFUSE_TEXT[key] for key in HONEST_PRODUCTION_REFUSE_IDS}:
        raise IntegrityError("honest production refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_PRODUCTION_HREFS[key] for key in HONEST_PRODUCTION_REFUSE_IDS}:
        raise IntegrityError("honest production refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest production refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest production" not in note:
        raise IntegrityError("honest production note keeps honest production", reason_code="CATALOG_REVIEW")
    if "a production sim is not production" not in note:
        raise IntegrityError("honest production note keeps a production sim is not production", reason_code="CATALOG_REVIEW")
    if "fixing all is not this plane" not in note:
        raise IntegrityError("honest production note keeps fixing all is not this plane", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "a production sim is not production" not in lede:
        raise IntegrityError("honest production lede keeps a production sim is not production", reason_code="CATALOG_REVIEW")
    if "making all much better is not launch" not in lede:
        raise IntegrityError("honest production lede keeps making all much better is not launch", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest production" not in site:
        raise IntegrityError("honest production site keeps honest production", reason_code="CATALOG_REVIEW")
    if "not a /firm route" not in site:
        raise IntegrityError("honest production site keeps not a /firm route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest production site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest production is not a complement", reason_code="CATALOG_REVIEW")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("production playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat a production sim as production", reason_code="CATALOG_REVIEW")


def run_production_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded rehearsal. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_production(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest production", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "production_sim_is_production": False,
        "fix_all_is_this_plane": False,
        "elements_are_live": False,
        "better_is_launch": False,
        "rehearsal_is_live_pin": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_production"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_production_certification()
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
        "production_sim_is_production": False,
        "fix_all_is_this_plane": False,
        "elements_are_live": False,
        "better_is_launch": False,
        "rehearsal_is_live_pin": False,
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
        "href": "#firm",
        "facts": [dict(item) for item in body.get("facts") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat a production sim as production.",
            "Treat fixing all as this plane.",
            "Treat rehearsed elements as live.",
            "Treat making all much better as launch.",
            "Treat a rehearsal as LIVE_PIN_OK.",
        ],
    }
