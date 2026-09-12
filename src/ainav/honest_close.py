"""Honest close. Recorded. A 10/10 close is not launch.

A booking is not recognized revenue. The Institute twin is not the assigned client sandbox.
A custom database is not a fourth SKU. A catalog list is not collection.
Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_CLOSE_FACT_IDS,
    HONEST_CLOSE_HOP_HREFS,
    HONEST_CLOSE_HOP_IDS,
    HONEST_CLOSE_HREFS,
    HONEST_CLOSE_REFUSE_IDS,
    HONEST_CLOSE_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.close.v1"
COMPLEMENT_COUNT = 8


def validate_honest_close(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_close")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest close", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest close kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "close_as_launch",
        "booking_as_revenue",
        "twin_as_assigned",
        "custom_db_as_sku",
        "list_as_collection",
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
        "signed_l1",
        "named_client",
        "billing_provider",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest close cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest close stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest close stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest close stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#path":
        raise IntegrityError("honest close sits on #path", reason_code="CATALOG_REVIEW")
    if body.get("close_as_launch") is not False:
        raise IntegrityError("a 10/10 close is not launch", reason_code="CATALOG_REVIEW")
    if body.get("booking_as_revenue") is not False:
        raise IntegrityError("a booking is not recognized revenue", reason_code="CATALOG_REVIEW")
    if body.get("twin_as_assigned") is not False:
        raise IntegrityError("the Institute twin is not the assigned client sandbox", reason_code="CATALOG_REVIEW")
    if body.get("custom_db_as_sku") is not False:
        raise IntegrityError("a custom database is not a fourth SKU", reason_code="CATALOG_REVIEW")
    if body.get("list_as_collection") is not False:
        raise IntegrityError("a catalog list is not collection", reason_code="CATALOG_REVIEW")
    hops = body.get("hops") or []
    if not isinstance(hops, list) or [item.get("id") for item in hops if isinstance(item, dict)] != list(
        HONEST_CLOSE_HOP_IDS
    ):
        raise IntegrityError("honest close hops stay catalog law", reason_code="CATALOG_REVIEW")
    hop_hrefs = {item.get("id"): item.get("href") for item in hops if isinstance(item, dict)}
    if hop_hrefs != {key: HONEST_CLOSE_HOP_HREFS[key] for key in HONEST_CLOSE_HOP_IDS}:
        raise IntegrityError("honest close hop hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("closed") is True or item.get("live") is True for item in hops if isinstance(item, dict)):
        raise IntegrityError("honest close hops are not closed or live", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_CLOSE_FACT_IDS):
        raise IntegrityError("honest close stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest close facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_CLOSE_FACT_IDS):
        raise IntegrityError("honest close facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest close facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_CLOSE_REFUSE_IDS):
        raise IntegrityError("honest close refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_CLOSE_REFUSE_TEXT[key] for key in HONEST_CLOSE_REFUSE_IDS}:
        raise IntegrityError("honest close refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_CLOSE_HREFS[key] for key in HONEST_CLOSE_REFUSE_IDS}:
        raise IntegrityError("honest close refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest close refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest close" not in note:
        raise IntegrityError("honest close note keeps honest close", reason_code="CATALOG_REVIEW")
    if "a 10/10 close is not launch" not in note:
        raise IntegrityError("honest close note keeps a 10/10 close is not launch", reason_code="CATALOG_REVIEW")
    if "a catalog list is not collection" not in note:
        raise IntegrityError("honest close note keeps a catalog list is not collection", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "a 10/10 close is not launch" not in lede:
        raise IntegrityError("honest close lede keeps a 10/10 close is not launch", reason_code="CATALOG_REVIEW")
    if "a custom database is not a fourth sku" not in lede:
        raise IntegrityError("honest close lede keeps a custom database is not a fourth SKU", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest close" not in site:
        raise IntegrityError("honest close site keeps honest close", reason_code="CATALOG_REVIEW")
    if "not a /close route" not in site:
        raise IntegrityError("honest close site keeps not a /close route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest close site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest close is not a complement", reason_code="CATALOG_REVIEW")
    owner = (catalog.get("plane_interface") or {}).get("gaps") or {}
    open_items = " ".join(str(item) for item in owner.get("owner_only_open") or [])
    for stem in ("seat B click", "G12/G13", "billing", "launch"):
        if stem not in open_items:
            raise IntegrityError("honest close cannot close " + stem, reason_code="GAP_OPEN")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("close playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat a 10/10 close as launch", reason_code="CATALOG_REVIEW")


def run_close_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded honest close. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_close(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest close", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "close_as_launch": False,
        "booking_as_revenue": False,
        "twin_as_assigned": False,
        "custom_db_as_sku": False,
        "list_as_collection": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_close"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_close_certification()
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
        "close_as_launch": False,
        "booking_as_revenue": False,
        "twin_as_assigned": False,
        "custom_db_as_sku": False,
        "list_as_collection": False,
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
        "hops": [dict(item) for item in body.get("hops") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat a 10/10 close as launch.",
            "Treat a booking as recognized revenue.",
            "Treat the Institute twin as the assigned client sandbox.",
            "Treat a custom database as a fourth SKU.",
            "Treat a catalog list as collection.",
        ],
    }
