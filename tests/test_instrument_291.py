from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import OPERATING_DAY_IDS, load_catalog, validate_catalog
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_291_microsoft_operating_day_roster():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.02.0"
    firm = cat["expert_review"]["success"]["operating_company"]
    run = firm["microsoft_run"]
    assert run["kind"] == "ainav.microsoft_run.v1"
    assert run["roster"] is True
    assert run["roster_is_sku"] is False
    assert "roster" in firm["glance"].lower()
    assert "licensed-not-wired" in firm["glance"].lower()
    assert [item["id"] for item in run["day_map"]] == OPERATING_DAY_IDS
    assert all(item["wired"] is False and item["live"] is False for item in run["day_map"])
    assert cat["programs"]["website"]["microsoft_roster"] is True
    assert cat["programs"]["website"]["microsoft_roster_is_sku"] is False
    assert any(
        "2.91.0" in item and "roster" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "roster" in principles
    assert "licensed-not-wired is visible" in principles
    missing = " ".join(cat["honest_missing"]).lower()
    assert "teams" in missing
    assert "sharepoint" in missing
    assert "sentinel" in missing
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 72
    assert upgrades[61]["who"] == "tree"
    assert upgrades[61]["done"] is True
    assert upgrades[61]["marks_live_pin"] is False
    blob = f"{upgrades[61]['title']} {upgrades[61]['do']}".lower()
    assert "roster" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.02.0" in html
    assert html.find('id="firm-ms"') < html.find('id="firm-day"')
    assert 'id="firm-open-assign"' in html
    assert "firm-wire-sharepoint" in html
    assert "firm-wire-sentinel" in html
    assert 'id="firm-ms-opens"' in html
    assert "licensed · not wired" in css
    assert "firm.needs" in js
    assert "run.owner_only" in js
    assert "run.note" in js
    assert "index.html#firm-ms" in twin
    assert "licensed-not-wired" in twin.lower()
    assert 'id="app-floor-ms"' in app
    assert "Microsoft operating day" in app
    assert "index.html#firm-ms" in app
    dash = public_dashboard()
    assert dash["release"] == "3.02.0"
    status = public_status()
    assert status["release"] == "3.02.0"
    assert status["website"]["microsoft_roster"] is True
    assert status["website"]["microsoft_roster_is_sku"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_291_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.90.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.91.0" not in item
        ]

    def roster_off(cat):
        cat["programs"]["website"]["microsoft_roster"] = False

    def roster_sku(cat):
        cat["programs"]["website"]["microsoft_roster_is_sku"] = True

    def product(cat):
        cat["programs"]["website"]["microsoft_is_the_product"] = True

    def run_roster(cat):
        cat["expert_review"]["success"]["operating_company"]["microsoft_run"]["roster"] = False

    def run_sku(cat):
        cat["expert_review"]["success"]["operating_company"]["microsoft_run"]["roster_is_sku"] = True

    def glance(cat):
        cat["expert_review"]["success"]["operating_company"]["glance"] = "Operating day. Launch gate closed."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "roster" not in item.lower()
        ]

    def missing(cat):
        cat["honest_missing"] = [
            item
            for item in cat["honest_missing"]
            if "teams" not in item.lower()
            and "sharepoint" not in item.lower()
            and "sentinel" not in item.lower()
        ]

    for mutator in (
        release,
        closed,
        roster_off,
        roster_sku,
        product,
        run_roster,
        run_sku,
        glance,
        principles,
        missing,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    roster_hole = copy.deepcopy(edge)
    roster_hole["programs"]["website"]["microsoft_roster"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_291(roster_hole, roster_hole["plane_interface"])
    glance_hole = copy.deepcopy(edge)
    glance_hole["expert_review"]["success"]["operating_company"]["glance"] = "Operating day."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_291(glance_hole, glance_hole["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "roster" not in item.lower() and "licensed-not-wired is visible" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_291(principles_hole, principles_hole["plane_interface"])
    missing_hole = copy.deepcopy(edge)
    missing_hole["honest_missing"] = [
        item
        for item in missing_hole["honest_missing"]
        if "teams" not in item.lower()
        and "sharepoint" not in item.lower()
        and "sentinel" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_291(missing_hole, missing_hole["plane_interface"])
    sku_hole = copy.deepcopy(edge)
    sku_hole["expert_review"]["success"]["operating_company"]["microsoft_run"]["roster_is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_291(sku_hole, sku_hole["plane_interface"])
    run_hole = copy.deepcopy(edge)
    run_hole["expert_review"]["success"]["operating_company"]["microsoft_run"]["roster"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_291(run_hole, run_hole["plane_interface"])
    closed_hole = copy.deepcopy(edge)
    closed_hole["engineering"]["closed_in_tree"] = [
        item for item in closed_hole["engineering"]["closed_in_tree"] if "2.91.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_291(closed_hole, closed_hole["plane_interface"])
    product_hole = copy.deepcopy(edge)
    product_hole["programs"]["website"]["microsoft_is_the_product"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_291(product_hole, product_hole["plane_interface"])
    site_sku = copy.deepcopy(edge)
    site_sku["programs"]["website"]["microsoft_roster_is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_291(site_sku, site_sku["plane_interface"])


def test_honest_missing_teams_sharepoint_sentinel_fail_closed():
    cat = copy.deepcopy(load_catalog())

    def only(stem):
        hole = copy.deepcopy(cat)
        hole["honest_missing"] = [
            item for item in hole["honest_missing"] if stem not in item.lower()
        ]
        return hole

    with pytest.raises(IntegrityError):
        catmod._validate_honest_missing(only("teams"))
    with pytest.raises(IntegrityError):
        catmod._validate_honest_missing(only("sharepoint"))
    with pytest.raises(IntegrityError):
        catmod._validate_honest_missing(only("sentinel"))
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "roster" not in item.lower()
            ]
        )
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "licensed-not-wired is visible" not in item.lower()
            ]
        )
    run = copy.deepcopy(cat["expert_review"]["success"]["operating_company"]["microsoft_run"])
    run["roster"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_microsoft_run(run)
    run_sku = copy.deepcopy(cat["expert_review"]["success"]["operating_company"]["microsoft_run"])
    run_sku["roster_is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_microsoft_run(run_sku)
    firm = copy.deepcopy(cat["expert_review"]["success"]["operating_company"])
    firm["glance"] = "Operating day. Launch gate closed."
    with pytest.raises(IntegrityError):
        catmod._validate_operating_company(firm)
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item for item in ciso["ciso"]["does_not"] if "roster as wired" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
