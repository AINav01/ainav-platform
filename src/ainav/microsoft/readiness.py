"""Honest readiness. Twin certified is not launch day.

Quality, operability, simulation, deliverability, updateability, and
debugging run in-tree. Gold is not launch. Launch stays owner-only.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_READY_HREFS,
    HONEST_READY_IDS,
    HONEST_READY_REFUSE_IDS,
    HONEST_READY_REFUSE_TEXT,
    HONEST_READY_ROLES,
    load_catalog,
)

KIND = "ainav.honest.readiness.v1"


def validate_honest_readiness(catalog: dict[str, Any]) -> None:
    stack = catalog.get("microsoft_stack") or {}
    if not isinstance(stack, dict):
        raise IntegrityError("catalog missing microsoft stack", reason_code="MICROSOFT_PRODUCT")
    body = stack.get("readiness")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest readiness review", reason_code="MICROSOFT_PRODUCT")
    if body.get("kind") != KIND:
        raise IntegrityError("honest readiness kind stays catalog law", reason_code="MICROSOFT_PRODUCT")
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
        "gold_is_launch",
        "twin_is_launch_day",
        "sim_is_production",
        "update_is_live_pin",
        "owner_gaps_closed",
        "launch_day_certified",
        "certified",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest readiness cannot claim " + flag.replace("_", " "),
                reason_code="MICROSOFT_PRODUCT",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest readiness stays honest", reason_code="MICROSOFT_PRODUCT")
    if body.get("gold_is_launch") is not False:
        raise IntegrityError("gold is not launch", reason_code="MICROSOFT_PRODUCT")
    if body.get("twin_is_launch_day") is not False:
        raise IntegrityError("twin certified is not launch day", reason_code="MICROSOFT_PRODUCT")
    if body.get("launch_day_certified") is not False:
        raise IntegrityError("this plane cannot certify launch day", reason_code="MICROSOFT_PRODUCT")
    lanes = body.get("lanes") or []
    if not isinstance(lanes, list) or len(lanes) != 7:
        raise IntegrityError(
            "honest readiness stays quality, operability, simulation, deliverability, updateability, debugging, launch",
            reason_code="MICROSOFT_PRODUCT",
        )
    if any(not isinstance(item, dict) for item in lanes):
        raise IntegrityError("honest readiness lanes stay objects", reason_code="MICROSOFT_PRODUCT")
    if [item.get("id") for item in lanes] != list(HONEST_READY_IDS):
        raise IntegrityError(
            "honest readiness stays quality, operability, simulation, deliverability, updateability, debugging, launch",
            reason_code="MICROSOFT_PRODUCT",
        )
    if any(item.get("installed") is not None or item.get("seat") is True for item in lanes):
        raise IntegrityError("the lanes stay installed=null and not seats", reason_code="MICROSOFT_PRODUCT")
    roles = {item.get("id"): item.get("role") for item in lanes}
    if roles != dict(HONEST_READY_ROLES):
        raise IntegrityError("roles stay certified then owner_only", reason_code="MICROSOFT_PRODUCT")
    hrefs = {item.get("id"): item.get("href") for item in lanes}
    if hrefs != {key: HONEST_READY_HREFS[key] for key in HONEST_READY_IDS}:
        raise IntegrityError("honest readiness hrefs stay catalog law", reason_code="MICROSOFT_PRODUCT")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_READY_REFUSE_IDS):
        raise IntegrityError("honest readiness refuse ids stay catalog law", reason_code="MICROSOFT_PRODUCT")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_READY_REFUSE_TEXT[key] for key in HONEST_READY_REFUSE_IDS}:
        raise IntegrityError("honest readiness refuse text stays catalog law", reason_code="MICROSOFT_PRODUCT")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_READY_HREFS[key] for key in HONEST_READY_REFUSE_IDS}:
        raise IntegrityError("honest readiness refuse hrefs stay catalog law", reason_code="MICROSOFT_PRODUCT")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    if operating.get("operator") != "cursor.cloud_agent":
        raise IntegrityError("recorded operator stays cursor.cloud_agent", reason_code="MICROSOFT_PRODUCT")
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    owner = operating.get("owner_principal")
    if playbook.get("actor") != owner:
        raise IntegrityError("readiness playbook actor must be the sole owner", reason_code="MICROSOFT_PRODUCT")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot certify launch day", reason_code="MICROSOFT_PRODUCT")
    note = str(body.get("note") or "").lower()
    if "honest readiness" not in note:
        raise IntegrityError("honest readiness note keeps honest readiness", reason_code="MICROSOFT_PRODUCT")
    if "gold is not launch" not in note:
        raise IntegrityError("honest readiness note keeps gold is not launch", reason_code="MICROSOFT_PRODUCT")
    if "twin certified is not launch day" not in note:
        raise IntegrityError("honest readiness note keeps twin certified is not launch day", reason_code="MICROSOFT_PRODUCT")
    if "owner gaps stay owner-only" not in note:
        raise IntegrityError("honest readiness note keeps owner gaps stay owner-only", reason_code="MICROSOFT_PRODUCT")
    lede = str(body.get("lede") or "").lower()
    if "gold is not launch" not in lede:
        raise IntegrityError("honest readiness lede keeps gold is not launch", reason_code="MICROSOFT_PRODUCT")
    if "twin certified is not launch day" not in lede:
        raise IntegrityError("honest readiness lede keeps twin certified is not launch day", reason_code="MICROSOFT_PRODUCT")
    if "owner gaps stay owner-only" not in lede:
        raise IntegrityError("honest readiness lede keeps owner gaps stay owner-only", reason_code="MICROSOFT_PRODUCT")


def run_twin_certification(catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    """In-tree probes. No live HTTP. Never launch. Never LIVE_PIN_OK."""
    cat = catalog or load_catalog()
    validate_honest_readiness(cat)
    from ainav.delivery import validate_delivery
    from ainav.examiner import action_schema, prove
    from ainav.microsoft.build import validate_honest_build
    from ainav.microsoft.institute_publish import publish_institute
    from ainav.ops import EXITS, STAGES
    from agent_gov import lua_simulator

    validate_delivery(cat)
    validate_honest_build(cat)
    held = publish_institute()
    if held.get("ok") is not False or held.get("reason") != "launch_not_ready":
        raise IntegrityError("institute publish stays launch_not_ready", reason_code="MICROSOFT_PRODUCT")
    if "L1_SOLD" not in STAGES or "KIT_PASS" not in STAGES:
        raise IntegrityError("operability keeps the commercial stages", reason_code="MICROSOFT_PRODUCT")
    if "LOST" not in EXITS:
        raise IntegrityError("operability keeps honest exits", reason_code="MICROSOFT_PRODUCT")
    schema = action_schema()
    if not isinstance(schema, dict) or not schema:
        raise IntegrityError("debugging keeps the action schema", reason_code="MICROSOFT_PRODUCT")
    if not callable(prove):
        raise IntegrityError("debugging keeps examiner prove", reason_code="MICROSOFT_PRODUCT")
    if lua_simulator is None:
        raise IntegrityError("simulation keeps the lua simulator", reason_code="MICROSOFT_PRODUCT")
    return {
        "kind": KIND,
        "quality": True,
        "operability": True,
        "simulation": True,
        "deliverability": True,
        "updateability": True,
        "debugging": True,
        "launch": False,
        "gold_is_launch": False,
        "twin_is_launch_day": False,
        "sim_is_production": False,
        "update_is_live_pin": False,
        "owner_gaps_closed": False,
        "launch_day_certified": False,
        "live": False,
        "live_pin_ok": False,
        "institute_publish": held.get("reason"),
    }


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["microsoft_stack"]["readiness"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    probes = run_twin_certification()
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
        "gold_is_launch": False,
        "twin_is_launch_day": False,
        "sim_is_production": False,
        "update_is_live_pin": False,
        "owner_gaps_closed": False,
        "launch_day_certified": False,
        "certified": False,
        "honest": True,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "lanes": [dict(item) for item in body.get("lanes") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "probes": probes,
        "this_agent_cannot": [
            "Treat gold as launch.",
            "Treat twin certified as launch day.",
            "Treat simulation as production.",
            "Treat an update as LIVE_PIN_OK.",
            "Close owner gaps from this plane.",
        ],
    }
