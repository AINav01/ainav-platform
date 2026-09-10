"""Industry area narratives stay segmented, honest, and not a named vertical."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog
from ainav.face_kit import public_llms, public_search
from ainav.industry_certify import validate_honest_industry


def test_industry_areas_tell_need_and_why():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    packs = html[html.index('id="packs"') : html.index('id="governance"')]
    assert 'id="industry-narratives"' in packs
    assert 'id="industry-narr-lede"' in packs
    assert "Five industry areas" in packs
    assert "A 10/10+ quality check is not launch" in packs
    assert "A named vertical is not a SKU" in packs
    assert 'id="industry-area-books"' in packs
    assert 'id="industry-area-sales"' in packs
    assert 'id="industry-area-keep"' in packs
    assert 'id="industry-area-libraries"' in packs
    assert 'id="industry-area-repositories"' in packs
    assert "Need: an unauthorized Business Central journal" in packs
    assert "Need: an unauthorized quote override" in packs
    assert "Need: the examiner cannot see who admitted" in packs
    assert "Need: a desk without identity and notify" in packs
    assert "Need: law has to live somewhere" in packs
    assert "Standard inclusions" in packs
    assert "industry.treasury" in packs
    assert "lib.l1.wedge" in packs
    assert "lib.udual.sales" in packs
    assert "lib.padm.records" in packs
    assert "repo.catalog" in packs
    assert "Never free with P-ADM" in packs
    assert "Not a named auditor" in packs
    assert "healthcare" not in packs.lower()
    assert "manufacturing sku" not in packs.lower()
    assert "licensed as wired" not in packs.lower()
    assert "nvidia inception member" not in packs.lower()
    assert html.count("Owner book") == 1
    assert 'id="industry.treasury"' in packs
    assert 'id="industry.sales"' in packs
    assert 'id="industry.retention"' in packs
    assert 'href="#industry.treasury"' in packs
    assert 'class="industry-desk-hops"' in packs
    assert "industry-narr-lede" not in js
    assert "#industry-narratives" in css
    assert "#industry-area-hops a" in css
    assert "#industry-area-hops { grid-template-columns: repeat(5" in css
    assert ".industry-desk-hops" in css
    assert ".industry-area-bands" in css
    search_js = Path("institute/search.js").read_text(encoding="utf-8")
    assert 'input.value = ""' in search_js
    assert 'root.textContent = ""' in search_js
    assert "hashchange" in search_js
    assert "function dismiss" in search_js
    assert "replaceState" in search_js
    assert "getElementById" in search_js
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#packs"' not in nav
    assert html.count("Walk the industry") >= 6
    assert html.count("Walk Agent Intent") >= 6
    assert 'href="#industry.treasury"' in html.split('id="industry-day"', 1)[1]
    assert 'href="#industry-area-libraries"' in html.split('id="industry-day"', 1)[1]
    assert 'href="#industry-area-repositories"' in html.split('id="industry-day"', 1)[1]
    assert 'href="#industry.bank"' in html.split('id="industry-rooms"', 1)[1]
    assert 'href="#industry.treasury"' in html.split('id="pack-industry"', 1)[1]
    intent = html[html.index('id="agent-intent"') : html.index('id="industry-rooms"')]
    assert "Agent Intent is what the buyer says" in intent
    assert "Those words are intents. They are not SKUs." in intent
    assert 'id="agent-intent-need"' in intent
    assert 'id="agent-intent-why"' in intent
    assert "Need: an unauthorized bank rec" in intent
    assert "Need: a reserve journal two humans did not admit" in intent
    assert "Need: a booked RWA receivable without two seats" in intent
    assert "Stablecoin mint / burn" in intent
    assert "Tokenization / RWA issuance" in intent
    assert "Crypto asset management" in intent
    assert "Custody / wallet / ATS" in intent
    assert "Tokenized deposits" in intent
    assert "MiCA / CASP product" in intent
    assert "A named vertical is not a SKU" in intent
    assert "Not a /crypto route" in intent
    assert 'data-room-refuse="stablecoin_mint"' in intent
    assert 'data-room-refuse="rwa_issue"' in intent
    assert 'data-room-refuse="crypto_ams"' in intent
    assert 'id="agent-intent-refuse"' in intent
    assert 'id="agent-intent-hops"' in intent
    assert 'href="#industry.bank"' in intent
    assert "agent-intent-lede" not in js
    assert "refuseIndustryCert" in js
    assert '"agent-intent-refuse"' in js
    assert "idFromHash" in js
    assert "markLanded" in js
    assert "is-landed" in js
    assert 'closest("a[href]")' in js
    assert "#agent-intent" in css
    assert "#agent-intent-walks" in css
    assert "#agent-intent-lede" in css
    assert "#agent-intent-hops" in css
    assert "#agent-intent-hops { grid-template-columns: repeat(5" in css
    assert ".is-landed" in css
    assert "section[id]:target" in css
    assert "color: var(--ink)" in css
    assert ".agent-intent-cut" in css
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#crypto"' not in nav
    assert 'href="#token"' not in nav
    assert 'href="#rwa"' not in nav
    assert 'href="#agent-intent"' not in nav


def test_industry_catalog_and_search_name_the_areas():
    body = load_catalog()["industry_certify"]
    for text in (body["lede"], body["note"], body["site"]):
        low = text.lower()
        assert "five" in low and "areas" in low
        assert "a 10/10+ quality check is not launch" in low
        assert "industry certify is not launch" in low
    llms = public_llms().lower()
    assert "five industry areas" in llms
    assert "walk the five areas" in llms
    assert "agent intent sits on #agent-intent" in llms
    assert "a 10/10+ quality check is not launch" in llms
    search = public_search()
    packs = next(item for item in search["records"] if item["id"] == "packs")
    assert packs["href"] == "index.html#packs"
    assert "five industry areas" in packs["text"].lower()
    assert "need and why" in packs["text"].lower()
    assert "walk the five areas" in packs["text"].lower()
    intent = next(item for item in search["records"] if item["id"] == "agent-intent")
    assert intent["href"] == "index.html#agent-intent"
    assert "banks" in intent["text"].lower()
    assert "stablecoin" in intent["text"].lower()
    assert "tokenization" in intent["text"].lower()
    assert "crypto asset management" in intent["text"].lower()
    assert "a named vertical is not a sku" in intent["text"].lower()
    assert "not a /crypto route" in intent["text"].lower()
    books = next(item for item in search["records"] if item["id"] == "industry-books")
    assert books["href"] == "index.html#industry-area-books"
    sales = next(item for item in search["records"] if item["id"] == "industry-sales")
    assert sales["href"] == "index.html#industry-area-sales"
    keep = next(item for item in search["records"] if item["id"] == "industry-keep")
    assert keep["href"] == "index.html#industry-area-keep"
    libs = next(item for item in search["records"] if item["id"] == "industry-libraries")
    assert libs["href"] == "index.html#industry-area-libraries"
    repos = next(item for item in search["records"] if item["id"] == "industry-repositories")
    assert repos["href"] == "index.html#industry-area-repositories"
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    assert "five areas" in twin.lower()
    assert "a 10/10+ quality check is not launch" in twin.lower()
    assert 'href="index.html#industry-narratives"' in twin
    assert 'href="index.html#agent-intent"' in twin
    assert "Walk Agent Intent" in twin
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert 'href="index.html#industry-narratives"' in identify
    assert "Walk the industry" in identify
    assert 'href="index.html#agent-intent"' in identify
    assert "Walk Agent Intent" in identify
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert 'href="index.html#agent-intent"' in app
    assert "Walk Agent Intent" in app


def test_industry_lede_refuses_area_fiction():
    cat = load_catalog()
    body = cat["industry_certify"]
    missing_plus = dict(cat)
    missing_plus["industry_certify"] = dict(body)
    missing_plus["industry_certify"]["lede"] = (
        "Detail every industry desk: standard or upsell. "
        "Five industry areas tell the need and the why: books, sales deepen, keep. "
        "Industry certify is not launch. Packs are not SKUs."
    )
    with pytest.raises(IntegrityError, match="10/10"):
        validate_honest_industry(missing_plus)
    missing_areas = dict(cat)
    missing_areas["industry_certify"] = dict(body)
    missing_areas["industry_certify"]["lede"] = (
        "Detail every industry desk: standard or upsell. Need and why. "
        "Industry certify is not launch. A 10/10+ quality check is not launch."
    )
    with pytest.raises(IntegrityError, match="segmented industry areas"):
        validate_honest_industry(missing_areas)
    missing_need = dict(cat)
    missing_need["industry_certify"] = dict(body)
    missing_need["industry_certify"]["lede"] = (
        "Detail every industry desk: standard or upsell. books, sales deepen, keep. "
        "Industry certify is not launch. A 10/10+ quality check is not launch."
    )
    with pytest.raises(IntegrityError, match="need and why"):
        validate_honest_industry(missing_need)
    note_plus = dict(cat)
    note_plus["industry_certify"] = dict(body)
    note_plus["industry_certify"]["note"] = (
        "Honest industry. Packs are not SKUs. Industry certify is not launch. Five areas: books."
    )
    with pytest.raises(IntegrityError, match="10/10"):
        validate_honest_industry(note_plus)
    note_areas = dict(cat)
    note_areas["industry_certify"] = dict(body)
    note_areas["industry_certify"]["note"] = (
        "Honest industry. Packs are not SKUs. Industry certify is not launch. "
        "A 10/10+ quality check is not launch."
    )
    with pytest.raises(IntegrityError, match="five areas"):
        validate_honest_industry(note_areas)
    site_plus = dict(cat)
    site_plus["industry_certify"] = dict(body)
    site_plus["industry_certify"]["site"] = (
        "Honest industry certify on #packs. Five industry areas. "
        "Industry certify is not launch. Not a /industry route."
    )
    with pytest.raises(IntegrityError, match="10/10"):
        validate_honest_industry(site_plus)
    site_areas = dict(cat)
    site_areas["industry_certify"] = dict(body)
    site_areas["industry_certify"]["site"] = (
        "Honest industry certify on #packs. Industry certify is not launch. "
        "A 10/10+ quality check is not launch. Not a /industry route."
    )
    with pytest.raises(IntegrityError, match="five industry areas"):
        validate_honest_industry(site_areas)
