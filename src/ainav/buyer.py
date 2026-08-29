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
        "contact_email": None,
        "mailto": None,
        "icp": icp_profile(),
        "signed_l1": False,
        "live": False,
    }
    refuse_claim(page["write_that_must_not_happen"], catalog=cat)
    return page


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
        "contact_email": None,
        "mailto": None,
        "named_customer": None,
        "signed_l1": False,
        "live": False,
    }
