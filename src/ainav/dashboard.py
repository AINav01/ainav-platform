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


def spec() -> dict[str, Any]:
    return dict(load_catalog()["plane_interface"])


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
        {"id": "plane_state", "label": "Plane state", "value": "OPEN", "note": "Not frozen. Fail-closed if thrown. Not LIVE_PIN_OK."},
        {"id": "pending_admits", "label": "Pending dual admits", "value": "0", "note": "No named treasury pair has a live bind."},
        {"id": "first_record", "label": "First record (SoR)", "value": "1 sandbox / 0 production", "note": "AINAV-L1 lab oids. Not two named humans."},
        {"id": "second_record", "label": "Second record", "value": "0", "note": "P-ADM keep not attached. Not live Purview."},
        {"id": "off_switch", "label": "Off switch", "value": "READY", "note": "Fail-closed freeze. Does not power down Copilot."},
        {"id": "last_keep", "label": "Last sealed keep", "value": "none", "note": "Weekly DecisionRecord export after kit PASS."},
        {"id": "recognized_revenue", "label": "Recognized revenue", "value": f"${int(fin['recognized_revenue']):,}", "note": "Not booked. No billing provider."},
        {"id": "named_customers", "label": "Named customers", "value": str(fin["named_customers"]), "note": "Do not invent a buyer."},
        {"id": "signed_l1", "label": "Signed L1", "value": str(fin["signed_l1"]), "note": "Counsel pack G13 stays open."},
        {
            "id": "year_one_if_all_three",
            "label": "Year-one if all three",
            "value": f"${all_three['min']:,}–${all_three['max']:,}",
            "note": "Catalog list. Not a forecast.",
        },
        {
            "id": "seats_recorded",
            "label": "Seats recorded",
            "value": "0 recorded / 1 invited",
            "note": f"{invited['name']} invited, not recorded. Email none.",
        },
        {
            "id": "compliance_maps",
            "label": "AI compliance maps",
            "value": f"{len(maps)} instruments / claimed=false",
            "note": "NIST, SOX, EU AI Act, ISO 42001. Not certified.",
        },
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
    tiles = "".join(
        (
            "<article>"
            f"<h3>{html.escape(item['label'])}</h3>"
            f"<p class=\"price\">{html.escape(item['value'])}</p>"
            f"<p class=\"note\">{html.escape(item['note'])}</p>"
            "</article>"
        )
        for item in body["tiles"]
    )
    levels = "".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(str(cell))}</td>"
            for cell in (
                item["name"],
                item["role"],
                str(item["admit"]),
                str(item["freeze"]),
                str(item["keep"]),
                item.get("note") or "",
            )
        )
        + "</tr>"
        for item in body["levels"]
    )
    depts = "".join(
        "<tr>"
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
        f"<li>{html.escape(item['name'])} — {html.escape(item.get('maps_to') or '')} "
        f"claimed={str(item.get('claimed')).lower()}</li>"
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
<title>{html.escape(body['legal'])} — Executive control-plane dashboard</title>
<style>
@page {{ size: letter; margin: 0.55in 0.6in; }}
body {{ font: 10.5pt/1.4 Georgia, Times, serif; color: #16181d; margin: 0; background: #fff; }}
.band {{ background: #11141a; color: #f4efe6; padding: 16pt 18pt; margin: 0 0 14pt; }}
.band .mark {{ font: 700 8.5pt Helvetica, Arial, sans-serif; letter-spacing: 0.22em; color: #c4a574; }}
.band h1 {{ font: 700 20pt Helvetica, Arial, sans-serif; margin: 4pt 0 2pt; }}
.band .sub {{ font: 8.5pt Helvetica, Arial, sans-serif; color: #d8d2c6; }}
h2 {{ font: 700 9pt Helvetica, Arial, sans-serif; letter-spacing: 0.08em; text-transform: uppercase; border-bottom: 1.2pt solid #c4a574; padding-bottom: 3pt; }}
.cards {{ display: flex; flex-wrap: wrap; gap: 8pt; margin: 0 0 12pt; }}
.cards article {{ flex: 1 1 140pt; border: 0.8pt solid #cfc6b6; background: #f7f3ea; padding: 8pt; }}
.cards h3 {{ font: 700 7.5pt Helvetica, Arial, sans-serif; letter-spacing: 0.08em; text-transform: uppercase; margin: 0; color: #6a6256; }}
.price {{ font: 700 12pt Helvetica, Arial, sans-serif; margin: 4pt 0; }}
.note {{ font: 8pt Helvetica, Arial, sans-serif; color: #555; margin: 0; }}
table {{ width: 100%; border-collapse: collapse; font: 8.2pt Helvetica, Arial, sans-serif; margin: 0 0 12pt; }}
th, td {{ border: 0.5pt solid #b9b1a4; padding: 4pt; text-align: left; vertical-align: top; }}
th {{ background: #11141a; color: #f4efe6; }}
ul {{ margin: 0 0 10pt 1.1em; }}
footer {{ border-top: 0.7pt solid #b9b1a4; padding-top: 6pt; font: 8pt Helvetica, Arial, sans-serif; color: #666; }}
</style>
</head>
<body>
<div class="band">
  <div class="mark">{html.escape(body['legal'].upper())}</div>
  <h1>Executive control-plane dashboard</h1>
  <p class="sub">Release {html.escape(body['release'])}  ·  Humans from the top  ·  Same Entra plane remote  ·  Compliance maps claimed=false  ·  Not a SKU  ·  Not LIVE_PIN_OK</p>
</div>
<p>{html.escape(body['thesis'])}</p>
<p class="note">Equation: {html.escape(body.get('equation') or '')}.</p>
<h2>How humans sit from the top</h2>
{paras}
<h2>Real-time tiles — admit ledger, not invented P&amp;L</h2>
<p class="note">{html.escape(body['dashboard'].get('realtime_means') or '')}</p>
<div class="cards">{tiles}</div>
<h2>Hierarchical access</h2>
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
<h2>Internal and remote</h2>
<p>Internal: {html.escape(access['internal'])}</p>
<p>Remote: {html.escape(access['remote'])}</p>
<p>Same plane: {html.escape(str(access['same_plane']).lower())}. Second remote plane: false. VPN SKU: false. PIM is not dual. Teams is not a seat.</p>
<h2>AI compliance maps</h2>
<ul>{maps}</ul>
<h2>Refuse</h2>
<ul>{refuse}</ul>
<footer>{html.escape(body['legal'])}  ·  {html.escape(body['institute'])}  ·  Invited: {html.escape(body['invited'])} recorded: no  ·  Do not treat as signed L1, a certificate, or LIVE_PIN_OK.</footer>
</body>
</html>
"""


def write_dashboard() -> Path:
    MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    MD_PATH.write_text(dashboard_markdown(), encoding="utf-8")
    HTML_PATH.write_text(dashboard_html(), encoding="utf-8")
    return HTML_PATH
