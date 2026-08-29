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
        if svc.get("attaches_udual") is True:
            raise IntegrityError("fee-for-service cannot attach U-DUAL", reason_code="UDUAL_NOT_FREE")
        if svc.get("billable") is True and svc.get("requires_l1") is not True:
            raise IntegrityError("billable FFS requires L1", reason_code="FFS_SCOPE")
    from ainav.business import validate_business
    from ainav.ip import validate_ip_doctrine
    from ainav.microsoft.agent_tools import validate_agent_tools
    from ainav.microsoft.connections import validate_connections
    from ainav.programs import validate_programs

    validate_ip_doctrine(catalog)
    validate_programs(catalog)
    validate_connections(catalog)
    validate_agent_tools(catalog)
    validate_business(catalog)
    from ainav.delivery import validate_delivery

    validate_delivery(catalog)
    _validate_operating(catalog)
    from ainav.org import validate_organization

    validate_organization(catalog)
    _validate_proof_day(catalog)
    _validate_next_pin(catalog)
    _validate_sandbox_evidence(catalog)
    _validate_buyer(catalog)
    _validate_icp(catalog)
    _validate_acceptance_kit(catalog)
    _validate_counsel(catalog)
    _validate_owner_gates(catalog)
    _validate_finance(catalog)
    _validate_expert_review(catalog)
    _validate_upsells(catalog)
    _validate_repositories(catalog)


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
    if body.get("owner_principal") == body.get("operator"):
        raise IntegrityError("owner cannot be the operator", reason_code="CATALOG_OPERATING")
    equations = catalog.get("equations") or {}
    if "named dual seats" not in str(equations.get("commercial") or ""):
        raise IntegrityError("commercial equation must name dual seats", reason_code="CATALOG_EQUATION")
    if equations.get("lab_pin") != "LIVE_PIN_OK":
        raise IntegrityError("lab pin stays LIVE_PIN_OK", reason_code="CATALOG_EQUATION")


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


