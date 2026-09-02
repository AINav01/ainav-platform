"""AI governance doctrine. Catalog-list maps. Not a certification. Not a SKU.

The client utilizes AI. AINav is the human control plane that sits
over every other client AI: failsafe, off switch, reset, rollback.
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
        "must_have": dict(body.get("must_have") or {}),
        "plane": dict(body.get("plane") or {}),
        "umbrella_equation": load_catalog()["equations"].get("umbrella"),
        "plane_equation": load_catalog()["equations"].get("plane"),
        "org_equation": load_catalog()["equations"].get("org"),
        "insulation_equation": load_catalog()["equations"].get("insulation"),
        "client_org": {
            "thesis": load_catalog()["client_org"]["thesis"],
            "replaces_org_chart": False,
            "do_not_invent_department_heads": True,
        },
        "maps": [dict(item) for item in body.get("maps") or []],
        "risks": [dict(item) for item in body.get("risks") or []],
        "immutable": dict(body.get("immutable") or {}),
        "reporting": dict(body.get("reporting") or {}),
        "consequences": dict(body.get("consequences") or {}),
        "calendar": dict(body.get("calendar") or {}),
        "estate_equation": load_catalog()["equations"].get("estate"),
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
        f"Umbrella: {load_catalog()['equations'].get('umbrella')}.",
        f"Plane: {load_catalog()['equations'].get('plane')}.",
        f"Org: {load_catalog()['equations'].get('org')}.",
        f"Insulation: {load_catalog()['equations'].get('insulation')}.",
        f"Estate: {load_catalog()['equations'].get('estate')}.",
        "Independent of Microsoft. Not a patent. Not uncopyable.",
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
        "## Must-have (not a mandate, not a fourth SKU)",
        "",
    ]
    must = body.get("must_have") or {}
    audience = must.get("for") or {}
    lines += [
        f"- Why: {must.get('why')}",
        f"- Mandated: {str(must.get('mandated')).lower()}. Certified: {str(must.get('certified')).lower()}. SKU: false.",
        f"- Owner: {audience.get('owner')}",
        f"- Board: {audience.get('board')}",
        f"- Examiner: {audience.get('examiner')}",
        "",
        "## Plane (sits over every client AI)",
        "",
    ]
    plane = body.get("plane") or {}
    switch = plane.get("off_switch") or {}
    reset = plane.get("reset") or {}
    rollback = plane.get("rollback") or {}
    lines += [
        "- Sits over: " + "; ".join(plane.get("sits_over") or []) + ".",
        "- Is the client's AI: false.",
        f"- **Off switch** — {switch.get('does')} Does not: {switch.get('does_not')}",
        f"- **Reset** — {reset.get('does')} Does not: {reset.get('does_not')}",
        f"- **Rollback** — {rollback.get('does')} Does not: {rollback.get('does_not')}",
        "",
        "## Client org chart (template, not a named customer)",
        "",
        (body.get("client_org") or {}).get("thesis") or load_catalog()["client_org"]["thesis"],
        "- Replaces org chart: false. Invented department heads: refused.",
        "",
        "## Maps (not certifications)",
        "",
    ]
    for item in body["maps"]:
        lines.append(
            f"- **{item['id']}** — {item['name']} ({item['scope']}). "
            f"Maps to: {item['maps_to']}. Claimed: false."
        )
    immutable = body.get("immutable") or {}
    lines += [
        "",
        "## Immutable (sealed, consume-once, hash-chained)",
        "",
        str(immutable.get("thesis") or ""),
        f"Crypto: {str(immutable.get('crypto')).lower()}. WORM: {str(immutable.get('worm')).lower()}. "
        f"17a-4: {str(immutable.get('seventeen_a4')).lower()}.",
        "",
    ]
    for item in immutable.get("pins") or []:
        lines.append(f"- **{item.get('name')}** — {item.get('note')}")
    reporting = body.get("reporting") or {}
    lines += [
        "",
        "## Reporting and archive",
        "",
        str(reporting.get("lede") or ""),
        f"- Archive: {reporting.get('archive')}",
        f"- Chat is not the keep: {str(reporting.get('chat_is_not_keep')).lower()}.",
        "",
        "## Consequences (not a mandate)",
        "",
        str((body.get("consequences") or {}).get("thesis") or ""),
        f"Mandated: {str((body.get('consequences') or {}).get('mandated')).lower()}. "
        f"Buying L1 closes clocks: {str((body.get('consequences') or {}).get('buying_l1_closes_clocks')).lower()}.",
        "",
    ]
    for item in (body.get("consequences") or {}).get("job_c") or []:
        lines.append(f"- **{item.get('id')}** — {item.get('harm')}")
    lines += ["", "## Calendar (counsel, claimed=false)", ""]
    for item in (body.get("calendar") or {}).get("items") or []:
        lines.append(
            f"- **{item.get('id')}** — {item.get('name')} ({item.get('status')} {item.get('when')}). "
            f"{item.get('note')} Claimed: false."
        )
    lines += ["", "## Risks if client AI writes without dual admit", ""]
    for item in body["risks"]:
        lines.append(f"- **{item['id']}** — {item['harm']}. {item['note']}")
    lines += ["", "## Refuse", ""]
    for item in body["refuse"]:
        lines.append(f"- {item}")
    lines += ["", body.get("note") or "", ""]
    return "\n".join(lines)
