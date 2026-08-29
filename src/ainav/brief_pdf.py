"""Printable executive brief for the invited second human. Not a recorded officer."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from ainav.catalog import load_catalog
from ainav.finance import model as finance_model
from ainav.packs import public_packs

BRIEF_PATH = Path("docs/CYNTHIA_HODNETT_BRIEF.pdf")
HTML_PATH = Path("docs/CYNTHIA_HODNETT_BRIEF.html")
MD_PATH = Path("docs/CYNTHIA_HODNETT_BRIEF.md")
PAGE_W = 612
PAGE_H = 792
LEFT = 54
RIGHT = 558
BODY_SIZE = 10
LEADING = 12.5


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
        "lab_pin": cat["equations"]["lab_pin"],
    }


def _money(lo: int, hi: int) -> str:
    return f"${lo:,}–${hi:,}"


def brief_document() -> list[dict[str, Any]]:
    """Company packet + Cynthia letter. Catalog-honest. Not a contract."""
    c = _ctx()
    cat = load_catalog()
    fin = finance_model()
    by_id = {row["id"]: row for row in fin["scenarios"]}
    all_three = by_id["all_three"]
    depts = cat["organization"]["departments"]
    packs = public_packs()["industry"]
    return [
        {
            "kind": "kicker",
            "text": (
                f"Confidential  ·  For {c['invited']}  ·  From {c['owner']}, sole owner of {c['legal']}  ·  "
                f"Release {c['release']}  ·  Not a contract  ·  Not signed L1  ·  Not {c['lab_pin']}  ·  "
                "Invited, not recorded"
            ),
        },
        {
            "kind": "p",
            "text": (
                "This letter is for you, not for a customer and not for GitHub. "
                f"{c['owner']} asked that it be written from the company's own catalog so nothing "
                "here is invented: no email for you, no stock, no officer title, no named buyer, "
                "no claim that the public site has launched. If a sentence would make the company "
                "look further along than it is, it was left out."
            ),
        },
        {
            "kind": "h",
            "text": "Why a client must have this",
        },
        {
            "kind": "callout",
            "title": "The write that must not happen",
            "text": cat.get("l1_incident_copy") or "",
        },
        {
            "kind": "p",
            "text": (
                ((cat.get("governance") or {}).get("must_have") or {}).get("why")
                or "Every new client AI is another unauthorized-write surface unless one human plane sits over all of them."
            )
            + " Mandated: false. Certified: false. Not a fourth SKU. Job C is two humans before the write.",
        },
        {
            "kind": "p",
            "text": (
                ((cat.get("plane_interface") or {}).get("floor") or {}).get("already_have")
                or "Controllers already have Business Central Premium, Entra, and two-person journal SOD."
            )
            + " "
            + (
                ((cat.get("plane_interface") or {}).get("floor") or {}).get("still_lack")
                or "They do not have a gate in front of the write."
            )
            + " A Teams vote, a PIM activation, or Copilot asking a human is not dual admit.",
        },
        {
            "kind": "callout",
            "title": "Owner, board, examiner — same plane, three reasons",
            "text": (
                "Owner: "
                + str((((cat.get("governance") or {}).get("must_have") or {}).get("for") or {}).get("owner") or "")
                + " Board: "
                + str((((cat.get("governance") or {}).get("must_have") or {}).get("for") or {}).get("board") or "")
                + " Examiner: "
                + str((((cat.get("governance") or {}).get("must_have") or {}).get("for") or {}).get("examiner") or "")
            ),
        },
        {
            "kind": "p",
            "text": (
                "The sale is the ninety-minute proof day. "
                + str((cat.get("buyer") or {}).get("proof_day") or "")
            ),
        },
        {
            "kind": "h",
            "text": "Investor packet — print the letter with the full upsell catalog",
        },
        {
            "kind": "callout",
            "title": "The company in one line",
            "text": (
                "Human control plane over every client AI that can draft a privileged "
                "system-of-record write. Job C: two distinct humans bind the same action_hash. "
                "No admit, no write. Print the letter packet: docs/CYNTHIA_HODNETT_INVESTOR.pdf. "
                "Not a priced round. Not a forecast. Not a contract. Not LIVE_PIN_OK."
            ),
        },
        {
            "kind": "table",
            "title": "Scoreboard today — catalog-honest",
            "headers": ["Recognized revenue", "Named customers", "Signed L1", "Year-one if all three"],
            "rows": [
                [
                    f"${fin['recognized_revenue']:,}",
                    str(fin["named_customers"]),
                    str(fin["signed_l1"]),
                    f"{_money(all_three['min'], all_three['max'])} catalog list, not booked",
                ],
            ],
        },
        {
            "kind": "p",
            "text": (
                "Business model: prove with L1 ($28–40k / 2–4 weeks), keep with P-ADM "
                "($40–60k / year after kit PASS), deepen with paid U-DUAL ($20–35k / year, never free). "
                "Fee-for-service is $3,500/day on the same plane after L1. Packs are not SKUs. "
                "The commercial close is named dual seats × proof day × signed L1 × P-ADM attach. "
                "Insulation is independence × Job C lockfile × fail-closed gold × catalog law. "
                "The ask of you is seat B — not stock, not Global Admin, not a priced round."
            ),
        },
        {
            "kind": "h",
            "text": "Why the ultimate control plane insulates",
        },
        {
            "kind": "callout",
            "title": "Last gate over every drafting AI — not another model",
            "text": (cat.get("investor") or {}).get("control_plane")
            or (cat.get("ip", {}).get("insulation") or {}).get("why_ultimate_plane")
            or "",
        },
        {
            "kind": "h",
            "text": "How humans sit on the plane — executive dashboard",
        },
        {
            "kind": "callout",
            "title": "Authorize, provision, keep — honest tiles, not a certificate",
            "text": (cat.get("plane_interface") or {}).get("letter") or "",
        },
        {
            "kind": "h",
            "text": "Part I — For Cynthia Hodnett",
        },
        {
            "kind": "callout",
            "title": "The ask, in one sentence",
            "text": (
                f"{c['owner']} is building a company that will not let a privileged money-movement "
                "write land unless two distinct humans admit the exact same action. He can write "
                f"that gate. He cannot be both humans. We are asking you, {c['invited']}, to be the "
                "second human — seat B — with your own business email and your own click. Not stock. "
                "Not Global Admin. Not this Cloud Agent. Not a rubber stamp."
            ),
        },
        {
            "kind": "h",
            "text": "The incident the company exists to stop",
        },
        {
            "kind": "p",
            "text": (
                "Picture a Dynamics 365 Business Central general journal. A line posts. Cash, "
                "accrual, or a clearing account moves. Two people did not look at the same action "
                "and say yes. That is the unauthorized general-journal post that two humans did "
                "not admit. Controllers already have a name for the human rule: segregation of "
                "duties. What they do not have is a gate that sits in front of the write itself."
            ),
        },
        {
            "kind": "p",
            "text": (
                "The product is that gate. Two distinct people. One exact action, hashed so the "
                "memo cannot be swapped after you look. The grant is consumed once — a replay is "
                "a refusal. The effect is fail-closed: if either person is missing, or the apply "
                "fails, the write does not land and there is no fake success. We call this Job C: "
                "dual-admitted effect authority before a privileged system-of-record write. We do "
                "not inventory agents (Job A). We do not replace Microsoft Entra (Job B)."
            ),
        },
        {
            "kind": "p",
            "text": (
                "Microsoft hosts, identifies, notifies, and receives the write after the two of "
                "you admit it. Microsoft is not the product. Teams is not a seat. A chat is not "
                "dual admit. Copilot is not the admit plane. A PIM activation is not dual admit. "
                f"This Cloud Agent ({c['operator']}) can operate the host. It cannot be seat A or "
                "seat B. Owner plus agent is still one human."
            ),
        },
        {
            "kind": "h",
            "text": "What we are building together",
        },
        {
            "kind": "p",
            "text": (
                f"{c['legal']} is a Delaware C corporation. {c['owner']} is the sole owner. "
                f"The product is the {c['product']}. {c['institute']} is the public law of that "
                "plane — hosted on Azure, not launched, not bound to ainav.institute until James "
                "says launch in his own words. Master mothership issues the lockfile and never "
                "writes a client system of record. Cloud and local motherships share one consume "
                "ledger. Azure, Microsoft 365 E7, Business Central Premium, Sales Enterprise, and "
                "Teams Premium are the fabric. They receive the write after you and James admit it."
            ),
        },
        {
            "kind": "p",
            "text": (
                "The client utilizes AI. The client's customers utilize AI. Every one of those "
                "systems can draft a privileged write. Copilot, Agent 365, a BYO MCP, or a "
                "counterparty model may draft a journal. AINav is not that AI. It is the human "
                "control plane that sits over all of them: failsafe, off switch, reset, rollback. "
                "The client's two seats admit, then the write. No admit, no write. First record "
                "is the SoR write. Second record is the sealed DecisionRecord. Off switch is "
                "fail-closed, not powering down Copilot. Rollback is a compensating write, not "
                "a time machine. We map NIST, SOX, fiduciary oversight, books-and-records, the "
                "EU AI Act, and ISO 42001. We do not claim those certificates. We do not invent "
                "a board or a regulator. The plane sits on the client's existing org chart. "
                "Treasury and controller hold the two seats. Department AI is not a seat. "
                "We do not invent named department heads. Governance is not a fourth SKU. "
                "The plane stays independent of Microsoft and of the client's other AI vendors. "
                "A Teams vote or a Copilot prompt is not dual admit. This is not a patent. "
                "This is not uncopyable. G12 stays open."
            ),
        },
        {
            "kind": "p",
            "text": (
                "We sell three things only. Packs, hours, and Microsoft licenses are not products. "
                "A controller buys the commercial close: named dual seats × proof day × signed L1 × "
                f"P-ADM attach. The lab pin {c['lab_pin']} is a separate engineering fact and is "
                "never marked from a sale. Signed L1 is a counsel pack. It is still open."
            ),
        },
        {
            "kind": "table",
            "title": "The three SKUs — catalog list, not recognized revenue",
            "headers": ["SKU", "What the buyer is buying", "List"],
            "rows": [
                [
                    "L1 — prove",
                    "Two to four weeks. Prove the unauthorized journal cannot land without two seats. Ninety-minute proof day. Acceptance Kit on the twin.",
                    "$28,000–$40,000",
                ],
                [
                    "P-ADM — keep",
                    "Keep the same admit plane covered after kit PASS. Never bundles free U-DUAL.",
                    "$40,000–$60,000 / year",
                ],
                [
                    "U-DUAL — deepen",
                    "Same plane, onto Sales (quote / order). Never free with P-ADM.",
                    "$20,000–$35,000 / year",
                ],
            ],
        },
        {
            "kind": "p",
            "text": (
                f"If one controller bought all three in year one, the catalog list is "
                f"{_money(all_three['min'], all_three['max'])}. "
                "There is no named customer. There is no recognized revenue. Pipeline attached is "
                "zero. That honesty is the company, not a placeholder."
            ),
        },
        {
            "kind": "table",
            "title": "Upsell catalog — desks on the same three SKUs, not a fourth product",
            "headers": ["Desk", "Requires", "List"],
            "rows": [
                [
                    f"{item['id']} — {item['name']}",
                    item["requires_sku"],
                    (
                        f"included with {item['requires_sku']}"
                        if item["included"]
                        else _money(item["min"], item["max"])
                    ),
                ]
                for item in packs
            ],
        },
        {
            "kind": "p",
            "text": (
                "Fee-for-service is $3,500/day after L1: integration, replay, QBR, mothership ops, "
                "desk workshop, keep wiring, governance workshop, institute failsafe, board briefing, "
                "org-chart workshop, IP hygiene. Hours never mint a SKU and never attach U-DUAL. "
                "Print the full packet: docs/CYNTHIA_HODNETT_INVESTOR.pdf."
            ),
        },
        {
            "kind": "h",
            "text": "Where we actually are",
        },
        {
            "kind": "p",
            "text": (
                "The admit plane runs in code. Gold tests pass. There is a real Business Central "
                "Sandbox company named AINav and a sandbox journal AINAV-L1 dated 28 August 2026 "
                "for $250.00. Those seats were lab operator identities — not two named treasury "
                "humans. Production is blocked. The Institute has an Azure hostname. The custom "
                "domain still serves a Coming Soon page. Microsoft for Startups and NVIDIA Inception "
                "are qualification targets. Membership is not claimed. Crypto-associated is false. "
                "We do not lead with custody or GPU production."
            ),
        },
        {
            "kind": "table",
            "title": "Honest split — working versus not claimed",
            "headers": ["Working now", "Not claimed, not asked of you today"],
            "rows": [
                [
                    "Job C admit plane in code; sandbox journal on Business Central; Azure-hosted Institute held until launch",
                    "Signed L1; P-ADM attached; Business Central Production; live Sales / Dataverse; ainav.institute launched",
                ],
                [
                    "You are invited by name as seat B / business executive",
                    "You as a recorded officer, stockholder, or second unique human in the catalog",
                ],
                [
                    "Commercial equation written: named dual seats × proof day × signed L1 × P-ADM attach",
                    f"{c['lab_pin']}; product high availability; counsel-signed MSA; recognized revenue",
                ],
            ],
        },
        {
            "kind": "h",
            "text": "Why we need you — not a second license",
        },
        {
            "kind": "p",
            "text": (
                f"{c['owner']} is one human principal. Job C is a two-human fact. A second Microsoft "
                "365 license, a second tool, a second agent, or James clicking twice does not create "
                "dual admit. The second person must be a different human, with a different Entra "
                "object id, who actually reads the action and clicks. That is why this is a letter "
                "to you and not a settings change."
            ),
        },
        {
            "kind": "p",
            "text": (
                "You are the person James trusts with treasury judgment. The seat opposite "
                f"treasury_approver is {c['seat_role']} — the controller who will not let a journal "
                "land because it was convenient. NVIDIA Inception also requires two unique contacts "
                f"with business emails: a developer (James) and a {c['inception_role'].replace('_', ' ')} "
                "(you, if you agree). Aliases and Gmail are refused. Sole owner does not collapse "
                "those two contacts. You are not recorded as an officer. You are not a stockholder. "
                "No email is stored until you agree and James says record it."
            ),
        },
        {
            "kind": "p",
            "text": (
                "Without a second distinct person who actually clicks, AINav can keep a lab. It "
                "cannot sign L1. It cannot apply to Inception. It cannot look a controller in the "
                "eye and say two humans admitted the journal. That is the whole reason this brief "
                "exists. Your yes or no is the first commercial gate. Everything else on James's "
                "owner list waits behind it."
            ),
        },
        {
            "kind": "h",
            "text": "Your role if you agree — what a Tuesday looks like",
        },
        {
            "kind": "table",
            "title": "Two humans, two jobs, one write",
            "headers": ["", f"{c['owner']}", f"{c['invited']} (if you agree)"],
            "rows": [
                ["Seat", "A", "B"],
                ["Treasury", "treasury_approver", c["seat_role"]],
                ["Inception", "developer / programmer", c["inception_role"].replace("_", " ")],
                ["Identity", "His Entra user", "Your own @ainav.institute mailbox — not an alias, not Gmail, not his login"],
                ["Click", "Admits the same action hash", "Admits or refuses the same action hash"],
            ],
        },
        {
            "kind": "p",
            "text": (
                "When a privileged write is proposed, you see the account, the amount, the memo, "
                "and the action hash. You admit or you refuse. Refusing is the product working. "
                "If James clicks both seats, it is not dual. If you approve without reading, it is "
                "not dual. Proof day is ninety minutes on the sandbox twin with two named humans. "
                "It is still not Production. After a customer buys L1, you are one of the two seats "
                "the Acceptance Kit requires."
            ),
        },
        {
            "kind": "ul",
            "title": "You do not need, and this brief does not give you",
            "items": [
                "Global Admin, Azure ownership, or a programming role",
                "Equity or an officer title — counsel decides stock later; this page does not issue shares",
                "To become Copilot, Teams, Agent 365, or this Cloud Agent",
                "To buy a customer, launch ainav.institute, enable Production, mark LIVE_PIN_OK, or sign an MSA today",
            ],
        },
        {
            "kind": "h",
            "text": "What your yes unlocks — and what it does not",
        },
        {
            "kind": "p",
            "text": (
                "Your yes lets James create your mailbox, lets you sign in once, and lets proof day "
                "use two named humans instead of lab operator ids. It lets Inception have a business "
                "executive contact when — and only when — James also has a custom domain, an "
                "incorporation date outside this tree, and says the public site may launch. It does "
                "not make the company live. It does not attach P-ADM. It does not write Production. "
                "It does not make you a stockholder. It does not publish AINAV.Institute."
            ),
        },
        {
            "kind": "p",
            "text": (
                "Your no, or not yet, is also a complete answer. Nothing is recorded. The invite "
                "stays open. The company stays a one-human lab until a second distinct human "
                "actually clicks. James will not invent a contact to paper over that."
            ),
        },
        {
            "kind": "h",
            "text": "Part II — Foundational buildout",
        },
        {
            "kind": "p",
            "text": (
                "Three motherships, one law. Master mothership (Azure-declared, AINav) issues the "
                "lockfile, catalog, and gold. It never writes a client system of record. Cloud "
                "mothership (Azure-declared client plane) and local mothership (client plane) share "
                "one consume ledger and run AdmitClient against a Business Central digital twin. "
                "They are not two products. They are not two deployed production planes. Today they "
                "are in-process on that shared ledger. Week one: provision master lockfile → "
                "provision the cloud + local pair → proof day or Acceptance Kit on the BC twin → "
                "notify Teams → store kit evidence in SharePoint sandbox → refuse the live pin."
            ),
        },
        {
            "kind": "p",
            "text": (
                "Week-one prove is L1 + industry.treasury + lib.l1.wedge on bc.sandbox, Entra "
                "identity, and Teams notify. That is provisioning.standard_l1. It is not the whole "
                "commercial standard band. Standard seating included with L1 is every L1 pack and "
                "library with included_in_sku=true, plus the client executive dashboard. The "
                "dashboard is that same plane, tiled. It is not an upsell and not a SKU. There is "
                "one dashboard. Do not sell Standard Dashboard versus Advanced Dashboard. Standard "
                "pair adds cloud and local hosts on one ledger. Industry packs seat the same admit "
                "plane: treasury and controller on the journal wedge; payables, bank, cash, "
                "fixed-asset, and inventory as priced L1 desks; sales and quote desk included with "
                "paid U-DUAL — not free, not included with L1; invoice, credit, returns, and "
                "pricing as priced U-DUAL desks; retention as a priced P-ADM keep; governance "
                "seating included with L1; oversight keep as a priced P-ADM desk. Advanced "
                "provision is the upsell band — still not a SKU: priced desks, P-ADM keep, paid "
                "U-DUAL, and fee-for-service hours after L1. included means included with the "
                "required SKU when that SKU is attached. U-DUAL is never free. Hours never attach "
                "U-DUAL. Libraries bundle those modules. Repositories hold the plane, catalog, "
                "Institute, finance, brief, review, packs, runbooks, owner steps, counsel, and "
                "governance. None of those are SKUs. A la carte is a desk attach on L1, P-ADM, or "
                "paid U-DUAL — never a fourth product."
            ),
        },
        {
            "kind": "p",
            "text": (
                "Microsoft fabric, 10/10 and no further: Azure host (eastus; Institute eastus2; "
                "West Europe blocked by policy). Microsoft 365 E7 / Entra for seat object ids. "
                "Business Central Premium for L1 SoR. Sales Enterprise for U-DUAL SoR. Teams "
                "Enterprise and Premium for notify. Complements: Key Vault, Monitor, SharePoint kit "
                "evidence, Defender XDR, Entra PIM, Sentinel (the mothership LAW is not a Sentinel "
                "workspace), Azure Policy. Copilot, Agent 365, and Agent Tools ship inside E7. They "
                "are not the admit plane. A 10/10 Microsoft estate that votes in Teams or lets "
                "Copilot post the journal is a failure of Job C, not a feature."
            ),
        },
        {
            "kind": "h",
            "text": "Part III — Organization and operations",
        },
        {
            "kind": "p",
            "text": (
                "Ten departments. The map is complete out of the gate. That does not mean Sales, "
                "Teams, Institute, legal, or programs are live. BD and sales are the same motion: "
                "qualify an ICP controller who already has Business Central Premium, Entra, and "
                "two-person journal SOD → generate a proof-day brief they can forward → ninety "
                "minutes → sell L1 that week → kit PASS → attach P-ADM → offer paid U-DUAL. "
                "Exits: LOST, KIT_FAIL, CHURN. Do not invent a contact inbox or a design-partner name."
            ),
        },
        {
            "kind": "table",
            "title": "Operating company — departments are not SKUs",
            "headers": ["Department", "Role", "Status", "Blocked by"],
            "rows": [
                [
                    item["name"],
                    item["role"],
                    item["status"],
                    "; ".join(item.get("blocked_by") or []) or "none",
                ]
                for item in depts
            ],
        },
        {
            "kind": "h",
            "text": "Part IV — What we sell, pricing, financial model",
        },
        {
            "kind": "p",
            "text": (
                "Three SKUs. Five pricing models. Fee-for-service at $3,500/day on the same plane "
                "after L1. Hours never mint a SKU and never attach U-DUAL. There is no billing "
                f"provider. Recognized revenue is {fin['recognized_revenue']}. Signed L1 is "
                f"{fin['signed_l1']}. Named customers are {fin['named_customers']}. The numbers "
                "below are if-then catalog list. They are not a forecast, not ARR, and not booked."
            ),
        },
        {
            "kind": "table",
            "title": "Pricing models",
            "headers": ["Item", "Model", "How it is sold"],
            "rows": [
                ["L1", "Fixed-scope project", "2–4 week engagement. Priced against the unauthorized journal, not hours."],
                ["P-ADM", "Annual keep", "Attaches only after L1 Acceptance Kit PASS. Never bundles free U-DUAL."],
                ["U-DUAL", "Annual deepen", "Same admit plane onto Sales. Never free with P-ADM or U-SOR."],
                ["FFS", "Day rate $3,500", "Integration, replay, QBR, mothership ops, desk workshop, keep wiring. Requires L1. Not a SKU."],
                ["Pack attach", "Annual desk", "Priced L1 / U-DUAL / P-ADM desks. Not a fourth SKU. Never attaches U-DUAL."],
            ],
        },
        {
            "kind": "table",
            "title": "If-then catalog list — zero customers today",
            "headers": ["Scenario", "If", "List"],
            "rows": [
                [row["name"], row["if"], _money(row["min"], row["max"])]
                for row in fin["scenarios"]
            ],
        },
        {
            "kind": "h",
            "text": "Part V — Expert review: what works, what to improve, 15 upgrades",
        },
        {
            "kind": "p",
            "text": (
                "Read as a coding first-principles review, a Microsoft-fabric review, and a "
                "business review. The bar is gold-standard Job C, not a prettier Coming Soon page. "
                "Apple polish without the gate is decoration. Elon-style first principles without "
                "two humans is a lab."
            ),
        },
        {
            "kind": "ul",
            "title": "Working well",
            "items": list(cat["expert_review"]["working_well"]),
        },
        {
            "kind": "ul",
            "title": "Could be improved — without inventing a fourth SKU",
            "items": list(cat["expert_review"]["improve"]),
        },
        {
            "kind": "ul",
            "title": "Fifteen specific upgrades. Tree = already encoded. Owner = James must click.",
            "items": [
                f"{item['n']}. [{item['who']}] {item['title']} — {item['do']}"
                for item in cat["expert_review"]["upgrades"]
            ],
        },
        {
            "kind": "h",
            "text": "What happens next",
        },
        {
            "kind": "ul",
            "title": "Five steps, in order. Stop after step 1 until Cynthia has decided.",
            "items": [
                "Cynthia decides — yes, no, or not yet.",
                "If yes, James creates her @ainav.institute mailbox. She signs in once. He does not click seat B.",
                "He sends this agent her business email and says record it. Until those words, no email is stored.",
                "Proof day uses two named humans on the Business Central twin. Still not Production.",
                "Equity, officer titles, and Delaware filings stay with counsel. They are not required for this role.",
            ],
        },
        {
            "kind": "status",
            "text": (
                f"Invited: {c['invited']}  ·  Recorded: no  ·  Email: none stored  ·  Equity: no  ·  "
                f"Second officer: none  ·  Operator: {c['operator']} (not a seat)  ·  "
                f"Commercial close: {c['commercial']}  ·  Recognized revenue: 0"
            ),
        },
    ]


def brief_sections() -> list[tuple[str, str]]:
    """Compatibility: flatten the document to (heading, body) pairs."""
    rows: list[tuple[str, str]] = []
    for block in brief_document():
        kind = block["kind"]
        if kind == "kicker":
            rows.append(("", block["text"]))
        elif kind == "h":
            rows.append((block["text"], ""))
        elif kind == "callout":
            rows.append((block["title"], block["text"]))
        elif kind in {"p", "status"}:
            if rows and rows[-1][1] == "" and rows[-1][0]:
                rows[-1] = (rows[-1][0], block["text"])
            else:
                rows.append(("", block["text"]))
        elif kind == "ul":
            body = block.get("title", "") + " " + " ".join(f"({i + 1}) {item}" for i, item in enumerate(block["items"]))
            rows.append(("", body.strip()))
        elif kind == "table":
            lines = [block.get("title") or ""]
            headers = block["headers"]
            lines.append(" / ".join(headers))
            for row in block["rows"]:
                lines.append(" — ".join(row))
            rows.append(("", "  ".join(part for part in lines if part)))
    return [(h, b) for h, b in rows if h or b]


def brief_lines() -> list[tuple[str, str]]:
    c = _ctx()
    rows: list[tuple[str, str]] = [
        ("title", f"{c['legal']}  —  Executive brief"),
        ("body", f"Release {c['release']}  ·  For {c['invited']}  ·  From {c['owner']}"),
        ("body", "Printable. Catalog-honest. Not a contract. Not signed L1. Not LIVE_PIN_OK."),
        ("rule", ""),
    ]
    for block in brief_document():
        kind = block["kind"]
        if kind == "kicker":
            rows.append(("body", block["text"]))
        elif kind == "h":
            rows.append(("head", block["text"]))
        elif kind == "callout":
            rows.append(("head", block["title"]))
            rows.append(("body", block["text"]))
        elif kind in {"p", "status"}:
            rows.append(("body", block["text"]))
        elif kind == "ul":
            if block.get("title"):
                rows.append(("body", block["title"]))
            for item in block["items"]:
                rows.append(("body", f"— {item}"))
        elif kind == "table":
            if block.get("title"):
                rows.append(("body", block["title"]))
            rows.append(("body", " | ".join(block["headers"])))
            for row in block["rows"]:
                rows.append(("body", " | ".join(row)))
        elif kind == "rule":
            rows.append(("rule", ""))
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
    for block in brief_document():
        kind = block["kind"]
        if kind == "kicker":
            lines += [block["text"], ""]
        elif kind == "h":
            lines += [f"## {block['text']}", ""]
        elif kind == "callout":
            lines += [f"## {block['title']}", "", block["text"], ""]
        elif kind in {"p", "status"}:
            lines += [block["text"], ""]
        elif kind == "ul":
            if block.get("title"):
                lines += [block["title"], ""]
            for item in block["items"]:
                lines.append(f"- {item}")
            lines.append("")
        elif kind == "table":
            if block.get("title"):
                lines += [f"*{block['title']}*", ""]
            headers = block["headers"]
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join("---" for _ in headers) + " |")
            for row in block["rows"]:
                lines.append("| " + " | ".join(row) + " |")
            lines.append("")
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
        "@page { size: letter; margin: 0.65in 0.7in 0.7in 0.7in; }",
        "html, body { margin: 0; padding: 0; }",
        "body { font: 11pt/1.42 'Times New Roman', Times, serif; color: #161616; }",
        "header { border-bottom: 2.5pt solid #111; padding-bottom: 9pt; margin-bottom: 12pt; }",
        ".mark { font: 700 11pt Helvetica, Arial, sans-serif; letter-spacing: 0.16em; }",
        ".kicker { font: 8.5pt Helvetica, Arial, sans-serif; color: #444; margin: 5pt 0 0; }",
        "h1 { font: 700 22pt Helvetica, Arial, sans-serif; margin: 2pt 0 0; letter-spacing: -0.03em; }",
        "h2 { font: 700 10.5pt Helvetica, Arial, sans-serif; margin: 13pt 0 5pt; text-transform: uppercase; letter-spacing: 0.05em; page-break-after: avoid; }",
        "p { margin: 0 0 7pt; orphans: 3; widows: 3; }",
        ".meta { font: 9pt Helvetica, Arial, sans-serif; color: #333; margin-bottom: 10pt; }",
        ".box { border: 1.25pt solid #111; padding: 9pt 11pt; margin: 8pt 0 12pt; page-break-inside: avoid; }",
        ".box h2 { margin-top: 0; }",
        ".box p { margin: 0; }",
        "table { width: 100%; border-collapse: collapse; margin: 4pt 0 10pt; font: 9.5pt/1.35 Helvetica, Arial, sans-serif; page-break-inside: avoid; }",
        "caption { caption-side: top; text-align: left; font: italic 10pt Times, serif; margin: 0 0 4pt; }",
        "th, td { border: 0.6pt solid #444; padding: 5pt 6pt; vertical-align: top; }",
        "th { background: #111; color: #fff; font-weight: 700; text-align: left; }",
        "ul { margin: 0 0 8pt 1.1em; padding: 0; }",
        "li { margin: 0 0 3pt; }",
        ".status { font: 8.5pt Helvetica, Arial, sans-serif; color: #333; }",
        "footer { border-top: 0.75pt solid #999; margin-top: 14pt; padding-top: 6pt; font: 8pt Helvetica, Arial, sans-serif; color: #555; }",
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
    for block in brief_document():
        kind = block["kind"]
        if kind == "kicker":
            blocks.append(f'<p class="meta">{html.escape(block["text"])}</p>')
        elif kind == "h":
            blocks.append(f"<h2>{html.escape(block['text'])}</h2>")
        elif kind == "callout":
            blocks.append('<div class="box">')
            blocks.append(f"<h2>{html.escape(block['title'])}</h2>")
            blocks.append(f"<p>{html.escape(block['text'])}</p>")
            blocks.append("</div>")
        elif kind == "p":
            blocks.append(f"<p>{html.escape(block['text'])}</p>")
        elif kind == "status":
            blocks.append(f'<p class="status">{html.escape(block["text"])}</p>')
        elif kind == "ul":
            if block.get("title"):
                blocks.append(f"<p>{html.escape(block['title'])}</p>")
            blocks.append("<ul>")
            for item in block["items"]:
                blocks.append(f"<li>{html.escape(item)}</li>")
            blocks.append("</ul>")
        elif kind == "table":
            blocks.append("<table>")
            if block.get("title"):
                blocks.append(f"<caption>{html.escape(block['title'])}</caption>")
            blocks.append("<thead><tr>")
            for cell in block["headers"]:
                blocks.append(f"<th>{html.escape(cell)}</th>")
            blocks.append("</tr></thead><tbody>")
            for row in block["rows"]:
                blocks.append("<tr>")
                for cell in row:
                    blocks.append(f"<td>{html.escape(cell)}</td>")
                blocks.append("</tr>")
            blocks.append("</tbody></table>")
    blocks += [
        "<footer>",
        f"{html.escape(c['legal'])}  ·  Job C admit plane  ·  Invited, not recorded  ·  "
        "Do not treat these pages as a signed L1, an equity grant, or LIVE_PIN_OK.",
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
    """Deterministic multi-page letter brief for printing."""
    commands: list[str] = []
    y = 732.0
    page_streams: list[str] = []

    def flush() -> None:
        nonlocal commands, y
        page_streams.append("\n".join(commands))
        commands = []
        y = 732.0

    def need(height: float) -> None:
        nonlocal y
        if y - height < 56:
            flush()

    def text_block(font: str, size: float, color: str, lines: list[str], gap: float) -> None:
        nonlocal y
        for line in lines:
            need(gap)
            commands.append("BT")
            commands.append(f"{font} {size} Tf")
            commands.append(color)
            commands.append(f"1 0 0 1 {LEFT} {y:.1f} Tm")
            commands.append(f"({_escape(line)}) Tj")
            commands.append("ET")
            y -= gap

    for style, text in brief_lines():
        if style == "title":
            continue
        if style == "rule":
            need(16)
            commands.append("0.55 0.55 0.55 RG")
            commands.append("0.6 w")
            commands.append(f"{LEFT} {y:.1f} m {RIGHT} {y:.1f} l S")
            y -= 14
            continue
        if style == "head":
            need(36)
            y -= 8
            text_block("/F2", 11, "0.08 0.08 0.08 rg", _wrap(text, 70), 15)
            y -= 3
            continue
        text_block("/F1", BODY_SIZE, "0.12 0.12 0.12 rg", _wrap(text, 86), LEADING)
        y -= 2.5
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
