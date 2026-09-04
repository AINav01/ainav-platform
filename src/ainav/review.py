"""Deep-dive review generated from the catalog. Catalog wins. Never LIVE_PIN_OK."""

from __future__ import annotations

from typing import Any

from ainav.catalog import honest_missing, load_catalog, sku
from ainav.institute_status import public_status
from ainav.microsoft.agent_tools import public_review as agent_tools_review
from ainav.org import human_gates


CLI_SURFACE = (
    "python -m ainav review",
    "python -m ainav review --probe",
    "python -m ainav org [--probe]",
    "python -m ainav connect --probe",
    "python -m ainav stack",
    "python -m ainav dns",
    "python -m ainav agent-tools [--probe]",
    "python -m ainav proof-day",
    "python -m ainav twin-demo",
    "python -m ainav programs",
    "python -m ainav finance",
    "python -m ainav governance",
    "python -m ainav brief-pdf",
)


def _money(amount: int) -> str:
    return f"${amount:,}"


def _sku_line(sku_id: str) -> str:
    item = sku(sku_id)
    price = item["price_usd"]
    return f"**{sku_id} {item['name']}** — {_money(price['min'])}–{_money(price['max'])} ({item['term']})"


def _equation(cat: dict[str, Any], opp: dict[str, Any]) -> dict[str, Any]:
    attached = opp.get("attached") or {}
    return {
        "text": cat["success_equation"],
        "live_pin_ok": False,
        "proof_day_executable": True,
        "proof_day_sold": False,
        "signed_l1": False,
        "p_adm_attached": int(attached.get("P-ADM") or 0),
        "closed": False,
    }


def _fit(cat: dict[str, Any], evidence: dict[str, Any], site: dict[str, Any], opp: dict[str, Any]) -> list[dict[str, str]]:
    operating = cat["operating"]
    year = opp["year_one_list_if_all_three"]
    return [
        {
            "id": "owner",
            "label": "Owner / operator",
            "status": "sole_owner",
            "note": (
                f"Owner {operating['owner_principal']}. Operator {operating['operator']} "
                "is not a seat and not dual admit. Second officer: none. "
                f"{cat['organization']['contacts']['invited']['name']} agreed. "
                f"Mailbox {cat['organization']['contacts']['invited'].get('email')} recorded. "
                "Number two for other aspects, not all aspects. "
                "Entra oid and click still open."
            ),
        },
        {
            "id": "admit",
            "label": "Job C admit plane",
            "status": "running_code",
            "note": (
                f"{cat['entity']['product']}. Two distinct humans bind one action_hash. "
                "Then the write. Cloud Agent is not seat_a or seat_b."
            ),
        },
        {
            "id": "l1",
            "label": "L1 / Business Central",
            "status": "sandbox_journal",
            "note": (
                f"Sandbox company {evidence['bc_company']} document `{evidence['bc_document']}` "
                f"on {evidence['date']} for {evidence['amount']}. "
                f"Wedge `{evidence['action_class']}`. {evidence['seats']}. "
                "Production stays blocked. Not LIVE_PIN_OK."
            ),
        },
        {
            "id": "p_adm",
            "label": "P-ADM attach",
            "status": "unattached",
            "note": (
                f"Attaches after {sku('P-ADM')['attach_after']}. "
                f"Attached={opp['attached']['P-ADM']}. Never bundles free U-DUAL."
            ),
        },
        {
            "id": "u_dual",
            "label": "U-DUAL / Sales",
            "status": "licensed_not_wired",
            "note": (
                "Sales Enterprise is licensed. Global Discovery returned zero instances. "
                "Ticket 2609030040009525: Canada affinity; United States not pinned. "
                f"Attached={opp['attached']['U-DUAL']}. Twin only until G14."
            ),
        },
        {
            "id": "institute",
            "label": "Institute / DNS",
            "status": "azure_hosted_not_custom",
            "note": (
                f"{site.get('azure_site')} on {site.get('azure_location')}. "
                f"launch_ready={str(site.get('launch_ready')).lower()}. "
                "Apex CNAME is empty Cloudflare Pages. No asuid. Do not publish until launch."
            ),
        },
        {
            "id": "programs",
            "label": "Programs",
            "status": "qualify_not_claimed",
            "note": (
                "Microsoft for Startups first. NVIDIA Inception second. "
                "Membership claimed: false. Crypto-associated: false. GPU production: false."
            ),
        },
        {
            "id": "pipeline",
            "label": "Commercial spine",
            "status": "catalog_list_not_revenue",
            "note": (
                f"Year-one catalog list if one controller buys all three: "
                f"{_money(year['min'])}–{_money(year['max'])}. "
                f"Signed L1={opp['signed_l1']}. Named customers: none. Recognized revenue: none."
            ),
        },
    ]


