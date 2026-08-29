"""Unsigned L1 order form and MSA skeleton. G12/G13 stay open."""

from __future__ import annotations

from typing import Any

from ainav.catalog import load_catalog, sku


def order_form() -> dict[str, Any]:
    cat = load_catalog()
    body = cat["counsel"]["order_form"]
    prices = {item["id"]: item["price_usd"] for item in cat["skus"]}
    return {
        "kind": body["kind"],
        "entity": cat["entity"]["legal"],
        "unsigned": True,
        "signed_l1": False,
        "live": False,
        "live_pin_ok": False,
        "seats": list(body["seats"]),
        "skus": [
            {
                "id": sku_id,
                "name": sku(sku_id)["name"],
                "min": prices[sku_id]["min"],
                "max": prices[sku_id]["max"],
                "term": sku(sku_id)["term"],
            }
            for sku_id in body["skus"]
        ],
        "rules": list(body["rules"]),
        "commercial_equation": cat["equations"]["commercial"],
        "note": "Catalog list. Not recognized revenue. Not a signed L1.",
    }


def order_form_markdown() -> str:
    form = order_form()
    lines = [
        f"# {form['entity']} — L1 order form (unsigned)",
        "",
        "G12 legal is open. This is not signed. This is not recognized revenue.",
        f"Commercial close: {form['commercial_equation']}",
        f"Seats: {' / '.join(form['seats'])}",
        "",
        "## SKUs",
        "",
    ]
    for item in form["skus"]:
        lines.append(
            f"- **{item['id']} {item['name']}** — ${item['min']:,}–${item['max']:,} ({item['term']})"
        )
    lines += ["", "## Rules", ""]
    for rule in form["rules"]:
        lines.append(f"- {rule}")
    lines += ["", form["note"], ""]
    return "\n".join(lines)


def msa_skeleton() -> dict[str, Any]:
    cat = load_catalog()
    body = cat["counsel"]["msa"]
    return {
        "kind": body["kind"],
        "entity": cat["entity"]["legal"],
        "unsigned": True,
        "g12_open": True,
        "g13_open": True,
        "live": False,
        "live_pin_ok": False,
        "product": cat["entity"]["product"],
        "job": cat["entity"]["job"],
        "must_not_change": list(cat["must_not_change"]),
        "note": body["note"],
    }


def msa_markdown() -> str:
    body = msa_skeleton()
    lines = [
        f"# {body['entity']} — MSA skeleton (unsigned)",
        "",
        body["note"],
        f"Product: {body['product']} (Job {body['job']}).",
        "",
        "Must not change:",
        "",
    ]
    for rule in body["must_not_change"]:
        lines.append(f"- {rule}")
    lines.append("")
    return "\n".join(lines)
