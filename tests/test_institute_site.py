from __future__ import annotations

import json
from pathlib import Path


def test_institute_foundation_is_catalog_honest():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert 'href="#main"' in html
    assert 'id="main"' in html
    assert 'class="skip"' in html
    assert "site.js" in html
    assert "href=\"mailto:" not in html
    assert "nvidia inception member" not in html.lower()
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "app.js" in app
    assert "nvidia inception member" not in app.lower()
    assert "Not a priced round" in app
    assert 'href="app.html"' in html
    assert "popovertarget" in html
    assert "site-search" in html
    assert Path("institute/kit.html").exists()
    assert "LIVE_PIN_OK" in html
    assert "scrollIntoView" in js
    assert "ainav-proof-day-brief.json" in js
    assert "prefers-reduced-motion" in css
    assert "@media (max-width: 520px)" in css
    assert ".plane-attention[hidden]" in css
    assert "--gold" in css
    swa = json.loads(Path("institute/staticwebapp.config.json").read_text(encoding="utf-8"))
    assert "/app.html" in swa["navigationFallback"]["exclude"]
    assert "/app.js" in swa["navigationFallback"]["exclude"]
    assert "/programs.json" in swa["navigationFallback"]["exclude"]
    assert "/kit.html" in swa["navigationFallback"]["exclude"]
    assert "/search.json" in swa["navigationFallback"]["exclude"]
    assert "/plane-business.json" in swa["navigationFallback"]["exclude"]
    assert "/llms.txt" in swa["navigationFallback"]["exclude"]
    assert "Content-Security-Policy" in swa["globalHeaders"]
    assert swa["responseOverrides"]["404"]["rewrite"] == "/404.html"
    assert Path("institute/404.html").exists()
    assert Path("institute/favicon.svg").exists()
    robots = Path("institute/robots.txt").read_text(encoding="utf-8")
    assert "Sitemap:" in robots
    manifest = json.loads(Path("institute/site.webmanifest").read_text(encoding="utf-8"))
    assert manifest["name"] == "AINAV.Institute"
    assert 'id="twin"' in html
    assert 'id="opportunity"' in html
    assert 'id="finance"' in html
    assert 'href="#finance"' in html
    assert 'id="governance"' in html
    assert 'href="#governance"' in html
    assert 'id="control-plane"' in html
    assert "Human control plane" in html
    assert 'id="plane-tiles"' in html
    assert 'id="plane-hierarchy"' in html
    assert 'id="plane-depts"' in html
    assert 'id="plane-maps"' in html
    assert "control-plane.html" in html
    plane_html = Path("institute/control-plane.html").read_text(encoding="utf-8")
    assert "app.html#floor" in plane_html
    assert "pointer" in plane_html.lower()
    assert "not a second dashboard" in plane_html.lower()
    assert 'id="app-floor-assign"' in Path("institute/app.html").read_text(encoding="utf-8")
    assert 'id="app-floor-estate"' in Path("institute/app.html").read_text(encoding="utf-8")
    assert 'id="plane-path"' in html
    assert "walkable rehearsal" in html.lower() or "command console" in plane_html.lower() or "walk entire" in plane_html.lower()
    assert "control-plane.json" in js
    assert "governance.json" in js
    assert "The client utilizes AI" in html
    assert "unauthorized general-journal" in html.lower()
    assert "customer's customer AI" in html.lower() or "customer AI" in html
    assert "two humans before the write" in html.lower()
    assert "already have" in html.lower()
    assert "gate in front of the write" in html.lower()
    assert 'id="must-for"' in html
    assert 'id="not-the-gate"' in html
    assert 'id="proof-close"' in html
    assert 'id="accountable"' in html
    assert 'id="hero-accountable"' in html
    assert 'id="hero-protect"' in html
    assert 'id="protect"' in html
    assert "cannot weaken Job C" in html
    assert "not a signature" in html
    assert "floor.protect" in js
    assert 'id="buyer-protect-lede"' in html
    assert "#protect.must-for" in css
    assert 'id="hero-memory"' in html
    assert 'id="memory"' in html
    assert "two records and a keep" in html
    assert "not a time machine" in html.lower()
    assert "A mailbox is not the second record" in html
    assert "floor.memory" in js
    assert 'id="buyer-memory-lede"' in html
    assert "#memory.must-for" in css
    assert html.index('class="hero"') < html.index('id="buyer"')
    assert html.index('id="must-for"') > html.index('id="buyer"')
    assert 'id="hero-integrate"' in html
    assert 'id="integrate"' in html
    assert "cannot create users" in html.lower()
    assert "https://admin.microsoft.com/Adminportal/Home#/users" in html
    assert "https://admin.cloud.microsoft/?source=applauncher#/agents/tools/all" in html
    assert "https://admin.powerplatform.microsoft.com/environments" in html
    assert "https://businesscentral.dynamics.com/ainav.institute/Sandbox" in html
    assert "floor.integrate" in js
    assert "paintIntegrate" in js
    assert "#integrate.stack" in css
    assert html.index('id="integrate"') > html.index('id="memory"')
    assert html.index('id="integrate"') < html.index('id="buyer-prices"')
    assert 'id="twin-lab"' in html
    assert "who may admit, freeze, keep" in html.lower()
    assert "lab oids are not two named treasury humans" in html.lower()
    assert "Inventory of models is not a control" in html
    assert "vendor-native button" in html.lower()
    assert "BC native dual approval" in html
    assert "In-harness AI governor" in html
    assert "Workflow User Groups" in html
    assert "sealed DecisionRecord" in html
    assert "write does not land" in html.lower()
    assert "gov-cascade" in html or "id=\"gov-cascade\"" in html
    assert "gov-records" in html or "id=\"gov-records\"" in html
    assert "First record" in html
    assert "Humans stay in control" in html
    assert "gov-must" in html or 'id="gov-must"' in html
    assert "gov-plane" in html or 'id="gov-plane"' in html
    assert "off switch" in html.lower()
    assert 'id="client-org"' in html
    assert "client-org.json" in js
    assert 'id="ip"' in html
    assert 'id="ip-thesis"' in html
    assert 'id="investor"' in html
    assert "investor.json" in js
    assert 'id="investor-exec-lede"' in html
    assert 'id="investor-exec-table"' in html
    assert 'id="investor-letter"' in html
    assert 'id="investor-letter-body"' in html
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    assert "#investor .letter" in css
    assert "#investor table.packet" in css
    assert "executive_summary" in js
    assert '"letter_voice": "first_person"' in Path("institute/investor.json").read_text(encoding="utf-8")
    assert 'id="investor-ffs"' in html
    assert 'id="investor-plane"' in html
    assert 'id="ip-ultimate"' in html
    assert 'id="ip-layers"' in html
    assert 'id="ip-pins"' in html
    assert "ip.json" in js
    gov = json.loads(Path("institute/governance.json").read_text(encoding="utf-8"))
    assert gov["kind"] == "ainav.governance.v1"
    assert gov["certified"] is False
    assert gov["sku"] is False
    assert "client AI" in " ".join(gov["failsafe"]["separate_from"])
    assert gov["cascade"]["counterparties_utilize_ai"] is True
    assert gov["cascade"]["client_institutes_ainav"] is True
    assert "sor" in gov["records"]["first"]["what"].lower()
    assert gov["records"]["sku"] is False
    assert gov["records"]["certified"] is False
    assert gov["must_have"]["mandated"] is False
    assert gov["plane"]["sits_over_client_ai"] is True
    assert "fail-closed" in gov["plane"]["off_switch"]["does"].lower()
    assert 'id="pack-industry"' in html
    assert 'id="pack-libraries"' in html
    assert "packs.json" in js
    packs = json.loads(Path("institute/packs.json").read_text(encoding="utf-8"))
    assert packs["kind"] == "ainav.institute.packs.v1"
    assert packs["sku"] is False
    assert packs["live"] is False
    assert {item["id"] for item in packs["industry"]} >= {
        "industry.cash",
        "industry.returns",
        "industry.retention",
        "industry.cascade",
        "industry.second_record",
        "industry.control_plane",
        "industry.off_switch",
        "industry.rollback",
        "industry.board",
        "industry.org",
        "industry.internal_audit",
        "industry.independence",
        "industry.ip_keep",
    }
    assert 'id="fabric"' in html
    assert 'id="stack-walk"' in html
    assert 'href="#stack-walk"' in html
    assert 'id="stack-walk-path"' in html
    assert 'id="stack-walk-complements"' in html
    assert "paintStackWalk" in js
    assert "https://dash.cloudflare.com" in html
    assert "https://security.microsoft.com" in html
    assert 'id="e7-cloudflare"' in html
    assert 'id="e7-cloudflare-already"' in html
    assert "not a ninth complement" in html.lower()
    assert 'id="review"' in html
    assert 'id="review-score"' in html
    assert 'id="review-fit"' in html
    assert 'id="success"' in html
    assert 'href="#success"' in html
    assert 'id="they-win"' in html
    assert 'id="we-win"' in html
    assert 'id="qualify-walk"' in html
    assert 'id="objections"' in html
    assert 'id="ciso-holds"' in html
    assert 'id="seat-b-not"' in html
    assert 'id="continuity"' in html
    assert 'id="review-upgrades"' in html
    assert "licensed substitute" in html.lower()
    assert "cheaper Workflow User Groups" in html
    assert "paintSuccess" in js
    assert "expert_review" in js
    assert 'href="#buyer"' in html
    assert 'href="#twin"' in html
    assert 'href="#open"' in html
    assert "James Hodnett" in html
    assert "Cynthia Hodnett agreed" in html
    assert "chodnett@ainav.institute" in html
    assert "href=\"mailto:" not in html
    assert 'id="hero-contrast"' in html
    assert 'id="hero-write-rail"' in html
    assert 'id="hero-rail-kicker"' in html
    assert 'id="plane-write-rail"' in html
    assert 'id="plane-dash-lede"' in html
    assert 'id="hero-skus"' in html
    assert 'id="included-upsells"' in html
    assert 'id="commercial-lede"' in html
    assert "not a gift" in html.lower()
    assert 'data-sku="L1"' in html
    assert 'data-sku="P-ADM"' in html
    assert 'data-sku="U-DUAL"' in html
    assert "paintPublicFace" in js
    assert "Owner book" in html
    assert "nav-menu" in html
    assert "nav-toggle" in html
    assert 'id="nav-open"' in html
    assert 'class="nav-check"' in html
    assert "<details class=\"nav-menu\">" not in html
    assert html.index('href="#closed"') < html.index('class="primary"')
    assert 'href="#success">Bake-off</a>' in html
    assert "Substitute vs Job C" in html
    assert "Workflow User Groups" in html
    assert "1 mailbox / 0 oid" in html
    assert "0 / 1 invited" not in html
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    assert "app.html#floor" in plane
    assert "1 mailbox / 0 oid" in plane
    assert "0 / 1 invited" not in plane
    assert 'id="complement-cards"' in html
    assert 'id="twin-notify"' in html
    assert 'id="twin-kit"' in html
    assert 'id="twin-pim"' in html
    assert 'id="twin-copilot"' in html
    assert 'id="twin-agent-tools"' in html
    assert 'id="agent-tools"' in html
    assert 'id="agent-tools-steps"' in html
    assert "admin.microsoft.com" in html
    assert 'id="week-path"' in html
    assert 'id="buyer-sale"' in html
    assert 'id="buyer-week"' in html
    assert "qualify → ninety-minute proof day" in html
    assert 'id="hero-sale"' in html
    assert 'id="hero-notes"' in html
    assert 'id="investor-catalog-detail"' in html
    assert 'id="investor-decision"' in html
    assert 'id="investor-tuesday"' in html
    assert 'id="about"' in html
    assert html.index('id="buyer"') < html.index('id="twin"') < html.index('id="product"') < html.index('id="about"') < html.index('id="opportunity"')
    assert "<h2>Proof day</h2>" in html
    assert "The product is the admit plane" in html
    assert 'id="opp-year-one"' in html
    assert "Business Central" in html
    assert "Sales Enterprise" in html
    assert "Microsoft twin bench" in html
    assert "Microsoft fabric" in html
    assert "d365.quote.discount_override" in html
    assert "A chat is not a seat" in html
    for complement in (
        "entra.id",
        "azure.keyvault",
        "azure.monitor",
        "sharepoint.kit",
        "defender.xdr",
        "entra.pim",
        "sentinel.siem",
        "azure.policy",
    ):
        assert f'data-id="{complement}"' in html
    assert "No Dataverse write" in js
    assert "grant already consumed" in js
    assert "d365.quote.discount_override" in js
    assert "bc.general_journal.post" in js
    assert "Graph is not called" in js
    assert "sharepoint.kit" in js
    assert "No SharePoint write" in js
    assert "PIM activation is not dual admit" in js
    assert "Copilot is not the admit plane" in js
    assert "m365.agent_tools" in js
    assert "agent-tools.json" in js
    assert "agent-tools-steps" in js
    assert "owner_playbook" in js
    assert "complement-cards" in js
    assert "e7_cloudflare" in js
    assert "e7-cloudflare-already" in js
    assert "year_one_list_if_all_three" in js
    assert "business.json" in js
    assert "review.json" in js
    assert "review-fit" in js
    assert "--azure" in css
    status = json.loads(Path("institute/status.json").read_text(encoding="utf-8"))
    assert status["live"] is False
    assert status["live_pin_ok"] is False
    assert status["production"] is False
    assert status["bc"]["operating_company"] == "AINav"
    assert status["sales"]["wired"] is False
    assert status["notify"]["wired"] is False
    assert status["opportunity"]["recognized_revenue"] is None
    assert status["opportunity"]["year_one_list_if_all_three"]["min"] == 88000
    assert status["fabric"]["live"] is False
    assert status["e7_cloudflare"]["full"] is True
    assert status["e7_cloudflare"]["sku"] is False
    assert status["e7_cloudflare"]["live_pin_ok"] is False
    assert status["engineering"]["gold_ci"]["exists"] is True
    assert status["engineering"]["gold_ci"]["observed_green"] is True
    assert status["engineering"]["sku"] is False
    assert 'href="#closed"' in html
    assert 'href="#missing"' in html
    assert html.index('href="#closed"') < html.index('href="#missing"')
    assert html.index('href="#missing"') < html.index('href="#open"')
    assert ">Owner<" in html
    assert "James must click" in html
    assert html.count('href="#missing">Owner</a>') >= 2
    assert "<h2>Owner — James must click</h2>" in html
    assert "G1/G10 LIVE_PIN_OK" in html
    assert "#missing" in css
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    assert 'href="index.html#closed"' in plane
    assert 'href="index.html#missing"' in plane
    assert status["engineering"]["live_pin_ok"] is False
    assert 'id="closed"' in html
    assert 'id="honest-missing"' in html
    assert "G12 legal (counsel pack unsigned)" in html
    assert "closed-in-tree" in js
    assert all(item["wired"] is False for item in status["complements"])
    review = json.loads(Path("institute/review.json").read_text(encoding="utf-8"))
    assert review["kind"] == "ainav.review.v1"
    assert review["live"] is False
    assert review["live_pin_ok"] is False
    assert review["launch_ready"] is False
    assert review["equation"]["closed"] is False
    assert "markdown" not in review
