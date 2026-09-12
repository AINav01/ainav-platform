"""Honest access. This plane does not need more secrets to stay honest.

Grok Build and Grok bot are operator maps. Not seats. Not AINav.
This Cloud Agent does not need Microsoft admin, grok login, or XAI_API_KEY.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_ACCESS_HAVE_IDS,
    HONEST_ACCESS_HREFS,
    HONEST_ACCESS_LANE_IDS,
    HONEST_ACCESS_NEED_NOT_IDS,
    HONEST_ACCESS_OPERATOR_IDS,
    HONEST_ACCESS_OWNER_IDS,
    HONEST_ACCESS_REFUSE_IDS,
    HONEST_ACCESS_REFUSE_TEXT,
    load_catalog,
)

KIND = "ainav.honest.access.v1"


def validate_honest_access(catalog: dict[str, Any]) -> None:
    stack = catalog.get("microsoft_stack") or {}
    if not isinstance(stack, dict):
        raise IntegrityError("catalog missing microsoft stack", reason_code="MICROSOFT_PRODUCT")
    body = stack.get("access")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest access review", reason_code="MICROSOFT_PRODUCT")
    if body.get("kind") != KIND:
        raise IntegrityError("honest access kind stays catalog law", reason_code="MICROSOFT_PRODUCT")
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
        "need_more",
        "grok_is_product",
        "grok_is_seat",
        "grok_wired",
        "additional_access_needed",
        "census",
        "agent_365_is_product",
        "cloud_agent_can_approve",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest access cannot claim " + flag.replace("_", " "),
                reason_code="MICROSOFT_PRODUCT",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest access stays honest", reason_code="MICROSOFT_PRODUCT")
    if body.get("need_more") is not False or body.get("additional_access_needed") is not False:
        raise IntegrityError("this plane does not need additional access", reason_code="MICROSOFT_PRODUCT")
    if body.get("grok_installed") is not None:
        raise IntegrityError("Grok Build stays installed=null", reason_code="MICROSOFT_PRODUCT")
    operators = body.get("operators") or []
    if [item.get("id") for item in operators] != list(HONEST_ACCESS_OPERATOR_IDS):
        raise IntegrityError("honest access operators stay catalog law", reason_code="MICROSOFT_PRODUCT")
    if any(item.get("installed") is not None or item.get("seat") is True for item in operators):
        raise IntegrityError("operators stay installed=null and not seats", reason_code="MICROSOFT_PRODUCT")
    cursor = next((item for item in operators if item.get("id") == "cursor"), {})
    if cursor.get("recorded") is not True:
        raise IntegrityError("Cursor Cloud Agent stays the recorded operator", reason_code="MICROSOFT_PRODUCT")
    if any(item.get("id") != "cursor" and item.get("recorded") is True for item in operators):
        raise IntegrityError("Grok and other operators stay mapped, not recorded", reason_code="MICROSOFT_PRODUCT")
    lanes = body.get("lanes") or []
    if [item.get("id") for item in lanes] != list(HONEST_ACCESS_LANE_IDS):
        raise IntegrityError("honest access lanes stay have/need_not/owner_only/operators/refuse", reason_code="MICROSOFT_PRODUCT")
    expected = {
        "have": list(HONEST_ACCESS_HAVE_IDS),
        "need_not": list(HONEST_ACCESS_NEED_NOT_IDS),
        "owner_only": list(HONEST_ACCESS_OWNER_IDS),
        "operators": list(HONEST_ACCESS_OPERATOR_IDS),
        "refuse": list(HONEST_ACCESS_REFUSE_IDS),
    }
    hrefs = {}
    refuse_items = []
    for lane in lanes:
        lane_id = lane.get("id")
        row_ids = [row.get("id") for row in lane.get("items") or []]
        if row_ids != expected.get(lane_id):
            raise IntegrityError("honest access lane items stay catalog law", reason_code="MICROSOFT_PRODUCT")
        for row in lane.get("items") or []:
            hrefs[row.get("id")] = row.get("href")
            if row.get("refuse") is True:
                refuse_items.append(row)
    if hrefs != HONEST_ACCESS_HREFS:
        raise IntegrityError("honest access hrefs stay catalog law", reason_code="MICROSOFT_PRODUCT")
    if [item.get("id") for item in refuse_items] != list(HONEST_ACCESS_REFUSE_IDS):
        raise IntegrityError("honest access refuse ids stay catalog law", reason_code="MICROSOFT_PRODUCT")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse_items}
    if texts != {key: HONEST_ACCESS_REFUSE_TEXT[key] for key in HONEST_ACCESS_REFUSE_IDS}:
        raise IntegrityError("honest access refuse text stays catalog law", reason_code="MICROSOFT_PRODUCT")
    playbook = body.get("owner_playbook") or {}
    owner = (catalog.get("operating") or {}).get("owner_principal")
    if playbook.get("actor") != owner:
        raise IntegrityError("access playbook actor must be the sole owner", reason_code="MICROSOFT_PRODUCT")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot run the access playbook", reason_code="MICROSOFT_PRODUCT")
    note = str(body.get("note") or "").lower()
    if "honest access" not in note or "does not need" not in note:
        raise IntegrityError("honest access note keeps does not need", reason_code="MICROSOFT_PRODUCT")
    if "grok build" not in note or "not a seat" not in note:
        raise IntegrityError("honest access note keeps Grok Build is not a seat", reason_code="MICROSOFT_PRODUCT")
    lede = str(body.get("lede") or "").lower()
    if "does not need additional access" not in lede:
        raise IntegrityError("honest access lede keeps does not need additional access", reason_code="MICROSOFT_PRODUCT")
    if "grok build is not a seat" not in lede:
        raise IntegrityError("honest access lede keeps Grok Build is not a seat", reason_code="MICROSOFT_PRODUCT")


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["microsoft_stack"]["access"])


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
        "need_more": False,
        "additional_access_needed": False,
        "grok_is_product": False,
        "grok_is_seat": False,
        "grok_wired": False,
        "grok_installed": None,
        "honest": True,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "have": [dict(item) for item in body.get("have") or []],
        "need_not": [dict(item) for item in body.get("need_not") or []],
        "operators": [dict(item) for item in body.get("operators") or []],
        "lanes": [dict(item) for item in body.get("lanes") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "this_agent_cannot": [
            "Sign in to admin.cloud.microsoft as the owner.",
            "Request grok login or XAI_API_KEY as additional access.",
            "Treat Grok Build as a seat.",
            "Treat a Grok bot as dual admit.",
            "Treat more access as admit.",
        ],
    }
