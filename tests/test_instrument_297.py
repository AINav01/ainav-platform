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
    load_catalog,
    validate_catalog,
)
from ainav.buyer import success_program
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_297_sit_down_industry_rooms():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.04.0"
    drawer = cat["expert_review"]["success"]["industry_drawer"]
    rooms = drawer["rooms"]
    assert rooms["kind"] == "ainav.industry_rooms.v1"
    assert rooms["live"] is False
    assert rooms["crypto_product"] is False
    assert rooms["seventeen_a4"] is False
    assert rooms["fourth_sku"] is False
    assert rooms["lead"] == "bc.general_journal.post"
    assert [item["id"] for item in rooms["room_1"]] == INDUSTRY_ROOM_1_IDS
    assert [item["id"] for item in rooms["room_2"]] == INDUSTRY_ROOM_2_IDS
    assert {item["id"]: item["href"] for item in rooms["room_1"]} == INDUSTRY_ROOM_1_HREFS
    assert {item["id"]: item["href"] for item in rooms["room_2"]} == INDUSTRY_ROOM_2_HREFS
    assert "industry.bank" in rooms["room_1"][0]["note"].lower()
    assert "reserve journal" in " ".join(item["note"].lower() for item in rooms["room_1"])
    assert "issuing the token" in " ".join(item["note"].lower() for item in rooms["room_1"])
    assert "wallet signing" in " ".join(item["note"].lower() for item in rooms["room_2"])
    assert "room 1 is books" in drawer["lede"].lower()
    assert "not a crypto product" in drawer["lede"].lower()
    assert "not 17a-4" in drawer["lede"].lower()
    assert "room 1 is books" in drawer["site"].lower()
    assert "not a crypto product" in drawer["site"].lower()
    assert cat["programs"]["website"]["industry_rooms"] is True
    assert cat["programs"]["website"]["industry_crypto"] is False
    assert cat["programs"]["website"]["industry_seventeen_a4"] is False
    assert "room 1" in cat["operations"]["note"].lower()
    assert "#industry" in cat["operations"]["note"].lower()
    assert "sku attach" in cat["operations"]["note"].lower()
    assert any(
        "2.97.0" in item and "room" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    assert any(
        "2.96.0" in item and "sit-down" in item.lower() and "industry" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "room 1 is books" in principles
    assert "not a crypto product" in principles
    assert "not 17a-4" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 74
    assert upgrades[67]["who"] == "tree"
    assert upgrades[67]["done"] is True
    assert upgrades[67]["marks_live_pin"] is False
    blob = f"{upgrades[67]['title']} {upgrades[67]['do']}".lower()
    assert "room 1" in blob
    assert "live_pin_ok" in blob
    exported = success_program()["industry_drawer"]
    assert exported["rooms"]["live"] is False
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.04.0" in html
    assert 'id="industry-rooms"' in html
    assert 'data-room="room_1"' in html
    assert 'data-room="room_2"' in html
    assert 'id="industry-token-sku"' in html
    assert 'id="industry-seventeen-a4"' in html
    assert "Room 1 is the journal" in html
    assert "Not a crypto product" in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#industry"' not in nav
    assert 'href="#crypto"' not in nav
    assert 'href="#token"' not in nav
    assert 'href="#rwa"' not in nav
    assert "paintIndustryDrawer" in js
    assert "industry-token-sku" in js
    assert "industry-seventeen-a4" in js
    assert ".industry-rooms" in css
    assert "room 1 is books" in twin.lower()
    assert "room 2 is refuse" in twin.lower()
    assert "not a crypto product" in twin.lower()
    assert "mfa identifies" in twin.lower()
    assert "Room 1" in app
    assert "Room 2" in app
    assert "Room 1" in identify
    assert "Room 2" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.04.0"
    status = public_status()
    assert status["release"] == "3.04.0"
    assert status["website"]["industry_rooms"] is True
    assert status["website"]["industry_crypto"] is False
    assert status["website"]["industry_seventeen_a4"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_297_fail_closed():
    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.97.0" not in item
        ]

    def rooms_off(cat):
        cat["programs"]["website"]["industry_rooms"] = False

    def crypto_on(cat):
        cat["programs"]["website"]["industry_crypto"] = True

    def worm_on(cat):
        cat["programs"]["website"]["industry_seventeen_a4"] = True

    def rooms_live(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["live"] = True

    def rooms_crypto(cat):
        cat["expert_review"]["success"]["industry_drawer"]["rooms"]["crypto_product"] = True

    def site(cat):
        cat["expert_review"]["success"]["industry_drawer"]["site"] = (
            "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
            "Sit / maps / attach / refuse. Not a /industry route."
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "room 1 is books" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. The operating day is #firm. Brand is #brand. "
            "The sit-down industry drawer is sit / maps / attach / refuse on #industry."
        )

    for mutator in (
        closed,
        rooms_off,
        crypto_on,
        worm_on,
        rooms_live,
        rooms_crypto,
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
        item for item in hole["engineering"]["closed_in_tree"] if "2.97.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_297(hole, hole["plane_interface"])
    live = copy.deepcopy(edge)
    live["expert_review"]["success"]["industry_drawer"]["rooms"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_297(live, live["plane_interface"])
    empty = copy.deepcopy(edge)
    empty["expert_review"]["success"]["industry_drawer"]["rooms"]["room_1"] = []
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(empty["expert_review"]["success"]["industry_drawer"]["rooms"])
    site_note = copy.deepcopy(edge)
    site_note["expert_review"]["success"]["industry_drawer"]["site"] = (
        "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
        "Non-compliance is #risk. First glance stays the write rail. "
        "Sit / maps / attach / refuse. Not a /industry route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_297(site_note, site_note["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "room 1 is books" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_297(principles_hole, principles_hole["plane_interface"])
    worm = copy.deepcopy(edge)
    worm["expert_review"]["success"]["industry_drawer"]["rooms"]["seventeen_a4"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_297(worm, worm["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = (
        "SKU attach chain. The sit-down industry drawer is sit / maps / attach / refuse on #industry. "
        "Maps stay claimed=false. Packs are not SKUs."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_297(ops_hole, ops_hole["plane_interface"])
    href_site = copy.deepcopy(edge["expert_review"]["success"]["industry_drawer"])
    href_site["site"] = (
        "First glance stays the write rail. Sit / maps / attach / refuse. Not a /industry route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(href_site)


def test_industry_rooms_fail_closed():
    cat = copy.deepcopy(load_catalog())
    hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    hole["kind"] = "ainav.industry.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(hole)
    live = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    live["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(live)
    crypto = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    crypto["crypto_product"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(crypto)
    worm = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    worm["seventeen_a4"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(worm)
    lead = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    lead["lead"] = "token.mint"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(lead)
    named = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    named["room_1"][0]["href"] = "/crypto"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(named)
    items = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    items["room_2"] = []
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(items)
    stem = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["rooms"])
    stem["room_2"][2]["note"] = "A desk."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_rooms(stem)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "room 1 is books" not in item.lower()
            ]
        )
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item
        for item in ciso["ciso"]["does_not"]
        if "crypto product" not in item.lower()
        and "17a-4 worm" not in item.lower()
        and "room 2" not in item.lower()
        and "tokenization sku" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
    lede = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    lede["lede"] = (
        "The sit-down industry drawer is who we sit. Maps stay claimed=false. Packs are not SKUs."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(lede)
    glance = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    glance["glance"] = "Sit-down industry drawer. Not a /industry route. Not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(glance)
    note = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    note["note"] = (
        "Packs are not SKUs. Maps stay claimed=false. Non-compliance that is ours is the landed write. Not a live filing."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(note)
    refuse = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    refuse["refuse"] = [
        "Treat maps as certificates",
        "Mint packs as SKUs",
        "Invent a named vertical",
        "A /industry route",
        "Healthcare GRC product",
        "ISO certificate mill",
        "Close regulator clocks by buying L1",
        "LIVE_PIN_OK theater",
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(refuse)
    papers = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    papers["papers"][-1]["note"] = "A paper."
    papers["papers"][-2]["note"] = "A paper."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(papers)
    missing = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    missing.pop("rooms")
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(missing)
    upgrade = copy.deepcopy(cat)
    by_n = {item["n"]: item for item in upgrade["expert_review"]["upgrades"]}
    by_n[67]["do"] = "Ship 2.97.0. Not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_catalog(upgrade)
