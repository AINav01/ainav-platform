from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import catalog_institute_twin, load_catalog, validate_catalog
from ainav.microsoft.dns import catalog_edge, probe_edge_quality


def test_institute_twin_is_swa_and_cloudflare_apex_is_empty():
    cat = load_catalog()
    twin = cat["microsoft_stack"]["edge"]["twin"]
    assert twin["kind"] == "ainav.institute.twin.v1"
    assert twin["authorized"] is False
    assert twin["launch"] is False
    assert twin["live_pin_ok"] is False
    assert twin["gold_floor"] == 99
    assert twin["development"]["host"] == "azure.swa"
    assert twin["development"]["is_public_apex"] is False
    assert twin["public_edge"]["host"] == "cloudflare"
    assert twin["public_edge"]["is_institute"] is False
    assert twin["public_edge"]["challenge_hold"] is False
    assert "404" in twin["public_edge"]["observed"]
    assert twin["release"]["authorized"] is False
    exported = catalog_institute_twin()
    assert exported["lede"] == twin["lede"]
    edge = catalog_edge()
    assert edge["twin"]["gold_floor"] == 99
    assert cat["programs"]["website"]["twin_host"] == "azure.swa"
    assert cat["programs"]["website"]["public_edge"] == "cloudflare"
    assert cat["programs"]["website"]["authorized_release"] is False
    wait = " ".join(
        str(item.get("do") or "")
        for item in cat["microsoft_stack"]["edge"]["activate"]["wait"]
    ).lower()
    assert "twin" in wait
    assert "gold" in wait
    assert "point the apex at azure swa wait" not in wait
    assert "asuid" in wait
    quality = cat["microsoft_stack"]["edge"]["quality"]
    assert quality["apex_is_institute"] is False
    assert quality["ssl_full_claimed"] is False
    verified = " ".join(quality["verified"]).lower()
    assert "404" in verified
    assert "403" not in verified or "no longer" in " ".join(
        item.get("do") or "" for item in cat["microsoft_stack"]["edge"]["activate"]["now"]
    ).lower()
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "digital twin" in blob
    assert "apex 404" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert 'id="institute-twin"' in html
    assert "404 empty on Cloudflare" in html
    assert "Create a US Power Platform" not in html
    assert "treat the apex 404 as launch" in html
    assert "edge.twin" in js
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#institute-twin"' not in nav
    assert 'href="#twin-review"' not in nav
    assert 'href="#dataverse"' not in nav
    assert 'href="twin.html"' in html
    assert cat["programs"]["website"]["twin_review"] is True
    assert cat["programs"]["website"]["review_path"] == "twin.html"
    twin_page = Path("institute/twin.html").read_text(encoding="utf-8")
    assert "Azure SWA" in twin_page
    assert "Not launch" in twin_page


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_institute_twin_fail_closed():
    def authorized(cat):
        cat["microsoft_stack"]["edge"]["twin"]["authorized"] = True

    def launch(cat):
        cat["microsoft_stack"]["edge"]["twin"]["launch"] = True

    def live(cat):
        cat["microsoft_stack"]["edge"]["twin"]["live_pin_ok"] = True

    def floor(cat):
        cat["microsoft_stack"]["edge"]["twin"]["gold_floor"] = 95

    def lede(cat):
        cat["microsoft_stack"]["edge"]["twin"]["lede"] = "Public site is live on Cloudflare."

    def host(cat):
        cat["microsoft_stack"]["edge"]["twin"]["development"]["host"] = "cloudflare.pages"

    def apex(cat):
        cat["microsoft_stack"]["edge"]["twin"]["development"]["is_public_apex"] = True

    def public_is(cat):
        cat["microsoft_stack"]["edge"]["twin"]["public_edge"]["is_institute"] = True

    def hold(cat):
        cat["microsoft_stack"]["edge"]["twin"]["public_edge"]["challenge_hold"] = True

    def observed(cat):
        cat["microsoft_stack"]["edge"]["twin"]["public_edge"]["observed"] = "200 Institute"

    def release(cat):
        cat["microsoft_stack"]["edge"]["twin"]["release"]["authorized"] = True

    def requires(cat):
        cat["microsoft_stack"]["edge"]["twin"]["release"]["requires"] = ["ship it"]

    def refuse(cat):
        cat["microsoft_stack"]["edge"]["twin"]["release"]["not"] = ["nope"]

    def shape(cat):
        cat["microsoft_stack"]["edge"]["twin"] = "nope"

    def website(cat):
        cat["programs"]["website"]["authorized_release"] = True

    def twin_host(cat):
        cat["programs"]["website"]["twin_host"] = "pages"

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "digital twin" not in item.lower()
        ]

    def quality_403(cat):
        cat["microsoft_stack"]["edge"]["quality"]["verified"] = [
            item for item in cat["microsoft_stack"]["edge"]["quality"]["verified"] if "404" not in item
        ]

    for mutator in (
        authorized,
        launch,
        live,
        floor,
        lede,
        host,
        apex,
        public_is,
        hold,
        observed,
        release,
        requires,
        refuse,
        shape,
        website,
        twin_host,
        principles,
        quality_403,
    ):
        _reject(mutator)