def review_model(*, probe: bool = False) -> dict[str, Any]:
    cat = load_catalog()
    status = public_status()
    evidence = dict(cat["sandbox_evidence"])
    site = cat["programs"]["website"]
    opp = status["opportunity"]
    tools = agent_tools_review()
    model = {
        "kind": "ainav.review.v1",
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "product": cat["entity"]["product"],
        "job": cat["entity"]["job"],
        "live": False,
        "live_pin_ok": False,
        "launch_ready": False,
        "signed_l1": False,
        "recognized_revenue": None,
        "named_customers": [],
        "second_officer": None,
        "owner": cat["operating"]["owner_principal"],
        "operator": cat["operating"]["operator"],
        "operator_is_seat": False,
        "agent_is_not_dual": True,
        "success_equation": cat["success_equation"],
        "equation": _equation(cat, opp),
        "fit": _fit(cat, evidence, site, opp),
        "attached": dict(opp["attached"]),
        "azure_url": site.get("azure_url"),
        "custom_domain_claimed": False,
        "public_deploy_claimed": False,
        "agent_tools_is_admit_plane": False,
        "cloud_agent_can_approve_tools": False,
        "agent_tools_admin": tools["admin_url"],
        "cli": list(CLI_SURFACE),
        "e7_cloudflare": dict(status["e7_cloudflare"]),
        "engineering": dict(status["engineering"]),
        "expert_review": {
            "working_well": list(cat["expert_review"]["working_well"]),
            "improve": list(cat["expert_review"]["improve"]),
            "upgrades": [dict(item) for item in cat["expert_review"]["upgrades"]],
            "success": dict(cat["expert_review"]["success"]),
        },
        "probed": False,
    }
    if probe:
        model["probe"] = _probe_overlay()
        model["probed"] = True
    return model


def public_card() -> dict[str, Any]:
    """Institute JSON. Catalog only. Never a live probe."""
    return review_model(probe=False)


