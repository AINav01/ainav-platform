"""Honest connect. Recorded. Connected is not live.

Licensed is not wired. Available is not a seat.
A Graph read is not LIVE_PIN_OK. A Cursor app is not a seat.
Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_CONNECT_FACT_IDS,
    HONEST_CONNECT_HREFS,
    HONEST_CONNECT_REFUSE_IDS,
    HONEST_CONNECT_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.connect.v1"
COMPLEMENT_COUNT = 8


def validate_honest_connect(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_connect")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest connect", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest connect kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "connected_is_live",
        "licensed_is_wired",
        "available_is_seat",
        "graph_read_is_live_pin",
        "cursor_app_is_seat",
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
                "honest connect cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest connect stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest connect stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest connect stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#missing":
        raise IntegrityError("honest connect sits on #missing", reason_code="CATALOG_REVIEW")
    if body.get("connected_is_live") is not False:
        raise IntegrityError("connected is not live", reason_code="CATALOG_REVIEW")
    if body.get("licensed_is_wired") is not False:
        raise IntegrityError("licensed is not wired", reason_code="CATALOG_REVIEW")
    if body.get("available_is_seat") is not False:
        raise IntegrityError("available is not a seat", reason_code="CATALOG_REVIEW")
    if body.get("graph_read_is_live_pin") is not False:
        raise IntegrityError("a Graph read is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    if body.get("cursor_app_is_seat") is not False:
        raise IntegrityError("a Cursor app is not a seat", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_CONNECT_FACT_IDS):
        raise IntegrityError("honest connect stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest connect facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_CONNECT_FACT_IDS):
        raise IntegrityError("honest connect facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest connect facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_CONNECT_REFUSE_IDS):
        raise IntegrityError("honest connect refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_CONNECT_REFUSE_TEXT[key] for key in HONEST_CONNECT_REFUSE_IDS}:
        raise IntegrityError("honest connect refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_CONNECT_HREFS[key] for key in HONEST_CONNECT_REFUSE_IDS}:
        raise IntegrityError("honest connect refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest connect refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest connect" not in note:
        raise IntegrityError("honest connect note keeps honest connect", reason_code="CATALOG_REVIEW")
    if "connected is not live" not in note:
        raise IntegrityError("honest connect note keeps connected is not live", reason_code="CATALOG_REVIEW")
    if "licensed is not wired" not in note:
        raise IntegrityError("honest connect note keeps licensed is not wired", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "licensed is not wired" not in lede:
        raise IntegrityError("honest connect lede keeps licensed is not wired", reason_code="CATALOG_REVIEW")
    if "connected is not authorized" not in lede and "connected is not live" not in lede:
        raise IntegrityError("honest connect lede keeps connected is not live", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest connect" not in site:
        raise IntegrityError("honest connect site keeps honest connect", reason_code="CATALOG_REVIEW")
    if "not a /connect route" not in site:
        raise IntegrityError("honest connect site keeps not a /connect route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest connect site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest connect is not a complement", reason_code="CATALOG_REVIEW")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("connect playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat connected as live", reason_code="CATALOG_REVIEW")


def run_connect_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded probe. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_connect(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest connect", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "connected_is_live": False,
        "licensed_is_wired": False,
        "available_is_seat": False,
        "graph_read_is_live_pin": False,
        "cursor_app_is_seat": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_connect"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_connect_certification()
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
        "connected_is_live": False,
        "licensed_is_wired": False,
        "available_is_seat": False,
        "graph_read_is_live_pin": False,
        "cursor_app_is_seat": False,
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
            "Treat connected as live.",
            "Treat licensed as wired.",
            "Treat available as a seat.",
            "Treat a Graph read as LIVE_PIN_OK.",
            "Treat a Cursor app as a seat.",
        ],
    }
