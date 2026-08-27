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
        "## Commercial spine (do not invent SKUs)",
        "",
    ]
    for sku_item in cat["skus"]:
        price = sku_item["price_usd"]
        lines.append(
            f"- **{sku_item['id']} {sku_item['name']}** — "
            f"${price['min']:,}–${price['max']:,} ({sku_item['term']})"
        )
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
        lines.append(
            f"- **{pack['id']}** — {pack['name']} "
            f"(requires {pack['requires_sku']}; {pack['note']})"
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
        "- **Master mothership** (AINav): issues lockfiles, gold vectors, catalog.",
        "- **Local mothership** (client): AdmitClient + lockfile + ledger + twin.",
        "- **L1 wedge:** `bc.general_journal.post` on a Business Central twin.",
        "- **U-DUAL deepen:** Sales Enterprise twin after a paid attach.",
        "- **Teams Enterprise / Premium:** notify only. A chat is not a seat.",
        "- **Entra (via Microsoft 365 E7):** seat object ids. Not an IdP replacement.",
        "- **Azure:** declared host for the master mothership and Institute static site.",
        "- **Business Central Premium / Sales Enterprise:** sandbox SoR until G14.",
        "- Copilot and Agent 365 ship inside E7. They are not the admit plane.",
        "- Complements: Entra ID, Azure Key Vault, Azure Monitor, SharePoint kit evidence, Defender XDR.",
        "",
        "## Business operating system",
        "",
        cat["business"]["thesis"],
        f"- Motion: {cat['business']['sales']['motion']}",
        f"- Services: {cat['business']['services']['principle']}",
        f"- Economics: {cat['business']['economics']['note']}",
        "- Complements are not SKUs. Industry packs and FFS hours are not SKUs.",
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
        "- NVIDIA Inception and Microsoft for Startups: prepare only. Membership is not claimed.",
        "- Later / complementary: NVIDIA Developer, GitHub for Startups, Microsoft ISV Success, NVIDIA Connect.",
        "- Inception excludes cryptocurrency-associated companies. Do not lead with gold-vector custody fixtures.",
        "- Ready to apply is false until a public website and incorporation date exist outside this tree.",
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