def test_validate_institute_twin_direct_holes():
    with pytest.raises(IntegrityError):
        catmod._validate_institute_twin({"twin": None})
    good = dict(load_catalog()["microsoft_stack"]["edge"])
    sku = copy.deepcopy(good)
    sku["twin"]["sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_institute_twin(sku)
    live = copy.deepcopy(good)
    live["twin"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_institute_twin(live)
    kind = copy.deepcopy(good)
    kind["twin"]["kind"] = "nope"
    with pytest.raises(IntegrityError):
        catmod._validate_institute_twin(kind)
    note = copy.deepcopy(good)
    note["twin"]["note"] = "Certified launch."
    with pytest.raises(IntegrityError):
        catmod._validate_institute_twin(note)
    quality_note = copy.deepcopy(load_catalog())
    quality_note["microsoft_stack"]["edge"]["quality"]["note"] = (
        "It is not Institute launch. This Cloud Agent cannot edit Cloudflare."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_edge_quality(quality_note["microsoft_stack"]["edge"])
    activate = copy.deepcopy(load_catalog())
    for item in activate["microsoft_stack"]["edge"]["activate"]["now"]:
        if item.get("id") == "waf.managed":
            item["do"] = "Leave WAF on. Challenge holding."
    with pytest.raises(IntegrityError):
        catmod._validate_microsoft_edge(activate)
    site = copy.deepcopy(load_catalog())
    site["programs"]["website"]["public_edge"] = "pages"
    with pytest.raises(IntegrityError):
        validate_catalog(site)
    wait_twin = copy.deepcopy(load_catalog())
    wait_twin["microsoft_stack"]["edge"]["activate"]["wait"] = [
        {"id": "bind", "do": "Do not add asuid. Launch stays owner-only."},
        {"id": "dmarc.reject", "do": "Do not raise DMARC to p=reject."},
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_microsoft_edge(wait_twin)
    wait_swa = copy.deepcopy(load_catalog())
    wait_swa["microsoft_stack"]["edge"]["activate"]["wait"] = [
        {"id": "bind", "do": "asuid launch twin gold"},
        {
            "id": "origin",
            "do": "Polish, Image Resizing, and Page Rules that point the apex at Azure SWA wait. That is launch.",
        },
        {"id": "dmarc.reject", "do": "reject"},
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_microsoft_edge(wait_swa)


def test_edge_quality_probe_keeps_404_and_never_marks_institute(monkeypatch):
    http = {
        "http://ainav.institute/": {
            "url": "http://ainav.institute/",
            "status": 301,
            "headers": {"server": "cloudflare", "location": "https://ainav.institute/"},
            "title": "301 Moved Permanently",
            "csp": "",
            "cf_mitigated": "",
            "hsts": "",
            "location": "https://ainav.institute/",
            "body_prefix": "",
        },
        "https://ainav.institute/": {
            "url": "https://ainav.institute/",
            "status": 404,
            "headers": {"server": "cloudflare", "cf-ray": "test"},
            "title": "",
            "csp": "",
            "cf_mitigated": "",
            "hsts": "max-age=15552000",
            "location": "",
            "body_prefix": "",
        },
        "https://www.ainav.institute/": {
            "url": "https://www.ainav.institute/",
            "status": 301,
            "headers": {"server": "cloudflare"},
            "title": "",
            "csp": "",
            "cf_mitigated": "",
            "hsts": "",
            "location": "https://ainav.institute/",
            "body_prefix": "",
        },
        "https://ainav-institute.pages.dev/": {
            "url": "https://ainav-institute.pages.dev/",
            "status": 404,
            "headers": {"server": "cloudflare"},
            "title": "",
            "csp": "",
            "cf_mitigated": "",
            "hsts": "",
            "location": "",
            "body_prefix": "",
        },
        "https://blue-river-010091a0f.7.azurestaticapps.net/": {
            "url": "https://blue-river-010091a0f.7.azurestaticapps.net/",
            "status": 200,
            "headers": {},
            "title": "AINAV.Institute",
            "csp": "script-src 'self'; form-action 'none'",
            "cf_mitigated": "",
            "hsts": "",
            "location": "",
            "body_prefix": "Job C",
        },
    }
    monkeypatch.setattr("ainav.microsoft.dns._http_probe", lambda url: http[url])
    monkeypatch.setattr(
        "ainav.microsoft.dns._tls_versions",
        lambda host: {"tls1_0": False, "tls1_1": False, "tls1_2": True, "tls1_3": True},
    )
    monkeypatch.setattr(
        "ainav.microsoft.dns._visitor_cert",
        lambda host: {
            "issuer": "US Google Trust Services WE1",
            "san": ["ainav.institute"],
            "notAfter": "Nov 28 22:27:17 2026 GMT",
            "note": "not Full",
        },
    )
    monkeypatch.setattr("ainav.microsoft.dns._dig", lambda name, rtype: ["52.96.10.1"])
    body = probe_edge_quality(
        dns={
            "website": {"swa_asuid_present": False},
            "e7_on_cloudflare": {"full": True},
            "microsoft_365": {"mx": ["0 ainav-institute.mail.protection.outlook.com"]},
        }
    )
    assert body["apex_is_institute"] is False
    assert body["authorized_release"] is False
    assert body["apex_404"] is True
    assert body["https_403_challenge"] is False
    assert body["cloudflare_edge"] is True
    assert body["apex_has_institute_csp"] is False
    assert body["twin_swa_200"] is True
    assert "swa twin" in body["note"].lower()
    assert "404 empty" in body["note"].lower()
