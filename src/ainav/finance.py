"""Catalog-list financial model. Not booked. Not recognized revenue."""

from __future__ import annotations

from typing import Any

from ainav.catalog import attach_band, industry_pack, load_catalog, sku


def _band(sku_id: str) -> tuple[int, int]:
    price = sku(sku_id)["price_usd"]
    return int(price["min"]), int(price["max"])


def _ffs_rate() -> int:
    cat = load_catalog()
    rates = [
        int(item["rate_usd_per_day"])
        for item in cat["fee_for_service"]
        if item.get("billable") is True
    ]
    return rates[0] if rates else 0


def _desks(*pack_ids: str) -> tuple[int, int]:
    lo = hi = 0
    for pack_id in pack_ids:
        band = attach_band(industry_pack(pack_id))
        lo += band[0]
        hi += band[1]
    return lo, hi


def spec() -> dict[str, Any]:
    return dict(load_catalog()["financial_model"])


def scenarios() -> list[dict[str, Any]]:
    """If-then catalog list. Zero customers. Zero recognized revenue."""
    l1_min, l1_max = _band("L1")
    keep_min, keep_max = _band("P-ADM")
    deep_min, deep_max = _band("U-DUAL")
    day = _ffs_rate()
    return [
        {
            "id": "l1_only",
            "name": "One controller — L1 only",
            "if": "One controller buys L1 and stops.",
            "skus": ["L1"],
            "n": 1,
            "min": l1_min,
            "max": l1_max,
        },
        {
            "id": "l1_padm",
            "name": "One controller — L1 then P-ADM",
            "if": "One controller buys L1, kit PASS, then attaches P-ADM.",
            "skus": ["L1", "P-ADM"],
            "n": 1,
            "min": l1_min + keep_min,
            "max": l1_max + keep_max,
        },
        {
            "id": "all_three",
            "name": "One controller — all three SKUs",
            "if": "One controller buys L1, attaches P-ADM, then pays for U-DUAL.",
            "skus": ["L1", "P-ADM", "U-DUAL"],
            "n": 1,
            "min": l1_min + keep_min + deep_min,
            "max": l1_max + keep_max + deep_max,
        },
        {
            "id": "three_l1_padm",
            "name": "Three controllers — L1 + P-ADM each",
            "if": "Three controllers each buy L1 and attach P-ADM. No named buyers exist.",
            "skus": ["L1", "P-ADM"],
            "n": 3,
            "min": 3 * (l1_min + keep_min),
            "max": 3 * (l1_max + keep_max),
        },
        {
            "id": "l1_plus_four_days",
            "name": "One L1 plus four FFS days",
            "if": "One controller buys L1 and four billable days on the same plane.",
            "skus": ["L1"],
            "ffs_days": 4,
            "n": 1,
            "min": l1_min + 4 * day,
            "max": l1_max + 4 * day,
        },
        {
            "id": "l1_plus_cascade",
            "name": "One L1 plus counterparty AI desk",
            "if": "One controller buys L1 then attaches industry.cascade for their customers' AI.",
            "skus": ["L1"],
            "packs": ["industry.cascade"],
            "n": 1,
            "min": l1_min + _desks("industry.cascade")[0],
            "max": l1_max + _desks("industry.cascade")[1],
        },
        {
            "id": "l1_padm_second_record",
            "name": "One controller — L1, P-ADM, second-record keep",
            "if": "One controller buys L1, attaches P-ADM, then attaches industry.second_record.",
            "skus": ["L1", "P-ADM"],
            "packs": ["industry.second_record"],
            "n": 1,
            "min": l1_min + keep_min + _desks("industry.second_record")[0],
            "max": l1_max + keep_max + _desks("industry.second_record")[1],
        },
        {
            "id": "l1_plus_off_switch",
            "name": "One L1 plus off-switch desk",
            "if": "One controller buys L1 then attaches industry.off_switch so humans can freeze writes.",
            "skus": ["L1"],
            "packs": ["industry.off_switch"],
            "n": 1,
            "min": l1_min + _desks("industry.off_switch")[0],
            "max": l1_max + _desks("industry.off_switch")[1],
        },
        {
            "id": "l1_padm_board",
            "name": "One controller — L1, P-ADM, board keep",
            "if": "One controller buys L1, attaches P-ADM, then attaches industry.board for owner/board/examiner evidence.",
            "skus": ["L1", "P-ADM"],
            "packs": ["industry.board"],
            "n": 1,
            "min": l1_min + keep_min + _desks("industry.board")[0],
            "max": l1_max + keep_max + _desks("industry.board")[1],
        },
        {
            "id": "l1_plus_two_desks",
            "name": "One L1 plus payables and bank desks",
            "if": "One controller buys L1 then attaches industry.payables and industry.bank.",
            "skus": ["L1"],
            "packs": ["industry.payables", "industry.bank"],
            "n": 1,
            "min": l1_min + _desks("industry.payables", "industry.bank")[0],
            "max": l1_max + _desks("industry.payables", "industry.bank")[1],
        },
        {
            "id": "l1_padm_oversight",
            "name": "One controller — L1, P-ADM, oversight keep",
            "if": "One controller buys L1, attaches P-ADM, then attaches industry.oversight.",
            "skus": ["L1", "P-ADM"],
            "packs": ["industry.oversight"],
            "n": 1,
            "min": l1_min + keep_min + _desks("industry.oversight")[0],
            "max": l1_max + keep_max + _desks("industry.oversight")[1],
        },
        {
            "id": "all_three_plus_desks",
            "name": "All three SKUs plus invoice and credit desks",
            "if": "One controller buys all three SKUs then attaches industry.invoice_desk and industry.credit.",
            "skus": ["L1", "P-ADM", "U-DUAL"],
            "packs": ["industry.invoice_desk", "industry.credit"],
            "n": 1,
            "min": l1_min + keep_min + deep_min + _desks("industry.invoice_desk", "industry.credit")[0],
            "max": l1_max + keep_max + deep_max + _desks("industry.invoice_desk", "industry.credit")[1],
        },
    ]


def model() -> dict[str, Any]:
    body = spec()
    return {
        "kind": body["kind"],
        "currency": body["currency"],
        "recognized_revenue": 0,
        "signed_l1": 0,
        "named_customers": 0,
        "billing_provider": False,
        "live": False,
        "live_pin_ok": False,
        "pricing_models": list(body["pricing_models"]),
        "scenarios": scenarios(),
        "note": body["note"],
    }


def finance_markdown() -> str:
    body = model()
    lines = [
        f"# {load_catalog()['entity']['legal']} — catalog-list financial model",
        "",
        body["note"],
        f"Recognized revenue: {body['recognized_revenue']}. Signed L1: {body['signed_l1']}. "
        f"Named customers: {body['named_customers']}. Billing provider: {str(body['billing_provider']).lower()}.",
        "",
        "## Pricing models",
        "",
    ]
    for item in body["pricing_models"]:
        extra = item.get("attach_after") or item.get("term") or ""
        rate = f" ${item['rate_usd']:,}/day" if item.get("rate_usd") else ""
        lines.append(f"- **{item['id']}** — {item['model']} ({item['unit']}){rate}. {extra}".rstrip())
    lines += ["", "## If-then catalog list (not a forecast)", ""]
    for row in body["scenarios"]:
        lines.append(
            f"- **{row['name']}** — {row['if']} "
            f"${row['min']:,}–${row['max']:,}."
        )
    lines.append("")
    return "\n".join(lines)


def public_finance() -> dict[str, Any]:
    return model()
