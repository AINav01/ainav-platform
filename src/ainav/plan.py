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
    for sku in cat["skus"]:
        price = sku["price_usd"]
        lines.append(
            f"- **{sku['id']} {sku['name']}** — ${price['min']:,}–${price['max']:,} ({sku['term']})"
        )
        for item in sku.get("includes", []):
            lines.append(f"  - includes: {item}")
        for item in sku.get("does_not_include", []):
            lines.append(f"  - does not include: {item}")
        if sku.get("never_free_with"):
            lines.append(f"  - never free with: {', '.join(sku['never_free_with'])}")
    lines += [
        "",
        "## Delivery",
        "",
        "- **Master mothership** (AINav): issues lockfiles, gold vectors, catalog.",
        "- **Local mothership** (client): AdmitClient + lockfile + ledger + twin.",
        "- **L1 wedge:** `bc.general_journal.post` on a Business Central twin.",
        "- **Teams:** notify only. A chat is not a seat.",
        "- **Entra:** seat object ids. Not an IdP replacement.",
        "",
        f"## Success equation",
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
