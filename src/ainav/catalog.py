"""Commercial catalog. Source of truth for SKUs. No invented products."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any

from agent_gov.errors import IntegrityError

ALLOWED_SKUS = frozenset({"L1", "P-ADM", "U-DUAL"})


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    raw = files("ainav.data").joinpath("catalog.json").read_text(encoding="utf-8")
    catalog = json.loads(raw)
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog: dict[str, Any]) -> None:
    if catalog.get("schema_version") != "ainav.catalog.v1":
        raise IntegrityError("unsupported catalog schema", reason_code="CATALOG_SCHEMA")
    if catalog.get("entity", {}).get("job") != "C":
        raise IntegrityError("catalog job must be C", reason_code="CATALOG_JOB")
    skus = {item["id"] for item in catalog.get("skus", [])}
    if skus != ALLOWED_SKUS:
        raise IntegrityError(
            f"catalog SKUs must be exactly {sorted(ALLOWED_SKUS)}",
            reason_code="CATALOG_SKU",
        )
    for sku_item in catalog["skus"]:
        if sku_item["id"] == "U-DUAL":
            never = set(sku_item.get("never_free_with") or [])
            if "P-ADM" not in never:
                raise IntegrityError("U-DUAL must never be free with P-ADM")
    module_ids: set[str] = set()
    for module in catalog.get("modules", []):
        if module.get("sku") not in ALLOWED_SKUS:
            raise IntegrityError(f"module {module.get('id')} has invented SKU")
        module_ids.add(module["id"])
    _validate_named_sets(catalog.get("industry_packs", []), module_ids, "industry pack")
    _validate_named_sets(catalog.get("libraries", []), module_ids, "library")
    for svc in catalog.get("fee_for_service", []):
        if svc.get("id") in ALLOWED_SKUS or svc.get("sku"):
            raise IntegrityError("fee-for-service is not a SKU", reason_code="CATALOG_SKU")
        included = svc.get("included_in")
        if included and included not in ALLOWED_SKUS:
            raise IntegrityError(
                f"fee-for-service {svc.get('id')} included_in invented SKU",
                reason_code="CATALOG_SKU",
            )
    from ainav.business import validate_business
    from ainav.ip import validate_ip_doctrine
    from ainav.microsoft.connections import validate_connections
    from ainav.programs import validate_programs

    validate_ip_doctrine(catalog)
    validate_programs(catalog)
    validate_connections(catalog)
    validate_business(catalog)
    from ainav.delivery import validate_delivery

    validate_delivery(catalog)
    _validate_operating(catalog)
    from ainav.org import validate_organization

    validate_organization(catalog)
    _validate_proof_day(catalog)
    _validate_next_pin(catalog)
    _validate_buyer(catalog)
    _validate_icp(catalog)
    _validate_acceptance_kit(catalog)


def _validate_operating(catalog: dict[str, Any]) -> None:
    body = catalog.get("operating")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing operating model", reason_code="CATALOG_OPERATING")
    if body.get("legal_entity") != catalog.get("entity", {}).get("legal"):
        raise IntegrityError("operating legal_entity must match entity.legal", reason_code="CATALOG_OPERATING")
    if body.get("sole_owner") is not True:
        raise IntegrityError("operating records the sole owner", reason_code="CATALOG_OPERATING")
    if body.get("operator_is_seat") is True or body.get("agent_is_not_dual") is not True:
        raise IntegrityError("the operator cannot be a dual seat", reason_code="CATALOG_OPERATING")
    if not str(body.get("owner_principal") or "").strip():
        raise IntegrityError("operating owner_principal is required", reason_code="CATALOG_OPERATING")


def _validate_proof_day(catalog: dict[str, Any]) -> None:
    body = catalog.get("proof_day")
    if not isinstance(body, dict) or body.get("requires_sku") != "L1":
        raise IntegrityError("proof day requires L1", reason_code="CATALOG_PROOF_DAY")
    if body.get("signed_l1") is True or body.get("live") is True:
        raise IntegrityError("proof day cannot close G13 or claim live", reason_code="SIGNED_L1_OPEN")
    if int(body.get("minutes") or 0) != 90:
        raise IntegrityError("proof day is ninety minutes", reason_code="CATALOG_PROOF_DAY")
    if body.get("action_class") != "bc.general_journal.post":
        raise IntegrityError("proof day is the L1 journal", reason_code="CATALOG_PROOF_DAY")
    if body.get("sor_target") != "bc.sandbox":
        raise IntegrityError("proof day stays on the BC twin", reason_code="CATALOG_PROOF_DAY")


def _validate_next_pin(catalog: dict[str, Any]) -> None:
    body = catalog.get("next_pin")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing next_pin", reason_code="CATALOG_NEXT_PIN")
    if body.get("id") != "bc.microsoft.sandbox":
        raise IntegrityError("next pin is bc.microsoft.sandbox", reason_code="CATALOG_NEXT_PIN")
    if body.get("connection") != "bc.premium":
        raise IntegrityError("next pin binds bc.premium", reason_code="CATALOG_NEXT_PIN")
    if body.get("live") is True or body.get("production") is True or body.get("sent") is True:
        raise IntegrityError("next pin cannot claim live, production, or sent", reason_code="LIVE_PIN_NOT_CLAIMED")
    if body.get("live_pin_ok") is True:
        raise IntegrityError("next pin cannot close LIVE_PIN_OK", reason_code="LIVE_PIN_NOT_CLAIMED")
    if body.get("from") != "bc.sandbox" or body.get("to") != "bc.microsoft.sandbox":
        raise IntegrityError("next pin is twin → microsoft sandbox", reason_code="CATALOG_NEXT_PIN")


def _validate_buyer(catalog: dict[str, Any]) -> None:
    body = catalog.get("buyer")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing buyer page", reason_code="CATALOG_BUYER")
    if body.get("contact_email") or body.get("mailto"):
        raise IntegrityError("do not invent a contact inbox", reason_code="BUYER_INBOX")
    write = body.get("write_that_must_not_happen") or ""
    if "journal" not in str(write).lower():
        raise IntegrityError("buyer page must name the journal write", reason_code="CATALOG_BUYER")
    seats = set(body.get("seats") or [])
    kit = catalog.get("acceptance_kit", {}).get("seats") or {}
    expected = {kit.get("seat_a", {}).get("role"), kit.get("seat_b", {}).get("role")}
    if seats != expected:
        raise IntegrityError("buyer seats must be the catalog treasury pair", reason_code="CATALOG_BUYER")
    prices = " ".join(body.get("prices") or [])
    for sku_id in ("L1", "P-ADM", "U-DUAL"):
        if sku_id not in prices:
            raise IntegrityError("buyer page must list the three SKUs", reason_code="CATALOG_BUYER")
    refuse = " ".join(body.get("refuse") or []).lower().replace("_", " ")
    for stem in ("teams vote", "copilot", "free u-dual", "live pin ok"):
        if stem not in refuse:
            raise IntegrityError(f"buyer page must refuse {stem}", reason_code="CATALOG_BUYER")


def _validate_icp(catalog: dict[str, Any]) -> None:
    icp = catalog.get("icp")
    if not isinstance(icp, dict):
        raise IntegrityError("catalog missing icp profile", reason_code="CATALOG_ICP")
    if icp.get("named_customers"):
        raise IntegrityError("do not invent a named customer", reason_code="ICP_NAMED")
    if icp.get("do_not_invent_names") is not True:
        raise IntegrityError("ICP must refuse invented names", reason_code="ICP_NAMED")
    if "Business Central" not in str(icp.get("erp") or ""):
        raise IntegrityError("ICP erp is Business Central Premium", reason_code="CATALOG_ICP")
    if "Entra" not in str(icp.get("identity") or ""):
        raise IntegrityError("ICP identity is Entra ID", reason_code="CATALOG_ICP")


def _validate_acceptance_kit(catalog: dict[str, Any]) -> None:
    kit = catalog.get("acceptance_kit")
    if not isinstance(kit, dict) or kit.get("requires_sku") != "L1":
        raise IntegrityError("acceptance kit must require L1", reason_code="CATALOG_KIT")
    cases = kit.get("cases") or []
    if not cases:
        raise IntegrityError("acceptance kit needs at least one case", reason_code="CATALOG_KIT")
    l1 = {
        m["id"]
        for m in catalog.get("modules", [])
        if m.get("sku") == "L1" and m.get("kind") == "action"
    }
    for case in cases:
        action = case.get("action") or {}
        if action.get("action_class") not in l1:
            raise IntegrityError("kit case must be the L1 action", reason_code="CATALOG_KIT")
        if action.get("sor_target") != "bc.sandbox":
            raise IntegrityError("kit case must stay on the BC twin", reason_code="CATALOG_KIT")


def _validate_named_sets(items: list[dict[str, Any]], module_ids: set[str], kind: str) -> None:
    for item in items:
        ident = item.get("id")
        if ident in ALLOWED_SKUS:
            raise IntegrityError(f"{kind} cannot be a SKU", reason_code="CATALOG_SKU")
        required = item.get("requires_sku")
        if required not in ALLOWED_SKUS:
            raise IntegrityError(f"{kind} {ident} has invented SKU", reason_code="CATALOG_SKU")
        for mid in item.get("modules", []):
            if mid not in module_ids:
                raise IntegrityError(f"{kind} {ident} references unknown module {mid}")


def sku(sku_id: str) -> dict[str, Any]:
    for item in load_catalog()["skus"]:
        if item["id"] == sku_id:
            return dict(item)
    raise IntegrityError(f"unknown SKU {sku_id}", reason_code="CATALOG_SKU")


def modules_for(sku_id: str) -> list[dict[str, Any]]:
    sku(sku_id)
    return [dict(m) for m in load_catalog()["modules"] if m["sku"] == sku_id]


def action_classes_for(sku_id: str) -> frozenset[str]:
    return frozenset(m["id"] for m in modules_for(sku_id) if m.get("kind") == "action")


def l1_action_classes() -> frozenset[str]:
    return action_classes_for("L1")


def udual_action_classes() -> frozenset[str]:
    return action_classes_for("U-DUAL")


def industry_pack(pack_id: str) -> dict[str, Any]:
    for item in load_catalog().get("industry_packs", []):
        if item["id"] == pack_id:
            return dict(item)
    raise IntegrityError(f"unknown industry pack {pack_id}", reason_code="CATALOG_PACK")


def library(library_id: str) -> dict[str, Any]:
    for item in load_catalog().get("libraries", []):
        if item["id"] == library_id:
            return dict(item)
    raise IntegrityError(f"unknown library {library_id}", reason_code="CATALOG_LIB")


def fee_for_service(service_id: str) -> dict[str, Any]:
    for item in load_catalog().get("fee_for_service", []):
        if item["id"] == service_id:
            return dict(item)
    raise IntegrityError(f"unknown fee-for-service {service_id}", reason_code="CATALOG_FFS")


def operations() -> dict[str, Any]:
    return dict(load_catalog()["operations"])


def acceptance_kit() -> dict[str, Any]:
    return dict(load_catalog()["acceptance_kit"])


def honest_missing() -> list[str]:
    return list(load_catalog().get("honest_missing") or [])


def l1_incident_copy() -> str:
    return str(load_catalog()["l1_incident_copy"])


def microsoft_stack() -> dict[str, Any]:
    return dict(load_catalog()["microsoft_stack"])
