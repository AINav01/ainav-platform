"""Investor-grade executive summary. Catalog-honest. Not a priced round.

Printable two-page letter for Cynthia Hodnett. Recognized revenue stays zero.
No invented valuation, forecast ARR, named buyer, or equity grant.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from ainav.catalog import load_catalog
from ainav.finance import model as finance_model

PDF_PATH = Path("docs/CYNTHIA_HODNETT_INVESTOR.pdf")
HTML_PATH = Path("docs/CYNTHIA_HODNETT_INVESTOR.html")
MD_PATH = Path("docs/CYNTHIA_HODNETT_INVESTOR.md")
PAGE_W = 612
PAGE_H = 792
LEFT = 48
RIGHT = 564


def spec() -> dict[str, Any]:
    return dict(load_catalog()["investor"])


def public_investor() -> dict[str, Any]:
    cat = load_catalog()
    body = spec()
    fin = finance_model()
    invited = cat["organization"]["contacts"]["invited"]
    by_id = {row["id"]: row for row in fin["scenarios"]}
    all_three = by_id["all_three"]
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
        "confidential": True,
        "release": cat["entity"]["release"],
        "legal": cat["entity"]["legal"],
        "product": cat["entity"]["product"],
        "institute": cat["entity"]["institute"],
        "owner": cat["operating"]["owner_principal"],
        "audience": body["audience"],
        "invited": invited["name"],
        "recorded": False,
        "email": None,
        "one_liner": body["one_liner"],
        "equation": cat["equations"].get("investor"),
        "commercial": cat["equations"]["commercial"],
        "insulation": cat["equations"].get("insulation"),
        "problem": body["problem"],
        "solution": body["solution"],
        "why_now": body["why_now"],
        "icp": body["icp"],
        "model": body["model"],
        "unit_economics_note": body["unit_economics_note"],
        "insulation_copy": body["insulation"],
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
            if row["id"]
            in {
                "l1_only",
                "l1_padm",
                "all_three",
                "three_l1_padm",
                "l1_plus_four_days",
            }
        ],
        "print": dict(body.get("print") or {}),
        "note": body.get("note"),
    }


def investor_markdown() -> str:
    body = public_investor()
    lines = [
        f"# {body['legal']} — Investor executive summary",
        "",
        f"Confidential. For {body['invited']}. From {body['owner']}. Release {body['release']}.",
        "Not a priced round. Not a forecast. Not a contract. Not signed L1. Not LIVE_PIN_OK.",
        "",
        f"**{body['one_liner']}**",
        "",
        f"Equation: {body.get('equation')}.",
        f"Commercial close: {body['commercial']}.",
        "",
        "## The company",
        "",
        f"{body['legal']} is a Delaware C corporation. Sole owner: {body['owner']}.",
        f"Product: {body['product']}. Public face: {body['institute']} (hosted, not launched).",
        "Job C only. Microsoft is identity, notify, SoR, and host. Microsoft is not the product.",
        "",
        "## Problem",
        "",
        body["problem"],
        "",
        "## Solution",
        "",
        body["solution"],
        "",
        "## Why now",
        "",
        body["why_now"],
        "",
        "## Who buys",
        "",
        body["icp"],
        "",
        "## Business model",
        "",
        body["model"],
        body["unit_economics_note"],
        "",
        "| SKU | Role | List | Term |",
        "| --- | --- | --- | --- |",
    ]
    for item in body["skus"]:
        lines.append(
            f"| {item['id']} | {item['kind']} | ${_money(item['min'], item['max'])} | {item['term']} |"
        )
    lines += [
        "",
        f"Year-one catalog list if one controller buys all three: "
        f"{_money(body['year_one_if_all_three']['min'], body['year_one_if_all_three']['max'])}. "
        "Not booked.",
        "",
        "## If-then catalog list (not a forecast)",
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
        "## Highlights",
        "",
    ]
    for item in body["highlights"]:
        lines.append(f"- {item}")
    lines += ["", "## Refuse", ""]
    for item in body["refuse"]:
        lines.append(f"- {item}")
    lines += ["", body.get("note") or "", ""]
    return "\n".join(lines)


def investor_html() -> str:
    body = public_investor()
    sku_rows = "".join(
        "<tr>"
        f"<td><strong>{html.escape(item['id'])}</strong></td>"
        f"<td>{html.escape(item['kind'])}</td>"
        f"<td>{html.escape(_money(item['min'], item['max']))}</td>"
        f"<td>{html.escape(item['term'])}</td>"
        "</tr>"
        for item in body["skus"]
    )
    scenario_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['name'])}</td>"
        f"<td>{html.escape(row['if'])}</td>"
        f"<td>{html.escape(_money(row['min'], row['max']))}</td>"
        "</tr>"
        for row in body["scenarios"]
    )
    highlights = "".join(f"<li>{html.escape(item)}</li>" for item in body["highlights"])
    refuse = "".join(f"<li>{html.escape(item)}</li>" for item in body["refuse"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(body['legal'])} — Investor executive summary</title>
<style>
@page {{ size: letter; margin: 0.55in 0.6in 0.6in 0.6in; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font: 10.5pt/1.38 "Helvetica Neue", Helvetica, Arial, sans-serif; color: #16181d; background: #fff; }}
.band {{ background: #11141a; color: #f4efe6; padding: 16pt 18pt 14pt; margin: 0 0 14pt; }}
.band .mark {{ font: 700 9pt Helvetica, Arial, sans-serif; letter-spacing: 0.22em; color: #c4a574; }}
.band h1 {{ font: 700 20pt Helvetica, Arial, sans-serif; margin: 4pt 0 2pt; letter-spacing: -0.03em; }}
.band .sub {{ font: 8.5pt Helvetica, Arial, sans-serif; color: #d8d2c6; margin: 0; }}
.kpis {{ display: flex; gap: 8pt; margin: 0 0 14pt; }}
.kpi {{ flex: 1; border: 0.8pt solid #cfc6b6; background: #f7f3ea; padding: 8pt 9pt; }}
.kpi .label {{ font: 700 7.5pt Helvetica, Arial, sans-serif; letter-spacing: 0.08em; text-transform: uppercase; color: #6a6256; }}
.kpi .value {{ font: 700 13pt Helvetica, Arial, sans-serif; margin-top: 3pt; }}
h2 {{ font: 700 9pt Helvetica, Arial, sans-serif; letter-spacing: 0.08em; text-transform: uppercase; color: #11141a; border-bottom: 1.2pt solid #c4a574; padding-bottom: 3pt; margin: 12pt 0 6pt; }}
p {{ margin: 0 0 7pt; }}
.lede {{ font: 700 11.5pt/1.35 Helvetica, Arial, sans-serif; color: #11141a; }}
.eq {{ font: italic 10pt Georgia, Times, serif; color: #3d3428; margin: 0 0 10pt; }}
.split {{ display: flex; gap: 14pt; }}
.split > div {{ flex: 1; }}
table {{ width: 100%; border-collapse: collapse; margin: 4pt 0 10pt; font-size: 9pt; }}
th, td {{ border: 0.5pt solid #b9b1a4; padding: 5pt 6pt; vertical-align: top; text-align: left; }}
th {{ background: #11141a; color: #f4efe6; font-weight: 700; }}
ul {{ margin: 0 0 8pt 1.1em; padding: 0; }}
li {{ margin: 0 0 3pt; }}
.ask {{ border: 1.4pt solid #11141a; padding: 10pt 12pt; margin: 8pt 0 12pt; background: #fbf8f1; }}
.ask h2 {{ margin-top: 0; border: 0; padding: 0; }}
.status {{ font: 8pt Helvetica, Arial, sans-serif; color: #555; }}
footer {{ border-top: 0.7pt solid #b9b1a4; margin-top: 12pt; padding-top: 6pt; font: 8pt Helvetica, Arial, sans-serif; color: #666; }}
@media print {{ .kpis, .split, table, .ask {{ break-inside: avoid; }} }}
</style>
</head>
<body>
<div class="band">
  <div class="mark">{html.escape(body['legal'].upper())}</div>
  <h1>Investor executive summary</h1>
  <p class="sub">Confidential  ·  For {html.escape(body['invited'])}  ·  From {html.escape(body['owner'])}  ·  Release {html.escape(body['release'])}  ·  Not a priced round  ·  Not LIVE_PIN_OK</p>
</div>
<p class="lede">{html.escape(body['one_liner'])}</p>
<p class="eq">Close = {html.escape(body['commercial'])}. Insulation = {html.escape(body.get('insulation') or '')}. Packet = {html.escape(body.get('equation') or '')}.</p>
<div class="kpis">
  <div class="kpi"><div class="label">Recognized revenue</div><div class="value">$0</div></div>
  <div class="kpi"><div class="label">Named customers</div><div class="value">0</div></div>
  <div class="kpi"><div class="label">Signed L1</div><div class="value">0</div></div>
  <div class="kpi"><div class="label">Year-one if all three</div><div class="value">{html.escape(_money(body['year_one_if_all_three']['min'], body['year_one_if_all_three']['max']))}</div></div>
</div>
<div class="split">
  <div>
    <h2>Problem</h2>
    <p>{html.escape(body['problem'])}</p>
  </div>
  <div>
    <h2>Solution</h2>
    <p>{html.escape(body['solution'])}</p>
  </div>
</div>
<h2>Business model</h2>
<p>{html.escape(body['model'])} {html.escape(body['unit_economics_note'])}</p>
<table>
  <thead><tr><th>SKU</th><th>Role</th><th>Catalog list</th><th>Term</th></tr></thead>
  <tbody>{sku_rows}</tbody>
</table>
<h2>If-then catalog list — not a forecast</h2>
<table>
  <thead><tr><th>Scenario</th><th>If</th><th>List</th></tr></thead>
  <tbody>{scenario_rows}</tbody>
</table>
<h2>Insulation and traction</h2>
<p>{html.escape(body['insulation_copy'])}</p>
<p>{html.escape(body['traction'])}</p>
<div class="ask">
  <h2>The ask</h2>
  <p>{html.escape(body['ask'])}</p>
</div>
<h2>Highlights</h2>
<ul>{highlights}</ul>
<h2>This packet refuses</h2>
<ul>{refuse}</ul>
<p class="status">{html.escape(body.get('note') or '')} Invited: {html.escape(body['invited'])}. Recorded: no. Email: none stored. Equity: no.</p>
<footer>{html.escape(body['legal'])}  ·  Job C  ·  {html.escape(body['institute'])}  ·  Two pages  ·  Print on letter  ·  Do not treat as a raise, equity grant, signed L1, or LIVE_PIN_OK.</footer>
</body>
</html>
"""


