from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import CLIENT_UNIVERSE_GROUP_IDS, CLIENT_UNIVERSE_HREFS, load_catalog, validate_catalog
from ainav.buyer import success_program
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_294_operable_universe():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.94.0"
    universe = cat["expert_review"]["success"]["client_universe"]
    assert universe["operable"] is True
    assert universe["refuse_is_visible"] is True
    assert universe["wells_are_live"] is False
    wells = universe["wells"]
    assert wells["client_mark"] == ""
    assert wells["assigned"] is False
    assert wells["first_record"] == 0
    assert wells["second_record"] == 0
    assert wells["maps_claimed"] is False
    assert wells["packs_attached"] == 0
    assert [item["id"] for item in universe["groups"]] == CLIENT_UNIVERSE_GROUP_IDS
    hrefs = {item["id"]: item["href"] for item in universe["surfaces"]}
    assert hrefs == CLIENT_UNIVERSE_HREFS
    assert "honest zeros" in universe["site"].lower()
    assert "refuse is visible" in universe["site"].lower()
    assert cat["programs"]["website"]["universe_operable"] is True
    assert cat["programs"]["website"]["universe_wells_live"] is False
    assert "honest zeros" in cat["operations"]["note"].lower()
    assert any(
        "2.94.0" in item and "operable" in item.lower() and "universe" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "operable client universe" in principles
    assert "honest zeros" in principles
    assert "refuse is visible" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 64
    assert upgrades[64]["who"] == "tree"
    assert upgrades[64]["done"] is True
    assert upgrades[64]["marks_live_pin"] is False
    blob = f"{upgrades[64]['title']} {upgrades[64]['do']}".lower()
    assert "operable" in blob
    assert "live_pin_ok" in blob
    exported = success_program()["client_universe"]
    assert exported["wells"]["first_record"] == 0
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "2.94.0" in html
    assert 'id="universe-wells"' in html
    assert 'id="universe-groups"' in html
    assert 'id="universe-refuse"' in html
    assert 'id="universe-ledger"' in html
    assert 'data-group="control"' in html
    assert 'data-group="marks"' in html
    assert 'data-group="govern"' in html
    assert 'data-group="offer"' in html
    assert 'aria-live="assertive"' in html
    assert "identify.html" in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#universe"' not in nav
    assert "refuseUniverse" in js
    assert "writeUniverseLedger" in js
    assert "universe-groups" in js
    assert ".universe-refuse.is-live" in css
    assert ".universe-console" in css
    assert "honest zeros" in twin.lower()
    assert "refuse is visible" in twin.lower()
    assert "Mark <b>unnamed</b>" in app or "unnamed" in app
    assert 'id="app-floor-universe"' in app
    dash = public_dashboard()
    assert dash["release"] == "2.94.0"
    status = public_status()
    assert status["release"] == "2.94.0"
    assert status["website"]["universe_operable"] is True
    assert status["website"]["universe_wells_live"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_294_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.93.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.94.0" not in item
        ]

    def operable_off(cat):
        cat["programs"]["website"]["universe_operable"] = False

    def wells_live(cat):
        cat["programs"]["website"]["universe_wells_live"] = True

    def refuse_hidden(cat):
        cat["expert_review"]["success"]["client_universe"]["refuse_is_visible"] = False

    def named(cat):
        cat["expert_review"]["success"]["client_universe"]["wells"]["client_mark"] = "Acme"

    def first(cat):
        cat["expert_review"]["success"]["client_universe"]["wells"]["first_record"] = 1

    def groups(cat):
        cat["expert_review"]["success"]["client_universe"]["groups"] = []

    def hrefs(cat):
        cat["expert_review"]["success"]["client_universe"]["surfaces"][0]["href"] = "/universe"

    def site(cat):
        cat["expert_review"]["success"]["client_universe"]["site"] = "Client universe on #universe. Not a /universe route."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "operable client universe" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. The operating day is #firm. The client universe is #universe."

    for mutator in (
        release,
        closed,
        operable_off,
        wells_live,
        refuse_hidden,
        named,
        first,
        groups,
        hrefs,
        site,
        principles,
        ops,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["entity"]["release"] = "2.93.0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_294(hole, hole["plane_interface"])
    live = copy.deepcopy(edge)
    live["expert_review"]["success"]["client_universe"]["wells_are_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_294(live, live["plane_interface"])
    href_hole = copy.deepcopy(edge)
    href_hole["expert_review"]["success"]["client_universe"]["surfaces"][5]["href"] = "/client"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_294(href_hole, href_hole["plane_interface"])


def test_operable_universe_fail_closed():
    cat = copy.deepcopy(load_catalog())
    hole = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    hole["operable"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(hole)
    live = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    live["wells"]["second_record"] = 2
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(live)
    claimed = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    claimed["wells"]["maps_claimed"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(claimed)
    groups = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    groups["groups"][0]["rails"] = ["identify"]
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(groups)
    href = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    href["surfaces"][0]["href"] = "/universe"
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(href)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "honest zeros" not in item.lower()
            ]
        )
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item
        for item in ciso["ciso"]["does_not"]
        if "refuse as a live record" not in item.lower() and "wells as named records" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
