"""Honest build. Do not give full access.

The twin is enough to build L1, P-ADM, U-DUAL, modules, packs, and repositories.
Launch stays owner-only. More secrets are not how we build.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    HONEST_BUILD_HREFS,
    HONEST_BUILD_IDS,
    HONEST_BUILD_REFUSE_IDS,
    HONEST_BUILD_REFUSE_TEXT,
    HONEST_BUILD_ROLES,
    load_catalog,
)

KIND = "ainav.honest.build.v1"


def validate_honest_build(catalog: dict[str, Any]) -> None:
    stack = catalog.get("microsoft_stack") or {}
    if not isinstance(stack, dict):
        raise IntegrityError("catalog missing microsoft stack", reason_code="MICROSOFT_PRODUCT")
    body = stack.get("build")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing honest build review", reason_code="MICROSOFT_PRODUCT")
    if body.get("kind") != KIND:
        raise IntegrityError("honest build kind stays catalog law", reason_code="MICROSOFT_PRODUCT")
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
        "need_full",
        "full_access_needed",
        "more_secrets_needed",
        "twin_is_launch",
        "packs_are_skus",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "honest build cannot claim " + flag.replace("_", " "),
                reason_code="MICROSOFT_PRODUCT",
            )
    if body.get("honest") is not True:
        raise IntegrityError("honest build stays honest", reason_code="MICROSOFT_PRODUCT")
    if body.get("need_full") is not False or body.get("full_access_needed") is not False:
        raise IntegrityError("this plane does not need full access", reason_code="MICROSOFT_PRODUCT")
    if body.get("twin_is_launch") is not False:
        raise IntegrityError("the twin is not launch", reason_code="MICROSOFT_PRODUCT")
    three = body.get("three") or []
    if not isinstance(three, list) or len(three) != 3:
        raise IntegrityError("honest build stays enough, build, launch", reason_code="MICROSOFT_PRODUCT")
    if any(not isinstance(item, dict) for item in three):
        raise IntegrityError("honest build cards stay objects", reason_code="MICROSOFT_PRODUCT")
    if [item.get("id") for item in three] != list(HONEST_BUILD_IDS):
        raise IntegrityError("honest build stays enough, build, launch", reason_code="MICROSOFT_PRODUCT")
    if any(item.get("installed") is not None or item.get("seat") is True for item in three):
        raise IntegrityError("the three stay installed=null and not seats", reason_code="MICROSOFT_PRODUCT")
    roles = {item.get("id"): item.get("role") for item in three}
    if roles != dict(HONEST_BUILD_ROLES):
        raise IntegrityError("roles stay have, catalog, owner_only", reason_code="MICROSOFT_PRODUCT")
    hrefs = {item.get("id"): item.get("href") for item in three}
    if hrefs != {key: HONEST_BUILD_HREFS[key] for key in HONEST_BUILD_IDS}:
        raise IntegrityError("honest build hrefs stay catalog law", reason_code="MICROSOFT_PRODUCT")
    refuse = [item for item in (body.get("refuse") or []) if isinstance(item, dict) and item.get("refuse") is True]
    if [item.get("id") for item in refuse] != list(HONEST_BUILD_REFUSE_IDS):
        raise IntegrityError("honest build refuse ids stay catalog law", reason_code="MICROSOFT_PRODUCT")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse}
    if texts != {key: HONEST_BUILD_REFUSE_TEXT[key] for key in HONEST_BUILD_REFUSE_IDS}:
        raise IntegrityError("honest build refuse text stays catalog law", reason_code="MICROSOFT_PRODUCT")
    refuse_hrefs = {item.get("id"): item.get("href") for item in refuse}
    if refuse_hrefs != {key: HONEST_BUILD_HREFS[key] for key in HONEST_BUILD_REFUSE_IDS}:
        raise IntegrityError("honest build refuse hrefs stay catalog law", reason_code="MICROSOFT_PRODUCT")
    operating = catalog.get("operating") if isinstance(catalog.get("operating"), dict) else {}
    if operating.get("operator") != "cursor.cloud_agent":
        raise IntegrityError("recorded operator stays cursor.cloud_agent", reason_code="MICROSOFT_PRODUCT")
    playbook = body.get("owner_playbook") if isinstance(body.get("owner_playbook"), dict) else {}
    owner = operating.get("owner_principal")
    if playbook.get("actor") != owner:
        raise IntegrityError("build playbook actor must be the sole owner", reason_code="MICROSOFT_PRODUCT")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot take full access or mark launch", reason_code="MICROSOFT_PRODUCT")
    note = str(body.get("note") or "").lower()
    if "honest build" not in note:
        raise IntegrityError("honest build note keeps honest build", reason_code="MICROSOFT_PRODUCT")
    if "does not need full access" not in note:
        raise IntegrityError("honest build note keeps does not need full access", reason_code="MICROSOFT_PRODUCT")
    if "twin is not launch" not in note:
        raise IntegrityError("honest build note keeps twin is not launch", reason_code="MICROSOFT_PRODUCT")
    if "packs, modules, and repositories are not skus" not in note:
        raise IntegrityError("honest build note keeps packs, modules, and repositories are not SKUs", reason_code="MICROSOFT_PRODUCT")
    lede = str(body.get("lede") or "").lower()
    if "does not need full access" not in lede:
        raise IntegrityError("honest build lede keeps does not need full access", reason_code="MICROSOFT_PRODUCT")
    if "twin is not launch" not in lede:
        raise IntegrityError("honest build lede keeps twin is not launch", reason_code="MICROSOFT_PRODUCT")
    if "packs, modules, and repositories are not skus" not in lede:
        raise IntegrityError("honest build lede keeps packs, modules, and repositories are not SKUs", reason_code="MICROSOFT_PRODUCT")


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["microsoft_stack"]["build"])


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
        "need_full": False,
        "full_access_needed": False,
        "more_secrets_needed": False,
        "twin_is_launch": False,
        "packs_are_skus": False,
        "honest": True,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "three": [dict(item) for item in body.get("three") or []],
        "refuse": [dict(item) for item in body.get("refuse") or []],
        "owner_playbook": dict(body.get("owner_playbook") or {}),
        "this_agent_cannot": [
            "Request full access as this Cloud Agent.",
            "Treat more secrets as the way to build.",
            "Mark the twin as launch.",
            "Treat packs, modules, or repositories as SKUs.",
        ],
    }
