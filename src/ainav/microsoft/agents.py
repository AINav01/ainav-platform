"""Microsoft 365 Agents registry review. Complements only. Never the admit plane.

Agents > All (#/agents/all) is the Agent 365 registry.
Agents > Tools is the MCP list. An agent is not a seat.
This Cloud Agent cannot sign in or take a census.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import (
    AGENTS_ALL_URL,
    MICROSOFT_AGENT_AROUND_IDS,
    MICROSOFT_AGENT_DRAFT_IDS,
    MICROSOFT_AGENT_HREFS,
    MICROSOFT_AGENT_LANE_IDS,
    MICROSOFT_AGENT_MCP_IDS,
    MICROSOFT_AGENT_NEVER_IDS,
    MICROSOFT_AGENT_OPERATE_IDS,
    MICROSOFT_AGENT_REFUSE_IDS,
    MICROSOFT_AGENT_REFUSE_TEXT,
    MICROSOFT_AGENT_REGISTRY_IDS,
    MICROSOFT_AGENT_TYPE_IDS,
    load_catalog,
)

KIND = "ainav.microsoft.agents.v1"


def validate_microsoft_agents(catalog: dict[str, Any]) -> None:
    stack = catalog.get("microsoft_stack") or {}
    if not isinstance(stack, dict):
        raise IntegrityError("catalog missing microsoft stack", reason_code="MICROSOFT_PRODUCT")
    body = stack.get("agents")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing microsoft agents review", reason_code="MICROSOFT_PRODUCT")
    if body.get("kind") != KIND:
        raise IntegrityError("microsoft agents kind stays catalog law", reason_code="MICROSOFT_PRODUCT")
    if body.get("admin_url") != AGENTS_ALL_URL:
        raise IntegrityError("microsoft agents admin_url is Agents > All", reason_code="MICROSOFT_PRODUCT")
    false_flags = (
        "is_sku",
        "fourth_sku",
        "is_connection",
        "is_admit_plane",
        "cms",
        "live",
        "live_pin_ok",
        "launch",
        "wired",
        "inventory_claimed",
        "census",
        "agent_365_is_product",
        "claimed",
        "control_is_live",
        "cloud_agent_can_approve",
    )
    for flag in false_flags:
        if body.get(flag) is True:
            raise IntegrityError(
                "microsoft agents cannot claim " + flag.replace("_", " "),
                reason_code="MICROSOFT_PRODUCT",
            )
    if body.get("honest") is not True:
        raise IntegrityError("microsoft agents stay honest", reason_code="MICROSOFT_PRODUCT")
    if body.get("cloud_agent_can_approve") is True:
        raise IntegrityError("Cloud Agent cannot approve agents", reason_code="MICROSOFT_PRODUCT")
    types = [item.get("id") for item in body.get("types") or []]
    if types != list(MICROSOFT_AGENT_TYPE_IDS):
        raise IntegrityError("microsoft agent types stay the Learn four", reason_code="MICROSOFT_PRODUCT")
    if any(item.get("claimed") is True for item in body.get("types") or []):
        raise IntegrityError("microsoft agent types stay claimed=false", reason_code="MICROSOFT_PRODUCT")
    draft_ids = [item.get("id") for item in body.get("draft") or []]
    if draft_ids != list(MICROSOFT_AGENT_DRAFT_IDS):
        raise IntegrityError("microsoft agent draft maps stay catalog law", reason_code="MICROSOFT_PRODUCT")
    if any(item.get("installed") is not None for item in body.get("draft") or []):
        raise IntegrityError("microsoft agent draft maps stay installed=null", reason_code="MICROSOFT_PRODUCT")
    around = body.get("around") or []
    if [item.get("id") for item in around] != list(MICROSOFT_AGENT_AROUND_IDS):
        raise IntegrityError("microsoft agent around maps stay catalog law", reason_code="MICROSOFT_PRODUCT")
    if any(item.get("claimed") is True or item.get("installed") is not None for item in around):
        raise IntegrityError("microsoft agent around maps stay claimed=false and installed=null", reason_code="MICROSOFT_PRODUCT")
    lanes = body.get("lanes") or []
    if [item.get("id") for item in lanes] != list(MICROSOFT_AGENT_LANE_IDS):
        raise IntegrityError("microsoft agent lanes stay operate/registry/draft/never/mcp/refuse", reason_code="MICROSOFT_PRODUCT")
    expected_lane_ids = {
        "operate": list(MICROSOFT_AGENT_OPERATE_IDS),
        "registry": list(MICROSOFT_AGENT_REGISTRY_IDS),
        "draft": list(MICROSOFT_AGENT_DRAFT_IDS),
        "never": list(MICROSOFT_AGENT_NEVER_IDS),
        "mcp": list(MICROSOFT_AGENT_MCP_IDS),
        "refuse": list(MICROSOFT_AGENT_REFUSE_IDS),
    }
    hrefs = {}
    refuse_items = []
    for lane in lanes:
        lane_id = lane.get("id")
        row_ids = [row.get("id") for row in lane.get("items") or []]
        if row_ids != expected_lane_ids.get(lane_id):
            raise IntegrityError("microsoft agent lane items stay catalog law", reason_code="MICROSOFT_PRODUCT")
        for row in lane.get("items") or []:
            hrefs[row.get("id")] = row.get("href")
            if row.get("refuse") is True:
                refuse_items.append(row)
    if hrefs != MICROSOFT_AGENT_HREFS:
        raise IntegrityError("microsoft agent hrefs stay catalog law", reason_code="MICROSOFT_PRODUCT")
    if [item.get("id") for item in refuse_items] != list(MICROSOFT_AGENT_REFUSE_IDS):
        raise IntegrityError("microsoft agent refuse ids stay catalog law", reason_code="MICROSOFT_PRODUCT")
    texts = {item.get("id"): item.get("refuse_text") for item in refuse_items}
    if texts != {key: MICROSOFT_AGENT_REFUSE_TEXT[key] for key in MICROSOFT_AGENT_REFUSE_IDS}:
        raise IntegrityError("microsoft agent refuse text stays catalog law", reason_code="MICROSOFT_PRODUCT")
    playbook = body.get("owner_playbook") or {}
    owner = (catalog.get("operating") or {}).get("owner_principal")
    if playbook.get("actor") != owner:
        raise IntegrityError("agents playbook actor must be the sole owner", reason_code="MICROSOFT_PRODUCT")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot run the agents playbook", reason_code="MICROSOFT_PRODUCT")
    note = str(body.get("note") or "").lower()
    if "honest agents" not in note or "not a seat" not in note:
        raise IntegrityError("microsoft agents note keeps honest agents", reason_code="MICROSOFT_PRODUCT")
    if "around the write" not in note or "total agents" not in note:
        raise IntegrityError("microsoft agents note keeps around the write and Total agents", reason_code="MICROSOFT_PRODUCT")
    lede = str(body.get("lede") or "").lower()
    if "agents > all" not in lede and "agents > all" not in str(body.get("site") or "").lower():
        if "#/agents/all" not in lede and "agent is not a seat" not in lede:
            raise IntegrityError("microsoft agents lede keeps the registry and not a seat", reason_code="MICROSOFT_PRODUCT")
    if "agent is not a seat" not in lede:
        raise IntegrityError("microsoft agents lede keeps an agent is not a seat", reason_code="MICROSOFT_PRODUCT")


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["microsoft_stack"]["agents"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    playbook = dict(body.get("owner_playbook") or {})
    return {
        "kind": KIND,
        "entity": load_catalog()["entity"]["legal"],
        "institute": load_catalog()["entity"]["institute"],
        "admin_url": body["admin_url"],
        "tools_url": body.get("tools_url"),
        "product": body["product"],
        "is_sku": False,
        "fourth_sku": False,
        "is_connection": False,
        "is_admit_plane": False,
        "live": False,
        "live_pin_ok": False,
        "wired": False,
        "inventory_claimed": False,
        "census": False,
        "agent_365_is_product": False,
        "cloud_agent_can_approve": False,
        "honest": True,
        "note": body["note"],
        "lede": body.get("lede"),
        "site": body.get("site"),
        "types": [dict(item) for item in body.get("types") or []],
        "lanes": [dict(item) for item in body.get("lanes") or []],
        "draft": [dict(item) for item in body.get("draft") or []],
        "around": [dict(item) for item in body.get("around") or []],
        "never_as_admit": list(body.get("never_as_admit") or []),
        "owner_playbook": playbook,
        "this_agent_cannot": [
            "Sign in to admin.cloud.microsoft as the owner.",
            "Take a live census of Agents > All.",
            "Paste Total agents, ownerless, or unmanaged into the catalog.",
            "Install, pin, block, or unblock an agent.",
            "Treat Agent 365 as AINav.",
            "Treat an agent as a seat.",
        ],
    }
