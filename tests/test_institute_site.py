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
    assert 'id="fabric"' in html
    assert 'id="complement-cards"' in html
    assert 'id="twin-notify"' in html
    assert 'id="twin-kit"' in html
    assert 'id="twin-pim"' in html
    assert 'id="twin-copilot"' in html
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
    assert "complement-cards" in js
    assert "year_one_list_if_all_three" in js
    assert "business.json" in js
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
