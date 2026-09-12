from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
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


def test_release_is_298_operable_industry_rooms():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.22.0"
    drawer = cat["expert_review"]["success"]["industry_drawer"]
    rooms = drawer["rooms"]
    assert rooms["kind"] == "ainav.industry_rooms.v1"
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
    assert "honest zeros" in rooms["site"].lower()
    assert "refuse is visible" in rooms["site"].lower()
    assert "not a /crypto route" in rooms["site"].lower()
    assert "honest zeros" in drawer["site"].lower()
    assert "refuse is visible" in drawer["site"].lower()
    assert cat["programs"]["website"]["industry_operable"] is True
    assert cat["programs"]["website"]["industry_rooms_live"] is False
    assert cat["programs"]["website"]["industry_wells_live"] is False
    assert "honest zeros" in cat["operations"]["note"].lower()
    assert "operable industry rooms" in cat["operations"]["note"].lower()
    assert "#industry" in cat["operations"]["note"].lower()
    assert "room 1" in cat["operations"]["note"].lower()
    assert "sku attach" in cat["operations"]["note"].lower()
    assert any(
        "2.98.0" in item and "operable" in item.lower() and "room" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    assert any(
        "2.97.0" in item and "room" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "operable industry rooms" in principles
    assert "honest zeros" in principles
    assert "refuse is visible" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 92
    assert upgrades[68]["who"] == "tree"
    assert upgrades[68]["done"] is True
    assert upgrades[68]["marks_live_pin"] is False
    blob = f"{upgrades[68]['title']} {upgrades[68]['do']}".lower()
    assert "operable industry" in blob
    assert "live_pin_ok" in blob
    exported = success_program()["industry_drawer"]
    assert exported["rooms"]["operable"] is True
    assert exported["rooms"]["rooms_are_live"] is False
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert 'id="industry-zeros"' in html
    assert 'id="industry-room-spine"' in html
    assert 'id="industry-rooms"' in html
    assert 'data-room="room_1"' in html
    assert 'data-room="room_2"' in html
    assert 'data-spine="room_1"' in html
    assert 'data-spine="room_2"' in html
    assert 'data-spine="after_l1"' in html
    assert 'data-room-refuse="stablecoin_mint"' in html
    assert 'data-room-refuse="rwa_issue"' in html
    assert 'data-room-refuse="crypto_ams"' in html
    assert 'data-room-refuse="wallet"' in html
    assert 'data-room-refuse="seventeen_a4"' in html
    assert 'id="industry-spine-room-2"' in html
    assert html.count("<button type=\"button\" class=\"ghost room-refuse\"") >= 5
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#industry"' not in nav
    assert 'href="#crypto"' not in nav
    assert "paintIndustryDrawer" in js
    assert "refuseIndustry" in js
    assert "ROOM_2_REFUSE" in js
    assert "bindIndustryRoomRefuses" in js
    assert "industry-assigned" in js
    assert "industry-room-spine" in js
    assert ".room-refuse" in css
    assert "#industry-room-spine" in css
    assert "honest zeros" in twin.lower()
    assert "refuse is visible" in twin.lower()
    assert "Honest zeros" in app
    assert "Refuse" in app
    assert "Honest zeros" in identify
    assert "Refuse" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.22.0"
    status = public_status()
    assert status["release"] == "3.22.0"
    assert status["website"]["industry_operable"] is True
    assert status["website"]["industry_rooms_live"] is False
    assert status["website"]["industry_wells_live"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_298_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.97.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.98.0" not in item
        ]

    def operable_off(cat):
        cat["programs"]["website"]["industry_operable"] = False

    def rooms_live(cat):
        cat["programs"]["website"]["industry_rooms_live"] = True

    def wells_live(cat):
        cat["programs"]["website"]["industry_wells_live"] = True

    def refuse_hidden(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["refuse_is_visible"] = False

    def rooms_operable_off(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["operable"] = False

    def assigned(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["assigned"] = True

    def named(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["wells"]["named"] = "BankCo"

    def first(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["wells"]["room_1"] = 1

    def site(cat):
        cat["expert_review"]["success"]["industry_drawer"]["site"] = (
            "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
            "Sit / maps / attach / refuse. Room 1 is books. Room 2 is refuse. "
            "Not a crypto product. Not 17a-4. Not a /industry route."
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "operable industry rooms" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. The operating day is #firm. Brand is #brand. "
            "The sit-down industry drawer is sit / maps / attach / refuse on #industry. Room 1 is books."
        )

    for mutator in (
        release,
        closed,
        operable_off,
        rooms_live,
        wells_live,
        refuse_hidden,
        rooms_operable_off,
        assigned,
        named,
        first,
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
    hole["engineering"]["closed_in_tree"] = [
        item for item in hole["engineering"]["closed_in_tree"] if "2.98.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(hole, hole["plane_interface"])
    live = copy.deepcopy(edge)
    live["expert_review"]["success"]["industry_drawer"]["rooms"]["rooms_are_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(live, live["plane_interface"])
    wells = copy.deepcopy(edge)
    wells["expert_review"]["success"]["industry_drawer"]["rooms"]["wells"]["room_2"] = 1
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(wells, wells["plane_interface"])
    spine = copy.deepcopy(edge)
    spine["expert_review"]["success"]["industry_drawer"]["rooms"]["spine_states"]["room_2"] = "ready"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(spine, spine["plane_interface"])
    site_note = copy.deepcopy(edge)
    site_note["expert_review"]["success"]["industry_drawer"]["site"] = (
        "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
        "Non-compliance is #risk. First glance stays the write rail. "
        "Sit / maps / attach / refuse. Room 1 is books. Room 2 is refuse. "
        "Not a crypto product. Not 17a-4. Not a /industry route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(site_note, site_note["plane_interface"])
    rooms_site = copy.deepcopy(edge)
    rooms_site["expert_review"]["success"]["industry_drawer"]["rooms"]["site"] = (
        "Industry rooms on #industry. Room 1 walks to #packs. Room 2 stays on #industry."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(rooms_site, rooms_site["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "operable industry rooms" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(principles_hole, principles_hole["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = (
        "SKU attach chain. The sit-down industry drawer is sit / maps / attach / refuse on #industry. "
        "Room 1 is books. Maps stay claimed=false. Packs are not SKUs."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(ops_hole, ops_hole["plane_interface"])
    closed_hole = copy.deepcopy(edge)
    closed_hole["engineering"]["closed_in_tree"] = [
        item for item in closed_hole["engineering"]["closed_in_tree"] if "2.98.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(closed_hole, closed_hole["plane_interface"])
    visible = copy.deepcopy(edge)
    visible["expert_review"]["success"]["industry_drawer"]["rooms"]["refuse_is_visible"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(visible, visible["plane_interface"])
    zeros = copy.deepcopy(edge)
    zeros["expert_review"]["success"]["industry_drawer"]["rooms"]["honest_zeros"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(zeros, zeros["plane_interface"])
    ops_room = copy.deepcopy(edge)
    ops_room["operations"]["note"] = (
        "SKU attach chain. The sit-down industry drawer is sit / maps / attach / refuse on #industry. "
        "Honest zeros. Operable industry rooms. Maps stay claimed=false. Packs are not SKUs."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_298(ops_room, ops_room["plane_interface"])


def test_industry_rooms_operable_fail_closed():
    cat = copy.deepcopy(load_catalog())
    hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    hole["operable"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(hole)
    hidden = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    hidden["refuse_is_visible"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(hidden)
    zeros = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    zeros["honest_zeros"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(zeros)
    assigned = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    assigned["assigned"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(assigned)
    named = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    named["named_vertical"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(named)
    live = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    live["rooms_are_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(live)
    wells_live = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    wells_live["wells_are_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(wells_live)
    wells = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    wells["wells"]["named"] = "Acme Bank"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(wells)
    count = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    count["wells"]["room_1"] = 1
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(count)
    spine = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    spine["spine_states"] = {"room_1": "ready", "room_2": "ready", "after_l1": "after_l1"}
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(spine)
    refuse = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    refuse["room_2"][0]["refuse"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(refuse)
    site = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    site["site"] = "Industry rooms on #industry. Room 1 walks to #packs."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(site)
    crypto = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    crypto["site"] = (
        "Operable industry rooms on #industry. Honest zeros sit the board. "
        "Refuse is visible. Room 1 walks to #packs. Room 2 refuse stays on #industry."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(crypto)
    wells_shape = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    wells_shape["wells"] = "named"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(wells_shape)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "operable industry rooms" not in item.lower()
            ]
        )
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item
        for item in ciso["ciso"]["does_not"]
        if "room 2 refuse as a live record" not in item.lower()
        and "room 1 wells as named records" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
    lede = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    lede["lede"] = (
        "The sit-down industry drawer is who we sit. Maps stay claimed=false. Packs are not SKUs. "
        "Room 1 is books. Room 2 is refuse. Not a crypto product. Not 17a-4."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(lede)
    glance = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    glance["glance"] = (
        "Sit-down industry drawer. Room 1 is books. Room 2 is refuse. "
        "Not a /industry route. Not a crypto product. Not LIVE_PIN_OK."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(glance)
    note = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    note["note"] = (
        "Packs are not SKUs. Maps stay claimed=false. Non-compliance that is ours is the landed write. "
        "Room 1 is books. Room 2 is refuse. Not a crypto product. Not 17a-4. Not a live filing."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(note)
    upgrade = copy.deepcopy(cat)
    upgrade["expert_review"]["upgrades"][-1]["title"] = "Rooms"
    upgrade["expert_review"]["upgrades"][-1]["do"] = "Ship 2.98.0. Not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_catalog(upgrade)