def _validate_sandbox_evidence(catalog: dict[str, Any]) -> None:
    body = catalog.get("sandbox_evidence")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing sandbox evidence", reason_code="CATALOG_SANDBOX")
    if body.get("action_class") != "bc.general_journal.post":
        raise IntegrityError("sandbox evidence is the L1 journal", reason_code="CATALOG_SANDBOX")
    if body.get("environment") != "sandbox":
        raise IntegrityError("sandbox evidence stays on sandbox", reason_code="CATALOG_SANDBOX")
    if body.get("production") is True or body.get("live") is True or body.get("live_pin_ok") is True:
        raise IntegrityError("sandbox evidence cannot claim production or live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if body.get("signed_l1") is True:
        raise IntegrityError("sandbox evidence cannot close signed L1", reason_code="SIGNED_L1_OPEN")


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


def _validate_counsel(catalog: dict[str, Any]) -> None:
    body = catalog.get("counsel")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing counsel pack", reason_code="G12_OPEN")
    if body.get("signed") is True or body.get("g12_open") is not True or body.get("g13_open") is not True:
        raise IntegrityError("counsel pack stays unsigned; G12/G13 stay open", reason_code="G12_OPEN")
    order = body.get("order_form") or {}
    msa = body.get("msa") or {}
    if order.get("unsigned") is not True or msa.get("unsigned") is not True:
        raise IntegrityError("order form and MSA stay unsigned", reason_code="G12_OPEN")
    rules = " ".join(order.get("rules") or [])
    if "U-DUAL is never free" not in rules:
        raise IntegrityError("order form must refuse free U-DUAL", reason_code="UDUAL_NOT_FREE")
    if "not SKUs" not in rules:
        raise IntegrityError("order form must refuse pack SKUs", reason_code="CATALOG_SKU")


def _validate_finance(catalog: dict[str, Any]) -> None:
    body = catalog.get("financial_model")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing financial model", reason_code="CATALOG_FINANCE")
    if body.get("recognized_revenue") not in (0, False):
        raise IntegrityError("do not invent recognized revenue", reason_code="CATALOG_FINANCE")
    if body.get("signed_l1") not in (0, False):
        raise IntegrityError("signed L1 is still open", reason_code="SIGNED_L1_OPEN")
    if body.get("named_customers") not in (0, False):
        raise IntegrityError("do not invent named customers", reason_code="ICP_NAMED")
    if body.get("billing_provider") is True:
        raise IntegrityError("no billing provider is claimed", reason_code="CATALOG_FINANCE")
    models = body.get("pricing_models") or []
    ids = {item.get("id") for item in models}
    if not {"L1", "P-ADM", "U-DUAL", "ffs", "pack_attach"} <= ids:
        raise IntegrityError(
            "financial model must price three SKUs, FFS, and pack attach",
            reason_code="CATALOG_FINANCE",
        )
    pack_attach = next(item for item in models if item.get("id") == "pack_attach")
    if pack_attach.get("sku") is True or pack_attach.get("attaches_udual") is True:
        raise IntegrityError("pack attach cannot be a SKU or attach U-DUAL", reason_code="CATALOG_SKU")


def _validate_expert_review(catalog: dict[str, Any]) -> None:
    body = catalog.get("expert_review")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing expert review", reason_code="CATALOG_REVIEW")
    upgrades = body.get("upgrades") or []
    if not 10 <= len(upgrades) <= 15:
        raise IntegrityError("expert review needs 10–15 upgrades", reason_code="CATALOG_REVIEW")
    if not body.get("working_well") or not body.get("improve"):
        raise IntegrityError("expert review needs working_well and improve", reason_code="CATALOG_REVIEW")
    if any(item.get("marks_live_pin") is True for item in upgrades):
        raise IntegrityError("upgrades cannot mark LIVE_PIN_OK", reason_code="LIVE_PIN_NOT_CLAIMED")


def _validate_owner_gates(catalog: dict[str, Any]) -> None:
    gates = catalog.get("owner_gates")
    if not isinstance(gates, list) or len(gates) < 6:
        raise IntegrityError("catalog missing owner gates", reason_code="CATALOG_ORG")
    for item in gates:
        if not item.get("do") or not item.get("url"):
            raise IntegrityError("owner gate needs a step and a link", reason_code="CATALOG_ORG")


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


def _validate_upsells(catalog: dict[str, Any]) -> None:
    wedges = [
        m
        for m in catalog.get("modules", [])
        if m.get("kind") == "action" and m.get("wedge") is True
    ]
    l1_wedges = [m["id"] for m in wedges if m.get("sku") == "L1"]
    if l1_wedges != ["bc.general_journal.post"]:
        raise IntegrityError("L1 wedge stays the general journal", reason_code="CATALOG_WEDGE")
    udual_wedges = {m["id"] for m in wedges if m.get("sku") == "U-DUAL"}
    if udual_wedges != {"d365.quote.discount_override", "d365.order.submit"}:
        raise IntegrityError("U-DUAL wedges stay quote and order", reason_code="CATALOG_WEDGE")
    for pack in catalog.get("industry_packs", []):
        if not pack.get("runbook"):
            raise IntegrityError(f"{pack.get('id')} needs a runbook", reason_code="CATALOG_PACK")
        if pack.get("sku") is True:
            raise IntegrityError("industry pack is not a SKU", reason_code="CATALOG_SKU")
        attach = pack.get("attach_usd") or {}
        lo = int(attach.get("min") or 0)
        hi = int(attach.get("max") or 0)
        if pack.get("included_in_sku") is True:
            if lo != 0 or hi != 0:
                raise IntegrityError(
                    f"{pack.get('id')} is included and cannot carry an attach price",
                    reason_code="CATALOG_PACK",
                )
        elif pack.get("ala_carte") is True:
            if lo < 1 or hi < lo:
                raise IntegrityError(
                    f"{pack.get('id')} needs a catalog-list attach band",
                    reason_code="CATALOG_PACK",
                )
    for lib in catalog.get("libraries", []):
        if not lib.get("note"):
            raise IntegrityError(f"{lib.get('id')} needs a note", reason_code="CATALOG_LIB")
        if lib.get("sku") is True:
            raise IntegrityError("library is not a SKU", reason_code="CATALOG_SKU")
    referenced = {
        mid
        for item in list(catalog.get("industry_packs") or []) + list(catalog.get("libraries") or [])
        for mid in item.get("modules") or []
    }
    for module in catalog.get("modules", []):
        if module.get("upsell") is True and module.get("wedge") is True:
            raise IntegrityError("a wedge cannot be an upsell", reason_code="CATALOG_WEDGE")
        if module.get("upsell") is True and module["id"] not in referenced:
            raise IntegrityError(
                f"upsell {module['id']} must be seated by a pack or library",
                reason_code="CATALOG_PACK",
            )


def _validate_repositories(catalog: dict[str, Any]) -> None:
    repos = catalog.get("repositories") or []
    ids = {item.get("id") for item in repos}
    if not {"repo.agent_gov", "repo.catalog", "repo.institute"} <= ids:
        raise IntegrityError("core repositories are required", reason_code="CATALOG_REPO")
    for item in repos:
        if item.get("id") in ALLOWED_SKUS or item.get("sku"):
            raise IntegrityError("repository is not a SKU", reason_code="CATALOG_SKU")
        if item.get("live") is True:
            raise IntegrityError("repository cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")


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


def wedge_action_classes(sku_id: str) -> frozenset[str]:
    return frozenset(
        m["id"]
        for m in modules_for(sku_id)
        if m.get("kind") == "action" and m.get("wedge") is True
    )


def module_by_id(module_id: str) -> dict[str, Any]:
    for item in load_catalog().get("modules", []):
        if item["id"] == module_id:
            return dict(item)
    raise IntegrityError(f"unknown module {module_id}", reason_code="CATALOG_PACK")


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


def attach_band(item: dict[str, Any]) -> tuple[int, int]:
    usd = item.get("attach_usd") or {}
    return int(usd.get("min") or 0), int(usd.get("max") or 0)


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
