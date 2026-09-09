from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import CLIENT_UNIVERSE_RAIL_IDS, load_catalog, validate_catalog
from ainav.buyer import success_program
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_293_client_universe():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.17.0"
    universe = cat["expert_review"]["success"]["client_universe"]
    assert universe["kind"] == "ainav.client_universe.v1"
    assert universe["sku"] is False
    assert universe["cms"] is False
    assert universe["fear_brand"] is False
    assert universe["mfa_admits"] is False
    assert universe["assigned"] is False
    assert universe["named_client"] is False
    assert universe["certified"] is False
    assert universe["forecast"] is False
    assert [item["id"] for item in universe["surfaces"]] == CLIENT_UNIVERSE_RAIL_IDS
    assert "#universe" in universe["site"]
    assert "not a /universe route" in universe["site"].lower()
    assert "mfa identifies" in universe["lede"].lower()
    assert "identify is not admit" in universe["lede"].lower()
    assert cat["programs"]["website"]["client_universe"] is True
    assert cat["programs"]["website"]["universe_is_sku"] is False
    assert cat["programs"]["website"]["universe_href"] == "#universe"
    assert "#universe" in cat["operations"]["note"]
    assert "#brand" in cat["operations"]["note"]
    assert any(
        "2.93.0" in item and "universe" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "client business universe" in principles
    assert "mfa identifies" in principles
    assert "identify is not admit" in principles
    assert "not a /universe route" in principles
    missing = " ".join(cat["honest_missing"]).lower()
    assert "assigned client universe" in missing
    assert "named client" in missing
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 87
    assert upgrades[63]["who"] == "tree"
    assert upgrades[63]["done"] is True
    assert upgrades[63]["marks_live_pin"] is False
    blob = f"{upgrades[63]['title']} {upgrades[63]['do']}".lower()
    assert "universe" in blob
    assert "live_pin_ok" in blob
    exported = success_program()["client_universe"]
    assert exported["lede"] == universe["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert 'id="universe-groups"' in html
    assert 'id="universe-lede"' in html
    assert 'id="universe-status"' in html
    assert 'id="universe-spine"' in html
    assert "universe-mfa-admit" in html
    assert "universe-named-client" in html
    assert "universe-sandbox-prod" in html
    assert "universe-certify" in html
    assert "universe-fourth-sku" in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#universe"' not in nav
    assert 'href="/universe"' not in html
    assert "paintClientUniverse" in js
    assert "#universe" in css
    assert "index.html#universe" in twin
    assert "mfa identifies" in twin.lower()
    assert "unnamed until signed l1" in twin.lower()
    assert 'id="app-floor-universe"' in app
    assert "index.html#universe" in app
    assert 'href="#universe"' in html.split('id="ops-note"', 1)[1].split("</p>", 1)[0]
    dash = public_dashboard()
    assert dash["release"] == "3.17.0"
    status = public_status()
    assert status["release"] == "3.17.0"
    assert status["website"]["client_universe"] is True
    assert status["website"]["universe_is_sku"] is False
    assert status["website"]["universe_href"] == "#universe"
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_293_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.92.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.93.0" not in item
        ]

    def universe_off(cat):
        cat["programs"]["website"]["client_universe"] = False

    def universe_sku(cat):
        cat["programs"]["website"]["universe_is_sku"] = True

    def href(cat):
        cat["programs"]["website"]["universe_href"] = "/universe"

    def kind(cat):
        cat["expert_review"]["success"]["client_universe"]["kind"] = "ainav.client_universe.v0"

    def mfa_admits(cat):
        cat["expert_review"]["success"]["client_universe"]["mfa_admits"] = True

    def assigned(cat):
        cat["expert_review"]["success"]["client_universe"]["assigned"] = True

    def named(cat):
        cat["expert_review"]["success"]["client_universe"]["named_client"] = True

    def surfaces(cat):
        cat["expert_review"]["success"]["client_universe"]["surfaces"] = []

    def site(cat):
        cat["expert_review"]["success"]["client_universe"]["site"] = "Universe lives on /universe."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "client business universe" not in item.lower()
        ]

    def missing(cat):
        cat["honest_missing"] = [
            item for item in cat["honest_missing"] if "named client" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. The operating day is #firm. The brand is #brand."

    for mutator in (
        release,
        closed,
        universe_off,
        universe_sku,
        href,
        kind,
        mfa_admits,
        assigned,
        named,
        surfaces,
        site,
        principles,
        missing,
        ops,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    off = copy.deepcopy(edge)
    off["programs"]["website"]["client_universe"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(off, off["plane_interface"])
    sku = copy.deepcopy(edge)
    sku["programs"]["website"]["universe_is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(sku, sku["plane_interface"])
    href_hole = copy.deepcopy(edge)
    href_hole["programs"]["website"]["universe_href"] = "/universe"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(href_hole, href_hole["plane_interface"])
    kind_hole = copy.deepcopy(edge)
    kind_hole["expert_review"]["success"]["client_universe"]["kind"] = "ainav.client_universe.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(kind_hole, kind_hole["plane_interface"])
    mfa_hole = copy.deepcopy(edge)
    mfa_hole["expert_review"]["success"]["client_universe"]["mfa_admits"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(mfa_hole, mfa_hole["plane_interface"])
    named_hole = copy.deepcopy(edge)
    named_hole["expert_review"]["success"]["client_universe"]["named_client"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(named_hole, named_hole["plane_interface"])
    assigned_hole = copy.deepcopy(edge)
    assigned_hole["expert_review"]["success"]["client_universe"]["assigned"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(assigned_hole, assigned_hole["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["expert_review"]["success"]["client_universe"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(certified, certified["plane_interface"])
    surfaces_hole = copy.deepcopy(edge)
    surfaces_hole["expert_review"]["success"]["client_universe"]["surfaces"] = []
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(surfaces_hole, surfaces_hole["plane_interface"])
    site_hole = copy.deepcopy(edge)
    site_hole["expert_review"]["success"]["client_universe"]["site"] = "Universe on /universe."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(site_hole, site_hole["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "client business universe" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(principles_hole, principles_hole["plane_interface"])
    missing_hole = copy.deepcopy(edge)
    missing_hole["honest_missing"] = [
        item for item in missing_hole["honest_missing"] if "named client" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(missing_hole, missing_hole["plane_interface"])
    closed_hole = copy.deepcopy(edge)
    closed_hole["engineering"]["closed_in_tree"] = [
        item for item in closed_hole["engineering"]["closed_in_tree"] if "2.93.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(closed_hole, closed_hole["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = "SKU attach chain. The operating day is #firm. The brand is #brand."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(ops_hole, ops_hole["plane_interface"])
    ops_sku = copy.deepcopy(edge)
    ops_sku["operations"]["note"] = "The client universe is #universe. The brand is #brand."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(ops_sku, ops_sku["plane_interface"])


def test_client_universe_and_first_principles_fail_closed():
    cat = copy.deepcopy(load_catalog())
    universe = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    universe["sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(universe)
    mfa = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    mfa["mfa_admits"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(mfa)
    named = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    named["named_client"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(named)
    assigned = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    assigned["assigned"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(assigned)
    site = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    site["site"] = "Universe lives on /universe."
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(site)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "client business universe" not in item.lower()
            ]
        )
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item
        for item in ciso["ciso"]["does_not"]
        if "mfa as admit" not in item.lower()
        and "named client universe" not in item.lower()
        and "universe as a sku" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
    for flag in (
        "fourth_sku",
        "cms",
        "fear_brand",
        "live",
        "live_pin_ok",
        "launch",
        "production",
        "certified",
        "forecast",
    ):
        hole = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
        hole[flag] = True
        with pytest.raises(IntegrityError):
            catmod._validate_client_universe(hole)
    kind = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    kind["kind"] = "ainav.client_universe.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(kind)
    surfaces = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    surfaces["surfaces"] = []
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(surfaces)
    stem = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    stem["surfaces"][0]["note"] = "A login."
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(stem)
    refuse = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    refuse["refuse"] = ["something else"]
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(refuse)
    owner = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    owner["owner_only"] = ["something else"]
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(owner)
    firm_site = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    firm_site["site"] = "Client universe on #universe. Not a /universe route."
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(firm_site)
    note = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    note["note"] = "A client face."
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(note)
    lede = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    lede["lede"] = "A client face."
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(lede)
    glance = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    glance["glance"] = "A board."
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(glance)
    clocks = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    clocks["note"] = "MFA identifies. Identify is not admit. Not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(clocks)
    packs = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    packs["lede"] = (
        "The client business universe is the post-close face. MFA identifies. "
        "Identify is not admit. Two humans bind one hash."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(packs)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item.replace("MFA identifies", "MFA gates").replace("Not a /universe route", "Not a second dashboard").replace("not a /universe route", "not a second dashboard")
                if "universe" in item.lower()
                else item
                for item in cat["expert_review"]["first_principles"]
            ]
        )
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item.replace("segregated branded", "assigned").replace("Not a /universe route", "Not a second dashboard")
                if "universe" in item.lower()
                else item
                for item in cat["expert_review"]["first_principles"]
            ]
        )
    write_rail = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    write_rail["site"] = (
        "Client universe on #universe. Close is #path. Twin is #twin. Brand is #brand. "
        "Firm is #firm. Not a /universe route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(write_rail)
    brand_sku = copy.deepcopy(cat)
    brand_sku["programs"]["website"]["brand_is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(brand_sku, brand_sku["plane_interface"])
    forecast = copy.deepcopy(cat)
    forecast["expert_review"]["success"]["client_universe"]["forecast"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(forecast, forecast["plane_interface"])
    sku_flag = copy.deepcopy(cat)
    sku_flag["expert_review"]["success"]["client_universe"]["sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(sku_flag, sku_flag["plane_interface"])
    route = copy.deepcopy(cat)
    route["expert_review"]["first_principles"] = [
        item.replace("Not a /universe route", "Not a second dashboard")
        if "/universe route" in item
        else item
        for item in route["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_293(route, route["plane_interface"])
