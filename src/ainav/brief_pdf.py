"""Printable executive brief for the invited second human. Not a recorded officer."""

from __future__ import annotations

import html
from pathlib import Path

from ainav.catalog import load_catalog

BRIEF_PATH = Path("docs/CYNTHIA_HODNETT_BRIEF.pdf")
HTML_PATH = Path("docs/CYNTHIA_HODNETT_BRIEF.html")
MD_PATH = Path("docs/CYNTHIA_HODNETT_BRIEF.md")
PAGE_W = 612
PAGE_H = 792
LEFT = 54
RIGHT = 558
TOP = 720
LEADING = 13
TITLE_SIZE = 16
BODY_SIZE = 10


def _ctx() -> dict[str, str]:
    cat = load_catalog()
    invited = cat["organization"]["contacts"]["invited"]
    return {
        "release": cat["entity"]["release"],
        "legal": cat["entity"]["legal"],
        "product": cat["entity"]["product"],
        "institute": cat["entity"]["institute"],
        "owner": cat["operating"]["owner_principal"],
        "operator": cat["operating"]["operator"],
        "invited": invited["name"],
        "seat_role": invited["seat_role"],
        "inception_role": invited["inception_role"],
        "commercial": cat["equations"]["commercial"],
        "product_eq": cat["equations"]["product"],
        "lab_pin": cat["equations"]["lab_pin"],
    }


def brief_sections() -> list[tuple[str, str]]:
    """Return (heading, body) pairs. Empty heading is the kicker."""
    c = _ctx()
    return [
        (
            "",
            f"Confidential briefing for {c['invited']}  ·  From {c['owner']}, sole owner of {c['legal']}  ·  "
            f"Release {c['release']}  ·  Printable. Not a contract. Not signed L1. Not {c['lab_pin']}.",
        ),
        (
            "The ask, in one sentence",
            f"{c['owner']} is building a company that will not let a privileged money-movement "
            "write land unless two distinct humans admit it. He can write the software. He cannot "
            f"be both humans. We are asking {c['invited']} to be the second human — seat B — "
            "with her own business email and her own click. Not stock. Not Global Admin. Not this Cloud Agent.",
        ),
        (
            "What we are building together",
            f"{c['legal']} is a Delaware C corporation. The product is the {c['product']}. "
            f"{c['institute']} is the public law of that plane. Microsoft hosts, identifies, "
            "notifies, and receives the write after two humans admit it. Microsoft is not the product. "
            "Teams is not a seat. Copilot is not the admit plane. A Cloud Agent can operate the host; "
            "it cannot be seat A or seat B.",
        ),
        (
            "",
            "The job is Job C: dual-admitted effect authority before a Dynamics 365 Business Central "
            "general-journal post that two humans did not admit. Two distinct people bind the same "
            "action hash. That grant is consumed once. The effect gate is fail-closed. If either "
            "human is missing, the write does not land.",
        ),
        (
            "",
            "We sell three things only. L1 proves the gate in two to four weeks ($28,000–$40,000). "
            "P-ADM keeps the same plane covered after kit PASS ($40,000–$60,000 / year). "
            "U-DUAL deepens the same plane onto Sales ($20,000–$35,000 / year) and is never free. "
            "Packs, hours, and Microsoft licenses are not products. A controller buys the commercial "
            f"close: {c['commercial']}. The lab pin {c['lab_pin']} is a separate engineering fact "
            "and is never marked from a sale.",
        ),
        (
            "Why we need you",
            f"{c['owner']} is the sole owner and one human principal. Job C cannot close with one "
            "human. NVIDIA Inception also wants two unique contacts with business emails — a developer "
            "and a business executive. Sole owner does not collapse that. You are the invited second "
            "human. You are not recorded as an officer. You are not a stockholder. No email is stored "
            "until you agree and James says record it.",
        ),
        (
            "",
            "Without a second distinct person who actually clicks, AINav can keep a lab. It cannot "
            "sign L1, apply to Inception, or tell a controller that two humans admitted the journal. "
            "That is why this brief exists, and why your yes or no matters before anything else.",
        ),
        (
            "Your role if you agree",
            f"Seat B — {c['seat_role']}. James is seat A — treasury_approver. "
            f"Inception — {c['inception_role']}. James is the developer / programmer. "
            "You receive your own @ainav.institute mailbox and your own Entra identity. "
            "Not an alias. Not Gmail. Not his login. When a privileged write is proposed, you "
            "review the action hash and admit or refuse. If he clicks both seats, it is not dual. "
            "If you rubber-stamp without reading, it is not dual.",
        ),
        (
            "",
            "You do not need Global Admin. You do not need equity in the C corp to do this job. "
            "You do not become Copilot, Teams, or this Cloud Agent. Available tools are not seats. "
            "A chat is not a seat. A PIM activation is not dual admit. Counsel decides stock later. "
            "This brief does not issue shares.",
        ),
        (
            "What you are not being asked",
            "You are not being asked to buy a customer. You are not being asked to mark LIVE_PIN_OK. "
            "You are not being asked to launch ainav.institute. You are not being asked to enable "
            "Business Central Production. You are not being asked to sign a counsel pack today. "
            "Those remain owner gates and stay open until James authorizes them in his own words.",
        ),
        (
            "How the three names fit",
            f"{c['legal']} is the company. {c['product']} is the product. {c['institute']} is the "
            "public face. Master mothership issues the lockfile and never writes a client system of "
            "record. Cloud and local motherships share one consume ledger. Azure, Microsoft 365 E7, "
            "Business Central Premium, Sales Enterprise, and Teams Premium are the fabric. They "
            "receive the write after you and James admit it.",
        ),
        (
            "What happens next",
            "1. You decide.  2. If yes, James creates your mailbox and you sign in once.  "
            "3. He sends this agent your business email and says record it.  "
            "4. Proof day uses two named humans on the twin — still not Production.  "
            "5. Equity, officer titles, and Delaware filings stay with counsel.",
        ),
        (
            "",
            f"Invited: {c['invited']}  ·  Recorded: no  ·  Email: none stored  ·  Equity: no  ·  "
            f"Operator: {c['operator']} (not a seat)  ·  Second officer: none",
        ),
    ]


