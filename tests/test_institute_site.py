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
    assert "LIVE_PIN_OK" in html
    assert "scrollIntoView" in js
    assert "ainav-proof-day-brief.json" in js
    assert "prefers-reduced-motion" in css
    assert "--gold" in css
    swa = json.loads(Path("institute/staticwebapp.config.json").read_text(encoding="utf-8"))
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
    assert 'id="plane-path"' in html
    assert "walkable rehearsal" in html.lower() or "command console" in Path("institute/control-plane.html").read_text(encoding="utf-8").lower()
    assert "control-plane.json" in js
    assert "governance.json" in js
    assert "The client utilizes AI" in html
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
    assert 'id="review"' in html
    assert 'id="review-score"' in html
    assert 'id="review-fit"' in html
    assert 'href="#buyer"' in html
    assert 'href="#twin"' in html
    assert 'href="#open"' in html
    assert "James Hodnett" in html
    assert "Cynthia Hodnett is invited" in html
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
    assert all(item["wired"] is False for item in status["complements"])
    review = json.loads(Path("institute/review.json").read_text(encoding="utf-8"))
    assert review["kind"] == "ainav.review.v1"
    assert review["live"] is False
    assert review["live_pin_ok"] is False
    assert review["launch_ready"] is False
    assert review["equation"]["closed"] is False
    assert "markdown" not in review
