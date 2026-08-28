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
    assert "Business Central" in html
    assert "Sales Enterprise" in html
    assert "Microsoft twin bench" in html
    assert "No Dataverse write" in Path("institute/site.js").read_text(encoding="utf-8")
    status = json.loads(Path("institute/status.json").read_text(encoding="utf-8"))
    assert status["live"] is False
    assert status["live_pin_ok"] is False
    assert status["production"] is False
    assert status["bc"]["operating_company"] == "AINav"
    assert status["sales"]["wired"] is False
    assert status["opportunity"]["recognized_revenue"] is None
