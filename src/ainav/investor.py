"""Letter packet for Cynthia Hodnett. Catalog-honest. Not a priced round.

Printable letter with the three SKUs, the full upsell catalog, list
prices, and the seat-B ask. Recognized revenue stays zero. Packs are
not SKUs.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from ainav.catalog import load_catalog
from ainav.finance import model as finance_model
from ainav.packs import public_packs

PDF_PATH = Path("docs/CYNTHIA_HODNETT_INVESTOR.pdf")
HTML_PATH = Path("docs/CYNTHIA_HODNETT_INVESTOR.html")
MD_PATH = Path("docs/CYNTHIA_HODNETT_INVESTOR.md")
PAGE_W = 612
PAGE_H = 792
LEFT = 48
RIGHT = 564
NAVY = "0.067 0.078 0.102"
GOLD = "0.769 0.647 0.455"
INK = "0.14 0.14 0.14"
MUTED = "0.35 0.30 0.24"


def spec() -> dict[str, Any]:
    return dict(load_catalog()["investor"])


def _money(lo: int, hi: int) -> str:
    return f"${lo:,}–${hi:,}"


def _price(item: dict[str, Any]) -> str:
    if item.get("included"):
        return f"included with {item['requires_sku']}"
    return _money(int(item.get("min") or 0), int(item.get("max") or 0))


def _clean_note(item: dict[str, Any], limit: int = 0) -> str:
    note = str(item.get("note") or "")
    for stem in (" Not a SKU.", " Not a fourth SKU.", " Not a SKU"):
        note = note.replace(stem, "")
    note = " ".join(note.split())
    if limit and len(note) > limit:
        return note[: limit - 1].rstrip() + "…"
    return note


def public_investor() -> dict[str, Any]:
    cat = load_catalog()
    body = spec()
    fin = finance_model()
    packs = public_packs()
    invited = cat["organization"]["contacts"]["invited"]
    by_id = {row["id"]: row for row in fin["scenarios"]}
    all_three = by_id["all_three"]
    industry = [dict(item) for item in packs["industry"]]
    return {
        "kind": body["kind"],
        "sku": False,
        "live": False,
        "live_pin_ok": False,
        "raise_claimed": False,
        "valuation_claimed": False,
        "forecast": False,
        "priced_round": False,
        "equity_offered": False,
        "not_a_round": True,
        "include_upsells": True,
        "confidential": True,
        "release": cat["entity"]["release"],
        "legal": cat["entity"]["legal"],
        "product": cat["entity"]["product"],
        "institute": cat["entity"]["institute"],
        "owner": cat["operating"]["owner_principal"],
        "audience": body["audience"],
        "date": body.get("date"),
        "letter_open": body.get("letter_open"),
        "letter_body": body.get("letter_body"),
        "letter_close": body.get("letter_close"),
        "executive_summary": dict(body.get("executive_summary") or {}),
        "signoff": body.get("signoff"),
        "invited": invited["name"],
        "recorded": False,
        "email": None,
        "one_liner": body["one_liner"],
        "equation": cat["equations"].get("investor"),
        "commercial": cat["equations"]["commercial"],
        "insulation": cat["equations"].get("insulation"),
        "company": body.get("company"),
        "problem": body["problem"],
        "solution": body["solution"],
        "why_now": body["why_now"],
        "icp": body["icp"],
        "model": body["model"],
        "unit_economics_note": body["unit_economics_note"],
        "stack": body.get("stack"),
        "seat_b": body.get("seat_b"),
        "will_not_ask": body.get("will_not_ask"),
        "capital": body.get("capital"),
        "sale_motion": body.get("sale_motion"),
        "tuesday": body.get("tuesday"),
        "upsell_note": body.get("upsell_note"),
        "insulation_copy": body["insulation"],
        "control_plane": body.get("control_plane"),
        "human_interface": cat.get("plane_interface", {}).get("letter"),
        "traction": body["traction"],
        "ask": body["ask"],
        "highlights": list(body.get("highlights") or []),
        "refuse": list(body.get("refuse") or []),
        "kpis": {
            "recognized_revenue": 0,
            "named_customers": 0,
            "signed_l1": 0,
            "billing_provider": False,
        },
        "skus": [
            {
                "id": item["id"],
                "name": item["name"],
                "kind": item["kind"],
                "min": int(item["price_usd"]["min"]),
                "max": int(item["price_usd"]["max"]),
                "term": item["term"],
            }
            for item in cat["skus"]
        ],
        "year_one_if_all_three": {
            "min": all_three["min"],
            "max": all_three["max"],
            "note": "Catalog list if one controller buys L1, P-ADM, and U-DUAL. Not booked.",
        },
        "scenarios": [
            {
                "id": row["id"],
                "name": row["name"],
                "if": row["if"],
                "min": row["min"],
                "max": row["max"],
            }
            for row in fin["scenarios"]
        ],
        "industry": industry,
        "libraries": [dict(item) for item in packs["libraries"]],
        "fee_for_service": [dict(item) for item in packs["fee_for_service"]],
        "print": dict(body.get("print") or {}),
        "note": body.get("note"),
    }


def _desk_rows(body: dict[str, Any], sku: str) -> list[list[str]]:
    rows = []
    for item in body["industry"]:
        if item["requires_sku"] != sku:
            continue
        rows.append(
            [
                f"{item['id']} — {item['name']}",
                _price(item),
                _clean_note(item),
            ]
        )
    return rows


def investor_markdown() -> str:
    body = public_investor()
    lines = [
        f"# {body['legal']} — Investor packet for {body['invited']}",
        "",
        f"{body.get('date') or ''}. Confidential. For {body['invited']}. From {body['owner']}. Release {body['release']}.",
        "Not a priced round. Not a forecast. Not a contract. Not signed L1. Not LIVE_PIN_OK.",
        "",
        f"**{body['one_liner']}**",
        "",
        "## Executive summary",
        "",
        (body.get("executive_summary") or {}).get("lede") or "",
        "",
        f"Job C: {(body.get('executive_summary') or {}).get('job_c') or ''}",
        "",
        f"Proof day: {(body.get('executive_summary') or {}).get('proof') or ''}",
        "",
        f"Three SKUs: {(body.get('executive_summary') or {}).get('skus') or ''}",
        "",
        f"Scoreboard: {(body.get('executive_summary') or {}).get('tiles') or ''}",
        "",
        f"Microsoft: {(body.get('executive_summary') or {}).get('microsoft') or ''}",
        "",
        f"Must-have: {(body.get('executive_summary') or {}).get('must_have') or ''}",
        "",
        f"Owner-only still open: {(body.get('executive_summary') or {}).get('opens') or ''}",
        "",
        f"The ask: {(body.get('executive_summary') or {}).get('ask') or ''}",
        "",
        "## A letter to Cynthia Hodnett",
        "",
        body.get("letter_open") or "",
        "",
        body.get("letter_body") or "",
        "",
        f"Equation: {body.get('equation')}.",
        f"Commercial close: {body['commercial']}.",
        f"Insulation: {body.get('insulation')}.",
        "",
        "## The company",
        "",
        body.get("company") or "",
        "",
        "## The problem",
        "",
        body["problem"],
        "",
        "## The product",
        "",
        body["solution"],
        "",
        "## Why the ultimate control plane insulates",
        "",
        body.get("control_plane") or "",
        "",
        "## How humans sit on the plane — interface and dashboard",
        "",
        body.get("human_interface") or "",
        "",
        "## Who buys, and why now",
        "",
        body["icp"],
        "",
        body["why_now"],
        "",
        "## What we are asking of you",
        "",
        body.get("seat_b") or "",
        "",
        body["ask"],
        "",
        "## What we will not ask",
        "",
        body.get("will_not_ask") or "",
        "",
        "## What a Tuesday looks like",
        "",
        body.get("tuesday") or "",
        "",
        "## How a sale works",
        "",
        body.get("sale_motion") or "",
        "",
        "## Business model — three SKUs only",
        "",
        body["model"],
        "",
        body["unit_economics_note"],
        "",
        body.get("stack") or "",
        "",
        "| SKU | Role | Catalog list | Term |",
        "| --- | --- | --- | --- |",
    ]
    for item in body["skus"]:
        lines.append(
            f"| {item['id']} | {item['kind']} | {_money(item['min'], item['max'])} | {item['term']} |"
        )
    lines += [
        "",
        f"Year-one catalog list if one controller buys all three: "
        f"{_money(body['year_one_if_all_three']['min'], body['year_one_if_all_three']['max'])}. "
        "Not booked.",
        "",
        body.get("capital") or "",
        "",
        "## Upsell catalog — not a fourth SKU",
        "",
        body.get("upsell_note") or "",
        "",
        "### L1 desks",
        "",
        "| Desk | List | What it is |",
        "| --- | --- | --- |",
    ]
    for row in _desk_rows(body, "L1"):
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} |")
    lines += [
        "",
        "### P-ADM keep after kit PASS",
        "",
        "| Keep | List | What it is |",
        "| --- | --- | --- |",
    ]
    for row in _desk_rows(body, "P-ADM"):
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} |")
    lines += [
        "",
        "### U-DUAL desks — never free",
        "",
        "| Desk | List | What it is |",
        "| --- | --- | --- |",
    ]
    for row in _desk_rows(body, "U-DUAL"):
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} |")
    lines += [
        "",
        "### Fee-for-service — $3,500/day after L1",
        "",
        "| Service | Rate | What it is |",
        "| --- | --- | --- |",
    ]
    for item in body["fee_for_service"]:
        rate = "inside L1" if not item.get("billable") else f"${int(item['rate_usd_per_day']):,}/day"
        lines.append(
            f"| {item['id']} — {item.get('name')} | {rate} | {_clean_note(item)} |"
        )
    lines += [
        "",
        "### Libraries — not SKUs",
        "",
        "| Library | Requires | What it is |",
        "| --- | --- | --- |",
    ]
    for item in body["libraries"]:
        lines.append(f"| {item['id']} | {item['requires_sku']} | {_clean_note(item)} |")
    lines += [
        "",
        "## If-then catalog list (not a forecast)",
        "",
        "These rows are attach math on list prices. They are not bookings and not a forecast.",
        "",
        "| Scenario | If | List |",
        "| --- | --- | --- |",
    ]
    for row in body["scenarios"]:
        lines.append(f"| {row['name']} | {row['if']} | {_money(row['min'], row['max'])} |")
    lines += [
        "",
        "## Insulation",
        "",
        body["insulation_copy"],
        f"Insulation equation: {body.get('insulation')}.",
        "",
        "## Traction — honest",
        "",
        body["traction"],
        "",
        f"- Recognized revenue: ${body['kpis']['recognized_revenue']:,}",
        f"- Named customers: {body['kpis']['named_customers']}",
        f"- Signed L1: {body['kpis']['signed_l1']}",
        f"- Billing provider: {str(body['kpis']['billing_provider']).lower()}",
        "",
        "## The ask",
        "",
        body["ask"],
        "",
        body.get("will_not_ask") or "",
        "",
        "## Highlights",
        "",
    ]
    for item in body["highlights"]:
        lines.append(f"- {item}")
    lines += ["", "## This packet refuses", ""]
    for item in body["refuse"]:
        lines.append(f"- {item}")
    lines += [
        "",
        body.get("note") or "",
        "",
        f"{body.get('letter_close') or body.get('signoff') or body['owner']}",
        "",
    ]
    return "\n".join(lines)


def _paras(text: str) -> str:
    chunks = [chunk.strip() for chunk in str(text or "").split("\n\n") if chunk.strip()]
    return "".join(f"<p>{html.escape(chunk)}</p>" for chunk in chunks)


def _table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(cell)}</th>" for cell in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def investor_html() -> str:
    body = public_investor()
    sku_rows = [
        [item["id"], item["kind"], _money(item["min"], item["max"]), item["term"]] for item in body["skus"]
    ]
    l1 = _desk_rows(body, "L1")
    padm = _desk_rows(body, "P-ADM")
    udual = _desk_rows(body, "U-DUAL")
    ffs = [
        [
            f"{item['id']} — {item.get('name') or ''}",
            "inside L1" if not item.get("billable") else f"${int(item['rate_usd_per_day']):,}/day",
            _clean_note(item),
        ]
        for item in body["fee_for_service"]
    ]
    libs = [
        [item["id"], item["requires_sku"], _clean_note(item, 140)] for item in body["libraries"]
    ]
    scenarios = [[row["name"], row["if"], _money(row["min"], row["max"])] for row in body["scenarios"]]
    highlights = "".join(f"<li>{html.escape(item)}</li>" for item in body["highlights"])
    refuse = "".join(f"<li>{html.escape(item)}</li>" for item in body["refuse"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(body['legal'])} — Investor packet for {html.escape(body['invited'])}</title>
<style>
@page {{ size: letter; margin: 0.55in 0.65in 0.6in 0.65in; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font: 10.5pt/1.42 Georgia, "Times New Roman", Times, serif; color: #16181d; background: #fff; }}
.band {{ background: #11141a; color: #f4efe6; padding: 18pt 20pt 16pt; margin: 0 0 16pt; }}
.band .mark {{ font: 700 8.5pt Helvetica, Arial, sans-serif; letter-spacing: 0.24em; color: #c4a574; }}
.band h1 {{ font: 700 22pt Helvetica, Arial, sans-serif; margin: 5pt 0 3pt; letter-spacing: -0.03em; }}
.band .sub {{ font: 8.5pt Helvetica, Arial, sans-serif; color: #d8d2c6; margin: 0; }}
.kpis {{ display: flex; gap: 8pt; margin: 0 0 16pt; }}
.kpi {{ flex: 1; border: 0.8pt solid #cfc6b6; background: #f7f3ea; padding: 8pt 9pt; }}
.kpi .label {{ font: 700 7pt Helvetica, Arial, sans-serif; letter-spacing: 0.1em; text-transform: uppercase; color: #6a6256; }}
.kpi .value {{ font: 700 12pt Helvetica, Arial, sans-serif; margin-top: 3pt; }}
h2 {{ font: 700 9pt Helvetica, Arial, sans-serif; letter-spacing: 0.1em; text-transform: uppercase; color: #11141a; border-bottom: 1.2pt solid #c4a574; padding-bottom: 3pt; margin: 16pt 0 7pt; page-break-after: avoid; }}
h3 {{ font: 700 11pt Georgia, Times, serif; margin: 12pt 0 5pt; color: #11141a; }}
p {{ margin: 0 0 8pt; }}
.lede {{ font: 700 13pt/1.35 Helvetica, Arial, sans-serif; color: #11141a; }}
.open {{ font: italic 11pt/1.45 Georgia, Times, serif; color: #2a241c; margin: 0 0 12pt; }}
.eq {{ font: italic 10pt Georgia, Times, serif; color: #3d3428; margin: 0 0 12pt; }}
.split {{ display: flex; gap: 16pt; }}
.split > div {{ flex: 1; }}
table {{ width: 100%; border-collapse: collapse; margin: 4pt 0 12pt; font: 8.2pt/1.3 Helvetica, Arial, sans-serif; page-break-inside: auto; }}
th, td {{ border: 0.5pt solid #b9b1a4; padding: 4pt 5pt; vertical-align: top; text-align: left; }}
th {{ background: #11141a; color: #f4efe6; font-weight: 700; }}
ul {{ margin: 0 0 10pt 1.15em; padding: 0; }}
li {{ margin: 0 0 3pt; }}
.ask {{ border: 1.5pt solid #11141a; padding: 12pt 14pt; margin: 10pt 0 14pt; background: #fbf8f1; page-break-inside: avoid; }}
.ask h2 {{ margin-top: 0; border: 0; padding: 0; }}
.sign {{ margin: 18pt 0 8pt; font: italic 11pt Georgia, Times, serif; }}
.status {{ font: 8.5pt Helvetica, Arial, sans-serif; color: #555; }}
footer {{ border-top: 0.7pt solid #b9b1a4; margin-top: 14pt; padding-top: 7pt; font: 8pt Helvetica, Arial, sans-serif; color: #666; }}
@media print {{ .kpis, .split, .ask {{ break-inside: avoid; }} }}
</style>
</head>
<body>
<div class="band">
  <div class="mark">{html.escape(body['legal'].upper())}</div>
  <h1>A letter to {html.escape(body['invited'])}</h1>
  <p class="sub">{html.escape(body.get('date') or '')}  ·  Confidential  ·  From {html.escape(body['owner'])}  ·  Release {html.escape(body['release'])}  ·  Investor packet  ·  Full upsell catalog  ·  Not a priced round</p>
</div>
<p class="lede">{html.escape(body['one_liner'])}</p>
<h2>Executive summary</h2>
<p>{html.escape((body.get('executive_summary') or {}).get('lede') or '')}</p>
<div class="split">
  <div><h3>Job C</h3><p>{html.escape((body.get('executive_summary') or {}).get('job_c') or '')}</p>
  <h3>Proof day</h3><p>{html.escape((body.get('executive_summary') or {}).get('proof') or '')}</p></div>
  <div><h3>Three SKUs</h3><p>{html.escape((body.get('executive_summary') or {}).get('skus') or '')}</p>
  <h3>Scoreboard</h3><p>{html.escape((body.get('executive_summary') or {}).get('tiles') or '')}</p></div>
</div>
<p>{html.escape((body.get('executive_summary') or {}).get('microsoft') or '')}</p>
<p>{html.escape((body.get('executive_summary') or {}).get('must_have') or '')}</p>
<p>{html.escape((body.get('executive_summary') or {}).get('opens') or '')}</p>
<p>{html.escape((body.get('executive_summary') or {}).get('ask') or '')}</p>
<h2>A letter to Cynthia Hodnett</h2>
<p class="open">{html.escape(body.get('letter_open') or '')}</p>
{_paras(body.get('letter_body') or '')}
<p class="eq">Close = {html.escape(body['commercial'])}. Insulation = {html.escape(body.get('insulation') or '')}. Packet = {html.escape(body.get('equation') or '')}.</p>
<div class="kpis">
  <div class="kpi"><div class="label">Recognized revenue</div><div class="value">$0</div></div>
  <div class="kpi"><div class="label">Named customers</div><div class="value">0</div></div>
  <div class="kpi"><div class="label">Signed L1</div><div class="value">0</div></div>
  <div class="kpi"><div class="label">Year-one if all three</div><div class="value">{html.escape(_money(body['year_one_if_all_three']['min'], body['year_one_if_all_three']['max']))}</div></div>
</div>
<h2>The company</h2>
<p>{html.escape(body.get('company') or '')}</p>
<div class="split">
  <div><h2>The problem</h2><p>{html.escape(body['problem'])}</p></div>
  <div><h2>The product</h2><p>{html.escape(body['solution'])}</p></div>
</div>
<h2>Why the ultimate control plane insulates</h2>
{_paras(body.get('control_plane') or '')}
<h2>How humans sit on the plane — interface and dashboard</h2>
{_paras(body.get('human_interface') or '')}
<h2>Who buys · why now</h2>
<p>{html.escape(body['icp'])}</p>
<p>{html.escape(body['why_now'])}</p>
<h2>What we are asking of you</h2>
<p>{html.escape(body.get('seat_b') or '')}</p>
<p>{html.escape(body['ask'])}</p>
<h2>What we will not ask</h2>
<p>{html.escape(body.get('will_not_ask') or '')}</p>
<h2>What a Tuesday looks like</h2>
<p>{html.escape(body.get('tuesday') or '')}</p>
<h2>How a sale works</h2>
<p>{html.escape(body.get('sale_motion') or '')}</p>
<h2>Business model — three SKUs only</h2>
<p>{html.escape(body['model'])}</p>
<p>{html.escape(body['unit_economics_note'])}</p>
<p>{html.escape(body.get('stack') or '')}</p>
{_table(["SKU", "Role", "Catalog list", "Term"], sku_rows)}
<p>{html.escape(body.get('capital') or '')}</p>
<h2>Upsell catalog — not a fourth SKU</h2>
<p>{html.escape(body.get('upsell_note') or '')}</p>
<h3>L1 desks</h3>
{_table(["Desk", "List", "What it is"], l1)}
<h3>P-ADM keep after kit PASS</h3>
{_table(["Keep", "List", "What it is"], padm)}
<h3>U-DUAL desks — never free</h3>
{_table(["Desk", "List", "What it is"], udual)}
<h3>Fee-for-service</h3>
{_table(["Service", "Rate", "What it is"], ffs)}
<h3>Libraries</h3>
{_table(["Library", "Requires", "What it is"], libs)}
<h2>If-then catalog list — not a forecast</h2>
<p>These rows are attach math on list prices. They are not bookings and not a forecast.</p>
{_table(["Scenario", "If", "List"], scenarios)}
<h2>Insulation</h2>
<p>{html.escape(body['insulation_copy'])}</p>
<h2>Traction — honest</h2>
<p>{html.escape(body['traction'])}</p>
<div class="ask">
  <h2>The ask</h2>
  <p>{html.escape(body['ask'])}</p>
  <p>{html.escape(body.get('will_not_ask') or '')}</p>
</div>
<h2>Highlights</h2>
<ul>{highlights}</ul>
<h2>This packet refuses</h2>
<ul>{refuse}</ul>
<p class="sign">{html.escape(body.get('letter_close') or body.get('signoff') or body['owner'])}</p>
<p class="status">{html.escape(body.get('note') or '')} Invited: {html.escape(body['invited'])}. Recorded: no. Email: none stored. Equity: no.</p>
<footer>{html.escape(body['legal'])}  ·  Job C  ·  {html.escape(body['institute'])}  ·  Investor packet  ·  Do not treat as a raise, equity grant, signed L1, or LIVE_PIN_OK.</footer>
</body>
</html>
"""


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap(text: str, width: int) -> list[str]:
    words = str(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if len(trial) > width:
            if current:
                lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines or [""]


class _Letter:
    def __init__(self, legal: str, invited: str, owner: str, release: str, date: str) -> None:
        self.legal = legal
        self.invited = invited
        self.owner = owner
        self.release = release
        self.date = date
        self.pages: list[list[str]] = []
        self.y = 0.0
        self._new(f"A letter to {invited}")

    def _draw(self, *cmds: str) -> None:
        self.pages[-1].extend(cmds)

    def _new(self, subtitle: str) -> None:
        self.pages.append([])
        self.y = 708
        self._draw(f"{NAVY} rg", "0 730 612 62 re f", f"{GOLD} rg", "0 726 612 4 re f")
        self.text(LEFT, 770, "/F2", 8, f"{GOLD} rg", self.legal.upper())
        self.text(LEFT, 750, "/F2", 15, "1 1 1 rg", subtitle[:64])
        self.text(
            LEFT,
            736,
            "/F3",
            8,
            "0.85 0.82 0.76 rg",
            f"{self.date}  ·  Confidential  ·  From {self.owner}  ·  Release {self.release}",
        )

    def need(self, height: float, subtitle: str = "Investor packet") -> None:
        if self.y - height < 52:
            self._new(subtitle)

    def text(self, x: float, y: float, font: str, size: float, rgb: str, line: str) -> None:
        self._draw("BT", f"{font} {size} Tf", rgb, f"1 0 0 1 {x:.1f} {y:.1f} Tm", f"({_escape(line)}) Tj", "ET")

    def heading(self, title: str, subtitle: str = "Upsell catalog") -> None:
        self.need(30, subtitle)
        self.y -= 6
        self.text(LEFT, self.y, "/F2", 9, f"{NAVY} rg", title.upper())
        self._draw(f"{GOLD} RG", "1.1 w", f"{LEFT} {self.y - 3:.1f} m {RIGHT} {self.y - 3:.1f} l S")
        self.y -= 16

    def para(self, text: str, width: int = 90, size: float = 9, rgb: str = f"{INK} rg", font: str = "/F1") -> None:
        lines = _wrap(text, width)
        self.need(len(lines) * 12 + 4)
        for line in lines:
            self.text(LEFT, self.y, font, size, rgb, line)
            self.y -= 12
        self.y -= 4

    def lede(self, text: str) -> None:
        lines = _wrap(text, 72)
        self.need(len(lines) * 14 + 4)
        for line in lines:
            self.text(LEFT, self.y, "/F2", 11.5, f"{NAVY} rg", line)
            self.y -= 14
        self.y -= 3

    def table(self, headers: list[str], rows: list[list[str]], cols: list[float], subtitle: str = "Upsell catalog") -> None:
        row_h = 14
        self.need(22 + row_h * min(len(rows) + 1, 8), subtitle)
        self._draw(f"{NAVY} rg", f"{LEFT} {self.y - 12:.1f} {RIGHT - LEFT:.1f} 16 re f")
        for i, head in enumerate(headers):
            self.text(cols[i], self.y - 8, "/F2", 7.2, "1 1 1 rg", head)
        self.y -= 16
        for row in rows:
            self.need(row_h + 2, subtitle)
            self._draw("0.98 0.97 0.95 rg", f"{LEFT} {self.y - 11:.1f} {RIGHT - LEFT:.1f} 14 re f")
            for i, cell in enumerate(row):
                self.text(cols[i], self.y - 7, "/F3", 7.1, "0.12 0.12 0.12 rg", str(cell)[:58])
            self.y -= row_h
        self.y -= 8

    def finish(self) -> None:
        n = len(self.pages)
        for i, page in enumerate(self.pages, start=1):
            label = (
                f"{self.legal}  ·  Page {i} of {n}  ·  For {self.invited}  ·  "
                "Not a priced round  ·  Not LIVE_PIN_OK"
            )
            page.extend(
                [
                    "BT",
                    "/F3 7.5 Tf",
                    "0.4 0.4 0.4 rg",
                    f"1 0 0 1 {LEFT:.1f} 28.0 Tm",
                    f"({_escape(label)}) Tj",
                    "ET",
                ]
            )


def render_investor_pdf() -> bytes:
    """Letter packet. Flowing pages. Catalog list only."""
    body = public_investor()
    doc = _Letter(
        body["legal"],
        body["invited"],
        body["owner"],
        body["release"],
        str(body.get("date") or ""),
    )
    doc.lede(body["one_liner"])
    summary = body.get("executive_summary") or {}
    doc.heading("Executive summary", "The company")
    doc.para(str(summary.get("lede") or ""))
    doc.para(f"Job C: {summary.get('job_c') or ''}")
    doc.para(f"Proof day: {summary.get('proof') or ''}")
    doc.para(f"Three SKUs: {summary.get('skus') or ''}")
    doc.para(f"Scoreboard: {summary.get('tiles') or ''}")
    doc.para(str(summary.get("microsoft") or ""))
    doc.para(str(summary.get("must_have") or ""))
    doc.para(str(summary.get("opens") or ""))
    doc.para(str(summary.get("ask") or ""))
    doc.heading("A letter to Cynthia Hodnett", "The company")
    doc.para(body.get("letter_open") or "", width=88, size=9.5, rgb=f"{MUTED} rg")
    for chunk in str(body.get("letter_body") or "").split("\n\n"):
        if chunk.strip():
            doc.para(chunk.strip(), width=88, size=9.5)
    doc.para(
        f"Close = {body['commercial']}.  Insulation = {body.get('insulation')}.  Packet = {body.get('equation')}.",
        rgb=f"{MUTED} rg",
        size=8.5,
        width=96,
    )
    kpis = [
        ("RECOGNIZED REVENUE", "$0"),
        ("NAMED CUSTOMERS", "0"),
        ("SIGNED L1", "0"),
        ("YEAR-ONE IF ALL THREE", _money(body["year_one_if_all_three"]["min"], body["year_one_if_all_three"]["max"])),
    ]
    doc.need(50)
    box_w = 124
    for i, (label, value) in enumerate(kpis):
        x = LEFT + i * (box_w + 8)
        doc._draw("0.969 0.953 0.918 rg", f"{x:.1f} {doc.y - 36:.1f} {box_w:.1f} 42 re f")
        doc._draw(f"{GOLD} RG", "1.2 w", f"{x:.1f} {doc.y - 36:.1f} m {x + box_w:.1f} {doc.y - 36:.1f} l S")
        doc.text(x + 8, doc.y - 6, "/F2", 6.5, "0.42 0.38 0.34 rg", label)
        doc.text(x + 8, doc.y - 24, "/F2", 9.5, f"{NAVY} rg", value)
    doc.y -= 50

    doc.heading("The company", "The company")
    doc.para(body.get("company") or "")
    doc.heading("The problem", "The company")
    doc.para(body["problem"])
    doc.heading("The product", "The company")
    doc.para(body["solution"])
    doc.heading("Why the ultimate control plane insulates", "The company")
    for chunk in str(body.get("control_plane") or "").split("\n\n"):
        if chunk.strip():
            doc.para(chunk.strip())
    doc.heading("How humans sit on the plane", "The company")
    for chunk in str(body.get("human_interface") or "").split("\n\n"):
        if chunk.strip():
            doc.para(chunk.strip())
    doc.heading("Who buys · why now", "The company")
    doc.para(body["icp"])
    doc.para(body["why_now"])
    doc.heading("What we are asking of you", "The company")
    doc.para(body.get("seat_b") or "")
    doc.para(body["ask"])
    doc.heading("What we will not ask", "The company")
    doc.para(body.get("will_not_ask") or "")
    doc.heading("What a Tuesday looks like", "The company")
    doc.para(body.get("tuesday") or "")
    doc.heading("How a sale works", "The company")
    doc.para(body.get("sale_motion") or "")

    doc.heading("Business model — three SKUs only", "Pricing")
    doc.para(body["model"])
    doc.para(body["unit_economics_note"])
    doc.para(body.get("stack") or "")
    doc.table(
        ["SKU", "Role", "Catalog list", "Term"],
        [[i["id"], i["kind"], _money(i["min"], i["max"]), i["term"]] for i in body["skus"]],
        [LEFT + 4, 130, 220, 400],
        "Pricing",
    )
    doc.para(body.get("capital") or "")

    doc.heading("Upsell catalog — not a fourth SKU", "Upsell catalog")
    doc.para(body.get("upsell_note") or "")
    doc.heading("L1 desks", "Upsell catalog")
    doc.table(
        ["Desk", "List", "What it is"],
        [
            [i["name"][:22], _price(i), _clean_note(i, 38)]
            for i in body["industry"]
            if i["requires_sku"] == "L1"
        ],
        [LEFT + 4, 168, 300],
    )
    doc.heading("P-ADM keep after kit PASS", "Upsell catalog")
    doc.table(
        ["Keep", "List", "What it is"],
        [
            [i["name"][:22], _price(i), _clean_note(i, 38)]
            for i in body["industry"]
            if i["requires_sku"] == "P-ADM"
        ],
        [LEFT + 4, 168, 300],
    )
    doc.heading("U-DUAL desks — never free", "Upsell catalog")
    doc.table(
        ["Desk", "List", "What it is"],
        [
            [i["name"][:22], _price(i), _clean_note(i, 38)]
            for i in body["industry"]
            if i["requires_sku"] == "U-DUAL"
        ],
        [LEFT + 4, 168, 300],
    )
    doc.heading("Fee-for-service — $3,500/day after L1", "Upsell catalog")
    ffs_rows = []
    for item in body["fee_for_service"]:
        rate = "inside L1" if not item.get("billable") else f"${int(item['rate_usd_per_day']):,}/day"
        ffs_rows.append([(item.get("name") or "")[:22], rate, _clean_note(item, 32)])
    doc.table(["Service", "Rate", "What it is"], ffs_rows, [LEFT + 4, 180, 280])
    doc.heading("Libraries — not SKUs", "Upsell catalog")
    doc.table(
        ["Library", "Requires", "What it is"],
        [[i["id"].replace("lib.", ""), i["requires_sku"], _clean_note(i, 36)] for i in body["libraries"]],
        [LEFT + 4, 200, 270],
    )

    doc.heading("If-then catalog list — not a forecast", "Financials")
    doc.para("These rows are attach math on list prices. They are not bookings and not a forecast.")
    doc.table(
        ["Scenario", "List"],
        [[row["name"][:44], _money(row["min"], row["max"])] for row in body["scenarios"]],
        [LEFT + 4, 400],
        "Financials",
    )

    doc.heading("Insulation", "Close")
    doc.para(body["insulation_copy"])
    doc.heading("Traction — honest", "Close")
    doc.para(body["traction"])
    doc.heading("The ask", "Close")
    doc.para(body["ask"])
    doc.para(body.get("will_not_ask") or "")
    doc.heading("Highlights", "Close")
    for item in body["highlights"]:
        doc.para(f"— {item}")
    doc.heading("This packet refuses", "Close")
    doc.para("  ·  ".join(body["refuse"]))
    doc.para(body.get("note") or "", rgb="0.4 0.4 0.4 rg", size=8)
    doc.para(body.get("letter_close") or body.get("signoff") or body["owner"], font="/F2", size=10)
    doc.finish()
    return _assemble(doc.pages)


def _assemble(page_streams: list[list[str]]) -> bytes:
    decorated = ["\n".join(stream) for stream in page_streams]
    objects: list[bytes] = [b""]
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + i} 0 R" for i in range(len(decorated)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(decorated)} >>".encode())
    font_times = 3 + len(decorated)
    font_helv_b = font_times + 1
    font_helv = font_helv_b + 1
    for index, _stream in enumerate(decorated):
        content_id = font_helv + 1 + index
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
                f"/Resources << /Font << /F1 {font_times} 0 R /F2 {font_helv_b} 0 R /F3 {font_helv} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            ).encode()
        )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for stream in decorated:
        raw = stream.encode("latin-1", "replace")
        objects.append(f"<< /Length {len(raw)} >>\nstream\n".encode() + raw + b"\nendstream")

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, payload in enumerate(objects[1:], start=1):
        offsets.append(len(out))
        out.extend(f"{number} 0 obj\n".encode())
        out.extend(payload)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        out.extend(f"{offset:010d} 00000 n \n".encode())
    out.extend(
        (
            f"trailer << /Size {len(objects)} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode()
    )
    return bytes(out)


def write_investor(path: Path | None = None) -> Path:
    target = path or PDF_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    html_path = HTML_PATH if path is None else target.with_suffix(".html")
    md_path = MD_PATH if path is None else target.with_suffix(".md")
    html_path.write_text(investor_html(), encoding="utf-8")
    md_path.write_text(investor_markdown(), encoding="utf-8")
    target.write_bytes(render_investor_pdf())
    return target
