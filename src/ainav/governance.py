"""AI governance doctrine. Catalog-list maps. Not a certification. Not a SKU.

AINav is a separate failsafe from client AI. Client AI may propose.
Two humans admit. Then the write. This module does not file, certify,
or replace counsel.
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
        "failsafe": dict(body["failsafe"]),
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
        f"Certified: {str(body['certified']).lower()}. Replaces counsel: "
        f"{str(body['replaces_counsel']).lower()}. SKU: false. LIVE_PIN_OK: false.",
        "",
        "## Failsafe (separate from client AI)",
        "",
        f"- Does: {fail['does']}",
        "- Separate from: " + "; ".join(fail.get("separate_from") or []) + ".",
        "- Does not: " + "; ".join(fail.get("does_not") or []) + ".",
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
