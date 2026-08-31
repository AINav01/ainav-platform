"""Hop-by-hop Microsoft stack walk. Catalog law. Never LIVE_PIN_OK."""

from __future__ import annotations

from typing import Any

from ainav.catalog import load_catalog


def stack_walk() -> dict[str, Any]:
    cat = load_catalog()
    walk = dict((cat.get("microsoft_stack") or {}).get("walk") or {})
    return {
        "kind": "ainav.stack.walk.v1",
        "entity": cat["entity"]["legal"],
        "product": cat["entity"]["product"],
        "institute": cat["entity"]["institute"],
        "release": cat["entity"]["release"],
        "sku": False,
        "live": False,
        "live_pin_ok": False,
        "is_admit_plane": False,
        "thesis": walk.get("thesis"),
        "implementation": walk.get("implementation"),
        "cli": walk.get("cli") or "python -m ainav stack",
        "path": [dict(item) for item in walk.get("path") or []],
        "complements": [dict(item) for item in walk.get("complements") or []],
        "cannot": list(walk.get("cannot") or []),
        "not_the_product": cat["microsoft_stack"]["not_the_product"],
        "edge": {
            "id": cat["microsoft_stack"]["edge"]["id"],
            "full": cat["microsoft_stack"]["edge"]["full"],
            "dashboard_url": cat["microsoft_stack"]["edge"]["dashboard_url"],
            "sku": False,
            "is_admit_plane": False,
        },
    }


def stack_walk_markdown() -> str:
    body = stack_walk()
    lines = [
        f"# {body['entity']} — stack walk",
        "",
        f"Release {body['release']}. Catalog-honest. Not LIVE_PIN_OK. Not a launch.",
        f"{body['not_the_product']}",
        "",
        f"**{body['thesis']}**",
        "",
        f"Implementation: {body['implementation']}",
        f"CLI: `{body['cli']}`. Probe is read-only: `python -m ainav connect --probe`.",
        "",
        "This Cloud Agent cannot: " + "; ".join(body["cannot"]) + ".",
        "",
        "## Privileged-write path",
        "",
    ]
    for item in body["path"]:
        lines.extend(_hop_lines(item))
    lines += ["", "## Complements (not hops on the write)", ""]
    for item in body["complements"]:
        lines.extend(_hop_lines(item))
    lines += [
        "",
        "## Stop",
        "",
        "A green health probe is not LIVE_PIN_OK. DNS full is not Institute launch. "
        "Sandbox AINAV-L1 is not Production. Mailbox recorded is not a seat B click.",
        "",
    ]
    return "\n".join(lines)


def _hop_lines(item: dict[str, Any]) -> list[str]:
    n = item.get("n")
    prefix = f"{n}. " if n is not None else "- "
    url = item.get("url") or ""
    label = item.get("url_label") or url
    learn = item.get("learn") or ""
    learn_label = item.get("learn_label") or "docs"
    link = f"[{label}]({url})" if url.startswith("https://") else label
    doc = f" · [{learn_label}]({learn})" if str(learn).startswith("https://") else ""
    return [
        f"{prefix}**{item.get('name')}** — `{item.get('status')}`. {item.get('in_tree') or ''}",
        f"   Owner: {item.get('owner') or ''} {link}{doc}",
        "",
    ]
