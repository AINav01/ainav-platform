"""One-page business plan generated from the catalog. Catalog wins."""

from __future__ import annotations

from ainav.catalog import load_catalog


def one_page() -> str:
    cat = load_catalog()
    entity = cat["entity"]
    lines = [
        f"# {entity['legal']} — one-page plan",
        "",
        f"**Institute:** {entity['institute']}",
        f"**Product:** {entity['product']} (Job {entity['job']})",
        f"**Category:** {entity['category']}",
        "",
        "## First principles",
        "",
        "A privileged write is a state transition. It is allowed only when two",
        "distinct humans bind the same `action_hash`, that grant is consumed once,",
        "and the effect gate is fail-closed. Microsoft supplies identity, notify,",
        "SoR, and audit. It is not the product.",
        "",
        "## AI governance (not a SKU, not a certificate)",
        "",
        cat["governance"]["thesis"],
        f"- Control: {cat['equations']['control']}",
        f"- Cascade: {cat['equations']['cascade']}",
        "- Certified: false. Replaces counsel: false. The failsafe is Job C.",
        "- First record: the admitted SoR write. Second record: the sealed DecisionRecord.",
        "- Maps: " + ", ".join(item["name"] for item in cat["governance"]["maps"]) + ".",
        "- A client-AI or customer-AI draft without the client's two seats is the write that must not happen.",
        "",
        "## The sale",
        "",
        cat["l1_incident_copy"],
        f"- Proof day: {cat['proof_day']['minutes']} minutes. `{cat['proof_day']['cli']}`",
        "- Two existing treasury seats. One journal. Sealed DecisionRecord. Merkle export. Walk out.",
        "- L1 is that week. Signed L1 is G13 and stays open.",
        "",
        "## Commercial spine (do not invent SKUs)",
        "",
    ]
    for sku_item in cat["skus"]:
        price = sku_item["price_usd"]
        lines.append(
            f"- **{sku_item['id']} {sku_item['name']}** — "
            f"${price['min']:,}–${price['max']:,} ({sku_item['term']})"
        )
        if sku_item.get("incident"):
            lines.append(f"  - incident: {sku_item['incident']}")
        for item in sku_item.get("includes", []):
            lines.append(f"  - includes: {item}")
        for item in sku_item.get("does_not_include", []):
            lines.append(f"  - does not include: {item}")
        if sku_item.get("never_free_with"):
            lines.append(f"  - never free with: {', '.join(sku_item['never_free_with'])}")
        if sku_item.get("attach_after"):
            lines.append(f"  - attach after: {sku_item['attach_after']}")
    lines += [
        "",
        "## Industry packs (not SKUs)",
        "",
    ]
    for pack in cat.get("industry_packs", []):
        attach = pack.get("attach_usd") or {}
        price = (
            "included"
            if pack.get("included_in_sku")
            else f"${int(attach.get('min') or 0):,}–${int(attach.get('max') or 0):,}/{attach.get('term') or 'year'}"
        )
        lines.append(
            f"- **{pack['id']}** — {pack['name']} "
            f"(requires {pack['requires_sku']}; {price}; {pack['note']})"
        )
    lines += [
        "",
        "## Libraries (not SKUs)",
        "",
    ]
    for lib in cat.get("libraries", []):
        lines.append(
            f"- **{lib['id']}** — requires {lib['requires_sku']}. {lib.get('note')}"
        )
    lines += [
        "",
        "## Fee-for-service (not SKUs)",
        "",
    ]
    for svc in cat.get("fee_for_service", []):
        extra = "included in L1" if svc.get("included_in") == "L1" else f"${svc.get('rate_usd_per_day', 0):,}/day"
        lines.append(f"- **{svc['id']}** — {svc['name']} ({extra}). {svc['note']}")
    lines += [
        "",
        "## Operations",
        "",
        " → ".join(cat["operations"]["stages"]),
        "Exits: " + " · ".join(cat["operations"].get("exits") or []),
        "",
    ]
    for rule in cat["operations"]["rules"]:
        lines.append(f"- {rule}")
    lines += [
        "",
        "## Delivery",
        "",
        cat["motherships"]["law"],
        "- **Master mothership** (AINav): issues lockfiles, gold vectors, catalog. Never writes client SoR.",
        "- **Cloud mothership** (Azure-declared client plane): same ledger as local. Sandbox twin. Not LIVE_PIN_OK.",
        "- **Local mothership** (client): same ledger as cloud. AdmitClient + twin + Teams notify.",
        "- **L1 wedge:** `bc.general_journal.post` on a Business Central twin.",
        "- **U-DUAL deepen:** Sales Enterprise twin after a paid attach.",
        "- **Teams Enterprise / Premium:** notify only. A chat is not a seat.",
        "- **Entra (via Microsoft 365 E7):** seat object ids. Not an IdP replacement.",
        "- **Azure:** declared host for master, cloud mothership, and Institute static site.",
        "- **Business Central Premium / Sales Enterprise:** sandbox SoR until G14.",
        "- Copilot and Agent 365 ship inside E7. They are not the admit plane. Agent Tools (MCP) stay complements; the owner reviews the registry. This Cloud Agent cannot approve tools.",
        "- Complements: Entra ID, Key Vault, Monitor, SharePoint, Defender XDR, Entra PIM, Sentinel, Azure Policy.",
        f"- RACI: {cat['delivery']['raci']['master']}",
        "",
        "## Repositories (not SKUs)",
        "",
    ]
    for repo in cat.get("repositories", []):
        lines.append(f"- **{repo['id']}** — {repo['path']}. {repo['note']}")
    lines += [
        "",
        "## Business operating system",
        "",
        cat["business"]["thesis"],
        f"- BD: {cat['business']['bd']['motion']}",
        f"- Motion: {cat['business']['sales']['motion']}",
        f"- Services: {cat['business']['services']['principle']}",
        f"- Economics: {cat['business']['economics']['note']}",
        "- Complements are not SKUs. Industry packs and FFS hours are not SKUs.",
        "",
        "## Operating organization (not SKUs)",
        "",
        cat["organization"]["note"],
        f"- Owner: {cat['operating']['owner_principal']}. Operator is not a seat.",
        f"- Invited second human: {cat['organization']['contacts']['invited']['name']} (not recorded).",
        f"- Commercial close: {cat['equations']['commercial']}",
        "- Second officer: none recorded. Do not invent one.",
        "- Incorporation date: not stored in this tree.",
    ]
    for dept in cat["organization"]["departments"]:
        lines.append(f"- **{dept['name']}** — {dept['status']}. {dept['note']}")
    lines += [
        "",
        "## IP and competitor boundary",
        "",
        f"- Owner: {cat['ip']['owner']}. {cat['ip']['copyright']}",
        f"- Product mark: {cat['ip']['product_mark']}. Institute: {cat['ip']['institute_mark']}.",
        f"- {cat['microsoft_stack']['not_the_product']}",
        "- Microsoft marks name integrations only. Copilot / Power Automate / Purview are not SKUs.",
        "- Competitor aliases cannot be provisioned as packs.",
        "- G12 legal is OPEN. No patent is claimed in this tree.",
        "",
        "## Programs (qualify, do not claim)",
        "",
        cat["programs"]["lead_narrative"],
        f"- Public wedge: `{cat['programs']['public_wedge']}`",
        "- Apply order: Microsoft for Startups first. NVIDIA Inception second. Membership is not claimed.",
        "- Later / complementary: NVIDIA Developer, GitHub for Startups, Microsoft ISV Success, NVIDIA Connect.",
        "- Inception excludes cryptocurrency-associated companies. Do not lead with gold-vector custody fixtures.",
        "- Inception also wants two unique contacts (developer + business executive, business emails). Sole owner does not collapse that.",
        f"- Azure hostname: {cat['programs']['website'].get('azure_url') or 'not published'}. ainav.institute custom domain is not claimed. Publish is held until launch.",
        "- Ready to apply is false until the custom domain, incorporation date, and second unique human exist outside this tree.",
        "",
        "## Buyer page and ICP",
        "",
        cat["buyer"]["write_that_must_not_happen"],
        f"- Door: {cat['buyer']['door']}",
        f"- ICP: {cat['icp']['erp']}; {cat['icp']['identity']}; {cat['icp']['control']}.",
        "- Named customers: none. Do not invent a design-partner name.",
        "",
        "## Next pin",
        "",
        cat["next_pin"]["note"],
        f"- `{cat['next_pin']['from']}` → `{cat['next_pin']['to']}` on {cat['next_pin']['connection']}. sent=False.",
        "",
        "## Acceptance Kit",
        "",
        cat["acceptance_kit"]["note"],
        f"- Seats: {cat['acceptance_kit']['seats']['seat_a']['role']} / {cat['acceptance_kit']['seats']['seat_b']['role']}",
        f"- Cases: {', '.join(case['id'] for case in cat['acceptance_kit']['cases'])}",
        "- Kit PASS requires a twin effect_applied. It is not signed L1.",
        "",
        "## Success equation",
        "",
        cat["success_equation"],
        "",
        "## Still missing (honest)",
        "",
    ]
    for item in cat.get("honest_missing", []):
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
        "## Must not change",
        "",
    ]
    for rule in cat["must_not_change"]:
        lines.append(f"- {rule}")
    lines.append("")
    return "\n".join(lines)
