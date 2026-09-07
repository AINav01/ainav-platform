from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    INDUSTRY_CONTROL_LANE_IDS,
    INDUSTRY_CONTROL_REFUSE_IDS,
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


def test_release_is_301_honest_control():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.04.0"
    drawer = cat["expert_review"]["success"]["industry_drawer"]
    control = drawer["control"]
    rooms = drawer["rooms"]
    assert drawer["honest_control"] is True
    assert drawer["complete"] is True
    assert drawer["fully_operable"] is True
    assert drawer["every_refuse_clicks"] is True
    assert control["kind"] == "ainav.industry_control.v1"
    assert control["honest"] is True
    assert control["every_refuse_clicks"] is True
    assert control["claimed"] is False
    assert control["genius_closed"] is False
    assert control["clarity_closed"] is False
    assert control["governess"] is False
    assert control["control_is_live"] is False
    assert [lane["id"] for lane in control["lanes"]] == INDUSTRY_CONTROL_LANE_IDS
    refuse_lane = next(lane for lane in control["lanes"] if lane["id"] == "refuse")
    assert [item["id"] for item in refuse_lane["items"]] == INDUSTRY_CONTROL_REFUSE_IDS
    assert {item["id"]: item["refuse_text"] for item in refuse_lane["items"]} == {
        key: INDUSTRY_REFUSE_TEXT[key] for key in INDUSTRY_CONTROL_REFUSE_IDS
    }
    assert "honest control" in drawer["lede"].lower()
    assert "honest control" in drawer["glance"].lower()
    assert "honest control" in drawer["site"].lower()
    assert "honest control" in drawer["note"].lower()
    assert "if you don't have it" in control["lede"].lower()
    assert "not ai governess" in control["lede"].lower()
    assert "genius" in drawer["site"].lower()
    assert "clarity" in drawer["site"].lower()
    assert rooms["complete"] is True
    assert rooms["rooms_are_live"] is False
    assert rooms["wells"]["room_1"] == 0
    assert rooms["wells"]["room_2"] == 0
    assert [item["id"] for item in rooms["room_1"]] == INDUSTRY_ROOM_1_IDS
    assert [item["id"] for item in rooms["room_2"]] == INDUSTRY_ROOM_2_IDS
    maps = {item["id"] for item in cat["governance"]["maps"]}
    assert "genius.act" in maps
    assert "clarity.act" in maps
    assert all(item["claimed"] is False for item in cat["governance"]["maps"])
    assert cat["programs"]["website"]["industry_control"] is True
    assert cat["programs"]["website"]["industry_honest"] is True
    assert cat["programs"]["website"]["industry_control_live"] is False
    assert cat["programs"]["website"]["industry_rooms_live"] is False
    assert "honest control" in cat["operations"]["note"].lower()
    assert any("3.01.0" in item and "honest control" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.00.0" in item and "complete" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest control" in principles
    assert "if you don't have it" in principles
    assert "company policy is not a sku" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 74
    assert upgrades[71]["who"] == "tree"
    assert upgrades[71]["done"] is True
    assert upgrades[71]["marks_live_pin"] is False
    blob = f"{upgrades[71]['title']} {upgrades[71]['do']}".lower()
    assert "honest control" in blob
    assert "live_pin_ok" in blob
    exported = success_program()["industry_drawer"]
    assert exported["honest_control"] is True
    assert exported["control"]["honest"] is True
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.04.0" in html
    assert "honest control" in html.lower()
    assert "if you don't have it" in html.lower()
    assert "genius act" in html.lower()
    assert "clarity act" in html.lower()
    assert "not ai governess" in html.lower() or "not ai governess" in html.lower()
    refuse_lane_html = html.split('data-lane="refuse"', 1)[1].split("</section>", 1)[0]
    assert "<a href=" not in refuse_lane_html
    control_html = html.split('id="industry-control"', 1)[1].split('id="industry-room-spine"', 1)[0]
    assert 'data-room-refuse="genius_close"' in control_html
    assert 'data-room-refuse="fear_first_glance"' in control_html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#industry"' not in nav
    assert 'href="#fear"' not in nav
    assert 'href="#risk"' not in nav
    assert "drawer.honest_control === false" in js
    assert "bindIndustryRoomRefuses(document.getElementById(\"industry-control\"))" in js
    assert "Honest" in app
    assert "Honest" in identify
    assert "honest control" in twin.lower()
    dash = public_dashboard()
    assert dash["release"] == "3.04.0"
    status = public_status()
    assert status["release"] == "3.04.0"
    assert status["website"]["industry_control"] is True
    assert status["website"]["industry_honest"] is True
    assert status["website"]["industry_control_live"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_301_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.00.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.01.0" not in item
        ]

    def control_off(cat):
        cat["programs"]["website"]["industry_control"] = False

    def live(cat):
        cat["programs"]["website"]["industry_control_live"] = True

    def honest_off(cat):
        cat["expert_review"]["success"]["industry_drawer"]["honest_control"] = False

    def control_live(cat):
        cat["expert_review"]["success"]["industry_drawer"]["control"]["control_is_live"] = True

    def site(cat):
        cat["expert_review"]["success"]["industry_drawer"]["site"] = (
            "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
            "Sit / maps / attach / refuse. Room 1 is books. Room 2 is refuse. "
            "Complete industry drawer. Every refuse clicks. Catalog is the message."
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest control" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. The sit-down industry drawer is sit / maps / attach / refuse on #industry. "
            "Complete industry drawer. Every refuse clicks."
        )

    for mutator in (
        release,
        closed,
        control_off,
        live,
        honest_off,
        control_live,
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
    hole["expert_review"]["success"]["industry_drawer"]["honest_control"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_301(hole, hole["plane_interface"])
    closed_hole = copy.deepcopy(edge)
    closed_hole["engineering"]["closed_in_tree"] = [
        item for item in closed_hole["engineering"]["closed_in_tree"] if "3.01.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_301(closed_hole, closed_hole["plane_interface"])
    flag = copy.deepcopy(edge)
    flag["expert_review"]["success"]["industry_drawer"]["honest_control"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_301(flag, flag["plane_interface"])
    live_flag = copy.deepcopy(edge)
    live_flag["expert_review"]["success"]["industry_drawer"]["control"]["genius_closed"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_301(live_flag, live_flag["plane_interface"])
    site_note = copy.deepcopy(edge)
    site_note["expert_review"]["success"]["industry_drawer"]["site"] = (
        "Industry drawer on #industry. Packs is #packs. Maps is #governance. "
        "Complete industry drawer. Every refuse clicks. Catalog is the message."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_301(site_note, site_note["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "honest control" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_301(principles_hole, principles_hole["plane_interface"])
    maps = copy.deepcopy(edge)
    maps["governance"]["maps"] = [
        item for item in maps["governance"]["maps"] if item.get("id") not in {"genius.act", "clarity.act"}
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_301(maps, maps["plane_interface"])


def test_industry_control_fail_closed():
    cat = copy.deepcopy(load_catalog())
    hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    hole["honest"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(hole)
    claimed = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    claimed["claimed"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(claimed)
    governess = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    governess["governess"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(governess)
    lede = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    lede["lede"] = lede["lede"].replace("Honest control", "").replace("honest control", "")
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(lede)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "honest control" not in item.lower()
            ]
        )
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item
        for item in ciso["ciso"]["does_not"]
        if "honest control board as a live filing" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
    upgrade = copy.deepcopy(cat)
    upgrade["expert_review"]["upgrades"][-1]["title"] = "Rooms"
    upgrade["expert_review"]["upgrades"][-1]["do"] = "Ship 3.01.0. Not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        validate_catalog(upgrade)
    principles_policy = copy.deepcopy(cat["expert_review"]["first_principles"])
    principles_policy = [
        item.replace("Company policy is not a SKU.", "Doctrine stays catalog law.").replace(
            "Not AI Governess.", "Not a fourth name."
        )
        for item in principles_policy
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_policy)
    for missing in (
        "Treat GENIUS or CLARITY as closed",
        "Treat fear as the first glance",
        "Treat company policy as a SKU",
        "Call the product AI Governess",
    ):
        ciso_hole = copy.deepcopy(cat["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
    drawer = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    drawer["refuse"] = [item for item in drawer["refuse"] if "GENIUS" not in item and "CLARITY" not in item]
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(drawer)
    for field in ("lede", "glance", "note"):
        field_hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
        field_hole[field] = field_hole[field].replace("Honest control", "Control").replace("honest control", "control")
        with pytest.raises(IntegrityError):
            catmod._validate_industry_drawer(field_hole)
    control = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    control["lede"] = control["lede"].replace("If you don't have it", "If it is missing")
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(control)
    governess_lede = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    governess_lede["lede"] = governess_lede["lede"].replace("Not AI Governess.", "Not another name.")
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(governess_lede)
    note_hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    note_hole["note"] = note_hole["note"].replace("claimed=false", "mapped")
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(note_hole)
    for flag in ("sku", "dno", "clarity_closed", "policy_sku", "fear_brand", "launch"):
        flag_hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
        flag_hole[flag] = True
        with pytest.raises(IntegrityError):
            catmod._validate_industry_control(flag_hole)
    kind_hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    kind_hole["kind"] = "ainav.industry_rooms.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(kind_hole)
    lanes_hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    lanes_hole["lanes"] = lanes_hole["lanes"][1:]
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(lanes_hole)
    href_hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    href_hole["lanes"][0]["items"][0]["href"] = "/fear"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(href_hole)
    stem_hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    stem_hole["lanes"][0]["items"][0]["note"] = "Missing the plane."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(stem_hole)
    kind_301 = copy.deepcopy(cat)
    kind_301["expert_review"]["success"]["industry_drawer"]["control"]["kind"] = "ainav.industry_rooms.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_301(kind_301, kind_301["plane_interface"])
    site_301 = copy.deepcopy(cat)
    site_301["expert_review"]["success"]["industry_drawer"]["control"]["site"] = (
        "Control on #industry. Need is #control. Not a live filing."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_301(site_301, site_301["plane_interface"])
    ops_301 = copy.deepcopy(cat)
    ops_301["operations"]["note"] = "SKU attach chain. #industry. Complete industry drawer."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_301(ops_301, ops_301["plane_interface"])
    refuse_text = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    refuse_text["lanes"][-1]["items"][0]["refuse_text"] = "Refused."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(refuse_text)
    glance_hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"]["control"])
    glance_hole["glance"] = glance_hole["glance"].replace("Honest control", "Control")
    with pytest.raises(IntegrityError):
        catmod._validate_industry_control(glance_hole)
    gov = copy.deepcopy(cat)
    gov["governance"]["refuse"] = [item for item in gov["governance"]["refuse"] if "GENIUS" not in item and "CLARITY" not in item]
    with pytest.raises(IntegrityError):
        validate_catalog(gov)
