"""Owner-only gates with Microsoft admin links. This Cloud Agent cannot click them."""

from __future__ import annotations

from typing import Any

from ainav.catalog import load_catalog


def owner_steps() -> list[dict[str, str]]:
    return [dict(item) for item in load_catalog()["owner_gates"]]


def owner_steps_markdown() -> str:
    cat = load_catalog()
    invited = cat["organization"]["contacts"]["invited"]
    lines = [
        f"# {cat['entity']['legal']} — owner steps",
        "",
        f"Release {cat['entity']['release']}. Catalog-honest. Not LIVE_PIN_OK. Not a launch.",
        f"Owner: {cat['operating']['owner_principal']}. Operator: {cat['operating']['operator']} (not a seat).",
        f"Invited second human: {invited['name']} ({invited['seat_role']} / {invited['inception_role']}). "
        "Not recorded. Email not stored.",
        "",
        "This Cloud Agent cannot create users, grant Graph roles, publish the Institute, or mark LIVE_PIN_OK.",
        "",
    ]
    for index, step in enumerate(owner_steps(), start=1):
        lines.append(f"{index}. {step['do']}")
        lines.append(f"   [{step['url_label']}]({step['url']})")
        lines.append("")
    return "\n".join(lines)


def public_owner_steps() -> dict[str, Any]:
    cat = load_catalog()
    invited = cat["organization"]["contacts"]["invited"]
    return {
        "kind": "ainav.owner_steps.v1",
        "entity": cat["entity"]["legal"],
        "release": cat["entity"]["release"],
        "owner": cat["operating"]["owner_principal"],
        "operator_is_seat": False,
        "invited": {
            "name": invited["name"],
            "recorded": False,
            "email": None,
            "seat_role": invited["seat_role"],
            "inception_role": invited["inception_role"],
            "equity": False,
        },
        "steps": owner_steps(),
        "live": False,
        "live_pin_ok": False,
        "launch_ready": False,
        "signed_l1": False,
    }
