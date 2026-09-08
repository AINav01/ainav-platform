from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    INDUSTRY_DRAWER_REFUSE_IDS,
    INDUSTRY_REFUSE_TEXT,
    INDUSTRY_ROOM_1_HREFS,
    INDUSTRY_ROOM_1_IDS,
    INDUSTRY_ROOM_2_HREFS,
    INDUSTRY_ROOM_2_IDS,
    INDUSTRY_ROOM_SPINE_STATES,
    load_catalog,
    validate_catalog,
)
from ainav.buyer import success_program
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_299_fully_operable_industry_drawer():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.12.0"
    drawer = cat["expert_review"]["success"]["industry_drawer"]
    rooms = drawer["rooms"]
    assert drawer["fully_operable"] is True
    assert drawer["every_refuse_clicks"] is True
    assert rooms["kind"] == "ainav.industry_rooms.v1"
    assert rooms["fully_operable"] is True
    assert rooms["every_refuse_clicks"] is True
    assert rooms["operable"] is True
    assert rooms["refuse_is_visible"] is True
    assert rooms["honest_zeros"] is True
    assert rooms["assigned"] is False
    assert rooms["named_vertical"] is False
    assert rooms["rooms_are_live"] is False
    assert rooms["wells_are_live"] is False
    assert rooms["live"] is False
    assert rooms["crypto_product"] is False
    assert rooms["seventeen_a4"] is False
    assert rooms["lead"] == "bc.general_journal.post"
    wells = rooms["wells"]
    assert wells["room_1"] == 0
    assert wells["room_2"] == 0
    assert wells["named"] == ""
    assert rooms["spine_states"] == INDUSTRY_ROOM_SPINE_STATES
    assert [item["id"] for item in rooms["room_1"]] == INDUSTRY_ROOM_1_IDS
    assert [item["id"] for item in rooms["room_2"]] == INDUSTRY_ROOM_2_IDS
    assert {item["id"]: item["href"] for item in rooms["room_1"]} == INDUSTRY_ROOM_1_HREFS
    assert {item["id"]: item["href"] for item in rooms["room_2"]} == INDUSTRY_ROOM_2_HREFS
    assert all(item.get("refuse") is True for item in rooms["room_2"])
    assert {item["id"]: item["refuse_text"] for item in rooms["room_2"]} == {
        key: INDUSTRY_REFUSE_TEXT[key] for key in INDUSTRY_ROOM_2_IDS
    }
    refuse_lane = next(lane for lane in drawer["lanes"] if lane["id"] == "refuse")
    assert [item["id"] for item in refuse_lane["items"]] == INDUSTRY_DRAWER_REFUSE_IDS
    assert all(item.get("refuse") is True for item in refuse_lane["items"])
    assert {item["id"]: item["refuse_text"] for item in refuse_lane["items"]} == {
        key: INDUSTRY_REFUSE_TEXT[key] for key in INDUSTRY_DRAWER_REFUSE_IDS
    }
    assert "every refuse clicks" in rooms["site"].lower()
    assert "catalog is the message" in rooms["site"].lower()
    assert "honest zeros" in rooms["site"].lower()
    assert "not a /crypto route" in rooms["site"].lower()
    assert "every refuse clicks" in drawer["lede"].lower()
    assert "catalog is the message" in drawer["lede"].lower()
    assert "every refuse clicks" in drawer["glance"].lower()
    assert "every refuse clicks" in drawer["site"].lower()
    assert "catalog is the message" in drawer["site"].lower()
    assert "every refuse clicks" in drawer["note"].lower()
    assert "catalog is the message" in drawer["note"].lower()
    assert "not a sox opinion" in drawer["note"].lower()
    assert "not a sox opinion" not in drawer["site"].lower()
    assert cat["programs"]["website"]["industry_fully_operable"] is True
    assert cat["programs"]["website"]["industry_operable"] is True
    assert cat["programs"]["website"]["industry_rooms_live"] is False
    assert cat["programs"]["website"]["industry_wells_live"] is False
    assert "every refuse clicks" in cat["operations"]["note"].lower()
    assert "catalog is the message" in cat["operations"]["note"].lower()
    assert "sku attach" in cat["operations"]["note"].lower()
    assert "#industry" in cat["operations"]["note"].lower()
    assert any(
        "2.99.0" in item and "fully operable" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    assert any(
        "2.98.0" in item and "operable" in item.lower() and "room" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "fully operable industry drawer" in principles
    assert "every refuse clicks" in principles
    assert "catalog is the message" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 82
    assert upgrades[69]["who"] == "tree"
    assert upgrades[69]["done"] is True
    assert upgrades[69]["marks_live_pin"] is False
    blob = f"{upgrades[69]['title']} {upgrades[69]['do']}".lower()
    assert "every refuse" in blob
    assert "live_pin_ok" in blob
    exported = success_program()["industry_drawer"]
    assert exported["fully_operable"] is True
    assert exported["every_refuse_clicks"] is True
    assert exported["rooms"]["fully_operable"] is True
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.12.0" in html
    assert 'id="industry-zeros"' in html
    assert 'id="industry-second"' in html
    assert "Room 2 records" in html
    assert 'id="industry-room-spine"' in html
    assert 'id="industry-rooms"' in html
    assert 'data-room="room_1"' in html
    assert 'data-room="room_2"' in html
    assert 'data-room-refuse="grc_product"' in html
    assert 'data-room-refuse="cert_mill"' in html
    assert 'data-room-refuse="pack_sku"' in html
    assert 'data-room-refuse="industry_route"' in html
    assert 'data-room-refuse="named_vertical"' in html
    assert 'data-room-refuse="stablecoin_mint"' in html
    assert 'data-refuse-text="Refused. Not a GRC product. Maps stay claimed=false."' in html
    assert 'data-refuse-text="Refused. Not a stablecoin SKU. Room 2 is refuse."' in html
    assert html.count("<button type=\"button\" class=\"ghost room-refuse\"") >= 10
    refuse_lane = html.split('data-lane="refuse"', 1)[1].split("</section>", 1)[0]
    assert "<a href=" not in refuse_lane
    assert "every refuse clicks" in html.lower()
    assert "catalog is the message" in html.lower()
    status = html.split('id="industry-status"', 1)[1].split("</p>", 1)[0].lower()
    assert "every refuse clicks" in status
    assert "catalog is the message" in status
    assert "sox opinion" not in status
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#industry"' not in nav
    assert 'href="#crypto"' not in nav
    assert "paintIndustryDrawer" in js
    assert "refuseIndustry" in js
    assert "bindIndustryRoomRefuses" in js
    assert 'bindIndustryRoomRefuses(document.getElementById("industry-day"))' in js
    assert "data-refuse-text" in js
    assert "industry-second" in js
    assert "every_refuse_clicks" in js
    assert "drawer.site || \"\"" in js
    assert ".industry-day [data-lane=\"refuse\"] button.room-refuse" in css
    assert "every refuse clicks" in twin.lower()
    assert "catalog is the message" in twin.lower()
    assert "Every refuse" in app
    assert "the message" in app
    assert "Every refuse" in identify
    assert "the message" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.12.0"
    exported_status = public_status()
    assert exported_status["release"] == "3.12.0"
    assert exported_status["website"]["industry_fully_operable"] is True
    assert exported_status["website"]["industry_operable"] is True
    assert exported_status["website"]["industry_rooms_live"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_299_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.98.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.99.0" not in item
        ]

    def fully_off(cat):
        cat["programs"]["website"]["industry_fully_operable"] = False

    def rooms_live(cat):
        cat["programs"]["website"]["industry_rooms_live"] = True

    def wells_live(cat):
        cat["programs"]["website"]["industry_wells_live"] = True

    def drawer_off(cat):
        cat["expert_review"]["success"]["industry_drawer"]["fully_operable"] = False

    def clicks_off(cat):
        cat["expert_review"]["success"]["industry_drawer"]["every_refuse_clicks"] = False

    def rooms_off(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["fully_operable"] = False

    def rooms_clicks_off(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["every_refuse_clicks"] = False

    def assigned(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["assigned"] = True

    def named(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["wells"]["named"] = "BankCo"

    def first(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["wells"]["room_1"] = 1

    def second(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["wells"]["room_2"] = 1

    def site(cat):
        cat["expert_review"]["success"]["industry_drawer"]["site"] = (
            "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
            "Sit / maps / attach / refuse. Room 1 is books. Room 2 is refuse. "
            "Honest zeros sit the board. Refuse is visible. Not a crypto product. "
            "Not 17a-4. Not a /industry route."
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "fully operable industry drawer" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. The operating day is #firm. Brand is #brand. "
            "The sit-down industry drawer is sit / maps / attach / refuse on #industry. "
            "Room 1 is books. Honest zeros. Refuse is visible."
        )

    def refuse_text(cat):
        cat["expert_review"]["success"]["industry_drawer"]["lanes"][-1]["items"][0]["refuse_text"] = "Nope."

    for mutator in (
        release,
        closed,
        fully_off,
        rooms_live,
        wells_live,
        drawer_off,
        clicks_off,
        rooms_off,
        rooms_clicks_off,
        assigned,
        named,
        first,
        second,
        site,
        principles,
        ops,
        refuse_text,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["engineering"]["closed_in_tree"] = [
        item for item in hole["engineering"]["closed_in_tree"] if "2.99.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(hole, hole["plane_interface"])
    live = copy.deepcopy(edge)
    live["programs"]["website"]["industry_rooms_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(live, live["plane_interface"])
    wells = copy.deepcopy(edge)
    wells["expert_review"]["success"]["industry_drawer"]["rooms"]["wells"]["room_2"] = 1
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(wells["expert_review"]["success"]["industry_drawer"]["rooms"])
    site_note = copy.deepcopy(edge)
    site_note["expert_review"]["success"]["industry_drawer"]["site"] = (
        "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
        "Non-compliance is #risk. First glance stays the write rail. "
        "Sit / maps / attach / refuse. Room 1 is books. Room 2 is refuse. "
        "Honest zeros sit the board. Refuse is visible. Not a crypto product. "
        "Not 17a-4. Not a /industry route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(site_note, site_note["plane_interface"])
    rooms_site = copy.deepcopy(edge)
    rooms_site["expert_review"]["success"]["industry_drawer"]["rooms"]["site"] = (
        "Operable industry rooms on #industry. Honest zeros sit the board. "
        "Refuse is visible. Room 1 walks to #packs. Room 2 refuse stays on #industry. "
        "Not a /crypto route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(rooms_site, rooms_site["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "fully operable industry drawer" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(principles_hole, principles_hole["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = (
        "SKU attach chain. The sit-down industry drawer is sit / maps / attach / refuse on #industry. "
        "Room 1 is books. Maps stay claimed=false. Packs are not SKUs. Honest zeros."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(ops_hole, ops_hole["plane_interface"])
    closed_hole = copy.deepcopy(edge)
    closed_hole["engineering"]["closed_in_tree"] = [
        item for item in closed_hole["engineering"]["closed_in_tree"] if "2.99.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(closed_hole, closed_hole["plane_interface"])
    text_hole = copy.deepcopy(edge)
    text_hole["expert_review"]["success"]["industry_drawer"]["lanes"][-1]["items"][0]["refuse_text"] = "Refused."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(text_hole, text_hole["plane_interface"])
    room_text = copy.deepcopy(edge)
    room_text["expert_review"]["success"]["industry_drawer"]["rooms"]["room_2"][0]["refuse_text"] = "Refused."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(room_text, room_text["plane_interface"])
    operable = copy.deepcopy(edge)
    operable["programs"]["website"]["industry_operable"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(operable, operable["plane_interface"])
    wells_flag = copy.deepcopy(edge)
    wells_flag["programs"]["website"]["industry_wells_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(wells_flag, wells_flag["plane_interface"])
    drawer_flag = copy.deepcopy(edge)
    drawer_flag["expert_review"]["success"]["industry_drawer"]["fully_operable"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(drawer_flag, drawer_flag["plane_interface"])
    clicks_flag = copy.deepcopy(edge)
    clicks_flag["expert_review"]["success"]["industry_drawer"]["every_refuse_clicks"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(clicks_flag, clicks_flag["plane_interface"])
    rooms_flag = copy.deepcopy(edge)
    rooms_flag["expert_review"]["success"]["industry_drawer"]["rooms"]["fully_operable"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(rooms_flag, rooms_flag["plane_interface"])
    rooms_clicks = copy.deepcopy(edge)
    rooms_clicks["expert_review"]["success"]["industry_drawer"]["rooms"]["every_refuse_clicks"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_299(rooms_clicks, rooms_clicks["plane_interface"])


def test_industry_drawer_fully_operable_fail_closed():
    cat = copy.deepcopy(load_catalog())
    hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    hole["fully_operable"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(hole)
    clicks = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    clicks["every_refuse_clicks"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(clicks)
    rooms = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    rooms["rooms"]["fully_operable"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(rooms)
    rooms_clicks = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    rooms_clicks["rooms"]["every_refuse_clicks"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(rooms_clicks)
    refuse = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    refuse["lanes"][-1]["items"][0]["refuse"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(refuse)
    text = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    text["lanes"][-1]["items"][2]["refuse_text"] = "Refused. Something else."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(text)
    room_text = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    room_text["room_2"][1]["refuse_text"] = "Refused. Something else."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(room_text)
    site = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    site["site"] = (
        "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
        "Non-compliance is #risk. First glance stays the write rail. "
        "Sit / maps / attach / refuse. Room 1 is books. Room 2 is refuse. "
        "Honest zeros sit the board. Refuse is visible. Not a crypto product. "
        "Not 17a-4. Not a /industry route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(site)
    lede = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    lede["lede"] = (
        "The sit-down industry drawer is who we sit. Maps stay claimed=false. Packs are not SKUs. "
        "Room 1 is books. Room 2 is refuse. Not a crypto product. Honest zeros. Refuse is visible."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(lede)
    glance = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    glance["glance"] = (
        "Sit-down industry drawer. Room 1 is books. Room 2 is refuse. "
        "Honest zeros. Refuse is visible. Not a /industry route. Not a crypto product. Not LIVE_PIN_OK."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(glance)
    note = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    note["note"] = (
        "Packs are not SKUs. Maps stay claimed=false. Non-compliance that is ours is the landed write. "
        "Room 1 is books. Room 2 is refuse. Honest zeros. Refuse is visible. "
        "Not a crypto product. Not 17a-4. Not a live filing."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(note)
    rooms_site = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    rooms_site["site"] = (
        "Operable industry rooms on #industry. Honest zeros sit the board. "
        "Refuse is visible. Room 1 walks to #packs. Room 2 refuse stays on #industry. "
        "Not a /crypto route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(rooms_site)
    zeros_site = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    zeros_site["site"] = (
        "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
        "Non-compliance is #risk. First glance stays the write rail. "
        "Sit / maps / attach / refuse. Room 1 is books. Room 2 is refuse. "
        "Fully operable industry drawer. Every refuse clicks. Catalog is the message. "
        "Not a crypto product. Not 17a-4. Not a /industry route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(zeros_site)
    packs_site = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    packs_site["site"] = (
        "Fully operable industry rooms on #industry. Every refuse clicks. "
        "Catalog is the message. Honest zeros sit the board. Refuse is visible. "
        "Room 1 walks. Room 2 refuse stays. Room 2 records stay 0."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(packs_site)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "fully operable industry drawer" not in item.lower()
            ]
        )
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item
        for item in ciso["ciso"]["does_not"]
        if "refuse lane walk as a live route" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
    upgrade = copy.deepcopy(cat)
    upgrade["expert_review"]["upgrades"][-1]["title"] = "Rooms"
    upgrade["expert_review"]["upgrades"][-1]["do"] = "Ship 2.99.0. Not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_catalog(upgrade)
