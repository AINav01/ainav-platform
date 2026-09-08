"""Honest remainder. Recorded. A remainder close is not launch.

Leftover copy is not LIVE_PIN_OK. Owner hrefs are not owner clicks.
Gold 99.5 is not production. A deep remainder is not a seated second human.
Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_REMAINDER_FACT_IDS,
    HONEST_REMAINDER_HREFS,
    HONEST_REMAINDER_REFUSE_IDS,
    HONEST_REMAINDER_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.remainder.v1"
COMPLEMENT_COUNT = 8


def validate_honest_remainder(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_remainder")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest remainder", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest remainder kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "remainder_is_launch",
        "leftover_copy_is_live_pin",
        "owner_hrefs_are_clicks",
        "gold_995_is_production",
        "deep_remainder_is_seated",
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
                "honest remainder cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest remainder stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest remainder stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest remainder stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#missing":
        raise IntegrityError("honest remainder sits on #missing", reason_code="CATALOG_REVIEW")
    if body.get("remainder_is_launch") is not False:
        raise IntegrityError("a remainder close is not launch", reason_code="CATALOG_REVIEW")
    if body.get("leftover_copy_is_live_pin") is not False:
        raise IntegrityError("leftover copy is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    if body.get("owner_hrefs_are_clicks") is not False:
        raise IntegrityError("owner hrefs are not owner clicks", reason_code="CATALOG_REVIEW")
    if body.get("gold_995_is_production") is not False:
        raise IntegrityError("gold 99.5 is not production", reason_code="CATALOG_REVIEW")
    if body.get("deep_remainder_is_seated") is not False:
        raise IntegrityError("a deep remainder is not a seated second human", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_REMAINDER_FACT_IDS):
        raise IntegrityError("honest remainder stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest remainder facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_REMAINDER_FACT_IDS):
        raise IntegrityError("honest remainder facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest remainder facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_REMAINDER_REFUSE_IDS):
        raise IntegrityError("honest remainder refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_REMAINDER_REFUSE_TEXT[key] for key in HONEST_REMAINDER_REFUSE_IDS}:
        raise IntegrityError("honest remainder refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_REMAINDER_HREFS[key] for key in HONEST_REMAINDER_REFUSE_IDS}:
        raise IntegrityError("honest remainder refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest remainder refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest remainder" not in note:
        raise IntegrityError("honest remainder note keeps honest remainder", reason_code="CATALOG_REVIEW")
    if "a remainder close is not launch" not in note:
        raise IntegrityError("honest remainder note keeps a remainder close is not launch", reason_code="CATALOG_REVIEW")
    if "leftover copy is not live_pin_ok" not in note:
        raise IntegrityError("honest remainder note keeps leftover copy is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "a remainder close is not launch" not in lede:
        raise IntegrityError("honest remainder lede keeps a remainder close is not launch", reason_code="CATALOG_REVIEW")
    if "gold 99.5 is not production" not in lede:
        raise IntegrityError("honest remainder lede keeps gold 99.5 is not production", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest remainder" not in site:
        raise IntegrityError("honest remainder site keeps honest remainder", reason_code="CATALOG_REVIEW")
    if "not a /remainder route" not in site:
        raise IntegrityError("honest remainder site keeps not a /remainder route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest remainder site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest remainder is not a complement", reason_code="CATALOG_REVIEW")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("remainder playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat a remainder close as launch", reason_code="CATALOG_REVIEW")


def run_remainder_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded remainder. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_remainder(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest remainder", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "remainder_is_launch": False,
        "leftover_copy_is_live_pin": False,
        "owner_hrefs_are_clicks": False,
        "gold_995_is_production": False,
        "deep_remainder_is_seated": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_remainder"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_remainder_certification()
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
        "remainder_is_launch": False,
        "leftover_copy_is_live_pin": False,
        "owner_hrefs_are_clicks": False,
        "gold_995_is_production": False,
        "deep_remainder_is_seated": False,
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
        "href": "#missing",
        "facts": [dict(item) for item in body.get("facts") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat a remainder close as launch.",
            "Treat leftover copy as LIVE_PIN_OK.",
            "Treat owner hrefs as owner clicks.",
            "Treat gold 99.5 as production.",
            "Treat a deep remainder as seated.",
        ],
    }
