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
    _validate_governance(catalog)
    _validate_client_org(catalog)
    _validate_investor(catalog)


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
    control = str(equations.get("control") or "").lower()
    if "client utilizes ai" not in control or "human" not in control:
        raise IntegrityError(
            "control equation is client utilizes AI \u00d7 human-control failsafe",
            reason_code="CATALOG_EQUATION",
        )
    cascade = str(equations.get("cascade") or "").lower()
    if "client" not in cascade or "institutes ainav" not in cascade:
        raise IntegrityError(
            "cascade equation is client's clients utilize AI \u00d7 client institutes AINav",
            reason_code="CATALOG_EQUATION",
        )
    umbrella = str(equations.get("umbrella") or "").lower()
    if "every client ai" not in umbrella or "one admit plane" not in umbrella:
        raise IntegrityError(
            "umbrella equation is every client AI \u00d7 one admit plane",
            reason_code="CATALOG_EQUATION",
        )
    plane = str(equations.get("plane") or "").lower()
    if "off-switch" not in plane or "rollback" not in plane:
        raise IntegrityError(
            "plane equation is failsafe \u00d7 off-switch \u00d7 reset \u00d7 rollback",
            reason_code="CATALOG_EQUATION",
        )
    org = str(equations.get("org") or "").lower()
    if "org chart" not in org or "sod" not in org:
        raise IntegrityError(
            "org equation is client org chart \u00d7 existing SOD \u00d7 one admit plane",
            reason_code="CATALOG_EQUATION",
        )
    insulation = str(equations.get("insulation") or "").lower()
    if "independence" not in insulation or "job c" not in insulation:
        raise IntegrityError(
            "insulation equation is independence \u00d7 Job C lockfile",
            reason_code="CATALOG_EQUATION",
        )
    for stem in ("lockfile", "gold", "catalog"):
        if stem not in insulation:
            raise IntegrityError(
                f"insulation equation must keep {stem}",
                reason_code="CATALOG_EQUATION",
            )
    investor = str(equations.get("investor") or "").lower()
    if "catalog list" not in investor or "zero booked" not in investor:
        raise IntegrityError(
            "investor equation is catalog list \u00d7 zero booked \u00d7 two-human close",
            reason_code="CATALOG_EQUATION",
        )
    if "two-human" not in investor and "two human" not in investor:
        raise IntegrityError(
            "investor equation must keep two-human close",
            reason_code="CATALOG_EQUATION",
        )


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
    for stem in (
        "teams vote",
        "copilot",
        "free u-dual",
        "live pin ok",
        "client ai as dual",
        "customer",
        "time-machine",
        "powers down",
        "mandated",
        "department",
        "org chart",
        "one title",
        "uncopyable",
        "patent",
        "cannot legally copy",
    ):
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


