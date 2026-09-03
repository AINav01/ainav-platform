"""Commercial catalog. Source of truth for SKUs. No invented products."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
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
    _validate_mailbox_law(catalog)
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
    _validate_plane_interface(catalog)
    _validate_investor(catalog)
    _validate_microsoft_edge(catalog)
    _validate_engineering(catalog)
    _validate_honest_missing(catalog)


def _validate_microsoft_edge(catalog: dict[str, Any]) -> None:
    edge = (catalog.get("microsoft_stack") or {}).get("edge")
    if not isinstance(edge, dict):
        raise IntegrityError("catalog missing Cloudflare edge", reason_code="CATALOG_EDGE")
    if edge.get("id") != "cloudflare.dns":
        raise IntegrityError("edge id is cloudflare.dns", reason_code="CATALOG_EDGE")
    if edge.get("product") != "Cloudflare":
        raise IntegrityError("edge product is Cloudflare", reason_code="CATALOG_EDGE")
    if edge.get("role") != "dns_edge":
        raise IntegrityError("edge role is dns_edge", reason_code="CATALOG_EDGE")
    if edge.get("dashboard_url") != "https://dash.cloudflare.com":
        raise IntegrityError("edge dashboard is dash.cloudflare.com", reason_code="CATALOG_EDGE")
    if str(edge.get("apex") or "") != "ainav.institute":
        raise IntegrityError("edge apex is ainav.institute", reason_code="CATALOG_EDGE")
    for flag in (
        "sku",
        "connection",
        "complement",
        "live",
        "live_pin_ok",
        "is_admit_plane",
    ):
        if edge.get(flag) is not False:
            raise IntegrityError(f"edge cannot claim {flag}", reason_code="CATALOG_EDGE")
    already = " ".join(str(item) for item in edge.get("already") or []).lower()
    for stem in ("nameserver", "mx", "spf", "entra", "autodiscover", "dkim", "dmarc"):
        if stem not in already:
            raise IntegrityError(f"edge already must include {stem}", reason_code="CATALOG_EDGE")
    missing_items = list(edge.get("missing") or [])
    missing = " ".join(str(item) for item in missing_items).lower()
    not_blob = " ".join(str(item) for item in edge.get("not") or []).lower()
    for stem in ("sku", "complement", "dual", "launch"):
        if stem not in not_blob:
            raise IntegrityError(f"edge not must include {stem}", reason_code="CATALOG_EDGE")
    note = str(edge.get("note") or "").lower()
    if "not the product" not in note:
        raise IntegrityError("edge note: Cloudflare is not the product", reason_code="CATALOG_EDGE")
    if "dns-only" not in note:
        raise IntegrityError("edge note: MX stays DNS-only", reason_code="CATALOG_EDGE")
    if "cannot edit" not in note:
        raise IntegrityError("edge note: Cloud Agent cannot edit Cloudflare", reason_code="CATALOG_EDGE")
    if "not institute launch" not in note:
        raise IntegrityError("edge note: not Institute launch", reason_code="CATALOG_EDGE")
    if str(edge.get("plan") or "") != "pro":
        raise IntegrityError("edge plan is Cloudflare Pro", reason_code="CATALOG_EDGE")
    if edge.get("plan_sku") is True:
        raise IntegrityError("Cloudflare Pro is not a SKU", reason_code="CATALOG_EDGE")
    if edge.get("from_this_plane") is True:
        raise IntegrityError("this plane cannot edit Cloudflare", reason_code="CATALOG_EDGE")
    activate = edge.get("activate") or {}
    if not isinstance(activate, dict) or activate.get("from_this_plane") is True:
        raise IntegrityError("Cloudflare Pro activate is owner-only", reason_code="CATALOG_EDGE")
    now_ids = [item.get("id") for item in activate.get("now") or []]
    for needed in ("ssl.full", "waf.managed", "perf.off", "dns.only"):
        if needed not in now_ids:
            raise IntegrityError(f"Pro activate now must include {needed}", reason_code="CATALOG_EDGE")
    wait_blob = " ".join(
        f"{item.get('id') or ''} {item.get('do') or ''}" for item in activate.get("wait") or []
    ).lower()
    if "launch" not in wait_blob or "asuid" not in wait_blob:
        raise IntegrityError("Pro activate wait keeps launch and asuid", reason_code="CATALOG_EDGE")
    now_blob = " ".join(
        f"{item.get('id') or ''} {item.get('do') or ''}" for item in activate.get("now") or []
    ).lower()
    for stem in ("flexible", "rocket loader", "dns only"):
        if stem not in now_blob:
            raise IntegrityError(f"Pro activate now must keep {stem}", reason_code="CATALOG_EDGE")
    if "pro" not in already:
        raise IntegrityError("edge already must record Cloudflare Pro", reason_code="CATALOG_EDGE")
    if "403" not in now_blob and "challenge" not in now_blob:
        raise IntegrityError("Pro activate must keep the apex challenge as holding", reason_code="CATALOG_EDGE")
    if "grey" not in now_blob and "outlook" not in now_blob:
        raise IntegrityError("Pro activate DNS must keep Outlook / grey cloud", reason_code="CATALOG_EDGE")
    if "reject" not in wait_blob:
        raise IntegrityError("Pro activate wait keeps DMARC reject", reason_code="CATALOG_EDGE")
    holding = edge.get("holding") or {}
    if not isinstance(holding, dict):
        raise IntegrityError("edge holding is empty Cloudflare Pages", reason_code="CATALOG_EDGE")
    if holding.get("id") != "cloudflare.pages":
        raise IntegrityError("edge holding is cloudflare.pages", reason_code="CATALOG_EDGE")
    if str(holding.get("origin") or "") != "ainav-institute.pages.dev":
        raise IntegrityError("edge holding origin is ainav-institute.pages.dev", reason_code="CATALOG_EDGE")
    for flag in ("host", "institute", "launch", "sku"):
        if holding.get(flag) is not False:
            raise IntegrityError(f"Pages cannot claim {flag}", reason_code="CATALOG_EDGE")
    hold_note = str(holding.get("note") or "").lower()
    if "not the institute" not in hold_note or "leave" not in hold_note:
        raise IntegrityError(
            "edge holding note: Pages is not the Institute; leave the zone",
            reason_code="CATALOG_EDGE",
        )
    if edge.get("full") is True:
        if missing_items:
            raise IntegrityError("edge cannot claim full while records are missing", reason_code="CATALOG_EDGE")
        for stem in ("sip", "lync"):
            if stem not in already:
                raise IntegrityError(f"edge full must record {stem}", reason_code="CATALOG_EDGE")
        if "dns is full" not in note:
            raise IntegrityError("edge note: DNS is full", reason_code="CATALOG_EDGE")
        _validate_edge_quality(edge)
    elif edge.get("full") is False:
        if "sip" not in missing:
            raise IntegrityError("edge missing must include Teams SIP", reason_code="CATALOG_EDGE")
        if "full is false" not in note:
            raise IntegrityError("edge note: full is false", reason_code="CATALOG_EDGE")
    else:
        raise IntegrityError("edge full must be boolean", reason_code="CATALOG_EDGE")
    _validate_stack_walk(catalog)
    _validate_graph_owner_consent(catalog)


def _validate_edge_quality(edge: dict[str, Any]) -> None:
    quality = edge.get("quality")
    if not isinstance(quality, dict):
        raise IntegrityError("edge quality is required", reason_code="CATALOG_EDGE")
    if quality.get("kind") != "ainav.edge.quality.v1":
        raise IntegrityError("edge quality kind is ainav.edge.quality.v1", reason_code="CATALOG_EDGE")
    for flag in (
        "sku",
        "live",
        "live_pin_ok",
        "from_this_plane",
        "apex_is_institute",
        "ssl_full_claimed",
        "rocket_loader_claimed",
    ):
        if quality.get(flag) is True:
            raise IntegrityError(f"edge quality cannot claim {flag}", reason_code="CATALOG_EDGE")
    if quality.get("e7_full") is not True:
        raise IntegrityError("edge quality records E7 DNS full", reason_code="CATALOG_EDGE")
    if str(quality.get("institute_host") or "") != "azure.swa":
        raise IntegrityError("edge quality host is Azure SWA", reason_code="CATALOG_EDGE")
    freshness = quality.get("host_freshness") or {}
    if not isinstance(freshness, dict):
        raise IntegrityError("edge quality host_freshness is required", reason_code="CATALOG_EDGE")
    if freshness.get("from_this_plane") is True:
        raise IntegrityError("edge quality cannot claim host republish from this plane", reason_code="CATALOG_EDGE")
    if freshness.get("republish_is_not_launch") is not True:
        raise IntegrityError("edge quality: republish is not launch", reason_code="CATALOG_EDGE")
    if freshness.get("published_host_is_swa") is not True or freshness.get("apex_is_not_the_host") is not True:
        raise IntegrityError("edge quality host is SWA, not the apex", reason_code="CATALOG_EDGE")
    owner_ssl = quality.get("owner_ssl") or {}
    if not isinstance(owner_ssl, dict):
        raise IntegrityError("edge quality owner_ssl is required", reason_code="CATALOG_EDGE")
    if owner_ssl.get("from_this_plane") is True or owner_ssl.get("live") is True or owner_ssl.get("live_pin_ok") is True:
        raise IntegrityError("owner_ssl cannot be claimed from this plane", reason_code="CATALOG_EDGE")
    if owner_ssl.get("automatic") is not True or str(owner_ssl.get("mode") or "") != "full_strict":
        raise IntegrityError("owner_ssl records Automatic Full (strict)", reason_code="CATALOG_EDGE")
    if owner_ssl.get("visitor_cert_is_not_proof") is not True:
        raise IntegrityError("owner_ssl: visitor cert is not proof", reason_code="CATALOG_EDGE")
    if owner_ssl.get("flexible") is True or owner_ssl.get("off") is True:
        raise IntegrityError("owner_ssl cannot be Flexible or Off", reason_code="CATALOG_EDGE")
    recorded = " ".join(str(item).lower() for item in quality.get("owner_recorded") or [])
    if "full (strict)" not in recorded or "owner" not in recorded:
        raise IntegrityError("edge quality owner_recorded must keep Full (strict)", reason_code="CATALOG_EDGE")
    verified = " ".join(str(item).lower() for item in quality.get("verified") or [])
    for stem in ("13/13", "403", "asuid", "301", "tls", "anycast"):
        if stem not in verified:
            raise IntegrityError(f"edge quality verified must keep {stem}", reason_code="CATALOG_EDGE")
    confirm = " ".join(str(item).lower() for item in quality.get("confirm") or [])
    for stem in ("flexible", "rocket", "grey"):
        if stem not in confirm:
            raise IntegrityError(f"edge quality confirm must keep {stem}", reason_code="CATALOG_EDGE")
    refuse = " ".join(str(item).lower() for item in quality.get("refuse") or [])
    for stem in ("asuid", "orange-cloud", "403"):
        if stem not in refuse:
            raise IntegrityError(f"edge quality refuse must keep {stem}", reason_code="CATALOG_EDGE")
    wait = " ".join(str(item).lower() for item in quality.get("wait") or [])
    if "reject" not in wait or "launch" not in wait:
        raise IntegrityError("edge quality wait keeps DMARC reject and launch", reason_code="CATALOG_EDGE")
    note = str(quality.get("note") or "").lower()
    if "not institute launch" not in note or "cannot edit" not in note:
        raise IntegrityError("edge quality note: not launch and cannot edit", reason_code="CATALOG_EDGE")


def _validate_stack_walk(catalog: dict[str, Any]) -> None:
    walk = (catalog.get("microsoft_stack") or {}).get("walk")
    if not isinstance(walk, dict):
        raise IntegrityError("catalog missing stack walk", reason_code="CATALOG_STACK")
    if walk.get("sku") is True or walk.get("is_admit_plane") is True:
        raise IntegrityError("stack walk is not a SKU or the admit plane", reason_code="CATALOG_STACK")
    if walk.get("live") is True or walk.get("live_pin_ok") is True:
        raise IntegrityError("stack walk cannot mark LIVE_PIN_OK", reason_code="LIVE_PIN_NOT_CLAIMED")
    thesis = str(walk.get("thesis") or "").lower()
    if "azure hosts" not in thesis or "ainav admits" not in thesis:
        raise IntegrityError("stack walk thesis is Azure hosts, AINav admits", reason_code="CATALOG_STACK")
    if "not a hop" not in thesis and "dns/edge" not in thesis:
        raise IntegrityError("stack walk must keep Cloudflare off the write hop", reason_code="CATALOG_STACK")
    path_ids = [item.get("id") for item in walk.get("path") or []]
    for needed in (
        "cloudflare.dns",
        "azure.host",
        "entra.id",
        "admit",
        "bc.premium",
        "sales.enterprise",
        "teams.enterprise",
        "graph.read",
        "agent_tools",
        "institute.launch",
    ):
        if needed not in path_ids:
            raise IntegrityError(f"stack walk path must include {needed}", reason_code="CATALOG_STACK")
    for item in (walk.get("path") or []) + (walk.get("complements") or []):
        url = str(item.get("url") or "")
        if not url.startswith("https://"):
            raise IntegrityError(f"stack walk {item.get('id')} needs an https link", reason_code="CATALOG_STACK")
        if item.get("live") is True or item.get("live_pin_ok") is True:
            raise IntegrityError("stack walk hops cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if "dash.cloudflare.com" not in str((walk.get("path") or [{}])[0].get("url") or ""):
        raise IntegrityError("first hop is the Cloudflare dashboard", reason_code="CATALOG_STACK")
    cannot = " ".join(str(item).lower() for item in walk.get("cannot") or [])
    for stem in ("create users", "graph", "cloudflare", "live_pin_ok"):
        if stem not in cannot:
            raise IntegrityError(f"stack walk cannot must keep {stem}", reason_code="CATALOG_STACK")
    share = next(
        (item for item in (catalog.get("connections") or {}).get("complements") or [] if item.get("id") == "sharepoint.kit"),
        {},
    )
    if share.get("write_from_this_plane") is not False:
        raise IntegrityError("SharePoint Write is not from this plane", reason_code="CATALOG_STACK")
    if str(share.get("consented_ask") or "") != "Sites.Read.All":
        raise IntegrityError("SharePoint consented ask is Sites.Read.All", reason_code="CATALOG_STACK")


def _validate_graph_owner_consent(catalog: dict[str, Any]) -> None:
    graph = (catalog.get("microsoft_stack") or {}).get("graph") or {}
    if not isinstance(graph, dict) or graph.get("kind") != "ainav.graph.owner_consent.v1":
        raise IntegrityError("graph owner consent kind is ainav.graph.owner_consent.v1", reason_code="CATALOG_STACK")
    if graph.get("from_this_plane") is True or graph.get("live") is True or graph.get("live_pin_ok") is True:
        raise IntegrityError("graph owner consent is not from this plane", reason_code="LIVE_PIN_NOT_CLAIMED")
    if graph.get("sku") is True:
        raise IntegrityError("graph owner consent is not a SKU", reason_code="CATALOG_STACK")
    if graph.get("graph_write_claimed") is True:
        raise IntegrityError("this plane cannot claim Graph Write", reason_code="CATALOG_STACK")
    remove = " ".join(str(item).lower() for item in graph.get("remove_before_grant") or [])
    for stem in ("speech", "service management", "key vault", "readwrite"):
        if stem not in remove:
            raise IntegrityError(f"graph remove_before_grant must keep {stem}", reason_code="CATALOG_STACK")
    reads = " ".join(str(item) for item in graph.get("four_reads") or [])
    for stem in (
        "Team.ReadBasic.All",
        "Sites.Read.All",
        "SecurityIncident.Read.All",
        "RoleEligibilitySchedule.Read.Directory",
    ):
        if stem not in reads:
            raise IntegrityError(f"graph four_reads must keep {stem}", reason_code="CATALOG_STACK")
    recorded = " ".join(str(item).lower() for item in graph.get("owner_recorded") or [])
    if "service principal" not in recorded or "speech" not in recorded:
        raise IntegrityError("graph owner_recorded must keep the leftover API failure", reason_code="CATALOG_STACK")
    note = str(graph.get("note") or "").lower()
    if "not live_pin_ok" not in note:
        raise IntegrityError("graph note: not LIVE_PIN_OK", reason_code="CATALOG_STACK")
    if "writes still" not in note or "not graph read closed" not in note:
        raise IntegrityError("graph note: Writes still Granted and not Graph Read closed", reason_code="CATALOG_STACK")


def _validate_engineering(catalog: dict[str, Any]) -> None:
    body = catalog.get("engineering")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing engineering", reason_code="CATALOG_ENGINEERING")
    if body.get("kind") != "ainav.engineering.v1":
        raise IntegrityError("engineering kind is ainav.engineering.v1", reason_code="CATALOG_ENGINEERING")
    for flag in (
        "sku",
        "connection",
        "complement",
        "live",
        "live_pin_ok",
        "launch",
        "is_admit_plane",
    ):
        if body.get(flag) is not False:
            raise IntegrityError(f"engineering cannot claim {flag}", reason_code="CATALOG_ENGINEERING")
    gold = body.get("gold_ci")
    if not isinstance(gold, dict):
        raise IntegrityError("engineering missing gold_ci", reason_code="CATALOG_ENGINEERING")
    if gold.get("id") != "github.actions.gold":
        raise IntegrityError("gold_ci id is github.actions.gold", reason_code="CATALOG_ENGINEERING")
    if gold.get("marks_live_pin") is not False:
        raise IntegrityError("gold_ci cannot mark LIVE_PIN_OK", reason_code="CATALOG_ENGINEERING")
    if gold.get("is_admit_plane") is not False:
        raise IntegrityError("gold_ci is not the admit plane", reason_code="CATALOG_ENGINEERING")
    if gold.get("coverage_floor") != 95:
        raise IntegrityError("gold coverage floor is 95", reason_code="CATALOG_ENGINEERING")
    pyproject = Path("pyproject.toml")
    if not pyproject.is_file():
        raise IntegrityError("pyproject.toml is missing", reason_code="CATALOG_ENGINEERING")
    if "fail_under = 95" not in pyproject.read_text(encoding="utf-8"):
        raise IntegrityError("pyproject fail_under must match gold floor 95", reason_code="CATALOG_ENGINEERING")
    if gold.get("command") != "make gold":
        raise IntegrityError("gold command is make gold", reason_code="CATALOG_ENGINEERING")
    note = str(gold.get("note") or "").lower()
    if "not live_pin_ok" not in note:
        raise IntegrityError("gold_ci note must refuse LIVE_PIN_OK", reason_code="CATALOG_ENGINEERING")
    closed = [str(item).lower() for item in body.get("closed_in_tree") or []]
    cannot = [str(item).lower() for item in body.get("cannot_close") or []]
    if not closed or not cannot:
        raise IntegrityError("engineering needs closed_in_tree and cannot_close", reason_code="CATALOG_ENGINEERING")
    if not any("live_pin" in item for item in cannot):
        raise IntegrityError("cannot_close must keep LIVE_PIN_OK", reason_code="CATALOG_ENGINEERING")
    if not any("cynthia" in item or "second unique" in item for item in cannot):
        raise IntegrityError("cannot_close must keep the second human", reason_code="CATALOG_ENGINEERING")
    if any("live_pin_ok" in item and "not" not in item for item in closed):
        raise IntegrityError("closed_in_tree cannot claim LIVE_PIN_OK", reason_code="CATALOG_ENGINEERING")
    law = str(body.get("note") or "").lower()
    if "not a sku" not in law:
        raise IntegrityError("engineering note: not a SKU", reason_code="CATALOG_ENGINEERING")
    if "not the admit plane" not in law:
        raise IntegrityError("engineering note: not the admit plane", reason_code="CATALOG_ENGINEERING")
    if gold.get("exists") is True:
        path = Path(str(gold.get("workflow") or ""))
        if path.as_posix() != ".github/workflows/gold.yml":
            raise IntegrityError("gold workflow path", reason_code="CATALOG_ENGINEERING")
        if not path.is_file():
            raise IntegrityError("gold workflow file missing", reason_code="CATALOG_ENGINEERING")
        text = path.read_text(encoding="utf-8").lower()
        if "make gold" not in text:
            raise IntegrityError("gold workflow must run make gold", reason_code="CATALOG_ENGINEERING")
        if "live_pin_ok" not in text:
            raise IntegrityError("gold workflow must refuse LIVE_PIN_OK", reason_code="CATALOG_ENGINEERING")
        if "green check" not in note:
            raise IntegrityError("gold_ci note: a green check is not LIVE_PIN_OK", reason_code="CATALOG_ENGINEERING")
        if not any("gold" in item or "github" in item or "workflow" in item for item in closed):
            raise IntegrityError("closed_in_tree must record gold CI", reason_code="CATALOG_ENGINEERING")
        if not re.search(r"actions/checkout@[0-9a-f]{40}", text):
            raise IntegrityError("gold workflow must pin checkout", reason_code="CATALOG_ENGINEERING")
        if not re.search(r"actions/setup-python@[0-9a-f]{40}", text):
            raise IntegrityError("gold workflow must pin setup-python", reason_code="CATALOG_ENGINEERING")
    elif gold.get("exists") is False:
        if "missing" not in note and "not in the tree" not in note:
            raise IntegrityError("missing gold_ci must say so", reason_code="CATALOG_ENGINEERING")
    else:
        raise IntegrityError("gold_ci.exists must be boolean", reason_code="CATALOG_ENGINEERING")
    if gold.get("observed_green") is True:
        if gold.get("exists") is not True:
            raise IntegrityError("cannot claim green without a workflow", reason_code="CATALOG_ENGINEERING")
        if "ran green" not in note:
            raise IntegrityError("observed_green note must say ran green", reason_code="CATALOG_ENGINEERING")
    elif gold.get("observed_green") is False:
        if "ran green" in note:
            raise IntegrityError("observed_green false cannot claim ran green", reason_code="CATALOG_ENGINEERING")
    else:
        raise IntegrityError("gold_ci.observed_green must be boolean", reason_code="CATALOG_ENGINEERING")
    _validate_catalog_shape(body)
    _validate_formal(body)


def _validate_catalog_shape(body: dict[str, Any]) -> None:
    shape = body.get("catalog_shape")
    if not isinstance(shape, dict):
        raise IntegrityError("engineering needs catalog_shape", reason_code="CATALOG_ENGINEERING")
    if shape.get("one_file") is not True or shape.get("do_not_split") is not True:
        raise IntegrityError("do not split catalog.json", reason_code="CATALOG_ENGINEERING")
    if str(shape.get("path") or "") != "src/ainav/data/catalog.json":
        raise IntegrityError("catalog_shape path is catalog.json", reason_code="CATALOG_ENGINEERING")
    extract = [str(item) for item in shape.get("extract") or []]
    if "src/ainav/data/action.schema.json" not in extract:
        raise IntegrityError("catalog_shape extracts action.schema.json", reason_code="CATALOG_ENGINEERING")
    schema = Path("src/ainav/data/action.schema.json")
    if not schema.is_file():
        raise IntegrityError("action.schema.json is missing", reason_code="CATALOG_ENGINEERING")


def _validate_formal(body: dict[str, Any]) -> None:
    formal = body.get("formal")
    if not isinstance(formal, dict):
        raise IntegrityError("engineering needs formal spec honesty", reason_code="CATALOG_ENGINEERING")
    if formal.get("claimed") is True or formal.get("verified") is True:
        raise IntegrityError("do not claim formally verified", reason_code="CATALOG_ENGINEERING")
    spec = Path(str(formal.get("spec") or ""))
    if spec.as_posix() != "src/agent_gov/spec/consume_once.tla":
        raise IntegrityError("formal spec path is consume_once.tla", reason_code="CATALOG_ENGINEERING")
    if not spec.is_file():
        raise IntegrityError("formal spec file missing", reason_code="CATALOG_ENGINEERING")
    text = spec.read_text(encoding="utf-8")
    if "CONSUME" not in text.upper() and "consume" not in text.lower():
        raise IntegrityError("formal spec must sketch consume-once", reason_code="CATALOG_ENGINEERING")


def catalog_engineering() -> dict[str, Any]:
    return dict(load_catalog()["engineering"])


def _validate_honest_missing(catalog: dict[str, Any]) -> None:
    missing = [str(item).lower() for item in catalog.get("honest_missing") or []]
    if not missing:
        raise IntegrityError("catalog missing honest_missing", reason_code="CATALOG_HONEST")
    if not any("live_pin" in item for item in missing):
        raise IntegrityError("honest_missing must keep LIVE_PIN_OK", reason_code="CATALOG_HONEST")
    if not any("second unique" in item or "cynthia" in item for item in missing):
        raise IntegrityError("honest_missing must keep the second human", reason_code="CATALOG_HONEST")
    if any(item.strip() == "live_pin_ok is marked" for item in missing):
        raise IntegrityError("honest_missing cannot claim LIVE_PIN_OK closed", reason_code="CATALOG_HONEST")


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
    interface = str(equations.get("interface") or "").lower()
    if "humans from the top" not in interface or "hierarchical" not in interface:
        raise IntegrityError(
            "interface equation is humans from the top \u00d7 hierarchical access",
            reason_code="CATALOG_EQUATION",
        )
    if "walkable rehearsal" not in interface:
        raise IntegrityError(
            "interface equation must keep walkable rehearsal",
            reason_code="CATALOG_EQUATION",
        )
    if "authorization lifecycle" not in interface or "sealed records" not in interface:
        raise IntegrityError(
            "interface equation must keep authorization lifecycle and sealed records",
            reason_code="CATALOG_EQUATION",
        )
    if "view assignment" not in interface or "mfa identify" not in interface:
        raise IntegrityError(
            "interface equation must keep view assignment and MFA identify",
            reason_code="CATALOG_EQUATION",
        )
    for stem in (
        "failsafe",
        "immutable",
        "other uses",
        "executive oversee",
        "ai governance maps",
        "internal audit",
        "regulator archive",
        "regulated entities",
    ):
        if stem not in interface:
            raise IntegrityError(
                f"interface equation must keep {stem}",
                reason_code="CATALOG_EQUATION",
            )
    estate_eq = str(equations.get("estate") or "").lower()
    for stem in ("other uses", "failsafe", "executive oversee", "sealed records", "immutable", "ai governance maps"):
        if stem not in estate_eq:
            raise IntegrityError(
                "estate equation is other uses × failsafe × executive oversee × sealed records × immutable × AI governance maps",
                reason_code="CATALOG_EQUATION",
            )
    if "must-have" not in interface:
        raise IntegrityError(
            "interface equation must keep must-have",
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
    audit_eq = str(equations.get("audit") or "").lower()
    for stem in ("internal audit", "regulator archive", "failure to comply", "room 1", "room 2"):
        if stem not in audit_eq:
            raise IntegrityError(
                "audit equation is internal audit × regulator archive × failure to comply × Room 1 books × Room 2 refuse",
                reason_code="CATALOG_EQUATION",
            )
    proof = str(equations.get("proof") or "").lower()
    for stem in ("write rail", "two seats", "one hash", "fail-closed"):
        if stem not in proof:
            raise IntegrityError(
                "proof equation is write rail × two seats × one hash × fail-closed write",
                reason_code="CATALOG_EQUATION",
            )
    instrument = str(equations.get("instrument") or "").lower()
    for stem in (
        "action schema",
        "admit client",
        "ai inventory",
        "examiner prove",
        "grant ttl",
        "passkey identify",
    ):
        if stem not in instrument:
            raise IntegrityError(
                "instrument equation is action schema × admit client × AI inventory × examiner prove × grant TTL × passkey identify",
                reason_code="CATALOG_EQUATION",
            )
    for stem in (
        "proof-day floor",
        "action schema",
        "admit client",
        "examiner prove",
        "pending bind",
        "freeze console",
        "examiner walk",
        "motions",
        "gaps board",
        "provision spine",
        "duty hints",
        "board packet",
        "lab pin",
        "edge quality",
        "graph owner consent",
    ):
        if stem not in interface:
            raise IntegrityError(
                f"interface equation must keep {stem}",
                reason_code="CATALOG_EQUATION",
            )
    motion = str(equations.get("motion") or "").lower()
    for stem in ("same l1", "ninety minutes", "qualify path", "counsel packet"):
        if stem not in motion:
            raise IntegrityError(
                "motion equation is same L1 × ninety minutes × qualify path × counsel packet",
                reason_code="CATALOG_EQUATION",
            )


def _validate_mailbox_law(catalog: dict[str, Any]) -> None:
    invited = ((catalog.get("organization") or {}).get("contacts") or {}).get("invited") or {}
    if invited.get("recorded") is not True:
        return
    if invited.get("seat_role") != "treasury_controller":
        raise IntegrityError("recorded invite seat is treasury_controller", reason_code="ORG_SECOND_OFFICER")
    if invited.get("inception_role") != "business_executive":
        raise IntegrityError("recorded invite Inception role is business_executive", reason_code="ORG_SECOND_OFFICER")
    stale = "invited, not recorded"
    for item in ((catalog.get("plane_interface") or {}).get("authorizations") or []):
        if item.get("id") != "seat":
            continue
        note = str(item.get("note") or "").lower()
        if "1 mailbox" not in note or "0 oid" not in note:
            raise IntegrityError("seat authorization must keep 1 mailbox / 0 oid", reason_code="CATALOG_PLANE")
        if stale in note or "0 recorded / 1 invited" in note:
            raise IntegrityError("seat authorization cannot revert to invited-not-recorded", reason_code="CATALOG_PLANE")
    investor = catalog.get("investor") or {}
    for field in ("letter_body", "letter_open", "seat_b", "ask"):
        if stale in str(investor.get(field) or "").lower():
            raise IntegrityError(
                "investor copy cannot say invited, not recorded after mailbox law",
                reason_code="CATALOG_INVESTOR",
            )
    if not any("chodnett@ainav.institute" in str(item).lower() for item in catalog.get("honest_missing") or []):
        raise IntegrityError("honest_missing must keep the recorded mailbox", reason_code="CATALOG_HONEST")
    seat = (((catalog.get("expert_review") or {}).get("success") or {}).get("seat_b") or {})
    if seat and str(seat.get("mailbox") or "") != "chodnett@ainav.institute":
        raise IntegrityError("success seat B must keep the recorded mailbox", reason_code="ORG_SECOND_OFFICER")


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
    if pages < 4 or pages > 10:
        raise IntegrityError("investor print is a four-to-ten page letter packet", reason_code="CATALOG_INVESTOR")
    if body.get("include_upsells") is not True:
        raise IntegrityError("investor packet must include the upsell catalog", reason_code="CATALOG_INVESTOR")
    if "same three skus" not in str(body.get("upsell_note") or "").lower() and "not a fourth" not in str(body.get("upsell_note") or "").lower():
        raise IntegrityError("upsell note must keep packs off a fourth SKU", reason_code="CATALOG_INVESTOR")
    if "dear cynthia" not in str(body.get("letter_open") or "").lower():
        raise IntegrityError("investor letter opens to Cynthia", reason_code="CATALOG_INVESTOR")
    if "second human" not in str(body.get("letter_open") or "").lower():
        raise IntegrityError("investor letter leads with the second-human ask", reason_code="CATALOG_INVESTOR")
    if "i am writing" not in str(body.get("letter_open") or "").lower():
        raise IntegrityError("investor letter is first person from the owner", reason_code="CATALOG_INVESTOR")
    if str(body.get("letter_voice") or "") != "first_person":
        raise IntegrityError("investor letter voice is first person", reason_code="CATALOG_INVESTOR")
    letter_body = str(body.get("letter_body") or "").lower()
    for stem in (
        "seat b",
        "mailbox recorded",
        "not stock",
        "not a priced round",
        "chodnett@ainav.institute",
        "number two",
        "not all aspects",
    ):
        if stem not in letter_body:
            raise IntegrityError(f"investor letter body must keep {stem}", reason_code="CATALOG_INVESTOR")
    if "$0" not in str(body.get("letter_body") or "") and "recognized revenue is $0" not in letter_body:
        raise IntegrityError("investor letter body must keep the $0 scoreboard", reason_code="CATALOG_INVESTOR")
    if "delaware" in letter_body:
        raise IntegrityError("investor letter body is the human ask — company dump belongs in the exec table", reason_code="CATALOG_INVESTOR")
    if "i will not ask" not in letter_body:
        raise IntegrityError("investor letter body must end on what James will not ask Cynthia for", reason_code="CATALOG_INVESTOR")
    if "i trust" not in letter_body:
        raise IntegrityError("investor letter body must say why James trusts Cynthia", reason_code="CATALOG_INVESTOR")
    if "sole owner" not in str(body.get("letter_close") or "").lower():
        raise IntegrityError("investor letter closes from the sole owner", reason_code="CATALOG_INVESTOR")
    if "seat b" not in str(body.get("seat_b") or "").lower():
        raise IntegrityError("investor letter names seat B", reason_code="CATALOG_INVESTOR")
    if "number two" not in str(body.get("seat_b") or "").lower() or "not all aspects" not in str(body.get("seat_b") or "").lower():
        raise IntegrityError("investor seat B is number two for other aspects, not all aspects", reason_code="CATALOG_INVESTOR")
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
    summary = body.get("executive_summary")
    if not isinstance(summary, dict):
        raise IntegrityError("investor packet missing executive summary", reason_code="CATALOG_INVESTOR")
    if summary.get("sku") is True or summary.get("certified") is True or summary.get("mandated") is True:
        raise IntegrityError("executive summary is not a SKU, certificate, or mandate", reason_code="CATALOG_INVESTOR")
    if summary.get("forecast") is True or summary.get("priced_round") is True:
        raise IntegrityError("executive summary cannot claim a forecast or priced round", reason_code="CATALOG_INVESTOR")
    if summary.get("live") is True or summary.get("live_pin_ok") is True:
        raise IntegrityError("executive summary cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    lede = str(summary.get("lede") or "").lower()
    for stem in ("job c", "ninety", "three sku", "zero"):
        if stem not in lede:
            raise IntegrityError(f"executive summary lede must keep {stem}", reason_code="CATALOG_INVESTOR")
    if "board packet" not in lede:
        raise IntegrityError("executive summary lede must say this is the board packet", reason_code="CATALOG_INVESTOR")
    if str(summary.get("proof") or "") != str((catalog.get("buyer") or {}).get("proof_day") or ""):
        raise IntegrityError("executive summary proof must match buyer proof day", reason_code="CATALOG_INVESTOR")
    if "two distinct humans" not in str(summary.get("job_c") or "").lower():
        raise IntegrityError("executive summary Job C is two distinct humans", reason_code="CATALOG_INVESTOR")
    tiles = str(summary.get("tiles") or "").lower()
    if "$0" not in str(summary.get("tiles") or "") or "mailbox recorded" not in tiles:
        raise IntegrityError("executive summary tiles stay $0 and mailbox recorded", reason_code="CATALOG_INVESTOR")
    if "not the product" not in str(summary.get("microsoft") or "").lower():
        raise IntegrityError("executive summary Microsoft is not the product", reason_code="CATALOG_INVESTOR")
    must = str(summary.get("must_have") or "").lower()
    if "not counsel" not in must or "not a certificate" not in must:
        raise IntegrityError("executive summary must-have is not counsel or a certificate", reason_code="CATALOG_INVESTOR")
    if "live_pin_ok cannot be marked" not in str(summary.get("opens") or "").lower():
        raise IntegrityError("executive summary opens cannot mark LIVE_PIN_OK", reason_code="CATALOG_INVESTOR")
    ask = str(summary.get("ask") or "").lower()
    if "seat b" not in ask or "mailbox" not in ask or "click" not in ask:
        raise IntegrityError("executive summary ask is seat B mailbox recorded, click still open", reason_code="CATALOG_INVESTOR")
    wanted = [
        ("job_c", "Job C", summary.get("job_c")),
        ("proof", "Proof day", summary.get("proof")),
        ("skus", "Three SKUs", summary.get("skus")),
        ("tiles", "Scoreboard today", summary.get("tiles")),
        ("microsoft", "Microsoft", summary.get("microsoft")),
        ("must_have", "Must-have", summary.get("must_have")),
        ("opens", "Owner-only still open", summary.get("opens")),
        ("ask", "The ask", summary.get("ask")),
    ]
    items = list(summary.get("items") or [])
    if [item.get("id") for item in items] != [row[0] for row in wanted]:
        raise IntegrityError("executive summary items must be the board-packet rows", reason_code="CATALOG_INVESTOR")
    for item, (iid, name, note) in zip(items, wanted, strict=True):
        if str(item.get("name") or "") != name or str(item.get("note") or "") != str(note or ""):
            raise IntegrityError(f"executive summary {iid} must match the scalar", reason_code="CATALOG_INVESTOR")


def _validate_expert_review(catalog: dict[str, Any]) -> None:
    body = catalog.get("expert_review")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing expert review", reason_code="CATALOG_REVIEW")
    upgrades = body.get("upgrades") or []
    if not 16 <= len(upgrades) <= 48:
        raise IntegrityError("expert review needs 16–48 upgrades", reason_code="CATALOG_REVIEW")
    if not any(
        item.get("n") == 16 and item.get("who") == "tree" and item.get("done") is True
        for item in upgrades
    ):
        raise IntegrityError("tree upgrade 16 is first-screen substitute vs Job C", reason_code="CATALOG_REVIEW")
    required_done = {
        17: ("bake-off", "independence"),
        18: ("walk away", "workflow"),
        19: ("objection", "pim"),
        20: ("graph write", "fail-closed"),
        21: ("chodnett@ainav.institute", "not a click"),
        22: ("missing", "product working"),
        23: ("stack walk", "cloudflare"),
        24: ("static", "owner book"),
        25: ("pro", "not a sku"),
        26: ("pages", "not the institute"),
        27: ("write rail", "not a cms"),
        28: ("write rail", "one dashboard"),
        29: ("application", "not a cms"),
        30: ("kit", "not a cms"),
        31: ("business", "not a priced round"),
        32: ("number two", "not all aspects"),
        33: ("visibility", "view_shows"),
        34: ("provision", "spine"),
        35: ("duty hint", "view"),
        36: ("freeze", "console"),
        37: ("examiner", "leaf"),
        38: ("gaps", "owner steps"),
        39: ("board packet", "seat b"),
        40: ("lab", "commercial"),
        41: ("quality", "probe"),
        42: ("tls", "1.2"),
        43: ("anycast", "outlook"),
        44: ("visitor", "full"),
        45: ("full (strict)", "owner"),
        46: ("leftover", "service principal"),
        47: ("four reads", "writes"),
        48: ("refus", "live_pin_ok"),
    }
    by_n = {item.get("n"): item for item in upgrades}
    for number, stems in required_done.items():
        item = by_n.get(number) or {}
        if item.get("who") != "tree" or item.get("done") is not True:
            raise IntegrityError(f"tree upgrade {number} must be done", reason_code="CATALOG_REVIEW")
        blob = f"{item.get('title') or ''} {item.get('do') or ''}".lower()
        if any(stem not in blob for stem in stems):
            raise IntegrityError(f"tree upgrade {number} must keep {stems[0]}", reason_code="CATALOG_REVIEW")
    if not body.get("working_well") or not body.get("improve"):
        raise IntegrityError("expert review needs working_well and improve", reason_code="CATALOG_REVIEW")
    if any(item.get("marks_live_pin") is True for item in upgrades):
        raise IntegrityError("upgrades cannot mark LIVE_PIN_OK", reason_code="LIVE_PIN_NOT_CLAIMED")
    _validate_success_program(body.get("success"))


def _validate_success_program(success: Any) -> None:
    if not isinstance(success, dict):
        raise IntegrityError("expert review needs a success program", reason_code="CATALOG_REVIEW")
    if success.get("sku") is True or success.get("mandated") is True or success.get("certified") is True:
        raise IntegrityError("success program is not a SKU, mandate, or certificate", reason_code="CATALOG_REVIEW")
    if success.get("live") is True or success.get("live_pin_ok") is True:
        raise IntegrityError("success program cannot mark LIVE_PIN_OK", reason_code="LIVE_PIN_NOT_CLAIMED")
    thesis = str(success.get("thesis") or "").lower()
    if "walk" not in thesis or "licensed substitute" not in thesis or "live_pin_ok" not in thesis:
        raise IntegrityError("success thesis is walk away from the licensed substitute", reason_code="CATALOG_REVIEW")
    bake = success.get("bake_off") or {}
    they = [item.get("id") for item in bake.get("they_win") or []]
    we = [item.get("id") for item in bake.get("we_win") or []]
    if not {"one_vendor", "cheaper", "speed"} <= set(they):
        raise IntegrityError("bake-off they-win must name one-vendor, cheaper, speed", reason_code="CATALOG_REVIEW")
    if not {"independence", "consume_once", "fail_closed", "counterparty"} <= set(we):
        raise IntegrityError("bake-off we-win must name independence and fail-closed", reason_code="CATALOG_REVIEW")
    if "cheaper button" not in str(bake.get("lede") or "").lower():
        raise IntegrityError("bake-off lede must name the cheaper button", reason_code="CATALOG_REVIEW")
    qualify = success.get("qualify") or {}
    walk = " ".join(str(item).lower() for item in qualify.get("walk_away") or [])
    must = " ".join(str(item).lower() for item in qualify.get("must") or [])
    if "workflow user groups" not in walk or "one human" not in walk:
        raise IntegrityError("qualify must walk away from cheaper native dual", reason_code="CATALOG_REVIEW")
    if "two existing treasury" not in must or "one title" not in must:
        raise IntegrityError("qualify must keep two existing treasury humans", reason_code="CATALOG_REVIEW")
    objections = {item.get("id"): item for item in success.get("objections") or []}
    for needed in ("price", "microsoft", "slow", "pim", "copilot_rfi"):
        if needed not in objections:
            raise IntegrityError(f"success objections must include {needed}", reason_code="CATALOG_REVIEW")
    blob = " ".join(
        f"{item.get('hear') or ''} {item.get('answer') or ''}".lower()
        for item in objections.values()
    )
    if "uncopyable" in blob or "patent granted" in blob:
        raise IntegrityError("objections cannot claim uncopyable or a patent", reason_code="CATALOG_REVIEW")
    if "walk away" not in str(objections["price"].get("answer") or "").lower():
        raise IntegrityError("price objection must offer the walk-away", reason_code="CATALOG_REVIEW")
    ciso = success.get("ciso") or {}
    holds = " ".join(str(item).lower() for item in ciso.get("holds") or [])
    does_not = " ".join(str(item).lower() for item in ciso.get("does_not") or [])
    if "no graph write" not in holds or "fail-closed" not in holds:
        raise IntegrityError("CISO posture must keep no Graph Write and fail-closed", reason_code="CATALOG_REVIEW")
    if "live_pin_ok" not in does_not or "inbox" not in does_not:
        raise IntegrityError("CISO posture cannot invent an inbox or LIVE_PIN_OK", reason_code="CATALOG_REVIEW")
    seat = success.get("seat_b") or {}
    if str(seat.get("mailbox") or "") != "chodnett@ainav.institute":
        raise IntegrityError("seat B meaning must keep the recorded mailbox", reason_code="ORG_SECOND_OFFICER")
    if str(seat.get("name") or "") != "Cynthia Hodnett":
        raise IntegrityError("seat B meaning must keep Cynthia Hodnett", reason_code="ORG_SECOND_OFFICER")
    is_not = " ".join(str(item).lower() for item in seat.get("is_not") or [])
    if "entra object id" not in is_not or "officer" not in is_not or "stockholder" not in is_not:
        raise IntegrityError("seat B meaning: mailbox is not oid, officer, or stock", reason_code="ORG_SECOND_OFFICER")
    is_yes = " ".join(str(item).lower() for item in seat.get("is") or [])
    if "number two" not in is_yes or "other aspects" not in is_yes:
        raise IntegrityError("seat B meaning: number two for other aspects", reason_code="ORG_SECOND_OFFICER")
    if "all aspects" not in is_not:
        raise IntegrityError("seat B meaning: not all aspects", reason_code="ORG_SECOND_OFFICER")
    continuity = success.get("continuity") or {}
    if "write does not land" not in str(continuity.get("lede") or "").lower():
        raise IntegrityError("continuity is the write does not land", reason_code="CATALOG_REVIEW")
    if "bypass" not in str(continuity.get("note") or "").lower():
        raise IntegrityError("continuity is not a bypass", reason_code="CATALOG_REVIEW")
    ledger = success.get("walk_away_ledger")
    if not isinstance(ledger, dict):
        raise IntegrityError("success needs a walk-away ledger", reason_code="CATALOG_REVIEW")
    if ledger.get("recorded") is True:
        raise IntegrityError("do not invent a recorded walk-away", reason_code="CATALOG_REVIEW")
    if int(ledger.get("count") or 0) != 0:
        raise IntegrityError("walk-away ledger count stays zero", reason_code="CATALOG_REVIEW")
    if list(ledger.get("items") or []) != []:
        raise IntegrityError("walk-away ledger items stay empty", reason_code="CATALOG_REVIEW")
    if ledger.get("do_not_invent_names") is not True:
        raise IntegrityError("walk-away ledger cannot invent names", reason_code="CATALOG_REVIEW")
    if "not recorded" not in str(ledger.get("note") or "").lower():
        raise IntegrityError("walk-away ledger note: first walk-away is not recorded", reason_code="CATALOG_REVIEW")


def _validate_owner_gates(catalog: dict[str, Any]) -> None:
    gates = catalog.get("owner_gates")
    if not isinstance(gates, list) or len(gates) < 6:
        raise IntegrityError("catalog missing owner gates", reason_code="CATALOG_ORG")
    for item in gates:
        if not item.get("do") or not item.get("url"):
            raise IntegrityError("owner gate needs a step and a link", reason_code="CATALOG_ORG")
        if item.get("id") == "invite.seat_b":
            do = str(item.get("do") or "").lower()
            if "chodnett@ainav.institute" not in do or "mailbox recorded" not in do:
                raise IntegrityError("invite.seat_b must keep the recorded mailbox", reason_code="ORG_SECOND_OFFICER")
            if "paid" not in do or "e7" not in do or "teams premium" not in do:
                raise IntegrityError("invite.seat_b records paid E7 and Teams Premium", reason_code="ORG_SECOND_OFFICER")
            if "fallback" not in do or "not a seat" not in do:
                raise IntegrityError("invite.seat_b keeps the fallback and Teams Premium is not a seat", reason_code="ORG_SECOND_OFFICER")
            if "invited, not recorded" in do:
                raise IntegrityError("invite.seat_b cannot revert to invited-not-recorded", reason_code="ORG_SECOND_OFFICER")


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
    if not {
        "nist.ai_rmf",
        "eu.ai_act",
        "iso.42001",
        "sox.icfr",
        "gdpr.art22",
        "coe.ai_convention",
        "sec.books_records",
    } <= maps:
        raise IntegrityError(
            "governance must map NIST, EU AI Act, ISO 42001, SOX, SEC books, GDPR Art. 22, and the CoE convention",
            reason_code="CATALOG_GOVERNANCE",
        )
    if any(item.get("claimed") is True for item in body.get("maps") or []):
        raise IntegrityError("governance maps cannot claim certification", reason_code="CATALOG_GOVERNANCE")
    refuse = " ".join(body.get("refuse") or []).lower()
    for stem in (
        "eu ai act certified",
        "nist certified",
        "replaces counsel",
        "client ai as dual",
        "17a-4 ready",
        "worm claimed",
        "crypto ledger",
        "gdpr certified",
        "eu-ready",
        "colorado sb 24-205",
    ):
        if stem not in refuse:
            raise IntegrityError(f"governance must refuse {stem}", reason_code="CATALOG_GOVERNANCE")
    immutable = body.get("immutable") or {}
    if immutable.get("sku") is True or immutable.get("certified") is True:
        raise IntegrityError("immutable is not a SKU or certificate", reason_code="CATALOG_GOVERNANCE")
    if immutable.get("crypto") is True or immutable.get("worm") is True or immutable.get("seventeen_a4") is True:
        raise IntegrityError("immutable is not crypto, WORM, or 17a-4", reason_code="CATALOG_GOVERNANCE")
    if immutable.get("uncopyable") is True:
        raise IntegrityError("immutable is not uncopyable", reason_code="CATALOG_GOVERNANCE")
    imm_thesis = str(immutable.get("thesis") or "").lower()
    if "sealed" not in imm_thesis or "consume-once" not in imm_thesis or "hash-chained" not in imm_thesis:
        raise IntegrityError("immutable thesis is sealed, consume-once, hash-chained", reason_code="CATALOG_GOVERNANCE")
    pin_ids = [item.get("id") for item in immutable.get("pins") or [] if isinstance(item, dict)]
    for needed in ("consume_once", "action_hash", "sealed_chain", "fail_closed", "lockfile"):
        if needed not in pin_ids:
            raise IntegrityError(f"immutable pins must include {needed}", reason_code="CATALOG_GOVERNANCE")
    reporting = body.get("reporting") or {}
    if reporting.get("sku") is True or reporting.get("certified") is True:
        raise IntegrityError("reporting is not a SKU or certificate", reason_code="CATALOG_GOVERNANCE")
    if reporting.get("chat_is_not_keep") is not True or reporting.get("mailbox_is_not_second_record") is not True:
        raise IntegrityError("a chat or mailbox is not the keep", reason_code="CATALOG_GOVERNANCE")
    consequences = body.get("consequences") or {}
    if consequences.get("mandated") is True or consequences.get("ainav_named_in_statute") is True:
        raise IntegrityError("must-have is not a statute that names AINav", reason_code="CATALOG_GOVERNANCE")
    if consequences.get("buying_l1_closes_clocks") is True:
        raise IntegrityError("buying L1 does not close regulator clocks", reason_code="CATALOG_GOVERNANCE")
    if consequences.get("certified") is True:
        raise IntegrityError("consequences are not a certificate", reason_code="CATALOG_GOVERNANCE")
    calendar = body.get("calendar") or {}
    if calendar.get("sku") is True or calendar.get("certified") is True:
        raise IntegrityError("governance calendar is not a SKU or certificate", reason_code="CATALOG_GOVERNANCE")
    if calendar.get("counsel") is not True:
        raise IntegrityError("governance calendar stays with counsel", reason_code="CATALOG_GOVERNANCE")
    cal_ids = {item.get("id") for item in calendar.get("items") or [] if isinstance(item, dict)}
    for needed in ("eu.ai_act.gpai_enforcement", "us.co.sb26_189", "eu.ai_act.annex_iii"):
        if needed not in cal_ids:
            raise IntegrityError(f"calendar must include {needed}", reason_code="CATALOG_GOVERNANCE")
    if any(item.get("claimed") is True for item in calendar.get("items") or [] if isinstance(item, dict)):
        raise IntegrityError("calendar items cannot claim certification", reason_code="CATALOG_GOVERNANCE")
    regulated = body.get("regulated") or {}
    if regulated.get("sku") is True or regulated.get("certified") is True:
        raise IntegrityError("regulated is not a SKU or certificate", reason_code="CATALOG_GOVERNANCE")
    if regulated.get("crypto_associated") is True or regulated.get("seventeen_a4") is True:
        raise IntegrityError("regulated is not crypto-associated or 17a-4", reason_code="CATALOG_GOVERNANCE")
    if regulated.get("lead") != "bc.general_journal.post":
        raise IntegrityError("regulated lead stays the general journal", reason_code="CATALOG_WEDGE")
    if regulated.get("room_1") != "books" or regulated.get("room_2") != "refuse":
        raise IntegrityError("Room 1 is books. Room 2 is refuse", reason_code="CATALOG_GOVERNANCE")
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


def _validate_public_face(face: Any) -> None:
    if not isinstance(face, dict):
        raise IntegrityError("floor public_face is required", reason_code="CATALOG_PLANE")
    if face.get("sku") is True:
        raise IntegrityError("public face is not a SKU", reason_code="CATALOG_SKU")
    if face.get("live") is True or face.get("live_pin_ok") is True or face.get("launch") is True:
        raise IntegrityError("public face cannot mark launch or LIVE_PIN_OK", reason_code="LIVE_PIN_NOT_CLAIMED")
    if face.get("cms") is True:
        raise IntegrityError("public face is not a CMS", reason_code="CATALOG_PLANE")
    if face.get("application") is not True:
        raise IntegrityError("public face is a catalog-honest application", reason_code="CATALOG_PLANE")
    if "static" not in str(face.get("host") or "").lower():
        raise IntegrityError("public face host is Azure Static Web Apps", reason_code="CATALOG_PLANE")
    thesis = str(face.get("thesis") or "").lower()
    for stem in ("static", "application", "first glance", "write rail", "owner book", "not a cms", "live_pin_ok"):
        if stem not in thesis:
            raise IntegrityError(f"public face thesis must keep {stem}", reason_code="CATALOG_PLANE")
    app = face.get("app") or {}
    if not isinstance(app, dict) or app.get("cms") is True or app.get("sku") is True:
        raise IntegrityError("application face is not a CMS or a SKU", reason_code="CATALOG_PLANE")
    if str(app.get("href") or "") != "app.html":
        raise IntegrityError("application face is app.html", reason_code="CATALOG_PLANE")
    work_ids = [item.get("id") for item in app.get("workspaces") or []]
    if not {"floor", "capital", "business", "programs"} <= set(work_ids):
        raise IntegrityError("application workspaces are floor, capital, business, and programs", reason_code="CATALOG_PLANE")
    primary = list(face.get("primary") or [])
    labels = [str(item.get("label") or "") for item in primary]
    if labels != ["The write", "Proof day", "Bake-off", "Dashboard", "Owner"]:
        raise IntegrityError("primary nav is write, proof day, bake-off, dashboard, owner", reason_code="CATALOG_PLANE")
    hrefs = [str(item.get("href") or "") for item in primary]
    if hrefs != ["#buyer", "#twin", "#success", "app.html", "#missing"]:
        raise IntegrityError("primary nav hrefs are buyer, twin, success, application, owner", reason_code="CATALOG_PLANE")
    book = list(face.get("owner_book") or [])
    book_ids = [item.get("id") for item in book]
    if book_ids != ["sale", "owner", "book"]:
        raise IntegrityError("owner book groups are sale, owner, book", reason_code="CATALOG_PLANE")
    owner_hrefs = [str(item.get("href") or "") for item in (book[1].get("items") or [])]
    if owner_hrefs[:3] != ["#closed", "#missing", "#open"]:
        raise IntegrityError("owner book keeps Closed, Owner, Open in order", reason_code="CATALOG_PLANE")
    book_hrefs = [str(item.get("href") or "") for item in (book[2].get("items") or [])]
    for needed in ("#finance", "#governance", "#investor"):
        if needed not in book_hrefs:
            raise IntegrityError(f"owner book must keep {needed}", reason_code="CATALOG_PLANE")
    ctas = [str(item.get("href") or "") for item in face.get("cta") or []]
    if "#twin" not in ctas or "#success" not in ctas or "#buyer" not in ctas:
        raise IntegrityError("public face CTAs are proof day, bake-off, and the write", reason_code="CATALOG_PLANE")
    cannot = " ".join(str(item) for item in face.get("cannot") or []).lower()
    for stem in ("inbox", "ainav.institute", "live_pin_ok", "cms"):
        if stem not in cannot:
            raise IntegrityError(f"public face cannot must keep {stem}", reason_code="CATALOG_PLANE")
    _validate_face_kit(face.get("kit"))


REQUIRED_KIT_TOOLS = (
    "jsonld",
    "llms_txt",
    "view_transitions",
    "speculation_rules",
    "popover",
    "minisearch",
    "playwright",
    "axe",
    "lighthouse",
    "eleventy",
    "lit",
    "swa_auth",
    "swa_api",
    "app_insights",
    "pagefind",
    "swa_cli",
    "storybook",
)


def _validate_face_kit(kit: Any) -> None:
    if not isinstance(kit, dict):
        raise IntegrityError("public face kit is required", reason_code="CATALOG_PLANE")
    if kit.get("sku") is True or kit.get("cms") is True or kit.get("compiler_is_cms") is True:
        raise IntegrityError("application kit is not a CMS or a SKU", reason_code="CATALOG_PLANE")
    if kit.get("live") is True or kit.get("live_pin_ok") is True or kit.get("launch") is True:
        raise IntegrityError("application kit cannot mark launch or LIVE_PIN_OK", reason_code="LIVE_PIN_NOT_CLAIMED")
    if kit.get("auth_is_admit") is True:
        raise IntegrityError("SWA identify is not admit", reason_code="CATALOG_PLANE")
    if kit.get("api_writes_sor") is True:
        raise IntegrityError("kit API cannot write a SoR", reason_code="CATALOG_PLANE")
    if kit.get("insights_claimed") is True or kit.get("connection_claimed") is True:
        raise IntegrityError("Application Insights is not claimed", reason_code="CATALOG_PLANE")
    if kit.get("pagefind_on_public_face") is True:
        raise IntegrityError("Pagefind stays on the kit, not the public CSP", reason_code="CATALOG_PLANE")
    if str(kit.get("href") or "") != "kit.html":
        raise IntegrityError("application kit is kit.html", reason_code="CATALOG_PLANE")
    if str(kit.get("compiler") or "") != "eleventy":
        raise IntegrityError("application kit compiler is Eleventy", reason_code="CATALOG_PLANE")
    thesis = str(kit.get("thesis") or "").lower()
    for stem in ("kit", "eleventy", "identify", "not a cms", "live_pin_ok"):
        if stem not in thesis:
            raise IntegrityError(f"application kit thesis must keep {stem}", reason_code="CATALOG_PLANE")
    ids = [item.get("id") for item in kit.get("tools") or []]
    missing = [item for item in REQUIRED_KIT_TOOLS if item not in ids]
    if missing:
        raise IntegrityError(f"application kit missing {missing[0]}", reason_code="CATALOG_PLANE")


def _validate_view_assignment(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    assign = body.get("view_assignment")
    if not isinstance(assign, dict):
        raise IntegrityError("catalog missing view assignment", reason_code="CATALOG_PLANE")
    if assign.get("sku") is True or assign.get("upsell") is True:
        raise IntegrityError("view assignment is not a SKU", reason_code="CATALOG_SKU")
    if assign.get("live") is True or assign.get("live_pin_ok") is True or assign.get("assignment_live") is True:
        raise IntegrityError("view assignment cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if assign.get("same_dashboard") is not True:
        raise IntegrityError("view assignment is the same dashboard", reason_code="CATALOG_PLANE")
    if assign.get("included_with") != "L1":
        raise IntegrityError("view assignment is included with L1", reason_code="CATALOG_PLANE")
    if assign.get("do_not_invent_names") is not True:
        raise IntegrityError("view assignment cannot invent named heads", reason_code="CATALOG_PLANE")
    if list(assign.get("named_assignments") or []) != []:
        raise IntegrityError("named assignments stay empty", reason_code="CATALOG_PLANE")
    if assign.get("department_ai_cannot_receive") is not True:
        raise IntegrityError("department AI cannot receive a view assignment", reason_code="CATALOG_PLANE")
    if assign.get("cloud_agent_cannot_assign") is not True:
        raise IntegrityError("Cloud Agent cannot assign views", reason_code="CATALOG_PLANE")
    if assign.get("duty_aware") is not True or assign.get("zero_standing") is not True:
        raise IntegrityError("view assignment is duty-aware and zero-standing", reason_code="CATALOG_PLANE")
    thesis = str(assign.get("thesis") or "").lower()
    for stem in ("org chart", "one dashboard", "fail-closed", "mfa", "does not admit"):
        if stem not in thesis:
            raise IntegrityError(f"view assignment thesis must keep {stem}", reason_code="CATALOG_PLANE")
    glance = assign.get("first_glance") or {}
    if glance.get("sku") is True:
        raise IntegrityError("view assignment first glance is not a SKU", reason_code="CATALOG_SKU")
    if str(glance.get("legal") or "") != str((catalog.get("entity") or {}).get("legal") or ""):
        raise IntegrityError("view assignment legal is AINav, Inc.", reason_code="CATALOG_PLANE")
    lede = str(glance.get("lede") or "").lower()
    if "org chart" not in lede or "fail-closed" not in lede or "does not admit" not in lede:
        raise IntegrityError("view assignment first glance is org-chart, fail-closed, MFA identify", reason_code="CATALOG_PLANE")
    provision = assign.get("provision") or {}
    if provision.get("standard") != "provision.standard" or provision.get("options") != "provision.advanced":
        raise IntegrityError("view assignment provision is standard plus options", reason_code="CATALOG_PLANE")
    if provision.get("week_one") != "provisioning.standard_l1":
        raise IntegrityError("view assignment week-one stays standard_l1", reason_code="CATALOG_PLANE")
    seats = list(provision.get("standard_seats") or [])
    for needed in ("client", "seats", "owner", "examiner", "remote", "it", "provision", "records"):
        if needed not in seats:
            raise IntegrityError(f"standard seats must include {needed}", reason_code="CATALOG_PLANE")
    unlock = [str(item).lower() for item in provision.get("options_unlock") or []]
    for needed in ("priced_desks", "padm_keep", "paid_udual", "hours"):
        if needed not in unlock:
            raise IntegrityError("options unlock priced desks, keep, paid U-DUAL, and hours", reason_code="CATALOG_PLANE")
    view_ids = {item.get("id") for item in body.get("views") or [] if isinstance(item, dict)}
    depts = {
        item.get("id"): item
        for item in ((catalog.get("client_org") or {}).get("departments") or [])
        if isinstance(item, dict)
    }
    covered: set[str] = set()
    matrix = assign.get("matrix") or []
    if len(matrix) != len(depts):
        raise IntegrityError("view assignment matrix covers every client department", reason_code="CATALOG_PLANE")
    for row in matrix:
        if not isinstance(row, dict):
            raise IntegrityError("view assignment matrix row is an object", reason_code="CATALOG_PLANE")
        nodes = list(row.get("org_nodes") or [])
        if not nodes:
            raise IntegrityError("view assignment row needs org nodes", reason_code="CATALOG_PLANE")
        for node in nodes:
            if node not in depts:
                raise IntegrityError(f"view assignment unknown org node {node}", reason_code="CATALOG_PLANE")
            if node in covered:
                raise IntegrityError("view assignment org node is unique", reason_code="CATALOG_PLANE")
            covered.add(node)
            if depts[node].get("role") != row.get("org_role"):
                raise IntegrityError("view assignment role must match the org chart", reason_code="CATALOG_PLANE")
        default = row.get("default_view")
        allowed = list(row.get("allowed_views") or [])
        if default not in allowed:
            raise IntegrityError("default view must be allowed", reason_code="CATALOG_PLANE")
        for view in allowed:
            if view not in view_ids:
                raise IntegrityError(f"view assignment unknown view {view}", reason_code="CATALOG_PLANE")
        if row.get("org_role") == "admit":
            if row.get("may_bind") is not True:
                raise IntegrityError("admit roles may bind", reason_code="CATALOG_PLANE")
            if row.get("seat") not in {"seat_a", "seat_b"}:
                raise IntegrityError("admit assignment names seat A or seat B", reason_code="CATALOG_PLANE")
        elif row.get("may_bind") is True:
            raise IntegrityError("only admit roles may bind", reason_code="CATALOG_PLANE")
        band = row.get("provision_band")
        if band not in {"provision.standard", "provision.advanced"}:
            raise IntegrityError("assignment band is standard or advanced provision", reason_code="CATALOG_PLANE")
    if covered != set(depts):
        raise IntegrityError("view assignment must cover the org chart", reason_code="CATALOG_PLANE")
    auth = assign.get("authorize") or {}
    if auth.get("sku") is True or auth.get("live") is True or auth.get("standing") is True:
        raise IntegrityError("authorize stays zero-standing and not a SKU", reason_code="CATALOG_PLANE")
    if auth.get("fail_closed") is not True:
        raise IntegrityError("authorize is fail-closed", reason_code="CATALOG_PLANE")
    if auth.get("uses") != "authorizations":
        raise IntegrityError("authorize uses the authorization lifecycle", reason_code="CATALOG_PLANE")
    if "seat_bind" not in (auth.get("requires_dual_humans_for") or []):
        raise IntegrityError("seat bind requires two humans", reason_code="CATALOG_PLANE")
    if list(auth.get("path") or []) != ["identify", "view", "seat", "bind"]:
        raise IntegrityError("authorize path is identify, view, seat, bind", reason_code="CATALOG_PLANE")
    deauth = assign.get("deauthorize") or {}
    if deauth.get("sku") is True or deauth.get("live") is True or deauth.get("standing") is True:
        raise IntegrityError("de-authorize stays zero-standing and not a SKU", reason_code="CATALOG_PLANE")
    if deauth.get("fail_closed") is not True:
        raise IntegrityError("de-authorize is fail-closed", reason_code="CATALOG_PLANE")
    if deauth.get("uses") != "revocations":
        raise IntegrityError("de-authorize uses revocations", reason_code="CATALOG_PLANE")
    if deauth.get("effect") != "console_hidden":
        raise IntegrityError("de-authorize hides the console", reason_code="CATALOG_PLANE")
    by = set(deauth.get("by") or [])
    if not {"freeze", "seat_revoke", "view_revoke"} <= by:
        raise IntegrityError("de-authorize by freeze, seat revoke, and view revoke", reason_code="CATALOG_PLANE")
    if "seat_revoke" not in (deauth.get("requires_dual_humans_for") or []):
        raise IntegrityError("seat revoke requires two humans", reason_code="CATALOG_PLANE")
    mfa = assign.get("mfa") or {}
    if mfa.get("sku") is True:
        raise IntegrityError("MFA is not a SKU", reason_code="CATALOG_SKU")
    if mfa.get("live") is True or mfa.get("mfa_live") is True:
        raise IntegrityError("MFA cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if mfa.get("is_admit") is True:
        raise IntegrityError("MFA is not admit", reason_code="CATALOG_PLANE")
    if mfa.get("same_plane") is not True or mfa.get("vpn_sku") is True:
        raise IntegrityError("remote MFA is the same plane, not a VPN SKU", reason_code="CATALOG_PLANE")
    if mfa.get("pim_is_not_dual") is not True:
        raise IntegrityError("PIM is not dual admit", reason_code="CATALOG_PLANE")
    internal = mfa.get("internal") or {}
    remote = mfa.get("remote") or {}
    if internal.get("admit") is True or remote.get("admit") is True:
        raise IntegrityError("internal and remote MFA do not admit", reason_code="CATALOG_PLANE")
    if internal.get("mfa_live") is True or remote.get("mfa_live") is True:
        raise IntegrityError("MFA cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if remote.get("same_plane") is not True or remote.get("vpn_sku") is True:
        raise IntegrityError("remote MFA is the same plane", reason_code="CATALOG_PLANE")
    mfa_note = str(mfa.get("note") or "").lower()
    if "identify" not in mfa_note or "not dual admit" not in mfa_note or "wired live" not in mfa_note:
        raise IntegrityError("MFA note is identify, not admit, not live", reason_code="CATALOG_PLANE")
    passkey = mfa.get("passkey")
    if not isinstance(passkey, dict):
        raise IntegrityError("MFA needs passkey identify", reason_code="CATALOG_PLANE")
    if passkey.get("is_admit") is True or passkey.get("live") is True:
        raise IntegrityError("passkey is identify, not admit, not live", reason_code="CATALOG_PLANE")
    if passkey.get("identify") is not True:
        raise IntegrityError("passkey identifies", reason_code="CATALOG_PLANE")
    if "does not admit" not in str(passkey.get("note") or "").lower():
        raise IntegrityError("passkey note: identify is not admit", reason_code="CATALOG_PLANE")
    disc = assign.get("disclaimers") or {}
    if str(disc.get("legal") or "") != str((catalog.get("entity") or {}).get("legal") or ""):
        raise IntegrityError("disclaimers are AINav, Inc.", reason_code="CATALOG_PLANE")
    if disc.get("sku") is True or disc.get("certified") is True or disc.get("counsel") is True:
        raise IntegrityError("disclaimers are not a SKU, certificate, or counsel", reason_code="CATALOG_PLANE")
    if disc.get("signature") is True or disc.get("live_pin_ok") is True:
        raise IntegrityError("disclaimers are not a signature or LIVE_PIN_OK", reason_code="CATALOG_PLANE")
    if disc.get("uses") != "floor.protect":
        raise IntegrityError("disclaimers use floor.protect", reason_code="CATALOG_PLANE")
    protect = ((body.get("floor") or {}).get("protect") or {})
    prot_items = {item.get("id"): item for item in protect.get("items") or [] if isinstance(item, dict)}
    disc_items = {item.get("id"): item for item in disc.get("items") or [] if isinstance(item, dict)}
    for needed in ("disclaimer", "attest", "policy", "update"):
        if needed not in disc_items:
            raise IntegrityError(f"disclaimers must include {needed}", reason_code="CATALOG_PLANE")
        if str((disc_items.get(needed) or {}).get("note") or "") != str((prot_items.get(needed) or {}).get("note") or ""):
            raise IntegrityError(f"disclaimer {needed} must match floor.protect", reason_code="CATALOG_PLANE")
    disc_lede = str(disc.get("lede") or "").lower()
    if "ainav, inc" not in disc_lede or "not counsel" not in disc_lede or "not a certificate" not in disc_lede:
        raise IntegrityError("disclaimer lede is AINav, Inc. catalog-map", reason_code="CATALOG_PLANE")
    advantage = assign.get("advantage") or {}
    if advantage.get("sku") is True or advantage.get("live") is True:
        raise IntegrityError("advantage is not a SKU or live", reason_code="CATALOG_PLANE")
    adv_ids = [item.get("id") for item in advantage.get("items") or [] if isinstance(item, dict)]
    for needed in ("org_chart_assignment", "fail_closed_revoke", "identify_not_admit", "duty_aware", "independence"):
        if needed not in adv_ids:
            raise IntegrityError(f"advantage must include {needed}", reason_code="CATALOG_PLANE")
    refuse = [str(item).lower() for item in assign.get("refuse") or []]
    for stem in (
        "view assignment as sku",
        "personalized dashboard as sku",
        "mfa as dual admit",
        "mfa live claimed",
        "dashboard as sku",
    ):
        if stem not in refuse:
            raise IntegrityError("view assignment must refuse " + stem, reason_code="CATALOG_PLANE")


def _validate_estate(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    estate = body.get("estate")
    if not isinstance(estate, dict):
        raise IntegrityError("catalog missing plane estate", reason_code="CATALOG_PLANE")
    if estate.get("sku") is True or estate.get("upsell") is True or estate.get("fourth_sku") is True:
        raise IntegrityError("estate is not a SKU", reason_code="CATALOG_SKU")
    if estate.get("live") is True or estate.get("live_pin_ok") is True:
        raise IntegrityError("estate cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if estate.get("same_dashboard") is not True or estate.get("included_with") != "L1":
        raise IntegrityError("estate is the same L1 dashboard", reason_code="CATALOG_PLANE")
    thesis = str(estate.get("thesis") or "").lower()
    for stem in ("failsafe", "not the ai", "two records", "hash-chained", "catalog map", "bc.general_journal.post"):
        if stem not in thesis:
            raise IntegrityError(f"estate thesis must keep {stem}", reason_code="CATALOG_PLANE")
    glance = estate.get("first_glance") or {}
    if glance.get("sku") is True:
        raise IntegrityError("estate first glance is not a SKU", reason_code="CATALOG_SKU")
    lede = str(glance.get("lede") or "").lower()
    for stem in ("failsafe", "sealed records", "immutable", "not a fourth sku"):
        if stem not in lede:
            raise IntegrityError(f"estate first glance must keep {stem}", reason_code="CATALOG_PLANE")
    columns = {item.get("id"): item for item in glance.get("columns") or [] if isinstance(item, dict)}
    if set(columns) != {"other_uses", "failsafe_oversee", "records_maps"}:
        raise IntegrityError(
            "estate first glance needs other_uses, failsafe_oversee, and records_maps",
            reason_code="CATALOG_PLANE",
        )
    for column in columns.values():
        if column.get("sku") is True or column.get("upsell") is True:
            raise IntegrityError("estate first glance column is not a SKU", reason_code="CATALOG_SKU")
    uses_blob = " ".join(str(item) for item in (columns["other_uses"].get("items") or [])).lower()
    if "bc.general_journal.post" not in uses_blob or "l1" not in uses_blob or "u-dual" not in uses_blob:
        raise IntegrityError("estate first glance other uses keep the journal lead", reason_code="CATALOG_PLANE")
    fail_blob = " ".join(str(item) for item in (columns["failsafe_oversee"].get("items") or [])).lower()
    if "admit" not in fail_blob or "not seats" not in fail_blob:
        raise IntegrityError("estate first glance failsafe keeps admit and not seats", reason_code="CATALOG_PLANE")
    rec_blob = " ".join(str(item) for item in (columns["records_maps"].get("items") or [])).lower()
    if "two records" not in rec_blob and "second record" not in rec_blob:
        raise IntegrityError("estate first glance records keep the second record", reason_code="CATALOG_PLANE")
    if "hash-chained" not in rec_blob or "maps" not in rec_blob:
        raise IntegrityError("estate first glance maps stay claimed maps", reason_code="CATALOG_PLANE")
    uses = estate.get("other_uses") or {}
    if uses.get("lead") != "bc.general_journal.post":
        raise IntegrityError("other uses lead stays the general journal", reason_code="CATALOG_WEDGE")
    modules = {
        item.get("id"): item
        for item in catalog.get("modules") or []
        if isinstance(item, dict)
    }
    bands = {item.get("id"): item for item in uses.get("bands") or [] if isinstance(item, dict)}
    for needed in ("prove", "deepen", "keep"):
        if needed not in bands:
            raise IntegrityError(f"other uses must include {needed}", reason_code="CATALOG_PLANE")
    prove = bands["prove"]
    deepen = bands["deepen"]
    keep = bands["keep"]
    if prove.get("sku") != "L1" or deepen.get("sku") != "U-DUAL" or keep.get("sku") != "P-ADM":
        raise IntegrityError("other uses bands stay L1 / U-DUAL / P-ADM", reason_code="CATALOG_SKU")
    if list(prove.get("wedge") or []) != ["bc.general_journal.post"]:
        raise IntegrityError("L1 other-uses wedge stays the general journal", reason_code="CATALOG_WEDGE")
    if set(deepen.get("wedge") or []) != {"d365.quote.discount_override", "d365.order.submit"}:
        raise IntegrityError("U-DUAL other-uses wedges stay quote and order", reason_code="CATALOG_WEDGE")
    for band in (prove, deepen, keep):
        for action_id in list(band.get("wedge") or []) + list(band.get("desks") or []):
            module = modules.get(action_id)
            if not module:
                raise IntegrityError(f"other uses unknown module {action_id}", reason_code="CATALOG_PLANE")
            if module.get("sku") != band.get("sku"):
                raise IntegrityError(f"other uses {action_id} must stay on {band.get('sku')}", reason_code="CATALOG_SKU")
    fail = estate.get("failsafe") or {}
    if fail.get("ainav_is_client_ai") is True:
        raise IntegrityError("estate failsafe is not the client's AI", reason_code="CATALOG_GOVERNANCE")
    if fail.get("uses") != "governance.plane":
        raise IntegrityError("estate failsafe uses governance.plane", reason_code="CATALOG_PLANE")
    verb_ids = [item.get("id") for item in fail.get("verbs") or [] if isinstance(item, dict)]
    for needed in ("admit", "off_switch", "reset", "rollback"):
        if needed not in verb_ids:
            raise IntegrityError(f"failsafe verbs must include {needed}", reason_code="CATALOG_PLANE")
    gov_plane = ((catalog.get("governance") or {}).get("plane") or {})
    verbs = {item.get("id"): item for item in fail.get("verbs") or [] if isinstance(item, dict)}
    for key in ("off_switch", "reset", "rollback"):
        if str((verbs.get(key) or {}).get("note") or "") != str((gov_plane.get(key) or {}).get("does") or ""):
            raise IntegrityError(f"estate {key} must match governance.plane", reason_code="CATALOG_PLANE")
    executive = estate.get("executive") or {}
    if executive.get("dashboard_is_sku") is True or executive.get("dashboard_included_with") != "L1":
        raise IntegrityError("executive dashboard is included with L1, not a SKU", reason_code="CATALOG_SKU")
    for who in ("owner", "board"):
        row = executive.get(who) or {}
        if row.get("admit") is True or row.get("role") != "oversee":
            raise IntegrityError(f"{who} oversees and does not admit", reason_code="CATALOG_PLANE")
        if row.get("freeze") != "request":
            raise IntegrityError(f"{who} may request a freeze", reason_code="CATALOG_PLANE")
    records = estate.get("records") or {}
    if records.get("certified") is True:
        raise IntegrityError("estate records are not a certificate", reason_code="CATALOG_GOVERNANCE")
    if records.get("uses") != "governance.records":
        raise IntegrityError("estate records use governance.records", reason_code="CATALOG_PLANE")
    rec_ids = [item.get("id") for item in records.get("items") or [] if isinstance(item, dict)]
    for needed in ("first", "second", "keep"):
        if needed not in rec_ids:
            raise IntegrityError(f"estate records must include {needed}", reason_code="CATALOG_PLANE")
    immutable = estate.get("immutable") or {}
    if immutable.get("crypto") is True or immutable.get("worm") is True:
        raise IntegrityError("estate immutable is not crypto or WORM", reason_code="CATALOG_GOVERNANCE")
    if immutable.get("uses") != "governance.immutable":
        raise IntegrityError("estate immutable uses governance.immutable", reason_code="CATALOG_PLANE")
    instruments = estate.get("instruments") or {}
    if instruments.get("certified") is True or instruments.get("mandated") is True:
        raise IntegrityError("estate instruments are not certified or mandated", reason_code="CATALOG_GOVERNANCE")
    if instruments.get("uses") != "governance.maps":
        raise IntegrityError("estate instruments use governance.maps", reason_code="CATALOG_PLANE")
    refuse = [str(item).lower() for item in estate.get("refuse") or []]
    for stem in (
        "estate as sku",
        "other uses as fourth sku",
        "failsafe as client ai",
        "owner as both seats",
        "board admits",
        "worm claimed",
        "crypto ledger",
        "eu-ready",
    ):
        if stem not in refuse:
            raise IntegrityError("estate must refuse " + stem, reason_code="CATALOG_PLANE")


def _validate_audit(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    audit = body.get("audit")
    if not isinstance(audit, dict):
        raise IntegrityError("catalog missing plane audit", reason_code="CATALOG_PLANE")
    if audit.get("sku") is True or audit.get("upsell") is True or audit.get("fourth_sku") is True:
        raise IntegrityError("audit is not a SKU", reason_code="CATALOG_SKU")
    if audit.get("live") is True or audit.get("live_pin_ok") is True:
        raise IntegrityError("audit cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if audit.get("same_dashboard") is not True or audit.get("included_with") != "L1":
        raise IntegrityError("audit is the same L1 dashboard", reason_code="CATALOG_PLANE")
    if audit.get("crypto_associated") is True or audit.get("seventeen_a4") is True:
        raise IntegrityError("audit is not crypto-associated or 17a-4", reason_code="CATALOG_GOVERNANCE")
    thesis = str(audit.get("thesis") or "").lower()
    for stem in (
        "internal audit",
        "does not admit",
        "17a-4",
        "room 1",
        "room 2",
        "bc.general_journal.post",
        "does not close regulator clocks",
    ):
        if stem not in thesis:
            raise IntegrityError(f"audit thesis must keep {stem}", reason_code="CATALOG_PLANE")
    glance = audit.get("first_glance") or {}
    if glance.get("sku") is True:
        raise IntegrityError("audit first glance is not a SKU", reason_code="CATALOG_SKU")
    columns = {item.get("id"): item for item in glance.get("columns") or [] if isinstance(item, dict)}
    if set(columns) != {"internal_audit", "regulator_archive", "consequences"}:
        raise IntegrityError(
            "audit first glance needs internal_audit, regulator_archive, and consequences",
            reason_code="CATALOG_PLANE",
        )
    for column in columns.values():
        if column.get("sku") is True or column.get("upsell") is True:
            raise IntegrityError("audit first glance column is not a SKU", reason_code="CATALOG_SKU")
    rooms = audit.get("rooms") or {}
    internal = rooms.get("internal") or {}
    if internal.get("admit") is True or internal.get("role") != "keep":
        raise IntegrityError("internal audit keeps and does not admit", reason_code="CATALOG_PLANE")
    if internal.get("default_view") != "examiner" or internal.get("pack") != "industry.internal_audit":
        raise IntegrityError("internal audit sits Examiner on industry.internal_audit", reason_code="CATALOG_PLANE")
    archive = rooms.get("archive") or {}
    if archive.get("seventeen_a4") is True or archive.get("worm") is True:
        raise IntegrityError("archive is not 17a-4 or WORM", reason_code="CATALOG_GOVERNANCE")
    if "merkle" not in str(archive.get("what") or "").lower():
        raise IntegrityError("archive is a Merkle walk", reason_code="CATALOG_PLANE")
    regulated = audit.get("regulated") or {}
    if regulated.get("lead") != "bc.general_journal.post":
        raise IntegrityError("regulated lead stays the general journal", reason_code="CATALOG_WEDGE")
    if regulated.get("crypto_associated") is True:
        raise IntegrityError("regulated is not crypto-associated", reason_code="CATALOG_GOVERNANCE")
    room_1 = regulated.get("room_1") or {}
    room_2 = regulated.get("room_2") or {}
    if room_1.get("id") != "room_1" or room_2.get("id") != "room_2":
        raise IntegrityError("regulated needs Room 1 and Room 2", reason_code="CATALOG_PLANE")
    if room_1.get("buy") != "L1 as today":
        raise IntegrityError("Room 1 buys L1 as today", reason_code="CATALOG_PLANE")
    if room_2.get("buy") is not False:
        raise IntegrityError("Room 2 is not a buy this week", reason_code="CATALOG_SKU")
    item_ids = [item.get("id") for item in regulated.get("items") or [] if isinstance(item, dict)]
    for needed in ("sec.books", "sec.17a4", "stablecoin", "rwa", "crypto_am", "mica"):
        if needed not in item_ids:
            raise IntegrityError(f"regulated items must include {needed}", reason_code="CATALOG_PLANE")
    if any(item.get("claimed") is True for item in regulated.get("items") or [] if isinstance(item, dict)):
        raise IntegrityError("regulated items cannot claim certification", reason_code="CATALOG_GOVERNANCE")
    if audit.get("consequences_uses") != "governance.consequences":
        raise IntegrityError("audit consequences use governance.consequences", reason_code="CATALOG_PLANE")
    refuse = [str(item).lower() for item in audit.get("refuse") or []]
    for stem in (
        "audit as sku",
        "17a-4 ready",
        "worm claimed",
        "stablecoin sku",
        "room 2 as lead",
        "buying l1 closes clocks",
    ):
        if stem not in refuse:
            raise IntegrityError("audit must refuse " + stem, reason_code="CATALOG_PLANE")


def _validate_instrument_plane(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    floor = body.get("proof_day_floor")
    if not isinstance(floor, dict):
        raise IntegrityError("catalog missing proof-day Floor", reason_code="CATALOG_PLANE")
    if floor.get("sku") is True:
        raise IntegrityError("proof-day Floor is not a SKU", reason_code="CATALOG_SKU")
    if floor.get("same_dashboard") is not True or floor.get("included_with") != "L1":
        raise IntegrityError("proof-day Floor is the same L1 dashboard", reason_code="CATALOG_PLANE")
    if int(floor.get("minutes") or 0) != 90:
        raise IntegrityError("proof-day Floor is ninety minutes", reason_code="CATALOG_PLANE")
    shows = [str(item) for item in floor.get("client_shows") or []]
    for needed in ("write_rail", "attention", "seats", "keep", "offer"):
        if needed not in shows:
            raise IntegrityError("Client proof-day Floor sits write rail, attention, seats, keep, offer", reason_code="CATALOG_PLANE")
    hides = [str(item) for item in floor.get("client_hides") or []]
    for needed in ("estate", "audit", "assignment"):
        if needed not in hides:
            raise IntegrityError("Client proof-day Floor hides estate, audit, and assignment", reason_code="CATALOG_PLANE")
    client_view = next(
        (item for item in body.get("views") or [] if isinstance(item, dict) and item.get("id") == "client"),
        {},
    )
    if "ninety-minute" not in str(client_view.get("can") or "").lower():
        raise IntegrityError("client view is the ninety-minute proof-day Floor", reason_code="CATALOG_PLANE")
    admit = body.get("admit_client")
    if not isinstance(admit, dict):
        raise IntegrityError("catalog missing admit client", reason_code="CATALOG_PLANE")
    if admit.get("sku") is True or admit.get("live") is True:
        raise IntegrityError("admit client is not a SKU or live", reason_code="CATALOG_PLANE")
    if admit.get("drafter_is_not_seat") is not True:
        raise IntegrityError("drafter is not a seat", reason_code="CATALOG_PLANE")
    examiner = body.get("examiner")
    if not isinstance(examiner, dict):
        raise IntegrityError("catalog missing examiner prove", reason_code="CATALOG_PLANE")
    if examiner.get("sku") is True or examiner.get("live") is True:
        raise IntegrityError("examiner is not a SKU or live", reason_code="CATALOG_PLANE")
    if examiner.get("read_only") is not True:
        raise IntegrityError("examiner prove is read-only", reason_code="CATALOG_PLANE")
    if examiner.get("seventeen_a4") is True or examiner.get("worm") is True:
        raise IntegrityError("examiner is not 17a-4 or WORM", reason_code="CATALOG_GOVERNANCE")
    if "examiner-prove" not in str(examiner.get("cli") or ""):
        raise IntegrityError("examiner cli is examiner-prove", reason_code="CATALOG_PLANE")
    inventory = body.get("ai_inventory")
    if not isinstance(inventory, dict):
        raise IntegrityError("catalog missing AI inventory", reason_code="CATALOG_PLANE")
    if inventory.get("sku") is True or inventory.get("live") is True:
        raise IntegrityError("AI inventory is not a SKU or live", reason_code="CATALOG_PLANE")
    if list(inventory.get("items") or []) != []:
        raise IntegrityError("AI inventory stays empty", reason_code="CATALOG_PLANE")
    if inventory.get("do_not_invent_names") is not True:
        raise IntegrityError("AI inventory cannot invent names", reason_code="CATALOG_PLANE")
    if inventory.get("drafter_is_not_seat") is not True:
        raise IntegrityError("AI inventory: drafter is not a seat", reason_code="CATALOG_PLANE")
    ttl = body.get("grant_ttl")
    if not isinstance(ttl, dict):
        raise IntegrityError("catalog missing grant TTL", reason_code="CATALOG_PLANE")
    if ttl.get("outside_digest") is not True or ttl.get("changes_policy_hash") is True:
        raise IntegrityError("grant TTL stays outside the lockfile digest", reason_code="CATALOG_PLANE")
    if ttl.get("default_seconds") is not None:
        raise IntegrityError("default grant TTL stays unset", reason_code="CATALOG_PLANE")
    if int(ttl.get("proof_day_seconds") or 0) != 5400:
        raise IntegrityError("proof-day grant TTL is 90 minutes outside the digest", reason_code="CATALOG_PLANE")
    proof_day = catalog.get("proof_day") or {}
    if int(proof_day.get("grant_ttl_seconds") or 0) != int(ttl.get("proof_day_seconds") or 0):
        raise IntegrityError("proof-day TTL must match grant_ttl.proof_day_seconds", reason_code="CATALOG_PLANE")
    if proof_day.get("lab_oids_are_not_named_seats") is not True:
        raise IntegrityError("lab oids are not named seats", reason_code="CATALOG_PLANE")
    _validate_instrument_271(catalog, body)
    _validate_instrument_272(catalog, body)
    _validate_instrument_273(catalog, body)
    _validate_instrument_274(catalog, body)
    _validate_instrument_275(catalog, body)
    _validate_instrument_276(catalog, body)
    _validate_instrument_277(catalog, body)
    _validate_instrument_278(catalog, body)


def _validate_instrument_272(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    gaps = body.get("gaps")
    if not isinstance(gaps, dict):
        raise IntegrityError("catalog missing gaps board", reason_code="CATALOG_PLANE")
    if gaps.get("sku") is True or gaps.get("live") is True or gaps.get("live_pin_ok") is True:
        raise IntegrityError("gaps board is not a SKU or live", reason_code="CATALOG_PLANE")
    if gaps.get("claimed") is True:
        raise IntegrityError("gaps board cannot claim closed owner clicks", reason_code="CATALOG_PLANE")
    if int(gaps.get("gold_floor") or 0) != 95:
        raise IntegrityError("gaps gold_floor is 95", reason_code="CATALOG_PLANE")
    gold = ((catalog.get("engineering") or {}).get("gold_ci") or {})
    if gaps.get("gold_floor") != gold.get("coverage_floor"):
        raise IntegrityError("gaps.gold_floor must match engineering.gold_ci.coverage_floor", reason_code="CATALOG_ENGINEERING")
    closed = [str(item).lower() for item in gaps.get("in_tree_closed") or []]
    owner = [str(item).lower() for item in gaps.get("owner_only_open") or []]
    cannot = [str(item).lower() for item in gaps.get("this_plane_cannot") or []]
    if not closed or not owner or not cannot:
        raise IntegrityError("gaps board needs in_tree_closed, owner_only_open, and this_plane_cannot", reason_code="CATALOG_PLANE")
    for stem in ("gold floor 95", "client offer", "pending bind"):
        if not any(stem in item for item in closed):
            raise IntegrityError("gaps in_tree_closed must keep " + stem, reason_code="CATALOG_PLANE")
    for stem in ("seat b", "graph", "dataverse", "g12", "billing", "launch"):
        if not any(stem in item for item in owner):
            raise IntegrityError("gaps owner_only_open must keep " + stem, reason_code="CATALOG_PLANE")
    for stem in ("entra_oid", "seat click", "live_pin_ok", "cloudflare", "asuid", "graph"):
        if not any(stem in item for item in cannot):
            raise IntegrityError("gaps this_plane_cannot must keep " + stem, reason_code="CATALOG_PLANE")
    if "do not invent" not in str(gaps.get("note") or "").lower():
        raise IntegrityError("gaps note must refuse invented owner clicks", reason_code="CATALOG_PLANE")
    floor = body.get("proof_day_floor") or {}
    if "gaps" not in (floor.get("owner_shows") or []) or "gaps" not in (floor.get("entire_shows") or []):
        raise IntegrityError("gaps board sits Owner and Entire", reason_code="CATALOG_PLANE")
    if "gaps" in (floor.get("client_shows") or []) or "gaps" in (floor.get("client_hides") or []):
        raise IntegrityError("Client proof-day Floor does not sit the gaps board", reason_code="CATALOG_PLANE")
    well = [str(item).lower() for item in ((catalog.get("expert_review") or {}).get("working_well") or [])]
    if not any("gold floor" in item and "95" in item for item in well):
        raise IntegrityError("working_well must keep gold floor 95", reason_code="CATALOG_REVIEW")
    if not any("gaps board" in item for item in well):
        raise IntegrityError("working_well must keep the gaps board", reason_code="CATALOG_REVIEW")
    traction = str(((catalog.get("investor") or {}).get("traction") or "")).lower()
    if "95" not in traction or "gold floor" not in traction:
        raise IntegrityError("investor traction must keep gold floor 95", reason_code="CATALOG_INVESTOR")
    closed_eng = [str(item).lower() for item in ((catalog.get("engineering") or {}).get("closed_in_tree") or [])]
    if not any("2.72.0" in item and "95" in item for item in closed_eng):
        raise IntegrityError("closed_in_tree must keep 2.72.0 gold floor 95", reason_code="CATALOG_ENGINEERING")


def _validate_instrument_273(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    closed_eng = [str(item).lower() for item in ((catalog.get("engineering") or {}).get("closed_in_tree") or [])]
    if not any("2.73.0" in item and "floor" in item for item in closed_eng):
        raise IntegrityError("closed_in_tree must keep 2.73.0 Floor view_shows", reason_code="CATALOG_ENGINEERING")
    floor = body.get("proof_day_floor") or {}
    view_shows = floor.get("view_shows")
    if not isinstance(view_shows, dict) or not view_shows:
        raise IntegrityError("proof-day Floor needs catalog view_shows", reason_code="CATALOG_PLANE")
    client = [str(item) for item in view_shows.get("client") or []]
    owner = [str(item) for item in view_shows.get("owner") or []]
    entire = [str(item) for item in view_shows.get("entire") or []]
    provision = [str(item) for item in view_shows.get("provision") or []]
    if "gaps" in client or "estate" in client or "audit" in client:
        raise IntegrityError("Client view_shows must stay lean", reason_code="CATALOG_PLANE")
    if "gaps" not in owner or "gaps" not in entire:
        raise IntegrityError("Owner and Entire view_shows must include gaps", reason_code="CATALOG_PLANE")
    if "provision_path" not in provision:
        raise IntegrityError("Provision view_shows must include provision_path", reason_code="CATALOG_PLANE")
    if "board_packet" not in owner:
        raise IntegrityError("Owner view_shows must include board_packet", reason_code="CATALOG_PLANE")
    if "board_packet" not in (floor.get("owner_shows") or []):
        raise IntegrityError("owner_shows must include board_packet", reason_code="CATALOG_PLANE")
    if "provision_path" not in (floor.get("provision_shows") or []):
        raise IntegrityError("provision_shows must include provision_path", reason_code="CATALOG_PLANE")
    hints = floor.get("duty_hints")
    if not isinstance(hints, dict):
        raise IntegrityError("proof-day Floor needs duty hints", reason_code="CATALOG_PLANE")
    for view in (
        "client",
        "entire",
        "owner",
        "seats",
        "examiner",
        "remote",
        "it",
        "provision",
        "records",
    ):
        if view not in hints or not str(hints[view]).strip():
            raise IntegrityError(f"duty hint missing for {view}", reason_code="CATALOG_PLANE")
    demo = ((body.get("examiner_walk") or {}).get("demo") or {})
    if demo.get("record_id") != "lab.demo.inclusion":
        raise IntegrityError("examiner demo leaf must be lab.demo.inclusion", reason_code="CATALOG_PLANE")
    if demo.get("included") is not True or demo.get("lab") is not True:
        raise IntegrityError("examiner demo leaf is a lab inclusion, not a named record", reason_code="CATALOG_PLANE")
    hrefs = (body.get("gaps") or {}).get("owner_only_hrefs")
    if not isinstance(hrefs, dict) or not hrefs:
        raise IntegrityError("owner-only gaps must have hrefs", reason_code="CATALOG_PLANE")
    for stem in ("missing", "twin", "stack-walk", "open"):
        if stem not in " ".join(str(item) for item in hrefs.values()):
            raise IntegrityError(f"owner-only hrefs must walk to {stem}", reason_code="CATALOG_PLANE")
    lab = body.get("lab_vs_commercial")
    if not isinstance(lab, dict):
        raise IntegrityError("catalog missing lab vs commercial", reason_code="CATALOG_PLANE")
    if lab.get("sku") is True or lab.get("live") is True or lab.get("live_pin_ok") is True:
        raise IntegrityError("lab vs commercial is not a SKU or live", reason_code="CATALOG_PLANE")
    if lab.get("lab_pin") != "AINAV-L1":
        raise IntegrityError("lab pin must stay AINAV-L1", reason_code="CATALOG_PLANE")
    if lab.get("commercial_close") is not False:
        raise IntegrityError("commercial close must stay false", reason_code="CATALOG_PLANE")
    packet = body.get("board_packet")
    if not isinstance(packet, dict):
        raise IntegrityError("catalog missing board packet", reason_code="CATALOG_PLANE")
    if packet.get("sku") is True or packet.get("live") is True or packet.get("live_pin_ok") is True:
        raise IntegrityError("board packet is not a SKU or live", reason_code="CATALOG_PLANE")
    tiles = [str(item) for item in packet.get("tile_ids") or []]
    for needed in ("must_have", "pending_admits", "seats_recorded", "signed_l1", "recognized_revenue"):
        if needed not in tiles:
            raise IntegrityError(f"board packet must include {needed}", reason_code="CATALOG_PLANE")
    if "seat b" not in str(packet.get("ask") or "").lower():
        raise IntegrityError("board packet ask must stay seat B click", reason_code="CATALOG_PLANE")
    well = [str(item).lower() for item in ((catalog.get("expert_review") or {}).get("working_well") or [])]
    if not any("catalog-driven floor" in item or "view_shows" in item for item in well):
        raise IntegrityError("working_well must keep catalog-driven Floor", reason_code="CATALOG_REVIEW")
    if not any("provision spine" in item for item in well):
        raise IntegrityError("working_well must keep the provision spine", reason_code="CATALOG_REVIEW")
    if not any("board packet" in item for item in well):
        raise IntegrityError("working_well must keep the board packet", reason_code="CATALOG_REVIEW")
    improve = [str(item).lower() for item in ((catalog.get("expert_review") or {}).get("improve") or [])]
    if not any("seat b click" in item for item in improve):
        raise IntegrityError("improve must still name seat B click", reason_code="CATALOG_REVIEW")
    upgrades = (catalog.get("expert_review") or {}).get("upgrades") or []
    by_n = {item.get("n"): item for item in upgrades}
    for number, needle in (
        (33, "visibility"),
        (34, "provision"),
        (35, "duty"),
        (36, "freeze"),
        (37, "examiner"),
        (38, "gaps"),
        (39, "packet"),
        (40, "lab"),
    ):
        item = by_n.get(number) or {}
        blob = f"{item.get('title') or ''} {item.get('do') or ''}".lower()
        if needle not in blob:
            raise IntegrityError(f"2.73.0 upgrade {number} must mention {needle}", reason_code="CATALOG_REVIEW")
        if item.get("who") != "tree" or item.get("done") is not True:
            raise IntegrityError(f"2.73.0 upgrade {number} must stay tree and done", reason_code="CATALOG_REVIEW")


def _validate_instrument_274(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    closed_eng = [str(item).lower() for item in ((catalog.get("engineering") or {}).get("closed_in_tree") or [])]
    if not any("2.74.0" in item and "quality" in item for item in closed_eng):
        raise IntegrityError("closed_in_tree must keep 2.74.0 Cloudflare quality", reason_code="CATALOG_ENGINEERING")
    quality = ((catalog.get("microsoft_stack") or {}).get("edge") or {}).get("quality") or {}
    if quality.get("ssl_full_claimed") is True or quality.get("apex_is_institute") is True:
        raise IntegrityError("2.74.0 cannot claim SSL Full or apex Institute", reason_code="CATALOG_EDGE")
    if quality.get("rocket_loader_claimed") is True:
        raise IntegrityError("2.74.0 cannot claim Rocket Loader Off", reason_code="CATALOG_EDGE")
    verified = " ".join(str(item).lower() for item in quality.get("verified") or [])
    if "tls" not in verified or "anycast" not in verified:
        raise IntegrityError("2.74.0 quality verified must keep tls and anycast", reason_code="CATALOG_EDGE")
    gaps = body.get("gaps") or {}
    owner = [str(item).lower() for item in gaps.get("owner_only_open") or []]
    if not any("seat b" in item for item in owner):
        raise IntegrityError("2.74.0 owner-only must still name seat B click", reason_code="CATALOG_PLANE")
    hrefs = " ".join(str(item) for item in (gaps.get("owner_only_hrefs") or {}).values())
    if "e7-cloudflare" not in hrefs:
        raise IntegrityError("2.74.0 owner-only hrefs must walk to #e7-cloudflare", reason_code="CATALOG_PLANE")
    closed = [str(item).lower() for item in gaps.get("in_tree_closed") or []]
    if not any("quality" in item and "anycast" in item for item in closed):
        raise IntegrityError("gaps in_tree_closed must keep the quality live probe", reason_code="CATALOG_PLANE")
    interface = str((catalog.get("equations") or {}).get("interface") or "").lower()
    if "edge quality" not in interface:
        raise IntegrityError("interface equation must keep edge quality", reason_code="CATALOG_EQUATION")
    well = [str(item).lower() for item in ((catalog.get("expert_review") or {}).get("working_well") or [])]
    if not any("quality probe" in item or "live cloudflare quality" in item for item in well):
        raise IntegrityError("working_well must keep the live quality probe", reason_code="CATALOG_REVIEW")
    improve = [str(item).lower() for item in ((catalog.get("expert_review") or {}).get("improve") or [])]
    if not any("ssl" in item and "full" in item and "rocket" in item for item in improve):
        raise IntegrityError("improve must keep SSL Full and Rocket Loader as owner confirm", reason_code="CATALOG_REVIEW")
    upgrades = (catalog.get("expert_review") or {}).get("upgrades") or []
    by_n = {item.get("n"): item for item in upgrades}
    for number, needle in ((41, "probe"), (42, "tls"), (43, "anycast"), (44, "visitor")):
        item = by_n.get(number) or {}
        blob = f"{item.get('title') or ''} {item.get('do') or ''}".lower()
        if needle not in blob:
            raise IntegrityError(f"2.74.0 upgrade {number} must mention {needle}", reason_code="CATALOG_REVIEW")
        if item.get("who") != "tree" or item.get("done") is not True:
            raise IntegrityError(f"2.74.0 upgrade {number} must stay tree and done", reason_code="CATALOG_REVIEW")


def _validate_instrument_275(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    closed_eng = [str(item).lower() for item in ((catalog.get("engineering") or {}).get("closed_in_tree") or [])]
    if not any("2.75.0" in item and "full (strict)" in item for item in closed_eng):
        raise IntegrityError("closed_in_tree must keep 2.75.0 Full (strict)", reason_code="CATALOG_ENGINEERING")
    quality = ((catalog.get("microsoft_stack") or {}).get("edge") or {}).get("quality") or {}
    if quality.get("ssl_full_claimed") is True or quality.get("apex_is_institute") is True:
        raise IntegrityError("2.75.0 cannot claim SSL Full from this plane", reason_code="CATALOG_EDGE")
    owner_ssl = quality.get("owner_ssl") or {}
    if owner_ssl.get("mode") != "full_strict" or owner_ssl.get("automatic") is not True:
        raise IntegrityError("2.75.0 owner_ssl is Automatic Full (strict)", reason_code="CATALOG_EDGE")
    if owner_ssl.get("from_this_plane") is True:
        raise IntegrityError("2.75.0 owner_ssl is not from this plane", reason_code="CATALOG_EDGE")
    recorded = " ".join(str(item).lower() for item in quality.get("owner_recorded") or [])
    if "full (strict)" not in recorded:
        raise IntegrityError("2.75.0 owner_recorded must keep Full (strict)", reason_code="CATALOG_EDGE")
    gaps = body.get("gaps") or {}
    owner = [str(item).lower() for item in gaps.get("owner_only_open") or []]
    if not any("seat b" in item for item in owner):
        raise IntegrityError("2.75.0 owner-only must still name seat B click", reason_code="CATALOG_PLANE")
    if not any("rocket" in item for item in owner):
        raise IntegrityError("2.75.0 owner-only must still name Rocket Loader confirm", reason_code="CATALOG_PLANE")
    if any("ssl full confirm" in item for item in owner):
        raise IntegrityError("2.75.0 SSL Full confirm is recorded, not still open", reason_code="CATALOG_PLANE")
    closed = [str(item).lower() for item in gaps.get("in_tree_closed") or []]
    if not any("full (strict)" in item and "owner recorded" in item for item in closed):
        raise IntegrityError("gaps in_tree_closed must keep owner recorded Full (strict)", reason_code="CATALOG_PLANE")
    well = [str(item).lower() for item in ((catalog.get("expert_review") or {}).get("working_well") or [])]
    if not any("full (strict)" in item and "owner recorded" in item for item in well):
        raise IntegrityError("working_well must keep owner recorded Full (strict)", reason_code="CATALOG_REVIEW")
    upgrades = (catalog.get("expert_review") or {}).get("upgrades") or []
    by_n = {item.get("n"): item for item in upgrades}
    item = by_n.get(45) or {}
    blob = f"{item.get('title') or ''} {item.get('do') or ''}".lower()
    if "full (strict)" not in blob or "owner" not in blob:
        raise IntegrityError("2.75.0 upgrade 45 must mention owner Full (strict)", reason_code="CATALOG_REVIEW")
    if item.get("who") != "tree" or item.get("done") is not True:
        raise IntegrityError("2.75.0 upgrade 45 must stay tree and done", reason_code="CATALOG_REVIEW")


def _validate_instrument_276(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    closed_eng = [str(item).lower() for item in ((catalog.get("engineering") or {}).get("closed_in_tree") or [])]
    if not any("2.76.0" in item and "service principal" in item for item in closed_eng):
        raise IntegrityError("closed_in_tree must keep 2.76.0 leftover service principal", reason_code="CATALOG_ENGINEERING")
    graph = (catalog.get("microsoft_stack") or {}).get("graph") or {}
    if graph.get("kind") != "ainav.graph.owner_consent.v1":
        raise IntegrityError("2.76.0 graph kind is ainav.graph.owner_consent.v1", reason_code="CATALOG_STACK")
    if graph.get("from_this_plane") is True:
        raise IntegrityError("2.76.0 cannot claim Graph from this plane", reason_code="CATALOG_STACK")
    if graph.get("graph_write_claimed") is True:
        raise IntegrityError("2.76.0 cannot claim Graph Write", reason_code="CATALOG_STACK")
    recorded = " ".join(str(item).lower() for item in graph.get("owner_recorded") or [])
    if "speech" not in recorded or "service principal" not in recorded:
        raise IntegrityError("2.76.0 owner_recorded must keep leftover Speech and service principal", reason_code="CATALOG_STACK")
    walk = next(
        (
            item
            for item in ((catalog.get("microsoft_stack") or {}).get("walk") or {}).get("path") or []
            if item.get("id") == "graph.read"
        ),
        {},
    )
    owner_blob = f"{walk.get('owner') or ''} {walk.get('in_tree') or ''}".lower()
    if "leftover" not in owner_blob or "key vault" not in owner_blob:
        raise IntegrityError("2.76.0 graph.read walk must keep leftover Key Vault", reason_code="CATALOG_STACK")
    gaps = body.get("gaps") or {}
    closed = [str(item).lower() for item in gaps.get("in_tree_closed") or []]
    if not any("service principal" in item and "leftover" in item for item in closed):
        raise IntegrityError("gaps in_tree_closed must keep leftover service principal", reason_code="CATALOG_PLANE")
    well = [str(item).lower() for item in ((catalog.get("expert_review") or {}).get("working_well") or [])]
    if not any("leftover" in item and "service principal" in item for item in well):
        raise IntegrityError("working_well must keep leftover service principal", reason_code="CATALOG_REVIEW")
    interface = str((catalog.get("equations") or {}).get("interface") or "").lower()
    if "graph owner consent" not in interface:
        raise IntegrityError("interface equation must keep graph owner consent", reason_code="CATALOG_EQUATION")
    upgrades = (catalog.get("expert_review") or {}).get("upgrades") or []
    by_n = {item.get("n"): item for item in upgrades}
    item = by_n.get(46) or {}
    blob = f"{item.get('title') or ''} {item.get('do') or ''}".lower()
    if "leftover" not in blob or "service principal" not in blob:
        raise IntegrityError("2.76.0 upgrade 46 must mention leftover service principal", reason_code="CATALOG_REVIEW")
    if item.get("who") != "tree" or item.get("done") is not True:
        raise IntegrityError("2.76.0 upgrade 46 must stay tree and done", reason_code="CATALOG_REVIEW")
    if item.get("marks_live_pin") is True:
        raise IntegrityError("2.76.0 upgrade 46 cannot mark LIVE_PIN_OK", reason_code="LIVE_PIN_NOT_CLAIMED")


def _validate_instrument_277(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    closed_eng = [str(item).lower() for item in ((catalog.get("engineering") or {}).get("closed_in_tree") or [])]
    if not any("2.77.0" in item and "four reads" in item for item in closed_eng):
        raise IntegrityError("closed_in_tree must keep 2.77.0 four Reads Granted", reason_code="CATALOG_ENGINEERING")
    graph = (catalog.get("microsoft_stack") or {}).get("graph") or {}
    if graph.get("four_reads_granted") is not True or graph.get("tenant_wide_grant_ok") is not True:
        raise IntegrityError("2.77.0 four Reads are Granted", reason_code="CATALOG_STACK")
    if graph.get("graph_write_claimed") is True or graph.get("from_this_plane") is True:
        raise IntegrityError("2.77.0 cannot claim Graph Write or consent from this plane", reason_code="CATALOG_STACK")
    if graph.get("status") != "four_reads_granted_writes_open":
        raise IntegrityError("2.77.0 graph status is four_reads_granted_writes_open", reason_code="CATALOG_STACK")
    if graph.get("error") != "graph_writes_still_granted":
        raise IntegrityError("2.77.0 Graph Writes still Granted", reason_code="CATALOG_STACK")
    writes = " ".join(str(item) for item in graph.get("writes_still_granted") or [])
    if "Organization.ReadWrite.All" not in writes or "User.ReadWrite.All" not in writes:
        raise IntegrityError("2.77.0 writes_still_granted must name the three Graph Writes", reason_code="CATALOG_STACK")
    recorded = " ".join(str(item).lower() for item in graph.get("owner_recorded") or [])
    if "successfully granted" not in recorded or "four reads" not in recorded:
        raise IntegrityError("2.77.0 owner_recorded must keep Grant succeeded and four Reads", reason_code="CATALOG_STACK")
    walk = next(
        (
            item
            for item in ((catalog.get("microsoft_stack") or {}).get("walk") or {}).get("path") or []
            if item.get("id") == "graph.read"
        ),
        {},
    )
    if walk.get("status") != "four_reads_granted_writes_open":
        raise IntegrityError("2.77.0 graph.read stays four_reads_granted_writes_open", reason_code="CATALOG_STACK")
    owner_blob = f"{walk.get('owner') or ''} {walk.get('in_tree') or ''}".lower()
    if "readwrite" not in owner_blob or "revoke" not in owner_blob:
        raise IntegrityError("2.77.0 graph.read walk must revoke ReadWrite", reason_code="CATALOG_STACK")
    gaps = body.get("gaps") or {}
    owner = [str(item).lower() for item in gaps.get("owner_only_open") or []]
    if not any("graph write" in item for item in owner):
        raise IntegrityError("2.77.0 owner-only must name Graph Writes revoke", reason_code="CATALOG_PLANE")
    if any("graph read" == item.strip() for item in owner):
        raise IntegrityError("2.77.0 Graph Read four Reads are recorded, not still the open line", reason_code="CATALOG_PLANE")
    closed = [str(item).lower() for item in gaps.get("in_tree_closed") or []]
    if not any("four reads" in item and "granted" in item for item in closed):
        raise IntegrityError("gaps in_tree_closed must keep four Reads Granted", reason_code="CATALOG_PLANE")
    well = [str(item).lower() for item in ((catalog.get("expert_review") or {}).get("working_well") or [])]
    if not any("four reads" in item and "granted" in item for item in well):
        raise IntegrityError("working_well must keep four Reads Granted", reason_code="CATALOG_REVIEW")
    improve = [str(item).lower() for item in ((catalog.get("expert_review") or {}).get("improve") or [])]
    if not any("graph write" in item and "revoke" in item for item in improve):
        raise IntegrityError("improve must keep Graph Writes revoke", reason_code="CATALOG_REVIEW")
    upgrades = (catalog.get("expert_review") or {}).get("upgrades") or []
    by_n = {item.get("n"): item for item in upgrades}
    item = by_n.get(47) or {}
    blob = f"{item.get('title') or ''} {item.get('do') or ''}".lower()
    if "four reads" not in blob or "writes" not in blob:
        raise IntegrityError("2.77.0 upgrade 47 must mention four Reads and Writes", reason_code="CATALOG_REVIEW")
    if item.get("who") != "tree" or item.get("done") is not True:
        raise IntegrityError("2.77.0 upgrade 47 must stay tree and done", reason_code="CATALOG_REVIEW")
    if item.get("marks_live_pin") is True:
        raise IntegrityError("2.77.0 upgrade 47 cannot mark LIVE_PIN_OK", reason_code="LIVE_PIN_NOT_CLAIMED")


def _validate_instrument_278(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    if catalog.get("entity", {}).get("release") != "2.78.0":
        raise IntegrityError("entity.release is 2.78.0", reason_code="CATALOG_PLANE")
    closed_eng = [str(item).lower() for item in ((catalog.get("engineering") or {}).get("closed_in_tree") or [])]
    if not any("2.78.0" in item and "refus" in item for item in closed_eng):
        raise IntegrityError("closed_in_tree must keep 2.78.0 refused owner-gap close", reason_code="CATALOG_ENGINEERING")
    gaps = body.get("gaps") or {}
    if gaps.get("claimed") is True or gaps.get("live_pin_ok") is True:
        raise IntegrityError("2.78.0 cannot claim owner gaps or LIVE_PIN_OK closed", reason_code="CATALOG_PLANE")
    owner = [str(item).lower() for item in gaps.get("owner_only_open") or []]
    for stem in ("seat b", "graph write", "dataverse", "g12", "billing", "launch"):
        if not any(stem in item for item in owner):
            raise IntegrityError("2.78.0 owner-only must keep " + stem, reason_code="CATALOG_PLANE")
    opens = str((((catalog.get("investor") or {}).get("executive_summary") or {}).get("opens")) or "").lower()
    if "graph write" not in opens or "graph read on the same" in opens:
        raise IntegrityError("2.78.0 investor opens must name Graph Writes, not Graph Read", reason_code="CATALOG_INVESTOR")
    upgrades = (catalog.get("expert_review") or {}).get("upgrades") or []
    item = next((row for row in upgrades if row.get("n") == 48), {})
    blob = f"{item.get('title') or ''} {item.get('do') or ''}".lower()
    if "refus" not in blob or "live_pin_ok" not in blob:
        raise IntegrityError("2.78.0 upgrade 48 must refuse owner-gap close", reason_code="CATALOG_REVIEW")
    if item.get("who") != "tree" or item.get("done") is not True or item.get("marks_live_pin") is True:
        raise IntegrityError("2.78.0 upgrade 48 must stay tree, done, and not LIVE_PIN_OK", reason_code="LIVE_PIN_NOT_CLAIMED")


def _validate_instrument_271(catalog: dict[str, Any], body: dict[str, Any]) -> None:
    offer = body.get("included_and_upsells") or {}
    included = next(
        (
            item
            for item in ((offer.get("first_glance") or {}).get("columns") or [])
            if isinstance(item, dict) and item.get("id") == "included_with_l1"
        ),
        {},
    )
    included_blob = " ".join(str(item) for item in included.get("items") or []).lower()
    if "estate — same plane" in included_blob or "audit — same plane" in included_blob:
        raise IntegrityError("Client offer cannot leak Estate or Audit encyclopedia", reason_code="CATALOG_PLANE")
    if "encyclopedia" not in included_blob or "drawer" not in included_blob:
        raise IntegrityError("Client offer keeps encyclopedia as a drawer on Entire", reason_code="CATALOG_PLANE")
    floor = body.get("proof_day_floor") or {}
    if "pending_bind" not in (floor.get("client_shows") or []):
        raise IntegrityError("Client proof-day Floor sits the pending bind", reason_code="CATALOG_PLANE")
    if "examiner_walk" not in (floor.get("examiner_shows") or []):
        raise IntegrityError("Examiner proof-day Floor sits the examiner walk", reason_code="CATALOG_PLANE")
    if "freeze_console" not in (floor.get("owner_shows") or []):
        raise IntegrityError("Owner proof-day Floor sits the freeze console", reason_code="CATALOG_PLANE")
    if "continuity" not in (floor.get("seats_shows") or []) and "continuity" not in (floor.get("entire_shows") or []):
        raise IntegrityError("continuity rehearsal sits Seats or Entire", reason_code="CATALOG_PLANE")
    pending = body.get("pending_bind")
    if not isinstance(pending, dict):
        raise IntegrityError("catalog missing pending bind", reason_code="CATALOG_PLANE")
    if pending.get("sku") is True or pending.get("live") is True or pending.get("live_pin_ok") is True:
        raise IntegrityError("pending bind is not a SKU or live", reason_code="CATALOG_PLANE")
    if int(pending.get("count") or 0) != 0:
        raise IntegrityError("pending bind count stays zero until a named pair", reason_code="CATALOG_PLANE")
    if pending.get("named_pair") is True:
        raise IntegrityError("pending bind cannot invent a named pair", reason_code="CATALOG_PLANE")
    if pending.get("action_class") != "bc.general_journal.post":
        raise IntegrityError("pending bind walks the public wedge", reason_code="CATALOG_PLANE")
    if str(pending.get("seat_a") or "") or str(pending.get("seat_b") or "") or str(pending.get("action_hash") or ""):
        raise IntegrityError("pending bind wells stay empty", reason_code="CATALOG_PLANE")
    if pending.get("refuse") is not True or pending.get("local_rehearsal") is not True:
        raise IntegrityError("pending bind is a local refuse rehearsal", reason_code="CATALOG_PLANE")
    freeze = body.get("freeze_console")
    if not isinstance(freeze, dict):
        raise IntegrityError("catalog missing freeze console", reason_code="CATALOG_PLANE")
    if freeze.get("sku") is True or freeze.get("live") is True or freeze.get("live_pin_ok") is True:
        raise IntegrityError("freeze console is not a SKU or live", reason_code="CATALOG_PLANE")
    if freeze.get("verb") != "request":
        raise IntegrityError("freeze console verb is request", reason_code="CATALOG_PLANE")
    if freeze.get("catalog_plane_stays_open") is not True:
        raise IntegrityError("freeze request cannot close the catalog plane", reason_code="CATALOG_PLANE")
    if freeze.get("local_to_browser") is not True:
        raise IntegrityError("freeze console is local to the browser", reason_code="CATALOG_PLANE")
    if freeze.get("inference_may_continue") is not True or freeze.get("consequence_does_not") is not True:
        raise IntegrityError("freeze: inference may continue, consequence does not", reason_code="CATALOG_PLANE")
    walk = body.get("examiner_walk")
    if not isinstance(walk, dict):
        raise IntegrityError("catalog missing examiner walk", reason_code="CATALOG_PLANE")
    if walk.get("sku") is True or walk.get("live") is True:
        raise IntegrityError("examiner walk is not a SKU or live", reason_code="CATALOG_PLANE")
    if walk.get("read_only") is not True:
        raise IntegrityError("examiner walk is read-only", reason_code="CATALOG_PLANE")
    if walk.get("seventeen_a4") is True or walk.get("worm") is True or walk.get("claimed") is True:
        raise IntegrityError("examiner walk is not 17a-4, WORM, or claimed", reason_code="CATALOG_GOVERNANCE")
    if int(walk.get("named_records") or 0) != 0:
        raise IntegrityError("examiner walk named records stay zero", reason_code="CATALOG_PLANE")
    demo = walk.get("demo") or {}
    if demo.get("lab") is not True:
        raise IntegrityError("examiner walk demo stays lab", reason_code="CATALOG_PLANE")
    if demo.get("record_id") == "lab.demo.inclusion":
        if demo.get("included") is not True:
            raise IntegrityError("lab demo leaf is a lab inclusion, not a named record", reason_code="CATALOG_PLANE")
        if demo.get("leaf") != "lab" or demo.get("root") != "catalog":
            raise IntegrityError("lab demo leaf stays lab / catalog", reason_code="CATALOG_PLANE")
    else:
        if demo.get("included") is True:
            raise IntegrityError("examiner walk demo stays not included unless it is the lab leaf", reason_code="CATALOG_PLANE")
        if str(demo.get("record_id") or "") or str(demo.get("leaf") or "") or str(demo.get("root") or ""):
            raise IntegrityError("examiner walk cannot invent a named record", reason_code="CATALOG_PLANE")
    groups = (body.get("view_assignment") or {}).get("entra_groups")
    if not isinstance(groups, dict):
        raise IntegrityError("catalog missing Entra-group view templates", reason_code="CATALOG_PLANE")
    if groups.get("sku") is True or groups.get("live") is True or groups.get("assignment_live") is True:
        raise IntegrityError("Entra-group assignment is not live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if groups.get("do_not_invent_names") is not True or groups.get("named_head") is True:
        raise IntegrityError("Entra-group templates cannot invent named heads", reason_code="CATALOG_PLANE")
    if groups.get("cloud_agent_cannot_assign") is not True:
        raise IntegrityError("Cloud Agent cannot assign Entra groups", reason_code="CATALOG_PLANE")
    templates = groups.get("templates") or []
    if not templates:
        raise IntegrityError("Entra-group templates are required", reason_code="CATALOG_PLANE")
    for row in templates:
        if not isinstance(row, dict):
            raise IntegrityError("Entra-group template is an object", reason_code="CATALOG_PLANE")
        if row.get("named_head") is True:
            raise IntegrityError("Entra-group template cannot name a head", reason_code="CATALOG_PLANE")
        if not row.get("org_node") or not row.get("group") or not row.get("default_view"):
            raise IntegrityError("Entra-group template needs org node, group, and view", reason_code="CATALOG_PLANE")
    refuse = [str(item).lower() for item in (body.get("view_assignment") or {}).get("refuse") or []]
    for stem in ("entra group assignment live", "named department head"):
        if stem not in refuse:
            raise IntegrityError("view assignment must refuse " + stem, reason_code="CATALOG_PLANE")
    motions = body.get("motions")
    if not isinstance(motions, dict):
        raise IntegrityError("catalog missing client motions", reason_code="CATALOG_PLANE")
    if motions.get("sku") is True or motions.get("fourth_sku") is True or motions.get("live") is True:
        raise IntegrityError("motions are not a SKU", reason_code="CATALOG_SKU")
    small = motions.get("small_client") or {}
    if small.get("sku") is True or small.get("express_sku") is True or small.get("discount_udual") is True:
        raise IntegrityError("small-client motion is not a SKU and does not discount U-DUAL", reason_code="CATALOG_SKU")
    if small.get("same_l1") is not True or int(small.get("minutes") or 0) != 90:
        raise IntegrityError("small-client motion is the same L1 ninety minutes", reason_code="CATALOG_PLANE")
    price = small.get("price_usd") or {}
    if int(price.get("min") or 0) != 28000 or int(price.get("max") or 0) != 40000:
        raise IntegrityError("small-client motion stays $28–40k", reason_code="CATALOG_PLANE")
    if "workflow" not in str(small.get("walk_away_if") or "").lower():
        raise IntegrityError("small-client motion walks away from Workflow User Groups", reason_code="CATALOG_PLANE")
    large = motions.get("large_client") or {}
    if large.get("sku") is True or large.get("certificate") is True or large.get("claimed") is True:
        raise IntegrityError("large-client motion is not a certificate", reason_code="CATALOG_GOVERNANCE")
    if large.get("sox") is True or large.get("seventeen_a4") is True:
        raise IntegrityError("large-client motion cannot claim SOX or 17a-4", reason_code="CATALOG_GOVERNANCE")
    if large.get("same_three_skus") is not True or large.get("g12_open") is not True:
        raise IntegrityError("large-client motion keeps three SKUs and G12 open", reason_code="CATALOG_PLANE")
    packet = large.get("counsel_ready") or {}
    for needed in ("order_form", "msa_skeleton", "icfr_kit_case", "examiner_export", "off_switch_evidence"):
        if packet.get(needed) is not True:
            raise IntegrityError(f"large-client counsel packet must include {needed}", reason_code="CATALOG_PLANE")
    host = body.get("hostname_rehearsal")
    if not isinstance(host, dict):
        raise IntegrityError("catalog missing hostname rehearsal", reason_code="CATALOG_PLANE")
    if host.get("sku") is True or host.get("live") is True or host.get("launch") is True:
        raise IntegrityError("hostname rehearsal is not launch", reason_code="CATALOG_PLANE")
    if host.get("asuid_added") is True or host.get("cloudflare_edited_from_this_plane") is True:
        raise IntegrityError("hostname rehearsal cannot add asuid or edit Cloudflare", reason_code="CATALOG_PLANE")
    if host.get("pages_is_not_institute") is not True:
        raise IntegrityError("Pages is not the Institute", reason_code="CATALOG_PLANE")
    cutover = [str(item).lower() for item in host.get("cutover") or []]
    for stem in ("pages empty", "swa", "asuid only then", "james"):
        if not any(stem in item for item in cutover):
            raise IntegrityError("hostname rehearsal cutover must keep " + stem, reason_code="CATALOG_PLANE")
    competitive = body.get("competitive")
    if not isinstance(competitive, dict):
        raise IntegrityError("catalog missing competitive one-pager", reason_code="CATALOG_PLANE")
    if competitive.get("sku") is True or competitive.get("live") is True:
        raise IntegrityError("competitive one-pager is not a SKU or live", reason_code="CATALOG_PLANE")
    if competitive.get("uncopyable") is True or competitive.get("patent") is True:
        raise IntegrityError("do not say uncopyable or patent", reason_code="CATALOG_PLANE")
    if list(competitive.get("we_win_only") or []) != ["consume_once", "fail_closed_sor", "counterparty_ai"]:
        raise IntegrityError("we win only on consume-once, fail-closed SoR, and counterparty AI", reason_code="CATALOG_PLANE")
    if list(competitive.get("columns") or []) != [
        "covers_this_vendor",
        "consume_once",
        "fail_closed_sor",
        "counterparty_ai",
    ]:
        raise IntegrityError("competitive columns are vendor, consume-once, fail-closed, counterparty", reason_code="CATALOG_PLANE")
    row_ids = [item.get("id") for item in competitive.get("rows") or [] if isinstance(item, dict)]
    for needed in ("job_c", "bc_workflow", "copilot_studio", "pim", "grc_icfr", "in_harness"):
        if needed not in row_ids:
            raise IntegrityError(f"competitive one-pager must include {needed}", reason_code="CATALOG_PLANE")
    job = next((item for item in competitive.get("rows") or [] if item.get("id") == "job_c"), {})
    if not (
        job.get("covers_this_vendor") is True
        and job.get("consume_once") is True
        and job.get("fail_closed_sor") is True
        and job.get("counterparty_ai") is True
    ):
        raise IntegrityError("Job C wins all four competitive columns", reason_code="CATALOG_PLANE")
    for item in competitive.get("rows") or []:
        if item.get("id") == "job_c":
            continue
        if item.get("consume_once") is True or item.get("fail_closed_sor") is True or item.get("counterparty_ai") is True:
            raise IntegrityError("substitutes do not win consume-once, fail-closed, or counterparty", reason_code="CATALOG_PLANE")
    if "uncopyable" in str(competitive.get("note") or "").lower() and "do not say uncopyable" not in str(
        competitive.get("note") or ""
    ).lower():
        raise IntegrityError("competitive note cannot claim uncopyable", reason_code="CATALOG_PLANE")
    success = (catalog.get("expert_review") or {}).get("success") or {}
    rehearsal = (success.get("continuity") or {}).get("rehearsal") or {}
    if not isinstance(rehearsal, dict) or not rehearsal:
        raise IntegrityError("continuity needs a Tuesday rehearsal", reason_code="CATALOG_REVIEW")
    if rehearsal.get("sku") is True or rehearsal.get("live") is True:
        raise IntegrityError("continuity rehearsal is not a SKU or live", reason_code="CATALOG_REVIEW")
    if rehearsal.get("write_lands") is True or rehearsal.get("sealed_deny") is not True:
        raise IntegrityError("continuity rehearsal: write does not land, sealed deny", reason_code="CATALOG_REVIEW")
    if str(rehearsal.get("seat_missing") or "") != "seat_b":
        raise IntegrityError("continuity rehearsal is seat B absent", reason_code="CATALOG_REVIEW")


def _validate_plane_interface(catalog: dict[str, Any]) -> None:
    body = catalog.get("plane_interface")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing plane interface", reason_code="CATALOG_PLANE")
    if body.get("sku") is True:
        raise IntegrityError("plane interface is not a SKU", reason_code="CATALOG_SKU")
    if body.get("live") is True or body.get("live_pin_ok") is True:
        raise IntegrityError("plane interface cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if body.get("certified") is True or body.get("real_time_claimed") is True or body.get("forecast") is True:
        raise IntegrityError("plane interface cannot claim live metrics or certification", reason_code="CATALOG_PLANE")
    thesis = str(body.get("thesis") or "").lower()
    letter = str(body.get("letter") or "").lower()
    for stem in ("human", "dashboard", "remote", "compliance", "not a fourth"):
        blob = thesis + " " + letter
        if stem not in blob and not (stem == "not a fourth" and "not a fourth" in blob):
            if stem == "not a fourth" and "fourth sku" in " ".join(body.get("refuse") or []).lower():
                continue
            if stem not in blob:
                raise IntegrityError(f"plane interface must keep {stem}", reason_code="CATALOG_PLANE")
    ids = [item.get("id") for item in body.get("levels") or []]
    for needed in ("owner", "board", "seat_a", "seat_b", "remote", "agent"):
        if needed not in ids:
            raise IntegrityError(f"plane interface levels must include {needed}", reason_code="CATALOG_PLANE")
    access = body.get("access") or {}
    if access.get("same_plane") is not True or access.get("second_remote_plane") is True:
        raise IntegrityError("remote access is the same plane", reason_code="CATALOG_PLANE")
    if access.get("vpn_sku") is True:
        raise IntegrityError("remote access is not a VPN SKU", reason_code="CATALOG_SKU")
    dash = body.get("dashboard") or {}
    if dash.get("sku") is True or dash.get("upsell") is True:
        raise IntegrityError("dashboard is not a SKU", reason_code="CATALOG_SKU")
    if dash.get("included_with") != "L1":
        raise IntegrityError("dashboard is included with L1", reason_code="CATALOG_PLANE")
    client_dash = body.get("client_dashboard")
    if not isinstance(client_dash, dict):
        raise IntegrityError("catalog missing client dashboard", reason_code="CATALOG_PLANE")
    if client_dash.get("sku") is True or client_dash.get("upsell") is True:
        raise IntegrityError("client dashboard is not a SKU or an upsell", reason_code="CATALOG_SKU")
    if client_dash.get("included_with") != "L1":
        raise IntegrityError("client dashboard is included with L1", reason_code="CATALOG_PLANE")
    if client_dash.get("live") is True:
        raise IntegrityError("client dashboard cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if client_dash.get("standard_vs_advanced_dashboard") is True:
        raise IntegrityError("do not sell Standard vs Advanced dashboard", reason_code="CATALOG_SKU")
    if client_dash.get("same_as") != "dashboard":
        raise IntegrityError("client dashboard is the same dashboard", reason_code="CATALOG_PLANE")
    if dash.get("same_as") != "client_dashboard":
        raise IntegrityError("dashboard is the client dashboard", reason_code="CATALOG_PLANE")
    board = client_dash.get("executive_board") or {}
    if not isinstance(board, dict):
        raise IntegrityError("catalog missing executive board", reason_code="CATALOG_PLANE")
    if board.get("sku") is True or board.get("upsell") is True:
        raise IntegrityError("executive board is not a SKU or an upsell", reason_code="CATALOG_SKU")
    if board.get("included_with") != "L1":
        raise IntegrityError("executive board is included with L1", reason_code="CATALOG_PLANE")
    if board.get("same_as") != "client_dashboard":
        raise IntegrityError("executive board is the client dashboard", reason_code="CATALOG_PLANE")
    if board.get("default_view") != "client":
        raise IntegrityError("executive board sits the client view first", reason_code="CATALOG_PLANE")
    board_lede = str(board.get("lede") or "").lower()
    if "sit the plane" not in board_lede or "one dashboard" not in board_lede:
        raise IntegrityError("executive board lede is sit the plane on one dashboard", reason_code="CATALOG_PLANE")
    section_ids = [item.get("id") for item in board.get("sections") or [] if isinstance(item, dict)]
    if section_ids != ["write_rail", "attention", "seats", "keep", "offer"]:
        raise IntegrityError("executive board is write rail, attention, seats, keep, offer", reason_code="CATALOG_PLANE")
    attention_ids = list(board.get("attention_ids") or [])
    if "must_have" not in attention_ids or "pending" not in attention_ids:
        raise IntegrityError("executive board attention keeps must-have and pending", reason_code="CATALOG_PLANE")
    if "seats_recorded" not in (board.get("seat_tile_ids") or []):
        raise IntegrityError("executive board seats keep seats recorded", reason_code="CATALOG_PLANE")
    if "second_record" not in (board.get("keep_tile_ids") or []):
        raise IntegrityError("executive board keep keeps the second record", reason_code="CATALOG_PLANE")
    if "signed_l1" not in (board.get("tile_ids") or []):
        raise IntegrityError("executive board ledger keeps signed L1", reason_code="CATALOG_PLANE")
    client_view = next(
        (item for item in body.get("views") or [] if isinstance(item, dict) and item.get("id") == "client"),
        {},
    )
    if "write_rail" not in (client_view.get("shows") or []) or "offer" not in (client_view.get("shows") or []):
        raise IntegrityError("client view sits the executive board", reason_code="CATALOG_PLANE")
    dash_glance = dash.get("first_glance") or {}
    if not isinstance(dash_glance, dict):
        raise IntegrityError("dashboard first glance is required", reason_code="CATALOG_PLANE")
    if dash_glance.get("sku") is True:
        raise IntegrityError("dashboard first glance is not a SKU", reason_code="CATALOG_SKU")
    if dash_glance.get("same_as") != "client_dashboard":
        raise IntegrityError("dashboard first glance is the client dashboard", reason_code="CATALOG_PLANE")
    if dash_glance.get("uses") != "write_rail":
        raise IntegrityError("dashboard first glance uses the write rail", reason_code="CATALOG_PLANE")
    dash_lede = str(dash_glance.get("lede") or "").lower()
    if "one dashboard" not in dash_lede or "same plane" not in dash_lede:
        raise IntegrityError("dashboard first glance is one dashboard on the same plane", reason_code="CATALOG_PLANE")
    dash_rail = [item.get("id") for item in dash_glance.get("write_rail") or []]
    if dash_rail != ["seat_a", "seat_b", "hash", "write"]:
        raise IntegrityError("dashboard write rail is seat A, seat B, hash, then the write", reason_code="CATALOG_PLANE")
    bands = body.get("provision_bands") or {}
    if bands.get("sku") is True:
        raise IntegrityError("provision bands are not a SKU", reason_code="CATALOG_SKU")
    band_items = {item.get("id"): item for item in bands.get("items") or []}
    if "provision.standard" not in band_items or "provision.advanced" not in band_items:
        raise IntegrityError("provision bands must include standard and advanced", reason_code="CATALOG_PLANE")
    standard = band_items["provision.standard"]
    advanced = band_items["provision.advanced"]
    if standard.get("sku") is True or advanced.get("sku") is True:
        raise IntegrityError("a provision band is not a SKU", reason_code="CATALOG_SKU")
    if standard.get("upsell") is True:
        raise IntegrityError("standard provision is not an upsell", reason_code="CATALOG_PLANE")
    if advanced.get("upsell") is not True:
        raise IntegrityError("advanced provision is the upsell band", reason_code="CATALOG_PLANE")
    if standard.get("requires_sku") != "L1" or advanced.get("requires_sku") != "L1":
        raise IntegrityError("provision bands require L1", reason_code="CATALOG_PLANE")
    if advanced.get("u_dual_never_free") is not True:
        raise IntegrityError("U-DUAL is never free", reason_code="CATALOG_PLANE")
    if advanced.get("hours_never_attach_udual") is not True:
        raise IntegrityError("hours never attach U-DUAL", reason_code="CATALOG_PLANE")
    if "included with" not in str(bands.get("attach_means") or "").lower():
        raise IntegrityError("included means included with the required SKU", reason_code="CATALOG_PLANE")
    if bands.get("week_one") != "provisioning.standard_l1":
        raise IntegrityError("week-one prove stays standard_l1", reason_code="CATALOG_PLANE")
    offer = body.get("included_and_upsells") or {}
    if not isinstance(offer, dict):
        raise IntegrityError("catalog missing included and upsells", reason_code="CATALOG_PLANE")
    if offer.get("sku") is True or offer.get("fourth_sku") is True:
        raise IntegrityError("included and upsells is not a SKU", reason_code="CATALOG_SKU")
    if offer.get("included_means_free") is True:
        raise IntegrityError("included does not mean free", reason_code="CATALOG_PLANE")
    if offer.get("u_dual_never_free") is not True:
        raise IntegrityError("U-DUAL is never free", reason_code="CATALOG_PLANE")
    if offer.get("hours_never_attach_udual") is not True:
        raise IntegrityError("hours never attach U-DUAL", reason_code="CATALOG_PLANE")
    if offer.get("standard_vs_advanced_dashboard") is True:
        raise IntegrityError("do not sell Standard vs Advanced dashboard", reason_code="CATALOG_SKU")
    if str(offer.get("attach_means") or "") != str(bands.get("attach_means") or ""):
        raise IntegrityError("included attach_means must match provision bands", reason_code="CATALOG_PLANE")
    thesis = str(offer.get("thesis") or "").lower()
    if "not free" not in thesis or "three sku" not in thesis or "upsell band" not in thesis:
        raise IntegrityError("included thesis is seating vs upsell band, not free, three SKUs", reason_code="CATALOG_PLANE")
    glance = offer.get("first_glance") or {}
    if not isinstance(glance, dict):
        raise IntegrityError("included and upsells first glance is required", reason_code="CATALOG_PLANE")
    if glance.get("sku") is True:
        raise IntegrityError("included and upsells first glance is not a SKU", reason_code="CATALOG_SKU")
    lede = str(glance.get("lede") or "").lower()
    if "not a gift" not in lede or "upsell band" not in lede or "fourth sku" not in lede:
        raise IntegrityError("included first glance is seating vs upsell, not a fourth SKU", reason_code="CATALOG_PLANE")
    columns = {item.get("id"): item for item in glance.get("columns") or [] if isinstance(item, dict)}
    if set(columns) != {"included_with_l1", "upsell_band"}:
        raise IntegrityError("included and upsells needs included_with_l1 and upsell_band", reason_code="CATALOG_PLANE")
    included = columns["included_with_l1"]
    upsell = columns["upsell_band"]
    if included.get("sku") is True or upsell.get("sku") is True:
        raise IntegrityError("an included or upsell column is not a SKU", reason_code="CATALOG_SKU")
    if included.get("upsell") is True or included.get("band") != "provision.standard":
        raise IntegrityError("included with L1 is standard provision, not an upsell", reason_code="CATALOG_PLANE")
    if upsell.get("upsell") is not True or upsell.get("band") != "provision.advanced":
        raise IntegrityError("upsell band is advanced provision", reason_code="CATALOG_PLANE")
    included_blob = " ".join(str(item) for item in included.get("items") or []).lower()
    if "week-one" not in included_blob or "dashboard" not in included_blob or "included_in_sku" not in included_blob:
        raise IntegrityError("included column must keep week-one, dashboard, and included seating", reason_code="CATALOG_PLANE")
    upsell_blob = " ".join(str(item) for item in upsell.get("items") or []).lower()
    if "p-adm" not in upsell_blob or "u-dual" not in upsell_blob or "hours" not in upsell_blob:
        raise IntegrityError("upsell column must keep priced desks, P-ADM, U-DUAL, and hours", reason_code="CATALOG_PLANE")
    if "never free" not in upsell_blob:
        raise IntegrityError("upsell column must keep U-DUAL never free", reason_code="CATALOG_PLANE")
    refuse = [str(item).lower() for item in offer.get("refuse") or []]
    for stem in ("included means free", "fourth sku", "u-dual free with p-adm", "dashboard as sku"):
        if stem not in refuse:
            raise IntegrityError("included and upsells must refuse " + stem, reason_code="CATALOG_PLANE")
    floor = body.get("floor") or {}
    lede = str(floor.get("lede") or "").lower()
    if "one dashboard" not in lede or "included with l1" not in lede:
        raise IntegrityError("floor lede must keep one dashboard included with L1", reason_code="CATALOG_PLANE")
    if "must-have" not in lede or "write surface" not in lede or "two humans" not in lede:
        raise IntegrityError("floor lede must keep must-have write surface", reason_code="CATALOG_PLANE")
    if "already have" not in lede or "gate" not in lede:
        raise IntegrityError("floor lede must keep already-have and the gate", reason_code="CATALOG_PLANE")
    already = str(floor.get("already_have") or "").lower()
    if "business central" not in already or "entra" not in already or "sod" not in already:
        raise IntegrityError("already-have is BC, Entra, and journal SOD", reason_code="CATALOG_PLANE")
    if "gate" not in str(floor.get("still_lack") or "").lower():
        raise IntegrityError("still-lack is the gate in front of the write", reason_code="CATALOG_PLANE")
    floor_must = floor.get("must_have") or {}
    if not isinstance(floor_must, dict):
        raise IntegrityError("floor must-have is required", reason_code="CATALOG_PLANE")
    if floor_must.get("sku") is True or floor_must.get("mandated") is True or floor_must.get("certified") is True:
        raise IntegrityError("must-have is not a SKU, mandate, or certificate", reason_code="CATALOG_GOVERNANCE")
    gov_why = str(((catalog.get("governance") or {}).get("must_have") or {}).get("why") or "")
    if str(floor_must.get("why") or "") != gov_why:
        raise IntegrityError("floor must-have why must match governance", reason_code="CATALOG_PLANE")
    if str(floor_must.get("incident") or "") != str(catalog.get("l1_incident_copy") or ""):
        raise IntegrityError("floor must-have incident must match l1_incident_copy", reason_code="CATALOG_PLANE")
    if "two humans before the write" not in str(floor_must.get("job_c_plain") or "").lower():
        raise IntegrityError("Job C plain is two humans before the write", reason_code="CATALOG_PLANE")
    gov_for = ((catalog.get("governance") or {}).get("must_have") or {}).get("for") or {}
    floor_for = floor_must.get("for") or {}
    for who in ("owner", "board", "examiner"):
        if str(floor_for.get(who) or "") != str(gov_for.get(who) or ""):
            raise IntegrityError(f"floor must-have for {who} must match governance", reason_code="CATALOG_PLANE")
    not_gate_ids = [item.get("id") for item in floor.get("not_the_gate") or []]
    for needed in ("vendor_native", "teams", "pim", "copilot", "bc_workflow", "in_harness", "grc_icfr"):
        if needed not in not_gate_ids:
            raise IntegrityError(f"not-the-gate must include {needed}", reason_code="CATALOG_PLANE")
    glance = floor.get("first_glance") or {}
    if not isinstance(glance, dict):
        raise IntegrityError("floor first_glance is required", reason_code="CATALOG_PLANE")
    if glance.get("sku") is True:
        raise IntegrityError("first glance is not a SKU", reason_code="CATALOG_SKU")
    if glance.get("uses") != "not_the_gate":
        raise IntegrityError("first glance uses not_the_gate", reason_code="CATALOG_PLANE")
    glance_lede = str(glance.get("lede") or "").lower()
    if "substitute" not in glance_lede or "job c" not in glance_lede:
        raise IntegrityError("first glance is substitute vs Job C", reason_code="CATALOG_PLANE")
    job_c = str(glance.get("job_c") or "").lower()
    if "sor write-gate" not in job_c or "not agent inventory" not in job_c:
        raise IntegrityError("first glance Job C is a SoR write-gate, not agent inventory", reason_code="CATALOG_PLANE")
    if list(glance.get("skus") or []) != ["L1", "P-ADM", "U-DUAL"]:
        raise IntegrityError("first glance names the same three SKUs", reason_code="CATALOG_PLANE")
    rail = list(glance.get("write_rail") or [])
    if [item.get("id") for item in rail] != ["seat_a", "seat_b", "hash", "write"]:
        raise IntegrityError("first glance write rail is seat A, seat B, hash, then the write", reason_code="CATALOG_PLANE")
    dash_ids = [item.get("id") for item in ((body.get("dashboard") or {}).get("first_glance") or {}).get("write_rail") or []]
    if dash_ids != [item.get("id") for item in rail]:
        raise IntegrityError("dashboard write rail must match the public write rail", reason_code="CATALOG_PLANE")
    rail_blob = " ".join(f"{item.get('name') or ''} {item.get('note') or ''}" for item in rail).lower()
    for stem in ("seat a", "seat b", "hash", "write"):
        if stem not in rail_blob:
            raise IntegrityError(f"first glance write rail must keep {stem}", reason_code="CATALOG_PLANE")
    kicker = str(glance.get("rail_kicker") or "").lower()
    if "gate" not in kicker or "cop" not in kicker:
        raise IntegrityError("first glance rail kicker is the gate then the licensed copies", reason_code="CATALOG_PLANE")
    _validate_public_face(floor.get("public_face"))
    success_floor = floor.get("success") or {}
    if not isinstance(success_floor, dict):
        raise IntegrityError("floor success is required", reason_code="CATALOG_PLANE")
    if success_floor.get("sku") is True:
        raise IntegrityError("floor success is not a SKU", reason_code="CATALOG_SKU")
    if success_floor.get("uses") != "expert_review.success":
        raise IntegrityError("floor success uses expert_review.success", reason_code="CATALOG_PLANE")
    review_thesis = str(((catalog.get("expert_review") or {}).get("success") or {}).get("thesis") or "")
    if str(success_floor.get("lede") or "") != review_thesis:
        raise IntegrityError("floor success lede must match the success thesis", reason_code="CATALOG_PLANE")
    close = floor.get("proof_close") or {}
    if close.get("minutes") != (catalog.get("proof_day") or {}).get("minutes"):
        raise IntegrityError("proof close minutes must match proof day", reason_code="CATALOG_PLANE")
    if list(close.get("walk_out") or []) != list((catalog.get("proof_day") or {}).get("walk_out") or []):
        raise IntegrityError("proof close walk-out must match proof day", reason_code="CATALOG_PLANE")
    if "ninety-minute" not in str(close.get("sale") or "").lower():
        raise IntegrityError("the sale is the ninety-minute proof", reason_code="CATALOG_PLANE")
    no_means = floor.get("no_means") or {}
    off = str((((catalog.get("governance") or {}).get("plane") or {}).get("off_switch") or {}).get("does") or "")
    if str(no_means.get("off_switch") or "") != off:
        raise IntegrityError("no-means off switch must match governance", reason_code="CATALOG_PLANE")
    if "write does not land" not in str(no_means.get("fail_closed") or "").lower():
        raise IntegrityError("fail-closed is the write does not land", reason_code="CATALOG_PLANE")
    if "refusing is the product working" not in str(no_means.get("refuse") or "").lower():
        raise IntegrityError("refusing is the product working", reason_code="CATALOG_PLANE")
    scope_ids = [item.get("id") for item in floor.get("scopes") or []]
    for needed in ("week_one", "included_seating", "advanced"):
        if needed not in scope_ids:
            raise IntegrityError(f"floor scopes must include {needed}", reason_code="CATALOG_PLANE")
    page = floor.get("page") or {}
    if page.get("product_first") is not True:
        raise IntegrityError("homepage is product-first", reason_code="CATALOG_PLANE")
    if str(page.get("twin_heading") or "") != "Proof day":
        raise IntegrityError("twin heading is Proof day", reason_code="CATALOG_PLANE")
    if str(page.get("twin_is") or "") != str(
        (catalog.get("microsoft_stack") or {}).get("not_the_product") or ""
    ):
        raise IntegrityError("twin is a test of the plane", reason_code="CATALOG_PLANE")
    if str(page.get("sale") or "") != str(close.get("sale") or ""):
        raise IntegrityError("page sale must match proof close", reason_code="CATALOG_PLANE")
    if list(page.get("product_path") or []) != ["buyer", "twin", "product"]:
        raise IntegrityError("product path is buyer, twin, product", reason_code="CATALOG_PLANE")
    if str(page.get("company_after") or "") != "about":
        raise IntegrityError("company dump sits after about", reason_code="CATALOG_PLANE")
    accountable = floor.get("accountable") or {}
    acc_lede = str(accountable.get("lede") or "").lower()
    if "duty matrix" not in acc_lede or "only seat a and seat b admit" not in acc_lede:
        raise IntegrityError("accountable lede is the duty matrix", reason_code="CATALOG_PLANE")
    acc_ids = [item.get("id") for item in accountable.get("items") or []]
    for needed in ("admit", "freeze", "keep", "not_a_seat"):
        if needed not in acc_ids:
            raise IntegrityError(f"accountable must include {needed}", reason_code="CATALOG_PLANE")
    acc_by = {item.get("id"): item for item in accountable.get("items") or []}
    if "only two humans" not in str((acc_by.get("admit") or {}).get("note") or "").lower():
        raise IntegrityError("admit is the only two humans", reason_code="CATALOG_PLANE")
    freeze_note = str((acc_by.get("freeze") or {}).get("note") or "").lower()
    if "they are not seats" not in freeze_note or "freeze" not in freeze_note:
        raise IntegrityError("owner and board are not seats", reason_code="CATALOG_PLANE")
    if str((acc_by.get("keep") or {}).get("note") or "") != str(floor_for.get("examiner") or ""):
        raise IntegrityError("keep must match examiner must-have", reason_code="CATALOG_PLANE")
    not_seat = str((acc_by.get("not_a_seat") or {}).get("note") or "").lower()
    if "one title cannot" not in not_seat or "lab oids are not two named" not in not_seat:
        raise IntegrityError("lab oids are not named seats", reason_code="CATALOG_PLANE")
    protect = floor.get("protect") or {}
    prot_lede = str(protect.get("lede") or "").lower()
    if "not counsel" not in prot_lede or "not a certificate" not in prot_lede:
        raise IntegrityError("protect lede is the catalog-map disclaimer", reason_code="CATALOG_PLANE")
    prot_ids = [item.get("id") for item in protect.get("items") or []]
    for needed in ("disclaimer", "attest", "policy", "update"):
        if needed not in prot_ids:
            raise IntegrityError(f"protect must include {needed}", reason_code="CATALOG_PLANE")
    prot_by = {item.get("id"): item for item in protect.get("items") or []}
    disc = str((prot_by.get("disclaimer") or {}).get("note") or "").lower()
    if "does not certify" not in disc or "not a signature" not in disc:
        raise IntegrityError("disclaimer is not a certificate or a signature", reason_code="CATALOG_PLANE")
    second = str((((catalog.get("governance") or {}).get("records") or {}).get("second") or {}).get("what") or "")
    if str((prot_by.get("attest") or {}).get("note") or "") != second:
        raise IntegrityError("attest must match the second record", reason_code="CATALOG_PLANE")
    pol = str((prot_by.get("policy") or {}).get("note") or "").lower()
    if "cannot weaken job c" not in pol or "live_pin_ok cannot be marked" not in pol:
        raise IntegrityError("policy cannot weaken Job C", reason_code="CATALOG_PLANE")
    if "a rebrand breaks gold" not in str((prot_by.get("update") or {}).get("note") or "").lower():
        raise IntegrityError("a system update cannot rebrand Job C", reason_code="CATALOG_PLANE")
    memory = floor.get("memory") or {}
    mem_lede = str(memory.get("lede") or "").lower()
    if "two records and a keep" not in mem_lede:
        raise IntegrityError("memory lede is two records and a keep", reason_code="CATALOG_PLANE")
    mem_ids = [item.get("id") for item in memory.get("items") or []]
    for needed in ("first", "keep", "reset", "rollback"):
        if needed not in mem_ids:
            raise IntegrityError(f"memory must include {needed}", reason_code="CATALOG_PLANE")
    mem_by = {item.get("id"): item for item in memory.get("items") or []}
    first_what = str((((catalog.get("governance") or {}).get("records") or {}).get("first") or {}).get("what") or "")
    if str((mem_by.get("first") or {}).get("note") or "") != first_what:
        raise IntegrityError("memory first must match the first record", reason_code="CATALOG_PLANE")
    keep_note = ""
    for item in body.get("write_path") or []:
        if item.get("id") == "keep":
            keep_note = str(item.get("note") or "")
            break
    if str((mem_by.get("keep") or {}).get("note") or "") != keep_note:
        raise IntegrityError("memory keep must match the write-path keep", reason_code="CATALOG_PLANE")
    reset_does = str((((catalog.get("governance") or {}).get("plane") or {}).get("reset") or {}).get("does") or "")
    if str((mem_by.get("reset") or {}).get("note") or "") != reset_does:
        raise IntegrityError("memory reset must match governance reset", reason_code="CATALOG_PLANE")
    rollback_note = str((mem_by.get("rollback") or {}).get("note") or "").lower()
    if "compensating write" not in rollback_note or "not a time machine" not in rollback_note:
        raise IntegrityError("rollback is a compensating write, not a time machine", reason_code="CATALOG_PLANE")
    integrate = floor.get("integrate") or {}
    int_lede = str(integrate.get("lede") or "").lower()
    if "cannot create users" not in int_lede or "live_pin_ok" not in int_lede:
        raise IntegrityError("integrate lede is the owner-click playbook", reason_code="CATALOG_PLANE")
    gates = catalog.get("owner_gates") or []
    int_items = list(integrate.get("items") or [])
    if [item.get("id") for item in int_items] != [item.get("id") for item in gates]:
        raise IntegrityError("integrate items must match owner gates", reason_code="CATALOG_PLANE")
    for gate, item in zip(gates, int_items, strict=True):
        if str(item.get("note") or "") != str(gate.get("do") or ""):
            raise IntegrityError(f"integrate {gate.get('id')} must match the owner gate", reason_code="CATALOG_PLANE")
        if str(item.get("url") or "") != str(gate.get("url") or ""):
            raise IntegrityError(f"integrate {gate.get('id')} url must match the owner gate", reason_code="CATALOG_PLANE")
        if not item.get("url") or not str(item.get("url")).startswith("https://"):
            raise IntegrityError("integrate steps need https links", reason_code="CATALOG_PLANE")
        if "entra_client_id" in str(item.get("url") or "").lower() or "2ad041b8" in str(item.get("url") or ""):
            raise IntegrityError("integrate urls cannot embed the Entra app id", reason_code="CATALOG_PLANE")
    if "with u-dual" not in str(bands.get("desk_band_means") or "").lower():
        raise IntegrityError("desk bands must keep included-with-SKU labels", reason_code="CATALOG_PLANE")
    refuse_blob = " ".join(str(item) for item in body.get("refuse") or []).lower()
    for stem in (
        "dashboard as sku",
        "standard provision as sku",
        "advanced provision as sku",
        "included means free",
        "must-have as sku",
        "must-have as mandate",
        "native approval as the plane",
        "vendor-native as dual",
        "microsoft as the product",
        "homepage as company first",
        "lab oids as named seats",
        "owner as a seat",
        "update weakens job c",
        "this page as a certificate",
        "this page as a signature",
        "mailbox as the second record",
        "rollback as a time machine",
        "reset wipes production",
        "new entra app",
        "graph write roles",
        "cloud agent clicks unblock",
        "view assignment as sku",
        "personalized dashboard as sku",
        "mfa as dual admit",
        "mfa live claimed",
    ):
        if stem not in refuse_blob:
            raise IntegrityError(f"plane refuse must keep {stem}", reason_code="CATALOG_PLANE")
    tiles = dash.get("tiles") or []
    for needed in ("plane_state", "recognized_revenue", "compliance_maps"):
        if needed not in tiles:
            raise IntegrityError(f"dashboard must tile {needed}", reason_code="CATALOG_PLANE")
    view_ids = [item.get("id") for item in body.get("views") or []]
    for needed in (
        "entire",
        "owner",
        "seats",
        "examiner",
        "remote",
        "it",
        "provision",
        "records",
        "client",
    ):
        if needed not in view_ids:
            raise IntegrityError(f"plane views must include {needed}", reason_code="CATALOG_PLANE")
    for item in body.get("views") or []:
        if item.get("sku") is True:
            raise IntegrityError("a view is not a SKU", reason_code="CATALOG_SKU")
    path_ids = [item.get("id") for item in body.get("write_path") or []]
    for needed in ("draft", "seat_a", "seat_b", "first_record", "keep"):
        if needed not in path_ids:
            raise IntegrityError(f"write path must include {needed}", reason_code="CATALOG_PLANE")
    lod_ids = [item.get("id") for item in body.get("lines_of_defense") or []]
    if not {"1lod", "2lod", "3lod"} <= set(lod_ids):
        raise IntegrityError("three lines of defense are required", reason_code="CATALOG_PLANE")
    for item in body.get("lines_of_defense") or []:
        if item.get("claimed") is True:
            raise IntegrityError("lines of defense are not a certificate", reason_code="CATALOG_PLANE")
    clock = body.get("clock") or {}
    if clock.get("live_clock_claimed") is True:
        raise IntegrityError("plane clock cannot claim a live Production clock", reason_code="CATALOG_PLANE")
    if clock.get("pending_binds") not in (0, "0"):
        raise IntegrityError("plane clock pending binds stay zero until a named pair", reason_code="CATALOG_PLANE")
    attention_ids = [item.get("id") for item in body.get("attention") or []]
    for needed in ("must_have", "pending", "production", "sandbox_first", "second_record"):
        if needed not in attention_ids:
            raise IntegrityError(f"attention board must include {needed}", reason_code="CATALOG_PLANE")
    for item in body.get("attention") or []:
        if item.get("id") in {"pending", "production", "second_record", "standing_grants"} and str(
            item.get("value")
        ) not in {"0", "0"}:
            raise IntegrityError(f"attention {item.get('id')} stays zero", reason_code="CATALOG_PLANE")
    zt = body.get("zero_trust") or {}
    if zt.get("sku") is True or zt.get("ztna_sku") is True:
        raise IntegrityError("zero trust is not a SKU", reason_code="CATALOG_SKU")
    if zt.get("identify_is_not_admit") is not True:
        raise IntegrityError("identify is not admit", reason_code="CATALOG_PLANE")
    auth_ids = [item.get("id") for item in body.get("authorizations") or []]
    for needed in ("identify", "seat", "bind", "revoke"):
        if needed not in auth_ids:
            raise IntegrityError(f"authorizations must include {needed}", reason_code="CATALOG_PLANE")
    for item in body.get("authorizations") or []:
        if item.get("standing") is True or item.get("live") is True:
            raise IntegrityError("authorizations stay zero-standing", reason_code="CATALOG_PLANE")
        if item.get("id") == "seat":
            note = str(item.get("note") or "").lower()
            if "1 mailbox" not in note or "0 oid" not in note:
                raise IntegrityError("seat authorization must keep 1 mailbox / 0 oid", reason_code="CATALOG_PLANE")
    if not {"freeze", "seat_revoke", "grant_expire"} <= {
        item.get("id") for item in body.get("revocations") or []
    }:
        raise IntegrityError("revocations must include freeze and seat revoke", reason_code="CATALOG_PLANE")
    provision = body.get("provisioning") or {}
    if provision.get("sku") is True:
        raise IntegrityError("provisioning is not a SKU", reason_code="CATALOG_SKU")
    if provision.get("u_dual_never_free") is not True:
        raise IntegrityError("U-DUAL is never free", reason_code="CATALOG_PLANE")
    attached = provision.get("attached") or {}
    if any(int(attached.get(key) or 0) for key in ("L1", "P-ADM", "U-DUAL")):
        raise IntegrityError("provisioned SKUs stay zero until a named buyer", reason_code="CATALOG_PLANE")
    for item in body.get("communications") or []:
        if item.get("seat") is True or item.get("keep") is True:
            raise IntegrityError("notify is not a seat or a keep", reason_code="CATALOG_PLANE")
    record_ids = [item.get("id") for item in body.get("records") or []]
    for needed in ("first_record", "second_record", "keep"):
        if needed not in record_ids:
            raise IntegrityError(f"records must include {needed}", reason_code="CATALOG_PLANE")
    for item in body.get("records") or []:
        if item.get("live") is True or item.get("certified") is True:
            raise IntegrityError("records are not live or certified", reason_code="CATALOG_PLANE")
    exception_ids = [item.get("id") for item in body.get("exceptions") or []]
    for needed in ("same_seat", "agent_click", "seat_refuse", "freeze", "replay"):
        if needed not in exception_ids:
            raise IntegrityError(f"exception paths must include {needed}", reason_code="CATALOG_PLANE")
    for item in body.get("exceptions") or []:
        if item.get("live") is True:
            raise IntegrityError("exception paths are not live incidents", reason_code="CATALOG_PLANE")
    rehearsal = body.get("rehearsal") or {}
    if rehearsal.get("sku") is True:
        raise IntegrityError("rehearsal is not a SKU", reason_code="CATALOG_SKU")
    if rehearsal.get("live") is True or rehearsal.get("production") is True or rehearsal.get("writes_sor") is True:
        raise IntegrityError("rehearsal cannot write SoR or claim live", reason_code="CATALOG_PLANE")
    if rehearsal.get("wedge") != "bc.general_journal.post":
        raise IntegrityError("rehearsal walks the public wedge", reason_code="CATALOG_PLANE")
    if rehearsal.get("named_humans") is True:
        raise IntegrityError("rehearsal cannot invent named humans", reason_code="CATALOG_PLANE")
    _validate_view_assignment(catalog, body)
    _validate_estate(catalog, body)
    _validate_audit(catalog, body)
    _validate_instrument_plane(catalog, body)


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


def catalog_graph() -> dict[str, Any]:
    return dict((load_catalog().get("microsoft_stack") or {}).get("graph") or {})