def deep_dive(*, probe: bool = False) -> str:
    cat = load_catalog()
    entity = cat["entity"]
    site = cat["programs"]["website"]
    evidence = cat["sandbox_evidence"]
    status = public_status()
    opp = status["opportunity"]
    tools = agent_tools_review()
    year = opp["year_one_list_if_all_three"]
    model = review_model(probe=False)
    equation = model["equation"]
    lines = [
        f"# {entity['legal']} — deep-dive review",
        "",
        "Catalog-honest. Not a live pin. Not a launch. Not recognized revenue.",
        "",
        "## Verdict",
        "",
        f"{entity['legal']} has a running Job {entity['job']} admit plane, a Microsoft sandbox twin, "
        "and an Azure-hosted Institute that is **held until launch**. "
        "The company can prove the L1 write-gate on Business Central Sandbox. "
        "It cannot yet sell a signed L1, attach P-ADM, or mark LIVE_PIN_OK.",
        "",
        f"**Success still open:** {cat['success_equation']}",
        f"**Commercial close:** {cat['equations']['commercial']}",
        f"**Lab pin:** {cat['equations']['lab_pin']} — never marked from sales.",
        f"**Owner:** {cat['operating']['owner_principal']} "
        f"(handle {cat['operating'].get('owner_handle')}). "
        f"**Operator:** {cat['operating']['operator']} (not a seat, not dual admit).",
        f"**Second officer:** none. **Invited:** {cat['organization']['contacts']['invited']['name']} "
        f"(mailbox {cat['organization']['contacts']['invited'].get('email')} recorded; "
        "number two for other aspects, not all aspects; "
        "Entra oid and click still open). "
        f"**Named customers:** none. **Recognized revenue:** none.",
        f"**Launch ready:** {str(site.get('launch_ready')).lower()}. "
        f"**Custom domain claimed:** {str(site.get('custom_domain_claimed')).lower()}.",
        "",
        "## Success equation scorecard",
        "",
        "The product equation is a lab pin times a sale. Controllers buy the commercial equation.",
        "",
        f"- **Commercial close** — {cat['equations']['commercial']}. Closed: false.",
        f"- **LIVE_PIN_OK** — {str(equation['live_pin_ok']).lower()}. Never marked from this plane.",
        "- **Proof day** — executable "
        f"(`{cat['proof_day']['cli']}`, {cat['proof_day']['minutes']} minutes). Sold: "
        f"{str(equation['proof_day_sold']).lower()}.",
        f"- **Signed L1** — {str(equation['signed_l1']).lower()}. G13. "
        "Sandbox journal AINAV-L1 used lab operator oids, not two named treasury humans.",
        f"- **P-ADM attach** — {equation['p_adm_attached']}. Attaches only after "
        f"{sku('P-ADM')['attach_after']}.",
        f"- **Closed:** {str(equation['closed']).lower()}.",
        "",
        "## How the pieces fit",
        "",
        "One company. Three SKUs. Ten departments. Six Microsoft connections. "
        "Eight complements. The Cloud Agent operates the host. It is not a seat.",
        "",
        "Azure hosts → Microsoft 365 E7 / Entra identifies → AINav admits → "
        "Business Central (L1 SoR) and Sales (U-DUAL SoR) receive the write → "
        "Teams notifies. Complements hold secrets, evidence, policy, and audit.",
        "",
    ]
    for item in model["fit"]:
        lines.append(f"- **{item['label']}** — `{item['status']}`. {item['note']}")
    lines += [
        "",
        "Refuse: " + "; ".join(cat["buyer"]["refuse"]) + ".",
        "",
        "## Competitive field (honest)",
        "",
        "Substitutes a controller already has or will be offered. They can copy these. "
        "This is not a patent. This is not uncopyable.",
        "",
    ]
    for item in cat["ip"]["insulation"]["what_they_can_copy"]:
        lines.append(f"- They can copy: {item}.")
    lines += [
        "",
        "What the build pins:",
        "",
    ]
    for item in cat["ip"]["insulation"]["what_the_build_pins"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "Others in the same conversation: "
        + "; ".join(cat["ip"]["insulation"]["others"])
        + ". None of those are Job C. Job C is a SoR write-gate, not agent inventory and not an IdP.",
        "",
        "Refuse: " + "; ".join(cat["ip"]["insulation"]["refuse"]) + ".",
        "",
        "## Success program — bake-off, qualify, walk away",
        "",
        cat["expert_review"]["success"]["thesis"],
        "",
        f"**Bake-off.** {cat['expert_review']['success']['bake_off']['lede']}",
        "",
        "They win when:",
        "",
    ]
    for item in cat["expert_review"]["success"]["bake_off"]["they_win"]:
        lines.append(f"- **{item['name']}** — {item['note']}")
    lines += [
        "",
        "We win when:",
        "",
    ]
    for item in cat["expert_review"]["success"]["bake_off"]["we_win"]:
        lines.append(f"- **{item['name']}** — {item['note']}")
    lines += [
        "",
        f"**Qualify.** {cat['expert_review']['success']['qualify']['lede']}",
        "",
        "Must:",
        "",
    ]
    for item in cat["expert_review"]["success"]["qualify"]["must"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "Walk away:",
        "",
    ]
    for item in cat["expert_review"]["success"]["qualify"]["walk_away"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "**Objections.**",
        "",
    ]
    for item in cat["expert_review"]["success"]["objections"]:
        lines.append(f"- **{item['hear']}** — {item['answer']}")
    lines += [
        "",
        f"**CISO.** {cat['expert_review']['success']['ciso']['lede']}",
        "",
    ]
    for item in cat["expert_review"]["success"]["ciso"]["holds"]:
        lines.append(f"- Holds: {item}")
    for item in cat["expert_review"]["success"]["ciso"]["does_not"]:
        lines.append(f"- Does not: {item}")
    seat = cat["expert_review"]["success"]["seat_b"]
    lines += [
        "",
        f"**Seat B meaning.** {seat['lede']} {seat['name']} · {seat['mailbox']}.",
        "",
    ]
    for item in seat["is"]:
        lines.append(f"- Is: {item}")
    for item in seat["is_not"]:
        lines.append(f"- Is not: {item}")
    cont = cat["expert_review"]["success"]["continuity"]
    human = cat["expert_review"]["success"]["human_control"]
    risk = cat["expert_review"]["success"]["executive_risk"]
    market = cat["expert_review"]["success"]["market_position"]
    us_dv = cat["microsoft_stack"]["us_dataverse"]
    lines += [
        "",
        f"**Continuity.** {cont['lede']} {cont['note']}",
        "",
        f"**Human control.** {human['lede']} {human['ours']} {human['not_ours']}",
        "",
        f"**Executive risk.** {risk['lede']} {risk['personal']} {risk['business']} {risk['compliance']} {risk['non_compliance']}",
        "",
        f"**Market position.** {market['lede']} {market['now']} {market['future']} {market['not_the_future']}",
        "",
        f"**US Dataverse.** {us_dv['lede']} {us_dv['finding']} {us_dv['note']}",
        "",
        "## Stack walk",
        "",
        cat["microsoft_stack"]["walk"]["thesis"],
        "",
        cat["microsoft_stack"]["walk"]["implementation"],
        "",
        "CLI: `python -m ainav stack`. Probe: `python -m ainav connect --probe`.",
        "",
    ]
    for item in cat["microsoft_stack"]["walk"]["path"]:
        url = item.get("url") or ""
        label = item.get("url_label") or url
        lines.append(
            f"- **{item['n']}. {item['name']}** — `{item['status']}`. {item['in_tree']} "
            f"[{label}]({url})"
        )
    lines += [
        "",
        "Complements (not hops on the write):",
        "",
    ]
    for item in cat["microsoft_stack"]["walk"]["complements"]:
        url = item.get("url") or ""
        label = item.get("url_label") or url
        lines.append(f"- **{item['name']}** — `{item['status']}`. [{label}]({url})")
    lines += [
        "",
        "## First principles",
        "",
        entity["category"] + ".",
        "A privileged write is allowed only when two distinct humans bind the same `action_hash`,",
        "that grant is consumed once, and the effect gate is fail-closed.",
        cat["microsoft_stack"]["not_the_product"],
        "",
        "## AI governance — failsafe, not a certificate",
        "",
        cat["governance"]["thesis"],
        f"- Certified: false. Replaces counsel: false. SKU: false.",
        f"- Control: {cat['equations']['control']}",
        f"- Cascade: {cat['equations']['cascade']}",
        f"- Umbrella: {cat['equations']['umbrella']}",
        f"- Plane: {cat['equations']['plane']}",
        f"- Org: {cat['equations']['org']}",
        f"- Insulation: {cat['equations']['insulation']}",
        f"- Investor: {cat['equations']['investor']}",
        "- Investor packet: letter to Cynthia Hodnett with the full upsell catalog, list prices, ultimate-plane insulation, and the human interface / executive dashboard. Not a priced round. Not a forecast. Not an equity grant.",
        f"- Interface: {cat['equations'].get('interface')}. Dashboard tiles the admit ledger. Not invented P&L. Not a SKU.",
        "- Independent of Microsoft. Not a patent. Not uncopyable. G12 stays open.",
        f"- Does: {cat['governance']['failsafe']['does']}",
        "- Separate from: " + "; ".join(cat["governance"]["failsafe"]["separate_from"]) + ".",
        f"- First record: {cat['governance']['records']['first']['what']}",
        f"- Second record: {cat['governance']['records']['second']['what']}",
        f"- Off switch: {cat['governance']['plane']['off_switch']['does']}",
        f"- Must-have: {cat['governance']['must_have']['why']}",
        "- Maps (claimed=false): " + ", ".join(item["id"] for item in cat["governance"]["maps"]) + ".",
        "- Risks: " + "; ".join(item["id"] for item in cat["governance"]["risks"]) + ".",
        "- Refuse: " + "; ".join(cat["governance"]["refuse"]) + ".",
        "",
        "Must not change:",
        "",
    ]
    for rule in cat["must_not_change"]:
        lines.append(f"- {rule}")
    lines += [
        "",
        "## The sale",
        "",
        cat["l1_incident_copy"],
        f"- Proof day: {cat['proof_day']['minutes']} minutes. `{cat['proof_day']['cli']}`",
        f"- Seats: {' / '.join(cat['buyer']['seats'])}",
        f"- Door: {cat['buyer']['door']}",
        "- Refuse: " + ", ".join(cat["buyer"]["refuse"]) + ".",
        "",
        "## Commercial spine",
        "",
        _sku_line("L1") + " — prove.",
        _sku_line("P-ADM") + f" — keep after {sku('P-ADM')['attach_after']}. Never bundles free U-DUAL.",
        _sku_line("U-DUAL") + " — deepen. Never free with P-ADM or U-SOR.",
        "A la carte packs attach after the required SKU. They are not SKUs.",
        "",
        f"Year-one catalog list if one controller buys all three: "
        f"{_money(year['min'])}–{_money(year['max'])}. {year['note']}",
        f"Pipeline attached: L1={opp['attached']['L1']}, P-ADM={opp['attached']['P-ADM']}, "
        f"U-DUAL={opp['attached']['U-DUAL']}. Signed L1={opp['signed_l1']}.",
        "",
        cat["business"]["thesis"],
        f"- Motion: {cat['business']['sales']['motion']}",
        f"- Economics: {cat['business']['economics']['note']}",
        "",
        "## Digital twin and Microsoft sandbox",
        "",
        "Three layers. They are not interchangeable.",
        "",
        "1. **In-process twin** — `bc.sandbox` and `d365.sales.sandbox` only. "
        "`python -m ainav twin-demo`. Institute `#twin` bench is browser-only. "
        "Graph, Dataverse, and Production are not called.",
        "2. **Business Central Sandbox (real)** — "
        f"company {evidence['bc_company']} (`{evidence['bc_company_id']}`). "
        f"Document `{evidence['bc_document']}` on {evidence['date']} for {evidence['amount']}. "
        f"Wedge `{evidence['action_class']}`. {evidence['note']} "
        f"Seats: {evidence['seats']}.",
        "3. **Sales twin only** — Dynamics 365 Sales Enterprise is licensed. "
        "No Dataverse instance. Quote override stays on the twin until G14.",
        "",
        f"Next pin: `{cat['next_pin']['from']}` → `{cat['next_pin']['to']}` on "
        f"{cat['next_pin']['connection']}. sent={cat['next_pin']['sent']}. "
        f"{cat['next_pin']['note']}",
        "",
        "## Microsoft fabric",
        "",
        "Path: Azure hosts → Microsoft 365 E7 / Entra identifies → AINav admits → "
        "Business Central (L1 SoR) and Sales (U-DUAL SoR) receive the write → "
        "Teams notifies. Complements hold secrets, evidence, policy, and audit.",
        "",
        "Fabric path (sandbox, not SKUs):",
        "",
    ]
    for item in status["fabric"]["path"]:
        lines.append(
            f"- **{item['id']}** — {item['product']} (`{item['lane']}`, {item['status']}). {item['note']}"
        )
    lines += [
        "",
        "Six connections (sandbox, not SKUs):",
        "",
    ]
    for item in cat["connections"]["items"]:
        lines.append(
            f"- **{item['id']}** — {item['product']} ({item['role']}). binds: {', '.join(item.get('binds') or [])}."
        )
    lines += [
        "",
        "Eight complements (not SKUs, not live, PIM is not dual, LAW is not Sentinel):",
        "",
    ]
    for item in cat["connections"]["complements"]:
        honesty = next(
            (row["note"] for row in status["complements"] if row["id"] == item["id"]),
            "",
        )
        lines.append(
            f"- **{item['id']}** — {item['product']} ({item['role']}). "
            f"binds: {', '.join(item.get('binds') or [])}. {honesty}"
        )
    lines += [
        "",
        "E7 on Cloudflare (DNS/edge, not a ninth complement, not a write-path hop):",
        "",
        f"- Product: {status['e7_cloudflare']['product']}. Role: {status['e7_cloudflare']['role']}. "
        f"full={str(status['e7_cloudflare']['full']).lower()}. "
        f"sku={str(status['e7_cloudflare']['sku']).lower()}. "
        f"is_admit_plane={str(status['e7_cloudflare']['is_admit_plane']).lower()}.",
        f"- Already pointed: {'; '.join(status['e7_cloudflare']['already'])}.",
        f"- Still missing: {'; '.join(status['e7_cloudflare']['missing']) or 'none. E7 DNS is full.'}.",
        f"- Not: {'; '.join(status['e7_cloudflare']['not'])}.",
        f"- {status['e7_cloudflare']['note']}",
        f"- Owner dashboard: {status['e7_cloudflare']['dashboard_url']}. "
        "This Cloud Agent cannot edit Cloudflare.",
        "",
        "E7 ships Copilot and Agent 365. They are not the admit plane.",
        f"Agent Tools admin: {tools['admin_url']}",
        "Leave Available (owner Unblocks if Blocked; this Cloud Agent cannot):",
        "",
    ]
    for item in tools["leave_available"]:
        lines.append(f"- **{item['name']}** — {item['note']}")
    lines += [
        "",
        "Owner steps:",
        "",
    ]
    for index, step in enumerate((tools.get("owner_playbook") or {}).get("steps") or [], start=1):
        url = step.get("url") or ""
        extra = f" {url}" if url else ""
        lines.append(f"{index}. {step['do']}{extra}")
    lines += [
        "",
        "Block until dual: " + ", ".join(item["name"] for item in tools["block_until_dual"]) + ".",
        "Never as admit: " + ", ".join(tools["never_as_admit"]) + ".",
        "This Cloud Agent cannot approve tools.",
        "",
        "## Institute and DNS",
        "",
        f"- Azure hostname: {site.get('azure_url')}",
        f"- Site: {site.get('azure_site')} in {site.get('azure_location')}",
        f"- public_deploy_claimed={site.get('public_deploy_claimed')} "
        f"custom_domain_claimed={site.get('custom_domain_claimed')} "
        f"launch_ready={site.get('launch_ready')}",
        "- Nameservers stay on Cloudflare. Apex CNAME is empty Cloudflare Pages. Pages is not the Institute host.",
        "- Squarespace registrar transfer is still in flight. Leave the zone as-is.",
        "- Microsoft 365 mail is pointed (MX, SPF, DKIM, autodiscover, Entra enrollment).",
        f"- E7-on-Cloudflare full={str(status['e7_cloudflare']['full']).lower()}. "
        "Orange-cloud MX is not dual admit. This is not Institute launch.",
        "- No Azure SWA `asuid`. Custom domain list on the Static Web App is empty.",
        "- `--publish-institute` returns `launch_not_ready` and does not upload.",
        "- Do not bind `ainav.institute` until the owner says launch.",
        "",
        "## Gold CI (in-tree, not a live pin)",
        "",
        f"- Workflow: `{status['engineering']['gold_ci']['workflow']}`. "
        f"Command: `{status['engineering']['gold_ci']['command']}`. "
        f"Coverage floor: {status['engineering']['gold_ci']['coverage_floor']}.",
        f"- exists={str(status['engineering']['gold_ci']['exists']).lower()}. "
        f"observed_green={str(status['engineering']['gold_ci']['observed_green']).lower()}. "
        f"marks_live_pin={str(status['engineering']['gold_ci']['marks_live_pin']).lower()}. "
        f"launch={str(status['engineering']['launch']).lower()}. "
        f"sku={str(status['engineering']['sku']).lower()}.",
        f"- {status['engineering']['gold_ci']['note']}",
        "- Closed in this tree: " + "; ".join(status["engineering"]["closed_in_tree"]) + ".",
        "- This Cloud Agent cannot close: " + "; ".join(status["engineering"]["cannot_close"]) + ".",
        f"- {status['engineering']['note']}",
        "",
        "## Operating organization",
        "",
        cat["organization"]["note"],
        f"- Owner {cat['operating']['owner_principal']}. Operator is not a seat.",
        "- Second unique human: false. Incorporation date: not stored in this tree.",
        "",
    ]
    for dept in cat["organization"]["departments"]:
        blocked = "; ".join(dept.get("blocked_by") or []) or "none recorded"
        systems = ", ".join(dept.get("systems") or []) or "none"
        lines.append(
            f"- **{dept['name']}** — {dept['status']}. systems: {systems}. "
            f"{dept['note']} Blocked by: {blocked}."
        )
    lines += [
        "",
        "## Delivery",
        "",
        cat["motherships"]["law"],
        f"- Master: {cat['business']['delivery']['master']}",
        f"- Cloud: {cat['business']['delivery']['cloud']}",
        f"- Local: {cat['business']['delivery']['local']}",
        "- Week one: " + " → ".join(cat["delivery"]["week_one"]) + ".",
        "",
        "## Programs",
        "",
        cat["programs"]["lead_narrative"],
        f"- Public wedge: `{cat['programs']['public_wedge']}`",
        "- Order: " + " → ".join(cat["programs"]["application_order"]) + ".",
        "- Membership claimed: false. Ready to apply: false. GPU workload claimed: false. Crypto-associated: false.",
        "",
        "## Human gates (owner only)",
        "",
    ]
    for item in human_gates():
        lines.append(f"- {item}")
    from ainav.finance import model

    fin = model()
    lines += [
        "",
        "## Financial model (catalog list)",
        "",
        fin["note"],
        f"Recognized revenue: {fin['recognized_revenue']}. Signed L1: {fin['signed_l1']}. "
        f"Named customers: {fin['named_customers']}. Billing provider: false.",
        "",
    ]
    for row in fin["scenarios"]:
        lines.append(f"- **{row['name']}** — ${row['min']:,}–${row['max']:,}. {row['if']}")
    review = cat["expert_review"]
    lines += ["", "## Expert review — working well", ""]
    for item in review["working_well"]:
        lines.append(f"- {item}")
    lines += ["", "## Expert review — could be improved", ""]
    for item in review["improve"]:
        lines.append(f"- {item}")
    lines += ["", "## Success upgrades", ""]
    for item in review["upgrades"]:
        lines.append(f"- **{item['n']}. [{item['who']}] {item['title']}** — {item['do']}")
    lines += [
        "",
        "## Owner — James must click",
        "",
    ]
    for item in honest_missing():
        lines.append(f"- {item}")
    lines += [
        "",
        "## OPEN (do not mark closed)",
        "",
    ]
    for gap in cat["open_gaps"]:
        lines.append(f"- {gap}")
    lines += [
        "",
        "## Read the company",
        "",
        "Catalog wins. `--probe` overlays live Microsoft and DNS health. "
        "Probe does not publish, write a SoR, or mark LIVE_PIN_OK.",
        "",
    ]
    for cmd in CLI_SURFACE:
        lines.append(f"- `{cmd}`")
    if probe:
        lines.extend(_probe_section())
    lines.append("")
    return "\n".join(lines)