def brief_lines() -> list[tuple[str, str]]:
    """(style, text) rows used by the fallback PDF renderer."""
    c = _ctx()
    rows: list[tuple[str, str]] = [
        ("title", f"{c['legal']}  —  Executive brief"),
        ("body", f"Release {c['release']}  ·  For {c['invited']}  ·  From {c['owner']}"),
        ("body", "Printable. Catalog-honest. Not a contract. Not signed L1. Not LIVE_PIN_OK."),
        ("rule", ""),
    ]
    for heading, body in brief_sections():
        if heading:
            rows.append(("head", heading))
        rows.append(("body", body))
    rows.append(("rule", ""))
    return rows


def brief_markdown() -> str:
    c = _ctx()
    lines = [
        f"# {c['legal']} — Executive brief for {c['invited']}",
        "",
        f"Release {c['release']}. From {c['owner']}. Printable companion: "
        "`docs/CYNTHIA_HODNETT_BRIEF.pdf`. Not a contract. Not signed L1. Not LIVE_PIN_OK.",
        "",
    ]
    for heading, body in brief_sections():
        if heading:
            lines += [f"## {heading}", "", body, ""]
        else:
            lines += [body, ""]
    return "\n".join(lines).rstrip() + "\n"


def brief_html() -> str:
    c = _ctx()
    blocks: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{html.escape(c['legal'])} — Executive brief for {html.escape(c['invited'])}</title>",
        "<style>",
        "@page { size: letter; margin: 0.7in 0.75in 0.75in 0.75in; }",
        "html, body { margin: 0; padding: 0; }",
        "body { font: 11pt/1.45 'Times New Roman', Times, serif; color: #1a1a1a; }",
        "header { border-bottom: 2.5pt solid #111; padding-bottom: 10pt; margin-bottom: 14pt; }",
        ".mark { font: 700 13pt Helvetica, Arial, sans-serif; letter-spacing: 0.12em; }",
        ".kicker { font: 9pt Helvetica, Arial, sans-serif; color: #444; margin-top: 4pt; }",
        "h1 { font: 700 20pt Helvetica, Arial, sans-serif; margin: 0 0 4pt; letter-spacing: -0.02em; }",
        "h2 { font: 700 11pt Helvetica, Arial, sans-serif; margin: 13pt 0 4pt; text-transform: uppercase; letter-spacing: 0.04em; }",
        "p { margin: 0 0 8pt; }",
        ".meta { font: 9.5pt Helvetica, Arial, sans-serif; color: #333; }",
        ".box { border: 1pt solid #111; padding: 8pt 10pt; margin: 8pt 0 12pt; }",
        ".box p { margin: 0; }",
        "footer { border-top: 0.75pt solid #999; margin-top: 16pt; padding-top: 6pt; font: 8.5pt Helvetica, Arial, sans-serif; color: #555; }",
        "</style>",
        "</head>",
        "<body>",
        "<header>",
        f'<div class="mark">{html.escape(c["legal"].upper())}</div>',
        "<h1>Executive brief</h1>",
        f'<p class="kicker">For {html.escape(c["invited"])}  ·  From {html.escape(c["owner"])}  ·  '
        f"Release {html.escape(c['release'])}  ·  {html.escape(c['institute'])}</p>",
        "</header>",
    ]
    first = True
    for heading, body in brief_sections():
        if first and not heading:
            blocks.append(f'<p class="meta">{html.escape(body)}</p>')
            first = False
            continue
        first = False
        if heading == "The ask, in one sentence":
            blocks.append('<div class="box">')
            blocks.append(f"<h2>{html.escape(heading)}</h2>")
            blocks.append(f"<p>{html.escape(body)}</p>")
            blocks.append("</div>")
            continue
        if heading:
            blocks.append(f"<h2>{html.escape(heading)}</h2>")
        blocks.append(f"<p>{html.escape(body)}</p>")
    blocks += [
        "<footer>",
        f"{html.escape(c['legal'])}  ·  Job C admit plane  ·  Invited, not recorded  ·  "
        "Do not treat this page as a signed L1, an equity grant, or LIVE_PIN_OK.",
        "</footer>",
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(blocks)


def _wrap(text: str, width: int = 92) -> list[str]:
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


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _page_chrome(page_no: int, page_count: int) -> list[str]:
    label = f"{_ctx()['legal']}  ·  Confidential executive brief  ·  {page_no} / {page_count}"
    return [
        "0.08 0.08 0.08 rg",
        "0 756 612 36 re f",
        "1 1 1 rg",
        "BT",
        "/F2 9 Tf",
        f"1 0 0 1 {LEFT} 770 Tm",
        f"({_escape(_ctx()['legal'].upper())}) Tj",
        "ET",
        "0.55 0.55 0.55 RG",
        "0.6 w",
        f"{LEFT} 36 m {RIGHT} 36 l S",
        "0.35 0.35 0.35 rg",
        "BT",
        "/F2 8 Tf",
        f"1 0 0 1 {LEFT} 24 Tm",
        f"({_escape(label)}) Tj",
        "ET",
    ]


def render_pdf() -> bytes:
    """Deterministic two-font letter brief for printing."""
    commands: list[str] = []
    y = 732
    page_streams: list[str] = []

    def flush() -> None:
        nonlocal commands, y
        page_streams.append("\n".join(commands))
        commands = []
        y = 732

    for style, text in brief_lines():
        if style == "title":
            continue
        if style == "rule":
            commands.append(f"{LEFT} {y} m {RIGHT} {y} l S")
            y -= 14
            continue
        size = 11 if style == "head" else BODY_SIZE
        font = "/F2" if style == "head" else "/F1"
        if style == "head":
            y -= 10
        wrapped = _wrap(text, 86 if style == "body" else 78)
        for line in wrapped:
            if y < 56:
                flush()
            commands.append("BT")
            commands.append(f"{font} {size} Tf")
            if style == "head":
                commands.append("0.08 0.08 0.08 rg")
            else:
                commands.append("0.12 0.12 0.12 rg")
            commands.append(f"1 0 0 1 {LEFT} {y} Tm")
            commands.append(f"({_escape(line)}) Tj")
            commands.append("ET")
            y -= 16 if style == "head" else LEADING
        y -= 5 if style == "head" else 3
    flush()

    count = len(page_streams)
    decorated = ["\n".join(_page_chrome(i + 1, count) + [stream]) for i, stream in enumerate(page_streams)]

    objects: list[bytes] = [b""]
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + i} 0 R" for i in range(len(decorated)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(decorated)} >>".encode())
    font_times = 3 + len(decorated)
    font_helv = font_times + 1
    for index, stream in enumerate(decorated):
        content_id = font_helv + 1 + index
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
                f"/Resources << /Font << /F1 {font_times} 0 R /F2 {font_helv} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            ).encode()
        )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
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


def write_brief(path: Path | None = None) -> Path:
    """Write PDF plus print-ready HTML and GitHub markdown twins."""
    target = path or BRIEF_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    html_path = HTML_PATH if path is None else target.with_suffix(".html")
    md_path = MD_PATH if path is None else target.with_suffix(".md")
    html_path.write_text(brief_html(), encoding="utf-8")
    md_path.write_text(brief_markdown(), encoding="utf-8")
    target.write_bytes(render_pdf())
    return target
