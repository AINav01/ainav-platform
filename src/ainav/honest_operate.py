"""Honest operate. Recorded. Closing all gaps is not this plane.

Outlook mail is not a click. grok login is not this plane.
An operate sim is not production. A 10/10 polish is not launch.
Complements stay eight.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_OPERATE_FACT_IDS,
    HONEST_OPERATE_HREFS,
    HONEST_OPERATE_REFUSE_IDS,
    HONEST_OPERATE_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.operate.v1"
COMPLEMENT_COUNT = 8


def validate_honest_operate(catalog: dict[str, Any]) -> None:
    body = catalog.get("honest_operate")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest operate", reason_code="CATALOG_REVIEW")
    if body.get("kind") != KIND:
        raise IntegrityError("honest operate kind stays catalog law", reason_code="CATALOG_REVIEW")
    false_flags = (
        "sku",
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_complement",
        "is_admit_plane",
        "is_job_c",
        "is_seat",
        "close_gaps_is_this_plane",
        "outlook_is_click",
        "grok_login_is_this_plane",
        "operate_sim_is_production",
        "polish_ten_is_launch",
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
                "honest operate cannot claim " + flag.replace("_", " "),
                reason_code="CATALOG_REVIEW",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest operate stays honest", reason_code="CATALOG_REVIEW")
    if body.get("considered") is not True:
        raise IntegrityError("honest operate stays considered", reason_code="CATALOG_REVIEW")
    if body.get("recorded") is not True:
        raise IntegrityError("honest operate stays recorded", reason_code="CATALOG_REVIEW")
    if body.get("href") != "#agent-tools":
        raise IntegrityError("honest operate sits on #agent-tools", reason_code="CATALOG_REVIEW")
    if body.get("close_gaps_is_this_plane") is not False:
        raise IntegrityError("closing all gaps is not this plane", reason_code="CATALOG_REVIEW")
    if body.get("outlook_is_click") is not False:
        raise IntegrityError("outlook mail is not a click", reason_code="CATALOG_REVIEW")
    if body.get("grok_login_is_this_plane") is not False:
        raise IntegrityError("grok login is not this plane", reason_code="CATALOG_REVIEW")
    if body.get("operate_sim_is_production") is not False:
        raise IntegrityError("an operate sim is not production", reason_code="CATALOG_REVIEW")
    if body.get("polish_ten_is_launch") is not False:
        raise IntegrityError("a 10/10 polish is not launch", reason_code="CATALOG_REVIEW")
    facts = body.get("facts") or []
    if not isinstance(facts, list) or len(facts) != len(HONEST_OPERATE_FACT_IDS):
        raise IntegrityError("honest operate stays five facts", reason_code="CATALOG_REVIEW")
    if any(not isinstance(item, dict) for item in facts):
        raise IntegrityError("honest operate facts stay objects", reason_code="CATALOG_REVIEW")
    if [item.get("id") for item in facts] != list(HONEST_OPERATE_FACT_IDS):
        raise IntegrityError("honest operate facts stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("sku") is True or item.get("admit") is True or item.get("live") is True for item in facts):
        raise IntegrityError("honest operate facts are not SKUs or admit", reason_code="CATALOG_REVIEW")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_OPERATE_REFUSE_IDS):
        raise IntegrityError("honest operate refuse ids stay catalog law", reason_code="CATALOG_REVIEW")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_OPERATE_REFUSE_TEXT[key] for key in HONEST_OPERATE_REFUSE_IDS}:
        raise IntegrityError("honest operate refuse text stays catalog law", reason_code="CATALOG_REVIEW")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_OPERATE_HREFS[key] for key in HONEST_OPERATE_REFUSE_IDS}:
        raise IntegrityError("honest operate refuse hrefs stay catalog law", reason_code="CATALOG_REVIEW")
    if any(item.get("claimed") is False or item.get("live") is False for item in refuse):
        raise IntegrityError("honest operate refuse cannot leftover claimed or live", reason_code="CATALOG_REVIEW")
    note = str(body.get("note") or "").lower()
    if "honest operate" not in note:
        raise IntegrityError("honest operate note keeps honest operate", reason_code="CATALOG_REVIEW")
    if "closing all gaps is not this plane" not in note:
        raise IntegrityError("honest operate note keeps closing all gaps is not this plane", reason_code="CATALOG_REVIEW")
    if "outlook mail is not a click" not in note:
        raise IntegrityError("honest operate note keeps outlook mail is not a click", reason_code="CATALOG_REVIEW")
    lede = str(body.get("lede") or "").lower()
    if "outlook mail is not a click" not in lede:
        raise IntegrityError("honest operate lede keeps outlook mail is not a click", reason_code="CATALOG_REVIEW")
    if "closing all gaps is not this plane" not in lede:
        raise IntegrityError("honest operate lede keeps closing all gaps is not this plane", reason_code="CATALOG_REVIEW")
    site = str(body.get("site") or "").lower()
    if "honest operate" not in site:
        raise IntegrityError("honest operate site keeps honest operate", reason_code="CATALOG_REVIEW")
    if "not a /operate route" not in site:
        raise IntegrityError("honest operate site keeps not a /operate route", reason_code="CATALOG_REVIEW")
    if "first glance stays the write rail" not in site:
        raise IntegrityError("honest operate site keeps first glance stays the write rail", reason_code="CATALOG_REVIEW")
    complements = (catalog.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight. Honest operate is not a complement", reason_code="CATALOG_REVIEW")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    if playbook.get("actor") != operating.get("owner_principal"):
        raise IntegrityError("operate playbook actor must be the sole owner", reason_code="CATALOG_REVIEW")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot close all gaps", reason_code="CATALOG_REVIEW")


def run_operate_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree recorded probe. No live HTTP. Never live. Never launch."""
    cat = catalog or load_catalog()
    validate_honest_operate(cat)
    from ainav.microsoft.institute_publish import publish_institute

    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="CATALOG_REVIEW")
    complements = (cat.get("connections") or {}).get("complements") or []
    if len(complements) != COMPLEMENT_COUNT:
        raise IntegrityError("complements stay eight after honest operate", reason_code="CATALOG_REVIEW")
    return {
        "kind": KIND,
        "considered": True,
        "recorded": True,
        "close_gaps_is_this_plane": False,
        "outlook_is_click": False,
        "grok_login_is_this_plane": False,
        "operate_sim_is_production": False,
        "polish_ten_is_launch": False,
        "complements": COMPLEMENT_COUNT,
        "created": False,
        "certified": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["honest_operate"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_operate_certification()
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
        "close_gaps_is_this_plane": False,
        "outlook_is_click": False,
        "grok_login_is_this_plane": False,
        "operate_sim_is_production": False,
        "polish_ten_is_launch": False,
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
        "href": "#agent-tools",
        "facts": [dict(item) for item in body.get("facts") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat closing all gaps as this plane.",
            "Treat Outlook mail as a click.",
            "Treat grok login as this plane.",
            "Treat an operate sim as production.",
            "Treat a 10/10 polish as launch.",
        ],
    }