def _probe_overlay() -> dict[str, Any]:
    from ainav.microsoft.dns import probe_dns
    from ainav.microsoft.health import stack_health
    from ainav.org import org_report

    health = stack_health(probe=True)
    dns = probe_dns()
    org = org_report(probe=True)
    return {
        "live": False,
        "live_pin_ok": False,
        "launch_ready": False,
        "connected": list(health.get("connected") or []),
        "blocked": list(health.get("blocked") or []),
        "wired_now": list(org.get("wired_now") or []),
        "blocked_now": list(org.get("blocked_now") or []),
        "cloudflare_nameservers": dns.get("cloudflare_nameservers"),
        "swa_asuid_present": (dns.get("website") or {}).get("swa_asuid_present"),
        "mx_outlook": (dns.get("microsoft_365") or {}).get("mx_outlook"),
        "teams_sip": (dns.get("microsoft_365") or {}).get("teams_sip"),
        "e7_on_cloudflare_full": (dns.get("e7_on_cloudflare") or {}).get("full"),
        "e7_on_cloudflare_mail": (dns.get("e7_on_cloudflare") or {}).get("mail_on_cloudflare"),
        "e7_on_cloudflare_missing": list((dns.get("e7_on_cloudflare") or {}).get("missing") or []),
        "custom_domain_claimed": False,
    }