def _validate_investor(catalog: dict[str, Any]) -> None:
    body = catalog.get("investor")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing investor packet", reason_code="CATALOG_INVESTOR")
    if body.get("sku") is True:
        raise IntegrityError("investor packet is not a SKU", reason_code="CATALOG_SKU")
    if body.get("live") is True or body.get("live_pin_ok") is True:
        raise IntegrityError("investor packet cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    for flag in ("raise_claimed", "valuation_claimed", "forecast", "priced_round", "equity_offered"):
        if body.get(flag) is True:
            raise IntegrityError(f"investor packet cannot claim {flag}", reason_code="CATALOG_INVESTOR")
    if body.get("not_a_round") is not True:
        raise IntegrityError("investor packet is not a priced round", reason_code="CATALOG_INVESTOR")
    if "cynthia" not in str(body.get("audience") or "").lower():
        raise IntegrityError("investor audience is Cynthia Hodnett", reason_code="CATALOG_INVESTOR")
    one = str(body.get("one_liner") or "").lower()
    if "human" not in one or "write" not in one:
        raise IntegrityError("investor one-liner is the human write-gate", reason_code="CATALOG_INVESTOR")
    if "not a priced round" not in str(body.get("ask") or "").lower():
        raise IntegrityError("investor ask is not a priced round", reason_code="CATALOG_INVESTOR")
    refuse = " ".join(body.get("refuse") or []).lower()
    for stem in ("priced round", "valuation", "forecast", "named customer", "equity"):
        if stem not in refuse:
            raise IntegrityError(f"investor packet must refuse {stem}", reason_code="CATALOG_INVESTOR")
    print_body = body.get("print") or {}
    pages = int(print_body.get("pages") or 0)
    if pages < 4 or pages > 8:
        raise IntegrityError("investor print is a four-to-eight page letter packet", reason_code="CATALOG_INVESTOR")
    if body.get("include_upsells") is not True:
        raise IntegrityError("investor packet must include the upsell catalog", reason_code="CATALOG_INVESTOR")
    if "same three skus" not in str(body.get("upsell_note") or "").lower() and "not a fourth" not in str(body.get("upsell_note") or "").lower():
        raise IntegrityError("upsell note must keep packs off a fourth SKU", reason_code="CATALOG_INVESTOR")
    if "dear cynthia" not in str(body.get("letter_open") or "").lower():
        raise IntegrityError("investor letter opens to Cynthia", reason_code="CATALOG_INVESTOR")
    if "seat b" not in str(body.get("seat_b") or "").lower():
        raise IntegrityError("investor letter names seat B", reason_code="CATALOG_INVESTOR")
    if "stock" not in str(body.get("will_not_ask") or "").lower():
        raise IntegrityError("investor letter refuses stock", reason_code="CATALOG_INVESTOR")
    if "6,000" not in str(body.get("stack") or "") and "$6" not in str(body.get("stack") or ""):
        raise IntegrityError("investor stack must price the upsell desks", reason_code="CATALOG_INVESTOR")
    plane = str(body.get("control_plane") or "").lower()
    if "control plane" not in plane:
        raise IntegrityError("investor letter must name the control plane", reason_code="CATALOG_INVESTOR")
    if "not a patent" not in plane:
        raise IntegrityError("control-plane insulation is not a patent", reason_code="IP_CLAIM")
    if "uncopyable" not in plane:
        raise IntegrityError("control-plane insulation must say this is not uncopyable", reason_code="IP_CLAIM")
    if "independen" not in plane and "vendor" not in plane:
        raise IntegrityError("control-plane insulation must keep independence", reason_code="CATALOG_INVESTOR")


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
    if icp.get("utilizes_ai") is not True:
        raise IntegrityError("ICP utilizes AI; AINav is not that AI", reason_code="CATALOG_ICP")
    if "not ainav" not in str(icp.get("ai") or "").lower():
        raise IntegrityError("ICP AI is the client's, not AINav", reason_code="CATALOG_ICP")
    if icp.get("counterparties_utilize_ai") is not True:
        raise IntegrityError("ICP counterparties utilize AI", reason_code="CATALOG_ICP")
    if icp.get("do_not_invent_counterparty_names") is not True:
        raise IntegrityError("do not invent counterparty names", reason_code="ICP_NAMED")
    if "institutes" not in str(icp.get("institutes_ainav") or "").lower():
        raise IntegrityError("ICP client institutes AINav", reason_code="CATALOG_ICP")
    if icp.get("sits_over_client_ai") is not True:
        raise IntegrityError("ICP plane sits over client AI", reason_code="CATALOG_ICP")
    needed = {"owner", "board", "examiner"}
    have = {str(item).lower() for item in icp.get("must_have_for") or []}
    if not needed <= have:
        raise IntegrityError("ICP must-have is owner, board, examiner", reason_code="CATALOG_ICP")
    if icp.get("org_chart") is not True:
        raise IntegrityError("ICP maps the client org chart", reason_code="CATALOG_ICP")
    if icp.get("do_not_invent_department_heads") is not True:
        raise IntegrityError("do not invent department heads", reason_code="ICP_NAMED")
    if icp.get("independent_of_microsoft") is not True:
        raise IntegrityError("ICP plane is independent of Microsoft", reason_code="CATALOG_ICP")


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


def _validate_governance(catalog: dict[str, Any]) -> None:
    body = catalog.get("governance")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing governance doctrine", reason_code="CATALOG_GOVERNANCE")
    if body.get("sku") is True:
        raise IntegrityError("governance is not a SKU", reason_code="CATALOG_SKU")
    if body.get("certified") is True or body.get("replaces_counsel") is True:
        raise IntegrityError("do not claim certification or replace counsel", reason_code="CATALOG_GOVERNANCE")
    if body.get("live") is True or body.get("live_pin_ok") is True:
        raise IntegrityError("governance cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    fail = body.get("failsafe") or {}
    separate = " ".join(fail.get("separate_from") or []).lower().replace("_", " ").replace(".", " ")
    for stem in ("client ai", "copilot", "cloud agent", "agent 365"):
        if stem not in separate:
            raise IntegrityError(
                f"failsafe must stay separate from {stem}",
                reason_code="CATALOG_GOVERNANCE",
            )
    thesis = str(body.get("thesis") or "").lower()
    if "two" not in thesis and "dual" not in thesis:
        raise IntegrityError("governance thesis must keep dual humans", reason_code="CATALOG_GOVERNANCE")
    if "utilizes" not in thesis or "control" not in thesis:
        raise IntegrityError(
            "governance thesis is client utilizes AI, humans control",
            reason_code="CATALOG_GOVERNANCE",
        )
    if fail.get("client_utilizes_ai") is not True or fail.get("human_control") is not True:
        raise IntegrityError("failsafe is human control of client-utilized AI", reason_code="CATALOG_GOVERNANCE")
    if fail.get("ainav_is_client_ai") is True:
        raise IntegrityError("AINav is not the client's AI", reason_code="CATALOG_GOVERNANCE")
    maps = {item.get("id") for item in body.get("maps") or []}
    if not {"nist.ai_rmf", "eu.ai_act", "iso.42001", "sox.icfr"} <= maps:
        raise IntegrityError("governance must map NIST, EU AI Act, ISO 42001, and SOX", reason_code="CATALOG_GOVERNANCE")
    if any(item.get("claimed") is True for item in body.get("maps") or []):
        raise IntegrityError("governance maps cannot claim certification", reason_code="CATALOG_GOVERNANCE")
    refuse = " ".join(body.get("refuse") or []).lower()
    for stem in ("eu ai act certified", "nist certified", "replaces counsel", "client ai as dual"):
        if stem not in refuse:
            raise IntegrityError(f"governance must refuse {stem}", reason_code="CATALOG_GOVERNANCE")
    if not body.get("risks"):
        raise IntegrityError("governance must name non-compliance risks", reason_code="CATALOG_GOVERNANCE")
    cascade = body.get("cascade") or {}
    if cascade.get("counterparties_utilize_ai") is not True:
        raise IntegrityError("cascade counterparties utilize AI", reason_code="CATALOG_GOVERNANCE")
    if cascade.get("client_institutes_ainav") is not True:
        raise IntegrityError("the client institutes AINav", reason_code="CATALOG_GOVERNANCE")
    if cascade.get("do_not_invent_names") is not True or cascade.get("buyer_is_the_client") is not True:
        raise IntegrityError("cascade buyer is the client; do not invent names", reason_code="ICP_NAMED")
    records = body.get("records") or {}
    first = records.get("first") or {}
    second = records.get("second") or {}
    if records.get("sku") is True or records.get("certified") is True:
        raise IntegrityError("records are not a SKU or certificate", reason_code="CATALOG_GOVERNANCE")
    if "sor" not in str(first.get("what") or "").lower():
        raise IntegrityError("first record is the SoR write", reason_code="CATALOG_GOVERNANCE")
    if "decisionrecord" not in str(second.get("what") or "").lower().replace(" ", ""):
        raise IntegrityError("second record is the DecisionRecord", reason_code="CATALOG_GOVERNANCE")
    if "counterparty ai" not in separate:
        raise IntegrityError("failsafe must stay separate from counterparty AI", reason_code="CATALOG_GOVERNANCE")
    plane_body = body.get("plane") or {}
    if plane_body.get("sits_over_client_ai") is not True or plane_body.get("is_the_clients_ai") is True:
        raise IntegrityError("plane sits over client AI and is not that AI", reason_code="CATALOG_GOVERNANCE")
    if plane_body.get("sku") is True:
        raise IntegrityError("the control plane is not a fourth SKU", reason_code="CATALOG_SKU")
    switch = plane_body.get("off_switch") or {}
    if "fail-closed" not in str(switch.get("does") or "").lower().replace(" ", "-") and "fail-closed" not in str(switch.get("does") or "").lower():
        raise IntegrityError("off switch is fail-closed", reason_code="CATALOG_GOVERNANCE")
    if "power" not in str(switch.get("does_not") or "").lower():
        raise IntegrityError("off switch does not power down Copilot", reason_code="CATALOG_GOVERNANCE")
    rollback = plane_body.get("rollback") or {}
    if "compensating" not in str(rollback.get("does") or "").lower():
        raise IntegrityError("rollback is a compensating write", reason_code="CATALOG_GOVERNANCE")
    if "time machine" not in str(rollback.get("does_not") or "").lower():
        raise IntegrityError("rollback is not a time machine", reason_code="CATALOG_GOVERNANCE")
    must = body.get("must_have") or {}
    if must.get("sku") is True or must.get("mandated") is True or must.get("certified") is True:
        raise IntegrityError("must-have is not a SKU, mandate, or certificate", reason_code="CATALOG_GOVERNANCE")
    audience = must.get("for") or {}
    for who in ("owner", "board", "examiner"):
        if not str(audience.get(who) or "").strip():
            raise IntegrityError(f"must-have must name the {who}", reason_code="CATALOG_GOVERNANCE")
    for stem in ("time-machine rollback", "powers down copilot", "mandated by sec"):
        if stem not in refuse:
            raise IntegrityError(f"governance must refuse {stem}", reason_code="CATALOG_GOVERNANCE")
    for stem in ("department ai as dual", "replaces the org chart"):
        if stem not in refuse:
            raise IntegrityError(f"governance must refuse {stem}", reason_code="CATALOG_GOVERNANCE")


def _validate_client_org(catalog: dict[str, Any]) -> None:
    from ainav.client_org import ALLOWED_ROLES, REQUIRED_CLIENT_DEPTS

    body = catalog.get("client_org")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing client org chart", reason_code="CATALOG_ORG")
    if body.get("sku") is True:
        raise IntegrityError("client org is not a SKU", reason_code="CATALOG_SKU")
    if body.get("replaces_org_chart") is True:
        raise IntegrityError("AINav does not replace the org chart", reason_code="CATALOG_ORG")
    if body.get("live") is True or body.get("live_pin_ok") is True:
        raise IntegrityError("client org cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if body.get("named_customers"):
        raise IntegrityError("do not invent a named customer", reason_code="ICP_NAMED")
    if body.get("do_not_invent_names") is not True or body.get("do_not_invent_department_heads") is not True:
        raise IntegrityError("do not invent department heads", reason_code="ICP_NAMED")
    seats = body.get("seats") or {}
    if (seats.get("seat_a") or {}).get("role") != "treasury_approver":
        raise IntegrityError("client seat A is treasury_approver", reason_code="CATALOG_ORG")
    if (seats.get("seat_b") or {}).get("role") != "treasury_controller":
        raise IntegrityError("client seat B is treasury_controller", reason_code="CATALOG_ORG")
    departments = body.get("departments") or []
    ids = [item.get("id") for item in departments]
    if ids != list(REQUIRED_CLIENT_DEPTS):
        raise IntegrityError("client org departments must be the template set", reason_code="CATALOG_ORG")
    admit = 0
    for item in departments:
        if item.get("role") not in ALLOWED_ROLES:
            raise IntegrityError(f"unknown client org role {item.get('role')!r}", reason_code="CATALOG_ORG")
        if item.get("department_ai_is_seat") is True:
            raise IntegrityError("department AI is not a seat", reason_code="CATALOG_ORG")
        if item.get("named_head"):
            raise IntegrityError("do not invent a department head", reason_code="ICP_NAMED")
        if item.get("sku") is True:
            raise IntegrityError("client department is not a SKU", reason_code="CATALOG_SKU")
        if item.get("role") == "admit":
            admit += 1
    if admit < 2:
        raise IntegrityError("client org needs two admit departments", reason_code="CATALOG_ORG")
    thesis = str(body.get("thesis") or "").lower()
    if "org chart" not in thesis or "not a seat" not in thesis:
        raise IntegrityError("client org thesis must keep the chart and refuse department AI as a seat", reason_code="CATALOG_ORG")


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
