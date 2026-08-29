"""AI governance doctrine. Catalog-list maps. Not a certification. Not a SKU.

The client utilizes AI. AINav is the failsafe and the human control.
Client AI drafts. Two humans admit. Then the write. This module does
not file, certify, or replace counsel.
"""

from __future__ import annotations

from typing import Any

from ainav.catalog import load_catalog


def spec() -> dict[str, Any]:
    return dict(load_catalog()["governance"])


def public_governance() -> dict[str, Any]:
    body = spec()
    return {
        "kind": body["kind"],
        "sku": False,
        "certified": False,
        "replaces_counsel": False,
        "live": False,
        "live_pin_ok": False,
        "thesis": body["thesis"],
        "control_equation": load_catalog()["equations"]["control"],
        "failsafe": dict(body["failsafe"]),
        "cascade": dict(body.get("cascade") or {}),
        "records": dict(body.get("records") or {}),
        "maps": [dict(item) for item in body.get("maps") or []],
        "risks": [dict(item) for item in body.get("risks") or []],
        "refuse": list(body.get("refuse") or []),
        "note": body.get("note"),
    }


def governance_markdown() -> str:
    body = public_governance()
    fail = body["failsafe"]
    lines = [
        f"# {load_catalog()['entity']['legal']} — AI governance (catalog map)",
        "",
        body["thesis"],
        f"Control: {body.get('control_equation') or load_catalog()['equations']['control']}.",
        f"Cascade: {load_catalog()['equations'].get('cascade')}.",
        f"Certified: {str(body['certified']).lower()}. Replaces counsel: "
        f"{str(body['replaces_counsel']).lower()}. SKU: false. LIVE_PIN_OK: false.",
        "",
        "## Failsafe (client utilizes AI; humans control)",
        "",
        f"- Client: {fail.get('client') or 'Utilizes AI.'}",
        f"- AINav: {fail.get('ainav') or 'Failsafe and human control.'}",
        f"- Does: {fail['does']}",
        "- Separate from: " + "; ".join(fail.get("separate_from") or []) + ".",
        "- Does not: " + "; ".join(fail.get("does_not") or []) + ".",
        "",
        "## Cascade (the client's customers utilize AI)",
        "",
    ]
    cascade = body.get("cascade") or {}
    lines += [
        f"- Does: {cascade.get('does')}",
        "- Stable the client institutes: " + ", ".join(cascade.get("stable") or []) + ".",
        "- Buyer is the client: " + str(cascade.get("buyer_is_the_client")).lower() + ".",
        "- Invented names: refused.",
        "",
        "## First and second records",
        "",
    ]
    records = body.get("records") or {}
    first = records.get("first") or {}
    second = records.get("second") or {}
    lines += [
        f"- **First record** — {first.get('what')} ({first.get('plane')}). {first.get('note')}",
        f"- **Second record** — {second.get('what')} ({second.get('plane')}). {second.get('note')}",
        "",
        "## Maps (not certifications)",
        "",
    ]
    for item in body["maps"]:
        lines.append(
            f"- **{item['id']}** — {item['name']} ({item['scope']}). "
            f"Maps to: {item['maps_to']}. Claimed: false."
        )
    lines += ["", "## Risks if client AI writes without dual admit", ""]
    for item in body["risks"]:
        lines.append(f"- **{item['id']}** — {item['harm']}. {item['note']}")
    lines += ["", "## Refuse", ""]
    for item in body["refuse"]:
        lines.append(f"- {item}")
    lines += ["", body.get("note") or "", ""]
    return "\n".join(lines)
