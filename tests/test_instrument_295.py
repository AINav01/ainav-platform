from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    CLIENT_UNIVERSE_DAY_HREFS,
    CLIENT_UNIVERSE_DAY_LANE_IDS,
    CLIENT_UNIVERSE_SPINE_STATES,
    load_catalog,
    validate_catalog,
)
from ainav.buyer import success_program
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_295_sit_down_day():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.26.0"
    universe = cat["expert_review"]["success"]["client_universe"]
    assert universe["sit_down"] is True
    assert universe["day_is_live"] is False
    assert universe["day_invented"] is False
    assert universe["spine_states"] == CLIENT_UNIVERSE_SPINE_STATES
    day = universe["day"]
    assert day["kind"] == "ainav.client_universe_day.v1"
    assert day["live"] is False
    assert day["invented"] is False
    assert [item["id"] for item in day["lanes"]] == CLIENT_UNIVERSE_DAY_LANE_IDS
    hrefs = {
        row["id"]: row["href"]
        for lane in day["lanes"]
        for row in lane["items"]
    }
    assert hrefs == CLIENT_UNIVERSE_DAY_HREFS
    assert "sit-down client day" in universe["site"].lower()
    assert "now / next / after l1" in universe["site"].lower()
    assert cat["programs"]["website"]["universe_sit_down"] is True
    assert cat["programs"]["website"]["universe_day_live"] is False
    assert "sit-down client day" in cat["operations"]["note"].lower()
    assert any(
        "2.95.0" in item and "sit-down" in item.lower() and "day" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "sit-down client day" in principles
    assert "now is recorded" in principles
    assert "not a live named day" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 96
    assert upgrades[65]["who"] == "tree"
    assert upgrades[65]["done"] is True
    assert upgrades[65]["marks_live_pin"] is False
    blob = f"{upgrades[65]['title']} {upgrades[65]['do']}".lower()
    assert "sit-down" in blob
    assert "live_pin_ok" in blob
    exported = success_program()["client_universe"]
    assert exported["day"]["live"] is False
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert 'id="universe-day"' in html
    assert 'data-lane="now"' in html
    assert 'data-lane="next"' in html
    assert 'data-lane="after_l1"' in html
    assert 'data-lane="blocked"' in html
    assert 'data-state="ready"' in html
    assert 'data-state="owner_only"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#universe"' not in nav
    assert "universe-day" in js
    assert "spine_states" in js
    assert ".universe-day" in css
    assert "sit-down day" in twin.lower()
    assert "now mailbox" in twin.lower() or "now mailbox recorded" in twin.lower()
    assert "After L1 <b>unnamed</b>" in app or "unnamed" in app
    assert 'id="identify-day"' in identify
    dash = public_dashboard()
    assert dash["release"] == "3.26.0"
    status = public_status()
    assert status["release"] == "3.26.0"
    assert status["website"]["universe_sit_down"] is True
    assert status["website"]["universe_day_live"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_295_fail_closed():
    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.95.0" not in item
        ]

    def sit_off(cat):
        cat["programs"]["website"]["universe_sit_down"] = False

    def day_live(cat):
        cat["programs"]["website"]["universe_day_live"] = True

    def invented(cat):
        cat["expert_review"]["success"]["client_universe"]["day_invented"] = True

    def lanes(cat):
        cat["expert_review"]["success"]["client_universe"]["day"]["lanes"] = []

    def site(cat):
        cat["expert_review"]["success"]["client_universe"]["site"] = (
            "Client universe on #universe. Honest zeros. Refuse is visible. Not a /universe route."
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "sit-down client day" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. The operating day is #firm. Brand is #brand. "
            "The client universe is #universe. Honest zeros sit the board."
        )

    for mutator in (closed, sit_off, day_live, invented, lanes, site, principles, ops):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["engineering"]["closed_in_tree"] = [
        item for item in hole["engineering"]["closed_in_tree"] if "2.95.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_295(hole, hole["plane_interface"])
    live = copy.deepcopy(edge)
    live["expert_review"]["success"]["client_universe"]["day"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_295(live, live["plane_interface"])
    spine = copy.deepcopy(edge)
    spine["expert_review"]["success"]["client_universe"]["spine_states"]["admit"] = "ready"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_295(spine, spine["plane_interface"])
    sit = copy.deepcopy(edge)
    sit["expert_review"]["success"]["client_universe"]["sit_down"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_295(sit, sit["plane_interface"])
    empty = copy.deepcopy(edge)
    empty["expert_review"]["success"]["client_universe"]["day"]["lanes"] = []
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_295(empty, empty["plane_interface"])
    site_note = copy.deepcopy(edge)
    site_note["expert_review"]["success"]["client_universe"]["site"] = (
        "Client universe on #universe. Close is #path. Twin is #twin. Brand is #brand. "
        "Firm is #firm. First glance stays the write rail. Honest zeros. Refuse is visible. Not a /universe route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_295(site_note, site_note["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "sit-down client day" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_295(principles_hole, principles_hole["plane_interface"])


def test_sit_down_day_fail_closed():
    cat = copy.deepcopy(load_catalog())
    hole = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    hole["sit_down"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(hole)
    live = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    live["day_is_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(live)
    day = copy.deepcopy(cat["expert_review"]["success"]["client_universe"]["day"])
    day["invented"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe_day(day)
    named = copy.deepcopy(cat["expert_review"]["success"]["client_universe"]["day"])
    named["lanes"][0]["items"][0]["href"] = "/acme"
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe_day(named)
    site = copy.deepcopy(cat["expert_review"]["success"]["client_universe"])
    site["site"] = (
        "Client universe on #universe. Close is #path. Twin is #twin. Brand is #brand. "
        "Firm is #firm. First glance stays the write rail. Honest zeros. Refuse is visible. Not a /universe route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe(site)
    day_note = copy.deepcopy(cat["expert_review"]["success"]["client_universe"]["day"])
    day_note["note"] = "A day board."
    with pytest.raises(IntegrityError):
        catmod._validate_client_universe_day(day_note)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "sit-down client day" not in item.lower()
            ]
        )
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item
        for item in ciso["ciso"]["does_not"]
        if "sit-down day as a live named day" not in item.lower()
        and "seat b click on the day board" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
