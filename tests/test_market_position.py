from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.buyer import success_program
from ainav.catalog import load_catalog, validate_catalog


def test_market_position_is_catalog_law_and_on_the_sale_site():
    cat = load_catalog()
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "market position" in blob
    assert "forecast" in blob
    assert "priced round" in blob
    market = cat["expert_review"]["success"]["market_position"]
    assert market["sku"] is False
    assert market["forecast"] is False
    assert market["priced_round"] is False
    assert market["tam"] is False
    assert market["launch"] is False
    assert market["live_pin_ok"] is False
    assert "unlaunched" in market["lede"].lower()
    assert "demand is 0" in market["now"].lower()
    exported = success_program()["market_position"]
    assert exported["lede"] == market["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert 'id="market"' in html
    assert "paintMarketPosition" in js
    assert 'href="#market">Market</a>' in html
    assert "zero booked" in html.lower()
    assert "demand is 0" in html.lower()
    assert 'data-id="share"' in html
    assert 'data-id="future"' in html
    assert "TAM / forecast as the product" in html
    assert "Invent TAM or forecast ARR" in html
    assert 'href="/market"' not in html
    assert html.index('id="risk"') < html.index('id="market"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#market"' not in nav
    assert 'href="#risk"' not in nav


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_market_position_fail_closed():
    def forecast(cat):
        cat["expert_review"]["success"]["market_position"]["forecast"] = True

    def priced(cat):
        cat["expert_review"]["success"]["market_position"]["priced_round"] = True

    def tam(cat):
        cat["expert_review"]["success"]["market_position"]["tam"] = True

    def launch(cat):
        cat["expert_review"]["success"]["market_position"]["launch"] = True

    def leader(cat):
        cat["expert_review"]["success"]["market_position"]["category_leader"] = True

    def live(cat):
        cat["expert_review"]["success"]["market_position"]["live_pin_ok"] = True

    def lede(cat):
        cat["expert_review"]["success"]["market_position"]["lede"] = "We lead the AI market."

    def now(cat):
        cat["expert_review"]["success"]["market_position"]["now"] = "Pipeline is strong."

    def future(cat):
        cat["expert_review"]["success"]["market_position"]["future"] = "Series A then IPO."

    def not_future(cat):
        cat["expert_review"]["success"]["market_position"]["not_the_future"] = "Growth."

    def also(cat):
        cat["expert_review"]["success"]["market_position"]["also"] = ["nope"]

    def site(cat):
        cat["expert_review"]["success"]["market_position"]["site"] = "Put TAM on the fold."

    def note(cat):
        cat["expert_review"]["success"]["market_position"]["note"] = "Certified."

    def shape(cat):
        cat["expert_review"]["success"]["market_position"] = "nope"

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "market position" not in item.lower()
        ]

    def share_objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item
            for item in cat["expert_review"]["success"]["objections"]
            if item.get("id") != "share"
        ]

    def future_objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item
            for item in cat["expert_review"]["success"]["objections"]
            if item.get("id") != "future"
        ]

    def walk(cat):
        cat["expert_review"]["success"]["qualify"]["walk_away"] = [
            item
            for item in cat["expert_review"]["success"]["qualify"]["walk_away"]
            if "tam" not in item.lower()
            and "forecast" not in item.lower()
            and "priced round" not in item.lower()
        ]

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "tam" not in item.lower()
            and "priced round" not in item.lower()
            and "institute launch" not in item.lower()
        ]

    def sale_book(cat):
        cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"] = [
            item
            for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"]
            if item.get("href") != "#market"
        ]

    for mutator in (
        forecast,
        priced,
        tam,
        launch,
        leader,
        live,
        lede,
        now,
        future,
        not_future,
        also,
        site,
        note,
        shape,
        principles,
        share_objection,
        future_objection,
        walk,
        ciso,
        sale_book,
    ):
        _reject(mutator)


def test_validate_market_position_direct_holes():
    good = dict(load_catalog()["expert_review"]["success"]["market_position"])
    with pytest.raises(IntegrityError):
        catmod._validate_market_position(None)
    sku = dict(good)
    sku["sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_market_position(sku)
    live = dict(good)
    live["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_market_position(live)
    brand = dict(good)
    brand["fear_brand"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_market_position(brand)
