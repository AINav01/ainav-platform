"""Honest operators. Cursor recorded. Grok Build mapped. Grok bot not admit.

These three are not interchangeable. Owner cannot be the operator.
This plane does not swap Cursor for Grok.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_OPERATOR_HREFS,
    HONEST_OPERATOR_IDS,
    HONEST_OPERATOR_REFUSE_IDS,
    HONEST_OPERATOR_REFUSE_TEXT,
    HONEST_OPERATOR_ROLES,
    load_catalog,
)

KIND = "ainav.honest.operators.v1"


def validate_honest_operators(catalog: dict[str, Any]) -> None:
    stack = catalog.get("microsoft_stack") or {}
    if not isinstance(stack, dict):
        raise IntegrityError("catalog missing microsoft stack", reason_code="MICROSOFT_PRODUCT")
    body = stack.get("operators")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest operators review", reason_code="MICROSOFT_PRODUCT")
    if body.get("kind") != KIND:
        raise IntegrityError("honest operators kind stays catalog law", reason_code="MICROSOFT_PRODUCT")
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
        "swap",
        "grok_is_recorded",
        "bot_is_operator",
        "bot_is_admit",
        "owner_is_operator",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest operators cannot claim " + flag.replace("_", " "),
                reason_code="MICROSOFT_PRODUCT",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest operators stay honest", reason_code="MICROSOFT_PRODUCT")
    if body.get("swap") is not False or body.get("grok_is_recorded") is not False:
        raise IntegrityError("Cursor stays recorded. Grok Build stays mapped", reason_code="MICROSOFT_PRODUCT")
    three = body.get("three") or []
    if not isinstance(three, list) or len(three) != 3:
        raise IntegrityError("honest operators stay Cursor, Grok Build, Grok bot", reason_code="MICROSOFT_PRODUCT")
    if any(not isinstance(item, dict) for item in three):
        raise IntegrityError("honest operator cards stay objects", reason_code="MICROSOFT_PRODUCT")
    if [item.get("id") for item in three] != list(HONEST_OPERATOR_IDS):
        raise IntegrityError("honest operators stay Cursor, Grok Build, Grok bot", reason_code="MICROSOFT_PRODUCT")
    if any(item.get("installed") is not None or item.get("seat") is True for item in three):
        raise IntegrityError("the three stay installed=null and not seats", reason_code="MICROSOFT_PRODUCT")
    roles = {item.get("id"): item.get("role") for item in three}
    if roles != dict(HONEST_OPERATOR_ROLES):
        raise IntegrityError("roles stay recorded, mapped, not_admit", reason_code="MICROSOFT_PRODUCT")
    cursor = next((item for item in three if item.get("id") == "cursor"), {})
    grok_bot = next((item for item in three if item.get("id") == "grok_bot"), {})
    if cursor.get("recorded") is not True:
        raise IntegrityError("Cursor Cloud Agent stays the recorded operator", reason_code="MICROSOFT_PRODUCT")
    if any(item.get("id") != "cursor" and item.get("recorded") is True for item in three):
        raise IntegrityError("Grok Build and Grok bot stay mapped, not recorded", reason_code="MICROSOFT_PRODUCT")
    if grok_bot.get("operator") is True:
        raise IntegrityError("Grok bot is not the operator", reason_code="MICROSOFT_PRODUCT")
    if grok_bot.get("admit") is True or grok_bot.get("job_c") is True:
        raise IntegrityError("Grok bot is not dual admit and not Job C", reason_code="MICROSOFT_PRODUCT")
    hrefs = {item.get("id"): item.get("href") for item in three}
    if hrefs != {key: HONEST_OPERATOR_HREFS[key] for key in HONEST_OPERATOR_IDS}:
        raise IntegrityError("honest operator hrefs stay catalog law", reason_code="MICROSOFT_PRODUCT")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_OPERATOR_REFUSE_IDS):
        raise IntegrityError("honest operator refuse ids stay catalog law", reason_code="MICROSOFT_PRODUCT")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_OPERATOR_REFUSE_TEXT[key] for key in HONEST_OPERATOR_REFUSE_IDS}:
        raise IntegrityError("honest operator refuse text stays catalog law", reason_code="MICROSOFT_PRODUCT")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_OPERATOR_HREFS[key] for key in HONEST_OPERATOR_REFUSE_IDS}:
        raise IntegrityError("honest operator refuse hrefs stay catalog law", reason_code="MICROSOFT_PRODUCT")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    if operating.get("operator") != "cursor.cloud_agent":
        raise IntegrityError("recorded operator stays cursor.cloud_agent", reason_code="MICROSOFT_PRODUCT")
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    owner = operating.get("owner_principal")
    if playbook.get("actor") != owner:
        raise IntegrityError("operators playbook actor must be the sole owner", reason_code="MICROSOFT_PRODUCT")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot swap the recorded operator", reason_code="MICROSOFT_PRODUCT")
    note = str(body.get("note") or "").lower()
    if "honest operators" not in note:
        raise IntegrityError("honest operators note keeps honest operators", reason_code="MICROSOFT_PRODUCT")
    if "cursor is recorded" not in note:
        raise IntegrityError("honest operators note keeps Cursor is recorded", reason_code="MICROSOFT_PRODUCT")
    if "grok build is mapped" not in note:
        raise IntegrityError("honest operators note keeps Grok Build is mapped", reason_code="MICROSOFT_PRODUCT")
    if "grok bot is not admit" not in note:
        raise IntegrityError("honest operators note keeps Grok bot is not admit", reason_code="MICROSOFT_PRODUCT")
    lede = str(body.get("lede") or "").lower()
    if "cursor is recorded" not in lede:
        raise IntegrityError("honest operators lede keeps Cursor is recorded", reason_code="MICROSOFT_PRODUCT")
    if "grok build is mapped" not in lede:
        raise IntegrityError("honest operators lede keeps Grok Build is mapped", reason_code="MICROSOFT_PRODUCT")
    if "grok bot is not admit" not in lede:
        raise IntegrityError("honest operators lede keeps Grok bot is not admit", reason_code="MICROSOFT_PRODUCT")


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["microsoft_stack"]["operators"])


def public_review() -> dict[str, Any]:
    body = doctrine()
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
        "swap": False,
        "grok_is_recorded": False,
        "bot_is_operator": False,
        "bot_is_admit": False,
        "honest": True,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "three": [dict(item) for item in body.get("three") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "this_agent_cannot": [
            "Swap Cursor for Grok Build as the recorded operator.",
            "Treat Grok Build as this recorded operator.",
            "Treat a Grok bot as the operator or as dual admit.",
            "Make James the operator.",
        ],
    }
