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
        "- **Teams:** notify only. A chat is not a seat.",
        "- **Entra:** seat object ids. Not an IdP replacement.",
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
        "## Success equation",
        "",
        cat["success_equation"],
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
