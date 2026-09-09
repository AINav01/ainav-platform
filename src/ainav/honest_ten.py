"""Honest ten. Recorded. A 10/10 quality check is not launch.

Gold 99.9 is not LIVE_PIN_OK. A competitor analysis is not a named client.
A green service is not production. A quality check is not a seated second human.
Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_TEN_FACT_IDS,
    HONEST_TEN_HREFS,
    HONEST_TEN_REFUSE_IDS,
    HONEST_TEN_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.ten.v1"
COMPLEMENT_COUNT = 8


def validate_honest_ten(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_ten")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest ten", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest ten kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "quality_ten_is_launch",
        "gold_999_is_live_pin",
        "compete_is_named_client",
        "service_green_is_production",
        "quality_is_seated",
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
                "honest ten cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest ten stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest ten stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest ten stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#success":
        raise IntegrityError("honest ten sits on #success", reason_code="CATALOG_REVIEW")
    if body.get("quality_ten_is_launch") is not False:
        raise IntegrityError("a 10/10 quality check is not launch", reason_code="CATALOG_REVIEW")
    if body.get("gold_999_is_live_pin") is not False:
        raise IntegrityError("gold 99.9 is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    if body.get("compete_is_named_client") is not False:
        raise IntegrityError("a competitor analysis is not a named client", reason_code="CATALOG_REVIEW")
    if body.get("service_green_is_production") is not False:
        raise IntegrityError("a green service is not production", reason_code="CATALOG_REVIEW")
    if body.get("quality_is_seated") is not False:
        raise IntegrityError("a quality check is not a seated second human", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_TEN_FACT_IDS):
        raise IntegrityError("honest ten stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest ten facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_TEN_FACT_IDS):
        raise IntegrityError("honest ten facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest ten facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_TEN_REFUSE_IDS):
        raise IntegrityError("honest ten refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_TEN_REFUSE_TEXT[key] for key in HONEST_TEN_REFUSE_IDS}:
        raise IntegrityError("honest ten refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_TEN_HREFS[key] for key in HONEST_TEN_REFUSE_IDS}:
        raise IntegrityError("honest ten refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest ten refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest ten" not in note:
        raise IntegrityError("honest ten note keeps honest ten", reason_code="CATALOG_REVIEW")
    if "a 10/10 quality check is not launch" not in note:
        raise IntegrityError("honest ten note keeps a 10/10 quality check is not launch", reason_code="CATALOG_REVIEW")
    if "gold 99.9 is not live_pin_ok" not in note:
        raise IntegrityError("honest ten note keeps gold 99.9 is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "a 10/10 quality check is not launch" not in lede:
        raise IntegrityError("honest ten lede keeps a 10/10 quality check is not launch", reason_code="CATALOG_REVIEW")
    if "gold 99.9 is not live_pin_ok" not in lede:
        raise IntegrityError("honest ten lede keeps gold 99.9 is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest ten" not in site:
        raise IntegrityError("honest ten site keeps honest ten", reason_code="CATALOG_REVIEW")
    if "not a /ten route" not in site:
        raise IntegrityError("honest ten site keeps not a /ten route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest ten site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest ten is not a complement", reason_code="CATALOG_REVIEW")
    rows = (((catalog.get("plane_interface") or {}).get("competitive") or {}).get("rows") or [])
    row_ids = [item.get("id") for item in rows if isinstance(item, dict)]
    for needed in ("teams_vote", "entra_mfa", "cursor_agent", "cloudflare_edge"):
        if needed not in row_ids:
            raise IntegrityError("honest ten competitive board must include " + needed, reason_code="CATALOG_REVIEW")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("ten playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot treat a 10/10 quality check as launch", reason_code="CATALOG_REVIEW")
    services = body.get("services") if isinstance(body.get("services"), dict) else {}
    if services.get("claimed_as_production") is True:
        raise IntegrityError("honest ten services cannot claim production", reason_code="CATALOG_REVIEW")
    cloudflare = services.get("cloudflare") if isinstance(services.get("cloudflare"), dict) else {}
    if cloudflare.get("ssl_full_claimed") is True:
        raise IntegrityError("honest ten cannot claim SSL Full", reason_code="CATALOG_REVIEW")
    github = services.get("github") if isinstance(services.get("github"), dict) else {}
    if github.get("green_check_is_not_live_pin_ok") is not True:
        raise IntegrityError("honest ten GitHub green check is not LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    cursor = services.get("cursor") if isinstance(services.get("cursor"), dict) else {}
    if cursor.get("cloud_agent_is_not_a_seat") is not True:
        raise IntegrityError("honest ten Cursor Cloud Agent is not a seat", reason_code="CATALOG_REVIEW")


def run_ten_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded honest ten. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_ten(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest ten", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "quality_ten_is_launch": False,
        "gold_999_is_live_pin": False,
        "compete_is_named_client": False,
        "service_green_is_production": False,
        "quality_is_seated": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_ten"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_ten_certification()
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
        "quality_ten_is_launch": False,
        "gold_999_is_live_pin": False,
        "compete_is_named_client": False,
        "service_green_is_production": False,
        "quality_is_seated": False,
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
        "href": "#success",
        "facts": [dict(item) for item in body.get("facts") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "services": dict(body.get("services") or {}),
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat a 10/10 quality check as launch.",
            "Treat gold 99.9 as LIVE_PIN_OK.",
            "Treat a competitor analysis as a named client.",
            "Treat a green service as production.",
            "Treat a quality check as a seated second human.",
        ],
    }
