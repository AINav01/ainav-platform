"""Microsoft 365 Agent Tools review. Complements only. Never the admit plane.

The admin page Agents > Tools is the Copilot / Agent 365 MCP registry.
This Cloud Agent cannot approve or block tools there. DayTradingMarkets can.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog
from ainav.microsoft.health import GRAPH_SCOPE, _get, _token, entra_configured

ADMIN_URL = "https://admin.cloud.microsoft/?source=applauncher#/agents/tools/all"
AGENT_365_APP_ID = "ea9ffc3e-8a23-4a7d-836d-234d7c7565c1"
LEAVE_AVAILABLE_IDS = (
    "workiq.user",
    "workiq.teams",
    "workiq.sharepoint",
    "workiq.mail",
    "mcp.management",
)
PLAYBOOK_STEP_IDS = (
    "sign_in",
    "open_registry",
    "leave_available",
    "confirm_five",
    "never_as_admit",
    "block_dataverse",
    "requests",
    "stop",
)


def validate_agent_tools(catalog: dict[str, Any]) -> None:
    body = (catalog.get("microsoft_stack") or {}).get("agent_tools")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing agent_tools review", reason_code="MICROSOFT_PRODUCT")
    if body.get("is_sku") or body.get("is_connection") or body.get("is_admit_plane"):
        raise IntegrityError(
            "Agent Tools cannot be a SKU, connection, or admit plane",
            reason_code="MICROSOFT_PRODUCT",
        )
    if body.get("cloud_agent_can_approve") is True:
        raise IntegrityError(
            "Cloud Agent cannot approve Agent Tools",
            reason_code="MICROSOFT_PRODUCT",
        )
    ids = [item.get("id") for item in body.get("leave_available") or []]
    if ids != list(LEAVE_AVAILABLE_IDS):
        raise IntegrityError(
            "Leave Available set must be the five Work IQ / MCP Management complements",
            reason_code="MICROSOFT_PRODUCT",
        )
    playbook = body.get("owner_playbook") or {}
    if playbook.get("actor") != "DayTradingMarkets":
        raise IntegrityError("owner playbook actor must be DayTradingMarkets", reason_code="MICROSOFT_PRODUCT")
    if playbook.get("cannot_be_done_by") != "cursor.cloud_agent":
        raise IntegrityError("Cloud Agent cannot run the owner playbook", reason_code="MICROSOFT_PRODUCT")
    step_ids = [item.get("id") for item in playbook.get("steps") or []]
    if step_ids != list(PLAYBOOK_STEP_IDS):
        raise IntegrityError("owner playbook steps are incomplete", reason_code="MICROSOFT_PRODUCT")


def doctrine() -> dict[str, Any]:
    return dict(load_catalog()["microsoft_stack"]["agent_tools"])


def public_review() -> dict[str, Any]:
    body = doctrine()
    playbook = dict(body["owner_playbook"])
    return {
        "kind": "ainav.institute.agent_tools.v1",
        "entity": load_catalog()["entity"]["legal"],
        "institute": load_catalog()["entity"]["institute"],
        "admin_url": body["admin_url"],
        "product": body["product"],
        "is_sku": False,
        "is_connection": False,
        "is_admit_plane": False,
        "live": False,
        "live_pin_ok": False,
        "wired": False,
        "cloud_agent_can_approve": False,
        "human_adds": True,
        "note": body["note"],
        "leave_available": [dict(item) for item in body["leave_available"]],
        "block_until_dual": [dict(item) for item in body["block_until_dual"]],
        "never_as_admit": list(body["never_as_admit"]),
        "owner_playbook": playbook,
        "you_do": [item["do"] for item in playbook.get("steps") or []],
        "this_agent_cannot": [
            "Sign in to admin.cloud.microsoft as the owner.",
            "Approve or block a tool.",
            "Grant Entra consent for an MCP server.",
            "Create a new Entra app.",
        ],
    }


def steps_markdown() -> str:
    review = public_review()
    playbook = review["owner_playbook"]
    lines = [
        "# Leave Available — owner playbook",
        "",
        "Catalog-honest. Not the admit plane. This Cloud Agent cannot click Unblock or Block.",
        f"Actor: {playbook['actor']}. Operator {playbook['cannot_be_done_by']} is not a seat.",
        "",
        "## Leave Available",
        "",
    ]
    for item in review["leave_available"]:
        lines.append(f"- **{item['name']}** — {item['note']}")
    lines += [
        "",
        "## Steps (you click these)",
        "",
    ]
    for index, step in enumerate(playbook["steps"], start=1):
        url = step.get("url") or ""
        label = step.get("url_label") or url
        suffix = f" [{label}]({url})" if url else ""
        doc = step.get("doc") or ""
        if doc:
            suffix += f" Docs: {doc}"
        lines.append(f"{index}. {step['do']}{suffix}")
    lines += [
        "",
        "## Docs",
        "",
    ]
    for item in playbook.get("docs") or []:
        lines.append(f"- [{item['title']}]({item['url']})")
    lines += [
        "",
        f"Registry: {review['admin_url']}",
        "Never as admit: " + ", ".join(review["never_as_admit"]) + ".",
        "",
    ]
    return "\n".join(lines)


def probe_agent_tools() -> dict[str, Any]:
    """Read-only. Directory SP read is 403 on this app. Never approves."""
    review = public_review()
    if not entra_configured():
        return {
            **review,
            "probed": False,
            "reason": "missing_env",
            "missing": ["ENTRA_TENANT_ID", "ENTRA_CLIENT_ID", "ENTRA_CLIENT_SECRET"],
        }
    tok = _token(GRAPH_SCOPE)
    if not tok.get("ok"):
        return {**review, "probed": True, "reason": str(tok.get("status")), "http": tok.get("http")}
    status, body = _get(
        (
            "https://graph.microsoft.com/v1.0/servicePrincipals"
            f"?$filter=appId%20eq%20'{AGENT_365_APP_ID}'"
            "&$select=id,appId,displayName"
        ),
        tok["token"],
    )
    return {
        **review,
        "probed": True,
        "agent_365_app_id": AGENT_365_APP_ID,
        "http": status,
        "reason": "graph_role_missing_Application_or_Directory" if status == 403 else "read_only",
        "detail": body if isinstance(body, str) else None,
        "next": (
            "Owner reviews https://admin.cloud.microsoft/?source=applauncher#/agents/tools/all. "
            "Do not make Copilot the admit plane."
        ),
    }