def _probe_section() -> list[str]:
    overlay = _probe_overlay()
    return [
        "",
        "## Live probe overlay (read-only)",
        "",
        "Not LIVE_PIN_OK. Not a SoR write. Not a publish. Does not promote blocked departments.",
        f"- Connected: {', '.join(overlay['connected']) or 'none'}",
        f"- Blocked: {', '.join(overlay['blocked']) or 'none'}",
        f"- Departments wired now: {', '.join(overlay['wired_now']) or 'none'}",
        f"- Departments blocked now: {', '.join(overlay['blocked_now']) or 'none'}",
        f"- Cloudflare NS: {overlay['cloudflare_nameservers']}. "
        f"SWA asuid: {overlay['swa_asuid_present']}. "
        f"Outlook MX: {overlay['mx_outlook']}. "
        f"Teams SIP: {overlay['teams_sip']}.",
        f"- E7 on Cloudflare: mail={overlay['e7_on_cloudflare_mail']} "
        f"full={overlay['e7_on_cloudflare_full']}. "
        f"Missing: {', '.join(overlay['e7_on_cloudflare_missing']) or 'none'}.",
        "- Custom domain claimed: false. Launch ready: false. "
        "Cloudflare is not a SKU and not on the privileged write path.",
    ]


def review_json(*, probe: bool = False) -> dict[str, Any]:
    model = review_model(probe=probe)
    model["markdown"] = deep_dive(probe=probe)
    return model
