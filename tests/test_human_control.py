from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.buyer import success_program
from ainav.catalog import load_catalog, validate_catalog


def test_human_control_is_catalog_law_and_on_the_sale_site():
    cat = load_catalog()
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "write-fear" in blob
    assert "doom-fear" in blob
    assert "loss of control" in blob
    control = cat["expert_review"]["success"]["human_control"]
    assert control["sku"] is False
    assert control["fear_brand"] is False
    assert control["live_pin_ok"] is False
    assert "write-fear" in control["ours"].lower()
    assert "doom-fear" in control["not_ours"].lower()
    exported = success_program()["human_control"]
    assert exported["lede"] == control["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert 'id="control"' in html
    assert "paintHumanControl" in js
    assert 'href="#control">Human control</a>' in html
    assert "write-fear" in html.lower()
    assert "doom-fear" in html.lower()
    assert 'data-id="doom"' in html
    assert "AI doom as the product" in html
    assert "Sell doom-fear" in html
    assert 'href="/fear"' not in html
    assert html.index('id="hero-write-rail"') < html.index('id="control"')
    assert html.index('id="success"') < html.index('id="control"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#control"' not in nav
    assert nav.count('href="#buyer"') == 1
    assert 'href="#twin"' in nav
    assert 'href="#success"' in nav
    assert "app.html" in nav
    assert 'href="#missing"' in nav


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_human_control_fail_closed():
    def fear_brand(cat):
        cat["expert_review"]["success"]["human_control"]["fear_brand"] = True

    def live(cat):
        cat["expert_review"]["success"]["human_control"]["live_pin_ok"] = True

    def lede(cat):
        cat["expert_review"]["success"]["human_control"]["lede"] = "Be afraid of AI."

    def ours(cat):
        cat["expert_review"]["success"]["human_control"]["ours"] = "AGI is the product."

    def loss(cat):
        cat["expert_review"]["success"]["human_control"]["loss"] = ["nope"]

    def restore(cat):
        cat["expert_review"]["success"]["human_control"]["restore"] = ["hope"]

    def site(cat):
        cat["expert_review"]["success"]["human_control"]["site"] = "Put doom on the fold."

    def social(cat):
        cat["expert_review"]["success"]["human_control"]["social"] = "Follow us."

    def note(cat):
        cat["expert_review"]["success"]["human_control"]["note"] = "Certified."

    def shape(cat):
        cat["expert_review"]["success"]["human_control"] = "nope"

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "write-fear" not in item.lower()
        ]

    def doom_principle(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "doom-fear" not in item.lower()
        ]

    def loss_principle(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "loss of control" not in item.lower()
        ]

    def doom_objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item
            for item in cat["expert_review"]["success"]["objections"]
            if item.get("id") != "doom"
        ]

    def doom_walk(cat):
        cat["expert_review"]["success"]["qualify"]["walk_away"] = [
            item
            for item in cat["expert_review"]["success"]["qualify"]["walk_away"]
            if "doom" not in item.lower() and "fear brand" not in item.lower()
        ]

    def ciso_doom(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "doom-fear" not in item.lower()
        ]

    def sale_book(cat):
        cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"] = [
            item
            for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"]
            if item.get("href") != "#control"
        ]

    for mutator in (
        fear_brand,
        live,
        lede,
        ours,
        loss,
        restore,
        site,
        social,
        note,
        shape,
        principles,
        doom_principle,
        loss_principle,
        doom_objection,
        doom_walk,
        ciso_doom,
        sale_book,
    ):
        _reject(mutator)


def test_validate_human_control_direct_holes():
    good = dict(load_catalog()["expert_review"]["success"]["human_control"])
    with pytest.raises(IntegrityError):
        catmod._validate_human_control(None)
    broken = dict(good)
    broken["cms"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_human_control(broken)
    sku = dict(good)
    sku["sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_human_control(sku)
    live = dict(good)
    live["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_human_control(live)
    brand = dict(good)
    brand["ours"] = "Write-fear as a fear brand."
    with pytest.raises(IntegrityError):
        catmod._validate_human_control(brand)
