"""Public Institute status. Catalog + sandbox evidence. Never LIVE_PIN_OK."""

from __future__ import annotations

from typing import Any

from ainav.catalog import catalog_engineering, honest_missing, load_catalog, sku
from ainav.microsoft.agent_tools import public_review as agent_tools_review
from ainav.microsoft.dns import catalog_edge

COMPLEMENT_HONESTY = {
    "entra.id": "Seat object ids. Not an IdP replacement. Copilot is not the admit plane.",
    "azure.keyvault": "Connection secret hold on the host. Not a live pin.",
    "azure.monitor": "Mothership health. LAW is not Sentinel. Not a live pin.",
    "sharepoint.kit": "Kit evidence store. Not a seat. Graph is not called from this page.",
    "defender.xdr": "E7 security sink. SecurityIncident.Read.All is not granted. Not the admit plane.",
    "entra.pim": "Eligible seats. A PIM activation is not dual admit.",
    "sentinel.siem": "DecisionRecord export sink. The mothership LAW is not a Sentinel workspace.",
    "azure.policy": "Host policy. West Europe is blocked. Cannot weaken Job C.",
}


def _sku_band(sku_id: str) -> dict[str, Any]:
    item = sku(sku_id)
    price = item["price_usd"]
    return {
        "id": sku_id,
        "name": item["name"],
        "kind": item["kind"],
        "min": price["min"],
        "max": price["max"],
        "term": item["term"],
    }


def _complements(cat: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": item["id"],
            "product": item["product"],
            "role": item["role"],
            "binds": list(item.get("binds") or []),
            "wired": False,
            "live": False,
            "mode": "sandbox",
            "note": COMPLEMENT_HONESTY[item["id"]],
        }
        for item in cat["connections"]["complements"]
    ]


def _fabric(cat: dict[str, Any], evidence: dict[str, Any], site: dict[str, Any]) -> dict[str, Any]:
    return {
        "live": False,
        "product": cat["entity"]["product"],
        "not_the_product": cat["microsoft_stack"]["not_the_product"],
        "e7_not_the_product": list(cat["microsoft_stack"].get("e7_not_the_product") or []),
        "path": [
            {
                "id": "azure.host",
                "lane": "host",
                "product": "Microsoft Azure",
                "status": "hosted_sandbox",
                "note": f"{site.get('azure_site')} on {site.get('azure_location')}. Custom domain not bound.",
            },
            {
                "id": "m365.e7",
                "lane": "identity",
                "product": "Microsoft 365 E7 / Microsoft Entra ID",
                "status": "connected_sandbox",
                "note": "Seat object ids. Copilot is not a seat. PIM is not dual admit.",
            },
            {
                "id": "admit",
                "lane": "admit",
                "product": cat["entity"]["product"],
                "status": "running_code",
                "note": "Two distinct humans. One action hash. Then the write.",
            },
            {
                "id": "bc.premium",
                "lane": "sor",
                "product": "Dynamics 365 Business Central Premium",
                "status": "sandbox_journal",
                "note": (
                    f"{evidence['environment']} · {evidence['bc_company']} · "
                    f"{evidence['action_class']}. Production blocked."
                ),
            },
            {
                "id": "sales.enterprise",
                "lane": "sor",
                "product": "Dynamics 365 Sales Enterprise",
                "status": "licensed_not_wired",
                "note": "License exists. No Dataverse instance. Twin only until G14.",
            },
            {
                "id": "teams.enterprise",
                "lane": "notify",
                "product": "Microsoft Teams Enterprise",
                "status": "licensed_not_wired",
                "note": "Effect notify. A chat is not a seat.",
            },
            {
                "id": "teams.premium",
                "lane": "notify",
                "product": "Microsoft Teams Premium",
                "status": "licensed_not_wired",
                "note": "Protected notify. A meeting is not a seat.",
            },
        ],
    }


def _opportunity() -> dict[str, Any]:
    prove = _sku_band("L1")
    keep = _sku_band("P-ADM")
    deepen = _sku_band("U-DUAL")
    return {
        "prove": prove["id"],
        "keep": keep["id"],
        "deepen": deepen["id"],
        "recognized_revenue": None,
        "named_customers": [],
        "signed_l1": 0,
        "attached": {"L1": 0, "P-ADM": 0, "U-DUAL": 0},
        "list": {"L1": prove, "P-ADM": keep, "U-DUAL": deepen},
        "year_one_list_if_all_three": {
            "min": prove["min"] + keep["min"] + deepen["min"],
            "max": prove["max"] + keep["max"] + deepen["max"],
            "note": (
                "Catalog list if one controller buys L1, then attaches P-ADM, "
                "then pays for U-DUAL. Not recognized revenue."
            ),
        },
        "note": "Pipeline math uses catalog list prices. It is not recognized revenue.",
    }


def public_status() -> dict[str, Any]:
    cat = load_catalog()
    evidence = dict(cat["sandbox_evidence"])
    site = cat["programs"]["website"]
    tools = agent_tools_review()
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
        "launch_ready": False,
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
        "fabric": _fabric(cat, evidence, site),
        "e7_cloudflare": catalog_edge(),
        "engineering": catalog_engineering(),
        "complements": _complements(cat),
        "agent_tools": {
            "admin_url": tools["admin_url"],
            "product": tools["product"],
            "wired": False,
            "live": False,
            "is_admit_plane": False,
            "cloud_agent_can_approve": False,
            "leave_available": [item["id"] for item in tools["leave_available"]],
            "block_until_dual": [item["id"] for item in tools["block_until_dual"]],
        },
        "opportunity": _opportunity(),
        "honest_missing": honest_missing(),
        "open_gaps": list(cat["open_gaps"]),
        "success_equation": cat["success_equation"],
        "commercial_equation": cat["equations"]["commercial"],
        "lab_pin": cat["equations"]["lab_pin"],
        "invited_second_human": {
            "name": cat["organization"]["contacts"]["invited"]["name"],
            "recorded": False,
            "email": None,
        },
    }
