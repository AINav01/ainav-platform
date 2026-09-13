from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    INDUSTRY_DRAWER_REFUSE_IDS,
    INDUSTRY_REFUSE_TEXT,
    INDUSTRY_ROOM_1_IDS,
    INDUSTRY_ROOM_2_IDS,
    load_catalog,
    validate_catalog,
)
from ainav.buyer import success_program
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_300_complete_industry_drawer():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.28.0"
    drawer = cat["expert_review"]["success"]["industry_drawer"]
    rooms = drawer["rooms"]
    assert drawer["complete"] is True
    assert drawer["fully_operable"] is True
    assert drawer["every_refuse_clicks"] is True
    assert rooms["complete"] is True
    assert rooms["fully_operable"] is True
    assert rooms["every_refuse_clicks"] is True
    assert rooms["assigned"] is False
    assert rooms["named_vertical"] is False
    assert rooms["rooms_are_live"] is False
    assert rooms["wells"]["room_1"] == 0
    assert rooms["wells"]["room_2"] == 0
    assert {item["id"]: item["refuse_text"] for item in rooms["room_2"]} == {
        key: INDUSTRY_REFUSE_TEXT[key] for key in INDUSTRY_ROOM_2_IDS
    }
    refuse_lane = next(lane for lane in drawer["lanes"] if lane["id"] == "refuse")
    assert [item["id"] for item in refuse_lane["items"]] == INDUSTRY_DRAWER_REFUSE_IDS
    assert "complete industry drawer" in drawer["lede"].lower()
    assert "complete industry drawer" in drawer["glance"].lower()
    assert "complete industry drawer" in drawer["site"].lower()
    assert "complete industry drawer" in drawer["note"].lower()
    assert "complete industry drawer" in rooms["site"].lower()
    assert "operable industry rooms" in rooms["site"].lower()
    assert "every refuse clicks" in drawer["site"].lower()
    assert "catalog is the message" in drawer["site"].lower()
    assert "sit / maps / attach / refuse" in drawer["site"].lower()
    assert cat["programs"]["website"]["industry_complete"] is True
    assert cat["programs"]["website"]["industry_fully_operable"] is True
    assert cat["programs"]["website"]["industry_rooms_live"] is False
    assert "complete industry drawer" in cat["operations"]["note"].lower()
    assert "sku attach" in cat["operations"]["note"].lower()
    assert any(
        "3.00.0" in item and "complete" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    assert any(
        "2.99.0" in item and "fully operable" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "complete industry drawer" in principles
    assert "every refuse clicks" in principles
    assert "catalog is the message" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 98
    assert upgrades[70]["who"] == "tree"
    assert upgrades[70]["done"] is True
    assert upgrades[70]["marks_live_pin"] is False
    blob = f"{upgrades[70]['title']} {upgrades[70]['do']}".lower()
    assert "complete industry" in blob
    assert "live_pin_ok" in blob
    exported = success_program()["industry_drawer"]
    assert exported["complete"] is True
    assert exported["rooms"]["complete"] is True
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert "complete industry drawer" in html.lower()
    assert "sit / maps / attach / refuse" in html.lower()
    assert [item["id"] for item in rooms["room_1"]] == INDUSTRY_ROOM_1_IDS
    refuse_lane_html = html.split('data-lane="refuse"', 1)[1].split("</section>", 1)[0]
    assert "<a href=" not in refuse_lane_html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#industry"' not in nav
    assert 'href="#crypto"' not in nav
    assert "drawer.complete === false" in js
    assert "Complete" in app
    assert "Complete" in identify
    assert "complete industry drawer" in twin.lower()
    dash = public_dashboard()
    assert dash["release"] == "3.28.0"
    status = public_status()
    assert status["release"] == "3.28.0"
    assert status["website"]["industry_complete"] is True
    assert status["website"]["industry_fully_operable"] is True
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_300_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.99.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.00.0" not in item
        ]

    def complete_off(cat):
        cat["programs"]["website"]["industry_complete"] = False

    def rooms_live(cat):
        cat["programs"]["website"]["industry_rooms_live"] = True

    def drawer_off(cat):
        cat["expert_review"]["success"]["industry_drawer"]["complete"] = False

    def rooms_off(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["complete"] = False

    def site(cat):
        cat["expert_review"]["success"]["industry_drawer"]["site"] = (
            "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
            "Sit / maps / attach / refuse. Room 1 is books. Room 2 is refuse. "
            "Fully operable industry drawer. Every refuse clicks. Catalog is the message. "
            "Honest zeros sit the board. Refuse is visible. Not a crypto product. "
            "Not 17a-4. Not a /industry route."
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "complete industry drawer" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. The sit-down industry drawer is sit / maps / attach / refuse on #industry. "
            "Room 1 is books. Fully operable industry drawer. Every refuse clicks."
        )

    for mutator in (
        release,
        closed,
        complete_off,
        rooms_live,
        drawer_off,
        rooms_off,
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
    hole["expert_review"]["success"]["industry_drawer"]["complete"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_300(hole, hole["plane_interface"])
    closed_hole = copy.deepcopy(edge)
    closed_hole["engineering"]["closed_in_tree"] = [
        item for item in closed_hole["engineering"]["closed_in_tree"] if "3.00.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_300(closed_hole, closed_hole["plane_interface"])
    flag = copy.deepcopy(edge)
    flag["expert_review"]["success"]["industry_drawer"]["complete"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_300(flag, flag["plane_interface"])
    rooms_flag = copy.deepcopy(edge)
    rooms_flag["expert_review"]["success"]["industry_drawer"]["rooms"]["complete"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_300(rooms_flag, rooms_flag["plane_interface"])
    site_note = copy.deepcopy(edge)
    site_note["expert_review"]["success"]["industry_drawer"]["site"] = (
        "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
        "Non-compliance is #risk. First glance stays the write rail. "
        "Sit / maps / attach / refuse. Room 1 is books. Room 2 is refuse. "
        "Fully operable industry drawer. Every refuse clicks. Catalog is the message. "
        "Honest zeros sit the board. Refuse is visible. Not a crypto product. "
        "Not 17a-4. Not a /industry route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_300(site_note, site_note["plane_interface"])
    rooms_site = copy.deepcopy(edge)
    rooms_site["expert_review"]["success"]["industry_drawer"]["rooms"]["site"] = (
        "Fully operable industry rooms on #industry. Every refuse clicks. "
        "Catalog is the message. Honest zeros sit the board. Refuse is visible. "
        "Room 1 walks to #packs. Room 2 refuse stays on #industry. Not a /crypto route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_300(rooms_site, rooms_site["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "complete industry drawer" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_300(principles_hole, principles_hole["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = (
        "SKU attach chain. The sit-down industry drawer is sit / maps / attach / refuse on #industry. "
        "Fully operable. Every refuse clicks. Catalog is the message."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_300(ops_hole, ops_hole["plane_interface"])
    live = copy.deepcopy(edge)
    live["programs"]["website"]["industry_wells_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_300(live, live["plane_interface"])
    fully = copy.deepcopy(edge)
    fully["programs"]["website"]["industry_fully_operable"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_300(fully, fully["plane_interface"])


def test_industry_drawer_complete_fail_closed():
    cat = copy.deepcopy(load_catalog())
    hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    hole["complete"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(hole)
    rooms = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    rooms["rooms"]["complete"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(rooms)
    lede = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    lede["lede"] = lede["lede"].replace("Complete industry drawer.", "").replace("complete industry drawer.", "")
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(lede)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "complete industry drawer" not in item.lower()
            ]
        )
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item
        for item in ciso["ciso"]["does_not"]
        if "complete industry drawer as a live named vertical" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
    upgrade = copy.deepcopy(cat)
    by_n = {item["n"]: item for item in upgrade["expert_review"]["upgrades"]}
    by_n[70]["title"] = "Rooms"
    by_n[70]["do"] = "Ship 3.00.0. Not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_catalog(upgrade)
