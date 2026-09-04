from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.buyer import success_program
from ainav.catalog import load_catalog, validate_catalog


def test_what_was_missing_is_catalog_law_and_on_the_sale_site():
    cat = load_catalog()
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "what you've been missing" in blob
    assert "you already have" in blob
    assert "fourth sku" in blob
    missing = cat["expert_review"]["success"]["what_was_missing"]
    assert missing["kind"] == "ainav.what_was_missing.v1"
    assert missing["sku"] is False
    assert missing["cms"] is False
    assert missing["fourth_sku"] is False
    assert missing["launch"] is False
    assert missing["live_pin_ok"] is False
    assert missing["forecast"] is False
    assert "been missing" in missing["lede"].lower()
    assert any("business central" in item.lower() for item in missing["already_have"])
    assert any("action_hash" in item.lower() for item in missing["been_missing"])
    exported = success_program()["what_was_missing"]
    assert exported["lede"] == missing["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    assert 'id="have"' in html
    assert "paintWhatWasMissing" in js
    assert 'href="#have">You\'ve been missing</a>' in html
    assert "You already have" in html
    assert "You've been missing" in html
    assert "Whole-business capabilities" in html
    assert "Tools around the plane" in html
    assert "We refuse to become" in html
    assert "fourth SKU" in html
    assert 'href="/have"' not in html
    assert html.index('id="market"') < html.index('id="have"')
    assert html.index('id="have"') < html.index('id="missing"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#have"' not in nav
    assert 'href="#missing"' in nav
    assert "index.html#have" in twin
    assert "Not #missing" in twin


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_what_was_missing_fail_closed():
    def sku(cat):
        cat["expert_review"]["success"]["what_was_missing"]["sku"] = True

    def cms(cat):
        cat["expert_review"]["success"]["what_was_missing"]["cms"] = True

    def fourth(cat):
        cat["expert_review"]["success"]["what_was_missing"]["fourth_sku"] = True

    def launch(cat):
        cat["expert_review"]["success"]["what_was_missing"]["launch"] = True

    def live(cat):
        cat["expert_review"]["success"]["what_was_missing"]["live_pin_ok"] = True

    def forecast(cat):
        cat["expert_review"]["success"]["what_was_missing"]["forecast"] = True

    def lede(cat):
        cat["expert_review"]["success"]["what_was_missing"]["lede"] = "A new Copilot."

    def already(cat):
        cat["expert_review"]["success"]["what_was_missing"]["already_have"] = ["nope"]

    def been(cat):
        cat["expert_review"]["success"]["what_was_missing"]["been_missing"] = ["nope"]

    def caps(cat):
        cat["expert_review"]["success"]["what_was_missing"]["capabilities"] = ["nope"]

    def tools(cat):
        cat["expert_review"]["success"]["what_was_missing"]["tools_around"] = ["nope"]

    def refuse(cat):
        cat["expert_review"]["success"]["what_was_missing"]["refuse_to_become"] = ["nope"]

    def site(cat):
        cat["expert_review"]["success"]["what_was_missing"]["site"] = "Put wow on the fold."

    def note(cat):
        cat["expert_review"]["success"]["what_was_missing"]["note"] = "Certified."

    def shape(cat):
        cat["expert_review"]["success"]["what_was_missing"] = "nope"

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "what you've been missing" not in item.lower()
        ]

    def have_objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item
            for item in cat["expert_review"]["success"]["objections"]
            if item.get("id") != "have"
        ]

    def walk(cat):
        cat["expert_review"]["success"]["qualify"]["walk_away"] = [
            item
            for item in cat["expert_review"]["success"]["qualify"]["walk_away"]
            if "cms" not in item.lower()
            and "fourth sku" not in item.lower()
            and "been missing" not in item.lower()
        ]

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "fourth sku" not in item.lower()
            and "cms" not in item.lower()
            and "sale wow" not in item.lower()
        ]

    def sale_book(cat):
        cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"] = [
            item
            for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"]
            if item.get("href") != "#have"
        ]

    for mutator in (
        sku,
        cms,
        fourth,
        launch,
        live,
        forecast,
        lede,
        already,
        been,
        caps,
        tools,
        refuse,
        site,
        note,
        shape,
        principles,
        have_objection,
        walk,
        ciso,
        sale_book,
    ):
        _reject(mutator)


def test_validate_what_was_missing_direct_holes():
    good = dict(load_catalog()["expert_review"]["success"]["what_was_missing"])
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(None)
    for key in ("sku", "cms", "fourth_sku", "launch", "fear_brand", "forecast", "live", "live_pin_ok"):
        hole = dict(good)
        hole[key] = True
        with pytest.raises(IntegrityError):
            catmod._validate_what_was_missing(hole)
    kind = dict(good)
    kind["kind"] = "ainav.wow.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(kind)
    lede = dict(good)
    lede["lede"] = "A new Copilot."
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(lede)
    site = dict(good)
    site["site"] = "Put wow on the fold."
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(site)
    note = dict(good)
    note["note"] = "Certified."
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(note)
    already = dict(good)
    already["already_have"] = ["nope"]
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(already)
    been = dict(good)
    been["been_missing"] = ["nope"]
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(been)
    caps = dict(good)
    caps["capabilities"] = ["nope"]
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(caps)
    tools = dict(good)
    tools["tools_around"] = ["nope"]
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(tools)
    refuse = dict(good)
    refuse["refuse_to_become"] = ["nope"]
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(refuse)
    short_already = dict(good)
    short_already["already_have"] = [
        "Business Central Entra Workflow Copilot Teams PIM"
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(short_already)
    short_been = dict(good)
    short_been["been_missing"] = [
        "action_hash consume-once fail-closed freeze independence counterparty"
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(short_been)
    short_caps = dict(good)
    short_caps["capabilities"] = [
        "Admit consume-once fail-closed keep freeze examiner walk-away twin dashboard"
    ] * 6
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(short_caps)
    short_tools = dict(good)
    short_tools["tools_around"] = [
        "Teams E7 Cloudflare Gold Kit SWA"
    ] * 4
    with pytest.raises(IntegrityError):
        catmod._validate_what_was_missing(short_tools)
