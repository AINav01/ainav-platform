from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.buyer import success_program
from ainav.catalog import load_catalog, validate_catalog


def test_executive_risk_is_catalog_law_and_on_the_sale_site():
    cat = load_catalog()
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "executive risk" in blob
    assert "non-compliance" in blob
    assert "sox opinion" in blob
    risk = cat["expert_review"]["success"]["executive_risk"]
    assert risk["sku"] is False
    assert risk["counsel"] is False
    assert risk["certified"] is False
    assert risk["sox_opinion"] is False
    assert risk["d_and_o"] is False
    assert risk["live_pin_ok"] is False
    assert "personal" in risk["lede"].lower()
    assert "write-fear" in risk["non_compliance"].lower()
    exported = success_program()["executive_risk"]
    assert exported["lede"] == risk["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert 'id="risk"' in html
    assert "paintExecutiveRisk" in js
    assert 'href="#risk">Executive risk</a>' in html
    assert "compliance-fear" in html.lower()
    assert "non-compliance that is ours" in html.lower()
    assert 'data-id="sox"' in html
    assert 'data-id="personal"' in html
    assert "SOX certificate as the product" in html
    assert "Sell a SOX certificate" in html
    assert 'href="/risk"' not in html
    assert html.index('id="control"') < html.index('id="risk"')
    assert html.index('id="success"') < html.index('id="risk"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#risk"' not in nav
    assert 'href="#control"' not in nav


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_executive_risk_fail_closed():
    def counsel(cat):
        cat["expert_review"]["success"]["executive_risk"]["counsel"] = True

    def sox(cat):
        cat["expert_review"]["success"]["executive_risk"]["sox_opinion"] = True

    def d_and_o(cat):
        cat["expert_review"]["success"]["executive_risk"]["d_and_o"] = True

    def live(cat):
        cat["expert_review"]["success"]["executive_risk"]["live_pin_ok"] = True

    def lede(cat):
        cat["expert_review"]["success"]["executive_risk"]["lede"] = "Be afraid of regulators."

    def personal(cat):
        cat["expert_review"]["success"]["executive_risk"]["personal"] = "We indemnify officers."

    def business(cat):
        cat["expert_review"]["success"]["executive_risk"]["business"] = "Buy L1 and clocks close."

    def compliance(cat):
        cat["expert_review"]["success"]["executive_risk"]["compliance"] = "Certified."

    def non_comp(cat):
        cat["expert_review"]["success"]["executive_risk"]["non_compliance"] = "Missed a map."

    def also(cat):
        cat["expert_review"]["success"]["executive_risk"]["also"] = ["nope"]

    def site(cat):
        cat["expert_review"]["success"]["executive_risk"]["site"] = "Put risk on the fold."

    def note(cat):
        cat["expert_review"]["success"]["executive_risk"]["note"] = "Certified."

    def shape(cat):
        cat["expert_review"]["success"]["executive_risk"] = "nope"

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "executive risk" not in item.lower()
        ]

    def sox_objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item
            for item in cat["expert_review"]["success"]["objections"]
            if item.get("id") != "sox"
        ]

    def personal_objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item
            for item in cat["expert_review"]["success"]["objections"]
            if item.get("id") != "personal"
        ]

    def walk(cat):
        cat["expert_review"]["success"]["qualify"]["walk_away"] = [
            item
            for item in cat["expert_review"]["success"]["qualify"]["walk_away"]
            if "sox" not in item.lower() and "compliant" not in item.lower() and "d&o" not in item.lower()
        ]

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "sox" not in item.lower() and "g12" not in item.lower() and "d&o" not in item.lower()
        ]

    def sale_book(cat):
        cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"] = [
            item
            for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"]
            if item.get("href") != "#risk"
        ]

    for mutator in (
        counsel,
        sox,
        d_and_o,
        live,
        lede,
        personal,
        business,
        compliance,
        non_comp,
        also,
        site,
        note,
        shape,
        principles,
        sox_objection,
        personal_objection,
        walk,
        ciso,
        sale_book,
    ):
        _reject(mutator)


def test_validate_executive_risk_direct_holes():
    good = dict(load_catalog()["expert_review"]["success"]["executive_risk"])
    with pytest.raises(IntegrityError):
        catmod._validate_executive_risk(None)
    certified = dict(good)
    certified["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_executive_risk(certified)
    worm = dict(good)
    worm["seventeen_a4"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_executive_risk(worm)
    brand = dict(good)
    brand["fear_brand"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_executive_risk(brand)
    sku = dict(good)
    sku["sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_executive_risk(sku)
    live = dict(good)
    live["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_executive_risk(live)
