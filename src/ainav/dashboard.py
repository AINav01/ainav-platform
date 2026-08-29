"""Ultimate control-plane interface. Humans from the top. Honest tiles.

Not a SKU. Not live Production metrics. Not a certificate.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from ainav.catalog import load_catalog
from ainav.client_org import public_client_org
from ainav.finance import model as finance_model
from ainav.governance import public_governance

MD_PATH = Path("docs/CONTROL_PLANE.md")
HTML_PATH = Path("docs/CONTROL_PLANE_DASHBOARD.html")

TILE_TONES = {
    "plane_state": "ready",
    "pending_admits": "hold",
    "first_record": "lab",
    "second_record": "hold",
    "off_switch": "ready",
    "last_keep": "hold",
    "recognized_revenue": "hold",
    "named_customers": "hold",
    "signed_l1": "hold",
    "year_one_if_all_three": "list",
    "seats_recorded": "hold",
    "compliance_maps": "map",
}

ROLE_ORDER = ("oversee", "keep", "admit", "draft", "host", "counsel", "same_plane", "not_a_seat")
ROLE_LABELS = {
    "oversee": "Oversee",
    "keep": "Keep",
    "admit": "Admit",
    "draft": "Draft",
    "host": "Host",
    "counsel": "Counsel",
    "same_plane": "Same plane",
    "not_a_seat": "Not a seat",
}


def spec() -> dict[str, Any]:
    return dict(load_catalog()["plane_interface"])


def _tile(ident: str, label: str, value: str, note: str) -> dict[str, str]:
    return {"id": ident, "label": label, "value": value, "note": note, "tone": TILE_TONES[ident]}


def _flag(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


def seating_cascade(levels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = {}
    for item in levels:
        grouped.setdefault(str(item.get("role") or "other"), []).append(str(item.get("name") or ""))
    rows = []
    for role in ROLE_ORDER:
        names = [name for name in grouped.get(role, []) if name]
        if not names:
            continue
        rows.append({"role": role, "label": ROLE_LABELS.get(role, role), "names": names})
    return rows


def public_dashboard() -> dict[str, Any]:
    cat = load_catalog()
    body = spec()
    fin = finance_model()
    gov = public_governance()
    org = public_client_org()
    invited = cat["organization"]["contacts"]["invited"]
    by_id = {row["id"]: row for row in fin["scenarios"]}
    all_three = by_id["all_three"]
    maps = [dict(item) for item in gov["maps"]]
    tiles = [
        _tile("plane_state", "Plane state", "OPEN", "Not frozen. Fail-closed if thrown. Not LIVE_PIN_OK."),
        _tile("pending_admits", "Pending dual admits", "0", "No named treasury pair has a live bind."),
        _tile("first_record", "First record (SoR)", "1 sandbox / 0 production", "AINAV-L1 lab oids. Not two named humans."),
        _tile("second_record", "Second record", "0", "P-ADM keep not attached. Not live Purview."),
        _tile("off_switch", "Off switch", "READY", "Fail-closed freeze. Does not power down Copilot."),
        _tile("last_keep", "Last sealed keep", "none", "Weekly DecisionRecord export after kit PASS."),
        _tile("recognized_revenue", "Recognized revenue", f"${int(fin['recognized_revenue']):,}", "Not booked. No billing provider."),
        _tile("named_customers", "Named customers", str(fin["named_customers"]), "Do not invent a buyer."),
        _tile("signed_l1", "Signed L1", str(fin["signed_l1"]), "Counsel pack G13 stays open."),
        _tile("year_one_if_all_three", "Year-one if all three", f"${all_three['min']:,}–${all_three['max']:,}", "Catalog list. Not a forecast."),
        _tile("seats_recorded", "Seats recorded", "0 recorded / 1 invited", f"{invited['name']} invited, not recorded. Email none."),
        _tile("compliance_maps", "AI compliance maps", f"{len(maps)} instruments / claimed=false", "NIST, SOX, EU AI Act, ISO 42001. Not certified."),
    ]
    return {
        "kind": body["kind"],
        "sku": False,
        "live": False,
        "live_pin_ok": False,
        "certified": False,
        "real_time_claimed": False,
        "forecast": False,
        "release": cat["entity"]["release"],
        "legal": cat["entity"]["legal"],
        "product": cat["entity"]["product"],
        "institute": cat["entity"]["institute"],
        "thesis": body["thesis"],
        "letter": body["letter"],
        "equation": cat["equations"].get("interface"),
        "plane_equation": cat["equations"].get("plane"),
        "org_equation": cat["equations"].get("org"),
        "levels": [dict(item) for item in body["levels"]],
        "cascade": seating_cascade(list(body["levels"])),
        "access": dict(body["access"]),
        "dashboard": dict(body["dashboard"]),
        "tiles": tiles,
        "maps": maps,
        "departments": [dict(item) for item in org["departments"]],
        "seats": dict(org["seats"]),
        "invited": invited["name"],
        "recorded": False,
        "refuse": list(body.get("refuse") or []),
        "note": body.get("note"),
    }


def dashboard_markdown() -> str:
    body = public_dashboard()
    lines = [
        f"# {body['legal']} — ultimate control plane interface",
        "",
        f"Release {body['release']}. Not a SKU. Not LIVE_PIN_OK. Not a certificate.",
        "",
        f"**{body['thesis']}**",
        "",
        f"Equation: {body.get('equation')}.",
        f"Plane: {body.get('plane_equation')}.",
        f"Org: {body.get('org_equation')}.",
        "",
        "## Seating cascade — from the top",
        "",
    ]
    for item in body["cascade"]:
        lines.append(f"- **{item['label']}** — {', '.join(item['names'])}")
    lines += [
        "",
        "## How humans sit from the top",
        "",
        body["letter"],
        "",
        "## Hierarchy",
        "",
        "| Level | Role | Admit | Freeze | Keep | Note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in body["levels"]:
        lines.append(
            f"| {item['name']} | {item['role']} | {item['admit']} | {item['freeze']} | "
            f"{item['keep']} | {item.get('note') or ''} |"
        )
    lines += [
        "",
        "## Throughout the client organization",
        "",
        "| Department | Role | Seat | AI | Note |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in body["departments"]:
        lines.append(
            f"| {item['name']} | {item['role']} | {item.get('seat') or '—'} | "
            f"{item.get('ai') or 'Not a seat.'} | {item.get('note') or ''} |"
        )
    access = body["access"]
    lines += [
        "",
        "## Internal and remote access",
        "",
        f"- Internal: {access['internal']}",
        f"- Remote: {access['remote']}",
        f"- Same plane: {str(access['same_plane']).lower()}. Second remote plane: "
        f"{str(access['second_remote_plane']).lower()}. VPN SKU: {str(access['vpn_sku']).lower()}.",
        f"- Entra required: {str(access['entra_required']).lower()}. PIM is not dual. Teams is not a seat.",
        "",
        "## Executive dashboard — honest tiles",
        "",
        f"{body['dashboard'].get('realtime_means')}",
        "",
        "| Tile | Value | Note |",
        "| --- | --- | --- |",
    ]
    for item in body["tiles"]:
        lines.append(f"| {item['label']} | {item['value']} | {item['note']} |")
    lines += [
        "",
        "## AI compliance maps (claimed = false)",
        "",
    ]
    for item in body["maps"]:
        lines.append(
            f"- **{item['name']}** — {item.get('maps_to')} Claimed: {str(item.get('claimed')).lower()}."
        )
    lines += ["", "## Refuse", ""]
    for item in body["refuse"]:
        lines.append(f"- {item}")
    lines += ["", body.get("note") or "", ""]
    return "\n".join(lines)


def dashboard_html() -> str:
    body = public_dashboard()
    by_id = {item["id"]: item for item in body["tiles"]}
    strip_ids = (
        "plane_state",
        "pending_admits",
        "off_switch",
        "recognized_revenue",
        "signed_l1",
        "seats_recorded",
    )
    strip = "".join(
        f"<span>{html.escape(by_id[ident]['label'])} <b>{html.escape(by_id[ident]['value'])}</b></span>"
        for ident in strip_ids
        if ident in by_id
    )
    tiles = "".join(
        (
            f"<article data-tone=\"{html.escape(item.get('tone') or 'hold')}\">"
            f"<h3>{html.escape(item['label'])}</h3>"
            f"<p class=\"price\">{html.escape(item['value'])}</p>"
            f"<p class=\"note\">{html.escape(item['note'])}</p>"
            "</article>"
        )
        for item in body["tiles"]
    )
    cascade = "".join(
        (
            f"<article data-role=\"{html.escape(item['role'])}\">"
            f"<h3>{html.escape(item['label'])}</h3>"
            f"<p>{html.escape(' · '.join(item['names']))}</p>"
            "</article>"
        )
        for item in body["cascade"]
    )
    levels = "".join(
        f"<tr data-role=\"{html.escape(str(item['role']))}\">"
        + "".join(
            f"<td>{html.escape(str(cell))}</td>"
            for cell in (
                item["name"],
                item["role"],
                _flag(item["admit"]),
                _flag(item["freeze"]),
                _flag(item["keep"]),
                item.get("note") or "",
            )
        )
        + "</tr>"
        for item in body["levels"]
    )
    depts = "".join(
        f"<tr data-role=\"{html.escape(str(item['role']))}\">"
        + "".join(
            f"<td>{html.escape(str(cell))}</td>"
            for cell in (
                item["name"],
                item["role"],
                item.get("seat") or "—",
                item.get("ai") or "Not a seat.",
                item.get("note") or "",
            )
        )
        + "</tr>"
        for item in body["departments"]
    )
    maps = "".join(
        "<tr>"
        f"<td>{html.escape(item['name'])}</td>"
        f"<td>{html.escape(item.get('maps_to') or '')}</td>"
        f"<td>{html.escape(item.get('scope') or '')}</td>"
        f"<td>claimed={html.escape(str(item.get('claimed')).lower())}</td>"
        "</tr>"
        for item in body["maps"]
    )
    refuse = "".join(f"<li>{html.escape(item)}</li>" for item in body["refuse"])
    access = body["access"]
    paras = "".join(
        f"<p>{html.escape(chunk.strip())}</p>"
        for chunk in body["letter"].split("\n\n")
        if chunk.strip()
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(body['legal'])} — Executive control-plane dashboard</title>
<style>
:root {{
  --ink: #0c0b09; --paper: #f4efe6; --mute: #6b6458; --gold: #8d7034; --gold-2: #c4a056;
  --void: #0c0b09; --ok: #3d5a3a; --hold: #8a5a2f; --rule: rgba(12,11,9,0.12);
}}
@page {{ size: letter; margin: 0.42in 0.48in; }}
html, body {{ margin: 0; background: var(--paper); color: var(--ink);
  font: 10.5pt/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
.band {{ background: var(--void); color: #f4efe6; padding: 16pt 18pt 12pt; }}
.band .mark {{ font: 700 8pt Helvetica, Arial, sans-serif; letter-spacing: 0.22em; color: var(--gold-2); }}
.band h1 {{ font: 560 22pt "Iowan Old Style", Georgia, serif; margin: 4pt 0 3pt; letter-spacing: -0.02em; }}
.band .sub {{ font: 8pt Helvetica, Arial, sans-serif; color: #d8d2c6; margin: 0; }}
.strip {{ display: flex; flex-wrap: wrap; gap: 8pt 16pt; background: #16140f; color: #f4efe6;
  padding: 8pt 18pt; font: 7.5pt/1.35 ui-monospace, Menlo, monospace; letter-spacing: 0.02em; }}
.strip b {{ color: var(--gold-2); font-size: 10pt; }}
.wrap {{ padding: 12pt 18pt 16pt; }}
h2 {{ font: 700 8pt Helvetica, Arial, sans-serif; letter-spacing: 0.1em; text-transform: uppercase;
  border-bottom: 1.1pt solid var(--gold); padding-bottom: 3pt; margin: 14pt 0 8pt; }}
.thesis {{ max-width: 46rem; }}
.equation {{ font: italic 12pt "Iowan Old Style", Georgia, serif; color: var(--gold); margin: 0 0 10pt; }}
.cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 7pt; margin: 0 0 8pt; }}
.cards article {{ border: 0.8pt solid var(--rule); background: #fff; padding: 8pt 9pt 9pt; min-height: 64pt; }}
.cards h3 {{ font: 700 7pt Helvetica, Arial, sans-serif; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--mute); margin: 0; }}
.price {{ font: 560 13pt "Iowan Old Style", Georgia, serif; margin: 4pt 0 3pt; }}
[data-tone="ready"] .price, [data-tone="lab"] .price {{ color: var(--ok); }}
[data-tone="hold"] .price, [data-tone="list"] .price, [data-tone="map"] .price {{ color: var(--hold); }}
.note {{ font: 7.8pt Helvetica, Arial, sans-serif; color: var(--mute); margin: 0; }}
.cascade {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6pt; margin: 0 0 10pt; }}
.cascade article {{ border: 0.8pt solid var(--rule); background: #fff; padding: 7pt 8pt; }}
.cascade h3 {{ font: 700 7pt Helvetica, Arial, sans-serif; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--gold); margin: 0 0 3pt; }}
.cascade article[data-role="admit"] {{ background: var(--void); color: #f4efe6; }}
.cascade article[data-role="admit"] h3 {{ color: var(--gold-2); }}
.cascade article[data-role="not_a_seat"] {{ color: var(--mute); }}
table {{ width: 100%; border-collapse: collapse; font: 7.8pt Helvetica, Arial, sans-serif; margin: 0 0 10pt; }}
th, td {{ border-bottom: 0.5pt solid #d4cdc0; padding: 4pt 5pt; text-align: left; vertical-align: top; }}
th {{ background: var(--void); color: #f4efe6; letter-spacing: 0.04em; text-transform: uppercase; font-size: 7pt; }}
tr[data-role="admit"] {{ background: #e7eee4; }}
tr[data-role="oversee"] {{ box-shadow: inset 3pt 0 0 var(--gold); }}
tr[data-role="not_a_seat"] {{ color: var(--mute); }}
.split {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; margin: 0 0 10pt; }}
.panel {{ border: 0.8pt solid var(--rule); background: #fff; padding: 8pt 10pt; }}
.panel h3 {{ font: 700 8pt Helvetica, Arial, sans-serif; letter-spacing: 0.06em; text-transform: uppercase; margin: 0 0 4pt; }}
ul {{ margin: 0 0 8pt 1.1em; }}
footer {{ border-top: 0.7pt solid #cfc6b6; padding: 8pt 18pt 12pt; font: 8pt Helvetica, Arial, sans-serif; color: var(--mute); }}
@media screen and (max-width: 820px) {{
  .cards {{ grid-template-columns: repeat(2, 1fr); }}
  .cascade, .split {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<div class="band">
  <div class="mark">{html.escape(body['legal'].upper())}</div>
  <h1>Executive control-plane dashboard</h1>
  <p class="sub">Release {html.escape(body['release'])}  ·  Humans from the top  ·  Same Entra plane remote  ·  Compliance maps claimed=false  ·  Not a SKU  ·  Not LIVE_PIN_OK</p>
</div>
<div class="strip">{strip}</div>
<div class="wrap">
<p class="thesis">{html.escape(body['thesis'])}</p>
<p class="equation">Interface = {html.escape(body.get('equation') or '')}</p>
<h2>Real-time tiles — admit ledger, not invented P&amp;L</h2>
<p class="note">{html.escape(body['dashboard'].get('realtime_means') or '')}</p>
<div class="cards">{tiles}</div>
<h2>Seating cascade — from the top</h2>
<div class="cascade">{cascade}</div>
<h2>How humans sit from the top</h2>
{paras}
<h2>Hierarchical access and control</h2>
<table>
<thead><tr><th>Level</th><th>Role</th><th>Admit</th><th>Freeze</th><th>Keep</th><th>Note</th></tr></thead>
<tbody>{levels}</tbody>
</table>
<h2>Throughout the client organization</h2>
<p class="note">Existing SOD. Not invented department heads. Department AI is not a seat.</p>
<table>
<thead><tr><th>Department</th><th>Role</th><th>Seat</th><th>AI</th><th>Note</th></tr></thead>
<tbody>{depts}</tbody>
</table>
<h2>Internal and remote access</h2>
<div class="split">
  <div class="panel">
    <h3>Internal</h3>
    <p>{html.escape(access['internal'])}</p>
  </div>
  <div class="panel">
    <h3>Remote</h3>
    <p>{html.escape(access['remote'])}</p>
  </div>
</div>
<p class="note">Same plane: yes. Second remote plane: no. VPN SKU: no. PIM is not dual. Teams is not a seat.</p>
<h2>AI compliance maps</h2>
<table>
<thead><tr><th>Instrument</th><th>Maps to</th><th>Scope</th><th>Claimed</th></tr></thead>
<tbody>{maps}</tbody>
</table>
<h2>Refuse</h2>
<ul>{refuse}</ul>
</div>
<footer>{html.escape(body['legal'])}  ·  {html.escape(body['institute'])}  ·  Invited: {html.escape(body['invited'])} recorded: no  ·  Do not treat as signed L1, a certificate, or LIVE_PIN_OK.</footer>
</body>
</html>
"""


def write_dashboard() -> Path:
    MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    MD_PATH.write_text(dashboard_markdown(), encoding="utf-8")
    HTML_PATH.write_text(dashboard_html(), encoding="utf-8")
    return HTML_PATH
