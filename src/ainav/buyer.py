"""Controller-forwardable buyer page. No invented inbox. No named customer."""

from __future__ import annotations

from typing import Any

from ainav.catalog import load_catalog
from ainav.ip import refuse_claim


def buyer_page() -> dict[str, Any]:
    cat = load_catalog()
    body = dict(cat["buyer"])
    page = {
        "kind": "ainav.institute.buyer.v1",
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "incident": cat["l1_incident_copy"],
        "write_that_must_not_happen": body["write_that_must_not_happen"],
        "seats": list(body["seats"]),
        "prices": list(body["prices"]),
        "proof_day": body["proof_day"],
        "minutes": cat["proof_day"]["minutes"],
        "refuse": list(body["refuse"]),
        "door": body["door"],
        "already_have": str(((cat.get("plane_interface") or {}).get("floor") or {}).get("already_have") or ""),
        "still_lack": str(((cat.get("plane_interface") or {}).get("floor") or {}).get("still_lack") or ""),
        "must_have_for": dict((((cat.get("governance") or {}).get("must_have") or {}).get("for") or {})),
        "not_the_gate": [dict(item) for item in ((cat.get("plane_interface") or {}).get("floor") or {}).get("not_the_gate") or []],
        "proof_close": dict(((cat.get("plane_interface") or {}).get("floor") or {}).get("proof_close") or {}),
        "no_means": dict(((cat.get("plane_interface") or {}).get("floor") or {}).get("no_means") or {}),
        "sale": str((((cat.get("plane_interface") or {}).get("floor") or {}).get("page") or {}).get("sale") or ""),
        "twin_is": str((((cat.get("plane_interface") or {}).get("floor") or {}).get("page") or {}).get("twin_is") or ""),
        "accountable": dict(((cat.get("plane_interface") or {}).get("floor") or {}).get("accountable") or {}),
        "protect": dict(((cat.get("plane_interface") or {}).get("floor") or {}).get("protect") or {}),
        "memory": dict(((cat.get("plane_interface") or {}).get("floor") or {}).get("memory") or {}),
        "integrate": dict(((cat.get("plane_interface") or {}).get("floor") or {}).get("integrate") or {}),
        "contact_email": None,
        "mailto": None,
        "icp": icp_profile(),
        "success": success_program(),
        "first_glance": dict(((cat.get("plane_interface") or {}).get("floor") or {}).get("first_glance") or {}),
        "public_face": dict(((cat.get("plane_interface") or {}).get("floor") or {}).get("public_face") or {}),
        "skus": [
            {
                "id": item["id"],
                "name": item["name"],
                "kind": item["kind"],
                "term": item["term"],
                "price_usd": dict(item["price_usd"]),
                "one_line": (
                    item.get("incident")
                    or (item.get("includes") or ["Keep the same admit plane"])[0]
                ),
            }
            for item in cat.get("skus") or []
            if item.get("id") in {"L1", "P-ADM", "U-DUAL"}
        ],
        "signed_l1": False,
        "live": False,
        "live_pin_ok": False,
        "launch": False,
    }
    refuse_claim(page["write_that_must_not_happen"], catalog=cat)
    return page


def success_program() -> dict[str, Any]:
    """Controller-facing success program. Catalog only. Not LIVE_PIN_OK."""
    body = dict((load_catalog().get("expert_review") or {}).get("success") or {})
    return {
        "sku": False,
        "live": False,
        "live_pin_ok": False,
        "certified": False,
        "mandated": False,
        "thesis": body.get("thesis"),
        "bake_off": dict(body.get("bake_off") or {}),
        "qualify": dict(body.get("qualify") or {}),
        "objections": [dict(item) for item in body.get("objections") or []],
        "ciso": dict(body.get("ciso") or {}),
        "seat_b": dict(body.get("seat_b") or {}),
        "continuity": dict(body.get("continuity") or {}),
        "human_control": dict(body.get("human_control") or {}),
        "executive_risk": dict(body.get("executive_risk") or {}),
        "market_position": dict(body.get("market_position") or {}),
    }


def icp_profile() -> dict[str, Any]:
    body = dict(load_catalog()["icp"])
    return {
        "erp": body["erp"],
        "identity": body["identity"],
        "control": body["control"],
        "utilizes_ai": bool(body.get("utilizes_ai")),
        "counterparties_utilize_ai": bool(body.get("counterparties_utilize_ai")),
        "institutes_ainav": body.get("institutes_ainav"),
        "ai": body.get("ai"),
        "counterparty_ai": body.get("counterparty_ai"),
        "named_customers": [],
        "do_not_invent_names": True,
        "do_not_invent_counterparty_names": True,
        "sits_over_client_ai": bool(body.get("sits_over_client_ai")),
        "must_have_for": list(body.get("must_have_for") or []),
        "org_chart": bool(body.get("org_chart")),
        "do_not_invent_department_heads": True,
        "independent_of_microsoft": True,
    }


def proof_day_brief(*, for_controller: str | None = None) -> dict[str, Any]:
    """Forwardable brief. No inbox. No invented customer name."""
    page = buyer_page()
    label = (for_controller or "").strip()
    if label and label.lower() in {"acme", "contoso", "fabrikam", "northwind"}:
        from ainav.errors import ProvisionError

        raise ProvisionError(
            "do not invent a named design partner",
            reason_code="ICP_NAMED",
        )
    return {
        "kind": "ainav.proof_day.brief.v1",
        "forwardable": True,
        "for_controller": label or None,
        "write_that_must_not_happen": page["write_that_must_not_happen"],
        "incident": page["incident"],
        "seats": page["seats"],
        "prices": page["prices"],
        "proof_day": page["proof_day"],
        "minutes": page["minutes"],
        "refuse": page["refuse"],
        "ask": "Ask for a ninety-minute proof day on the existing treasury SOD.",
        "bake_off": dict((page.get("success") or {}).get("bake_off") or {}),
        "qualify": dict((page.get("success") or {}).get("qualify") or {}),
        "walk_away": list(((page.get("success") or {}).get("qualify") or {}).get("walk_away") or []),
        "contact_email": None,
        "mailto": None,
        "named_customer": None,
        "signed_l1": False,
        "live": False,
    }
