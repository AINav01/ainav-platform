"""Client org chart template. Not AINav, Inc. departments. Not a named customer.

The plane sits on the buyer's existing SOD. Departments are not SKUs.
Department AI is not a seat. Do not invent named heads.
"""

from __future__ import annotations

from typing import Any

from ainav.catalog import load_catalog


REQUIRED_CLIENT_DEPTS = (
    "client.treasury",
    "client.controller",
    "client.payables",
    "client.sales",
    "client.it",
    "client.compliance",
    "client.internal_audit",
    "client.legal",
    "client.executive",
    "client.board",
)
ALLOWED_ROLES = frozenset({"admit", "draft", "keep", "host", "counsel", "oversee"})


def spec() -> dict[str, Any]:
    return dict(load_catalog()["client_org"])


def public_client_org() -> dict[str, Any]:
    body = spec()
    return {
        "kind": body["kind"],
        "sku": False,
        "live": False,
        "live_pin_ok": False,
        "named_customers": [],
        "do_not_invent_names": True,
        "do_not_invent_department_heads": True,
        "replaces_org_chart": False,
        "thesis": body["thesis"],
        "equation": load_catalog()["equations"].get("org"),
        "seats": dict(body.get("seats") or {}),
        "departments": [dict(item) for item in body.get("departments") or []],
        "note": body.get("note"),
    }


def client_org_markdown() -> str:
    body = public_client_org()
    lines = [
        f"# {load_catalog()['entity']['legal']} — client org chart (catalog template)",
        "",
        body["thesis"],
        f"Equation: {body.get('equation')}.",
        "SKU: false. Named customers: none. Replaces org chart: false. LIVE_PIN_OK: false.",
        "",
        "## Seats (existing SOD)",
        "",
    ]
    seats = body.get("seats") or {}
    for key in ("seat_a", "seat_b"):
        seat = seats.get(key) or {}
        lines.append(f"- **{key}** — {seat.get('role')} (usually {seat.get('usually')}).")
    lines += ["", "## Departments (not SKUs, not named heads)", ""]
    for item in body["departments"]:
        lines.append(
            f"- **{item['id']}** — {item['name']} ({item['role']}). "
            f"{item.get('note')} Department AI is a seat: false."
        )
    lines += ["", body.get("note") or "", ""]
    return "\n".join(lines)
