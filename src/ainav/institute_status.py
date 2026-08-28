"""Public Institute status. Catalog + sandbox evidence. Never LIVE_PIN_OK."""

from __future__ import annotations

from typing import Any

from ainav.catalog import honest_missing, load_catalog


def public_status() -> dict[str, Any]:
    cat = load_catalog()
    evidence = dict(cat["sandbox_evidence"])
    site = cat["programs"]["website"]
    return {
        "kind": "ainav.institute.status.v1",
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "product": cat["entity"]["product"],
        "job": cat["entity"]["job"],
        "live": False,
        "live_pin_ok": False,
        "production": False,
        "wrote_sor": False,
        "signed_l1": False,
        "custom_domain_claimed": False,
        "azure_url": site.get("azure_url"),
        "bc": {
            "connection": "bc.premium",
            "product": "Dynamics 365 Business Central Premium",
            "environment": evidence["environment"],
            "operating_company": evidence["bc_company"],
            "operating_company_id": evidence["bc_company_id"],
            "wedge": evidence["action_class"],
            "sandbox_document": evidence["bc_document"],
            "amount": evidence["amount"],
            "date": evidence["date"],
            "live_pin_ok": False,
            "note": evidence["note"],
        },
        "sales": {
            "connection": "sales.enterprise",
            "product": "Dynamics 365 Sales Enterprise",
            "licensed": True,
            "wired": False,
            "instances": 0,
            "note": "License exists. No Dataverse instance. Twin only until G14.",
        },
        "identity": {
            "connection": "m365.e7",
            "product": "Microsoft 365 E7 / Microsoft Entra ID",
            "note": "Seat object ids. Not an IdP replacement. Copilot is not the admit plane.",
        },
        "notify": {
            "connections": ["teams.enterprise", "teams.premium"],
            "wired": False,
            "note": "Licensed. A chat is not a seat.",
        },
        "host": {
            "connection": "azure.host",
            "location": "eastus / eastus2",
            "institute_site": site.get("azure_site"),
        },
        "opportunity": {
            "prove": "L1",
            "keep": "P-ADM",
            "deepen": "U-DUAL",
            "recognized_revenue": None,
            "named_customers": [],
        },
        "honest_missing": honest_missing(),
        "open_gaps": list(cat["open_gaps"]),
        "success_equation": cat["success_equation"],
    }