def _money(lo: int, hi: int) -> str:
    return f"${lo:,}–${hi:,}"


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
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


def render_investor_pdf() -> bytes:
    """Two-page letter. Deterministic. No raise claimed."""
    body = public_investor()
    pages: list[list[str]] = [[], []]

    def fill(page: int, x: float, y: float, w: float, h: float, rgb: str) -> None:
        pages[page] += [f"{rgb} rg", f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re f"]

    def stroke(page: int, x1: float, y1: float, x2: float, y2: float, rgb: str, w: float = 0.8) -> None:
        pages[page] += [f"{rgb} RG", f"{w} w", f"{x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S"]

    def text(page: int, x: float, y: float, font: str, size: float, rgb: str, line: str) -> None:
        pages[page] += [
            "BT",
            f"{font} {size} Tf",
            rgb,
            f"1 0 0 1 {x:.1f} {y:.1f} Tm",
            f"({_escape(line)}) Tj",
            "ET",
        ]

    def block(page: int, x: float, y: float, font: str, size: float, rgb: str, lines: list[str], gap: float) -> float:
        for line in lines:
            text(page, x, y, font, size, rgb, line)
            y -= gap
        return y

    # Page 1 header
    fill(0, 0, 732, 612, 60, "0.067 0.078 0.102")
    fill(0, 0, 728, 612, 4, "0.769 0.647 0.455")
    text(0, LEFT, 768, "/F2", 8, "0.769 0.647 0.455 rg", body["legal"].upper())
    text(0, LEFT, 750, "/F2", 18, "1 1 1 rg", "Investor executive summary")
    text(
        0,
        LEFT,
        736,
        "/F3",
        8,
        "0.85 0.82 0.76 rg",
        f"Confidential  ·  For {body['invited']}  ·  From {body['owner']}  ·  Release {body['release']}",
    )

    y = 710
    y = block(0, LEFT, y, "/F2", 11, "0.067 0.078 0.102 rg", _wrap(body["one_liner"], 78), 14)
    y -= 4
    y = block(
        0,
        LEFT,
        y,
        "/F1",
        9,
        "0.35 0.30 0.24 rg",
        _wrap(
            f"Close = {body['commercial']}.  Insulation = {body.get('insulation')}.  Packet = {body.get('equation')}.",
            92,
        ),
        12,
    )
    y -= 8

    kpis = [
        ("RECOGNIZED REVENUE", "$0"),
        ("NAMED CUSTOMERS", "0"),
        ("SIGNED L1", "0"),
        ("YEAR-ONE IF ALL THREE", _money(body["year_one_if_all_three"]["min"], body["year_one_if_all_three"]["max"])),
    ]
    box_w = 124
    gap = 8
    for i, (label, value) in enumerate(kpis):
        x = LEFT + i * (box_w + gap)
        fill(0, x, y - 36, box_w, 42, "0.969 0.953 0.918")
        stroke(0, x, y - 36, x + box_w, y - 36, "0.769 0.647 0.455", 1.2)
        text(0, x + 8, y - 6, "/F2", 6.5, "0.42 0.38 0.34 rg", label)
        text(0, x + 8, y - 24, "/F2", 11, "0.067 0.078 0.102 rg", value)
    y -= 54

    text(0, LEFT, y, "/F2", 9, "0.067 0.078 0.102 rg", "PROBLEM")
    stroke(0, LEFT, y - 3, 292, y - 3, "0.769 0.647 0.455", 1.1)
    text(0, 316, y, "/F2", 9, "0.067 0.078 0.102 rg", "SOLUTION")
    stroke(0, 316, y - 3, RIGHT, y - 3, "0.769 0.647 0.455", 1.1)
    y -= 16
    left_y = block(0, LEFT, y, "/F1", 8.5, "0.14 0.14 0.14 rg", _wrap(body["problem"], 42), 11)
    right_y = block(0, 316, y, "/F1", 8.5, "0.14 0.14 0.14 rg", _wrap(body["solution"], 42), 11)
    y = min(left_y, right_y) - 10

    text(0, LEFT, y, "/F2", 9, "0.067 0.078 0.102 rg", "BUSINESS MODEL")
    stroke(0, LEFT, y - 3, RIGHT, y - 3, "0.769 0.647 0.455", 1.1)
    y -= 16
    y = block(
        0,
        LEFT,
        y,
        "/F1",
        9,
        "0.14 0.14 0.14 rg",
        _wrap(f"{body['model']} {body['unit_economics_note']}", 92),
        12,
    )
    y -= 8

    headers = ["SKU", "Role", "Catalog list", "Term"]
    col_x = [LEFT, 130, 220, 400]
    fill(0, LEFT, y - 14, RIGHT - LEFT, 18, "0.067 0.078 0.102")
    for i, head in enumerate(headers):
        text(0, col_x[i] + 4, y - 10, "/F2", 8, "1 1 1 rg", head)
    y -= 18
    for item in body["skus"]:
        fill(0, LEFT, y - 14, RIGHT - LEFT, 16, "0.98 0.97 0.95")
        stroke(0, LEFT, y - 14, RIGHT, y - 14, "0.78 0.74 0.68", 0.4)
        vals = [item["id"], item["kind"], _money(item["min"], item["max"]), item["term"]]
        for i, val in enumerate(vals):
            text(0, col_x[i] + 4, y - 10, "/F3", 8.5, "0.12 0.12 0.12 rg", val)
        y -= 16
    y -= 12

    text(0, LEFT, y, "/F2", 9, "0.067 0.078 0.102 rg", "WHO BUYS  ·  WHY NOW")
    stroke(0, LEFT, y - 3, RIGHT, y - 3, "0.769 0.647 0.455", 1.1)
    y -= 16
    y = block(0, LEFT, y, "/F1", 9, "0.14 0.14 0.14 rg", _wrap(body["icp"], 92), 12)
    y -= 4
    y = block(0, LEFT, y, "/F1", 9, "0.14 0.14 0.14 rg", _wrap(body["why_now"], 92), 12)

    text(0, LEFT, 28, "/F3", 7.5, "0.4 0.4 0.4 rg", f"{body['legal']}  ·  Page 1 of 2  ·  Not a priced round  ·  Not LIVE_PIN_OK")

    # Page 2
    fill(1, 0, 732, 612, 60, "0.067 0.078 0.102")
    fill(1, 0, 728, 612, 4, "0.769 0.647 0.455")
    text(1, LEFT, 768, "/F2", 8, "0.769 0.647 0.455 rg", body["legal"].upper())
    text(1, LEFT, 750, "/F2", 16, "1 1 1 rg", "Unit economics, insulation, ask")
    text(1, LEFT, 736, "/F3", 8, "0.85 0.82 0.76 rg", "Catalog list only. Zero booked. Two-human close.")

    y = 710
    text(1, LEFT, y, "/F2", 9, "0.067 0.078 0.102 rg", "IF-THEN CATALOG LIST — NOT A FORECAST")
    stroke(1, LEFT, y - 3, RIGHT, y - 3, "0.769 0.647 0.455", 1.1)
    y -= 18
    fill(1, LEFT, y - 14, RIGHT - LEFT, 18, "0.067 0.078 0.102")
    text(1, LEFT + 4, y - 10, "/F2", 8, "1 1 1 rg", "Scenario")
    text(1, 250, y - 10, "/F2", 8, "1 1 1 rg", "If")
    text(1, 470, y - 10, "/F2", 8, "1 1 1 rg", "List")
    y -= 18
    for row in body["scenarios"]:
        fill(1, LEFT, y - 22, RIGHT - LEFT, 24, "0.98 0.97 0.95")
        text(1, LEFT + 4, y - 8, "/F2", 8, "0.12 0.12 0.12 rg", row["name"][:34])
        text(1, 250, y - 8, "/F3", 7.5, "0.2 0.2 0.2 rg", row["if"][:48])
        text(1, 470, y - 8, "/F2", 8, "0.12 0.12 0.12 rg", _money(row["min"], row["max"]))
        text(1, 250, y - 18, "/F3", 7.5, "0.35 0.35 0.35 rg", (row["if"][48:96] if len(row["if"]) > 48 else ""))
        y -= 26
    y -= 8

    text(1, LEFT, y, "/F2", 9, "0.067 0.078 0.102 rg", "INSULATION")
    stroke(1, LEFT, y - 3, RIGHT, y - 3, "0.769 0.647 0.455", 1.1)
    y -= 16
    y = block(1, LEFT, y, "/F1", 9, "0.14 0.14 0.14 rg", _wrap(body["insulation_copy"], 92), 12)
    y -= 8

    text(1, LEFT, y, "/F2", 9, "0.067 0.078 0.102 rg", "TRACTION — HONEST")
    stroke(1, LEFT, y - 3, RIGHT, y - 3, "0.769 0.647 0.455", 1.1)
    y -= 16
    y = block(1, LEFT, y, "/F1", 9, "0.14 0.14 0.14 rg", _wrap(body["traction"], 92), 12)
    y -= 10

    fill(1, LEFT, y - 62, RIGHT - LEFT, 68, "0.969 0.953 0.918")
    stroke(1, LEFT, y - 62, LEFT, y + 6, "0.111 0.129 0.165", 2.4)
    text(1, LEFT + 12, y - 8, "/F2", 9, "0.067 0.078 0.102 rg", "THE ASK")
    y = block(1, LEFT + 12, y - 22, "/F1", 9, "0.14 0.14 0.14 rg", _wrap(body["ask"], 86), 12)
    y -= 18

    text(1, LEFT, y, "/F2", 9, "0.067 0.078 0.102 rg", "HIGHLIGHTS")
    stroke(1, LEFT, y - 3, RIGHT, y - 3, "0.769 0.647 0.455", 1.1)
    y -= 16
    for item in body["highlights"]:
        y = block(1, LEFT, y, "/F1", 9, "0.14 0.14 0.14 rg", _wrap(f"— {item}", 92), 12)
        y -= 2
    y -= 8

    text(1, LEFT, y, "/F2", 9, "0.067 0.078 0.102 rg", "THIS PACKET REFUSES")
    stroke(1, LEFT, y - 3, RIGHT, y - 3, "0.769 0.647 0.455", 1.1)
    y -= 16
    y = block(1, LEFT, y, "/F1", 9, "0.14 0.14 0.14 rg", _wrap("  ·  ".join(body["refuse"]), 92), 12)
    y -= 10
    y = block(1, LEFT, y, "/F3", 8, "0.35 0.35 0.35 rg", _wrap(body.get("note") or "", 92), 11)
    text(
        1,
        LEFT,
        28,
        "/F3",
        7.5,
        "0.4 0.4 0.4 rg",
        f"{body['legal']}  ·  Page 2 of 2  ·  Invited, not recorded  ·  Equity: no  ·  Print on letter",
    )

    return _assemble(pages)


def _assemble(page_streams: list[list[str]]) -> bytes:
    decorated = ["\n".join(stream) for stream in page_streams]
    objects: list[bytes] = [b""]
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + i} 0 R" for i in range(len(decorated)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(decorated)} >>".encode())
    font_times = 3 + len(decorated)
    font_helv_b = font_times + 1
    font_helv = font_helv_b + 1
    for index, stream in enumerate(decorated):
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
    for number, body in enumerate(objects[1:], start=1):
        offsets.append(len(out))
        out.extend(f"{number} 0 obj\n".encode())
        out.extend(body)
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
