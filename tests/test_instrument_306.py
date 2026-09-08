from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_READY_HREFS,
    HONEST_READY_IDS,
    HONEST_READY_REFUSE_IDS,
    HONEST_READY_REFUSE_TEXT,
    HONEST_READY_ROLES,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute
from ainav.microsoft.readiness import public_review


def test_release_is_306_honest_readiness():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.08.0"
    ready = cat["microsoft_stack"]["readiness"]
    assert ready["kind"] == "ainav.honest.readiness.v1"
    assert ready["honest"] is True
    assert ready["gold_is_launch"] is False
    assert ready["twin_is_launch_day"] is False
    assert ready["sim_is_production"] is False
    assert ready["update_is_live_pin"] is False
    assert ready["owner_gaps_closed"] is False
    assert ready["launch_day_certified"] is False
    assert ready["certified"] is False
    assert ready["is_admit_plane"] is False
    assert [item["id"] for item in ready["lanes"]] == list(HONEST_READY_IDS)
    assert {item["id"]: item["role"] for item in ready["lanes"]} == dict(HONEST_READY_ROLES)
    refuse = [item for item in ready["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_READY_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_READY_REFUSE_TEXT[key] for key in HONEST_READY_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in ready["lanes"]}
    hrefs.update({item["id"]: item["href"] for item in refuse})
    assert hrefs == HONEST_READY_HREFS
    assert all(item["installed"] is None and item["seat"] is not True for item in ready["lanes"])
    assert "honest readiness" in ready["note"].lower()
    assert "gold is not launch" in ready["note"].lower()
    assert "twin certified is not launch day" in ready["note"].lower()
    assert "owner gaps stay owner-only" in ready["note"].lower()
    assert "gold is not launch" in ready["lede"].lower()
    assert "twin certified is not launch day" in ready["lede"].lower()
    assert cat["programs"]["website"]["honest_readiness"] is True
    assert cat["programs"]["website"]["honest_build"] is True
    assert cat["programs"]["website"]["honest_readiness_live"] is False
    assert cat["programs"]["website"]["gold_is_launch"] is False
    assert cat["programs"]["website"]["twin_is_launch_day"] is False
    assert cat["programs"]["website"]["launch_day_certified"] is False
    assert "honest readiness" in cat["operations"]["note"].lower()
    assert any("3.06.0" in item and "honest readiness" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "gold as launch" in does_not
    assert "twin certified as launch day" in does_not
    assert "simulation as production" in does_not
    assert "an update as live_pin_ok" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest readiness" in principles
    assert "gold is not launch" in principles
    assert "twin certified is not launch day" in principles
    assert "owner gaps stay owner-only" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 78
    assert upgrades[76]["who"] == "tree"
    assert upgrades[76]["done"] is True
    assert upgrades[76]["marks_live_pin"] is False
    blob = f"{upgrades[76]['title']} {upgrades[76]['do']}".lower()
    assert "honest readiness" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.08.0" in html
    assert "honest readiness" in html.lower()
    assert "gold is not launch" in html.lower()
    assert "twin certified is not launch day" in html.lower()
    assert "owner gaps stay owner-only" in html.lower()
    assert 'id="ready-lanes"' in html
    assert 'data-ready-refuse="gold_as_launch"' in html
    assert 'data-ready-refuse="twin_as_launch_day"' in html
    assert 'data-ready-refuse="sim_as_production"' in html
    assert 'data-ready-refuse="update_as_live_pin"' in html
    assert 'data-ready-refuse="close_owner_from_plane"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#agent-tools"' not in nav
    assert 'href="/ready"' not in nav
    assert 'href="/build"' not in nav
    assert "bindReadyRefuses" in js
    assert "refuseReady" in js
    assert "ready-lede" not in js
    assert "build-lede" not in js
    assert "operator-lede" not in js
    assert "access-lede" not in js
    assert "agent-tools-lede" not in js
    assert "honest readiness" in twin.lower()
    assert "twin certified is not launch day" in twin.lower()
    assert "readiness" in app.lower()
    assert "Gold is launch" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.08.0"
    status = public_status()
    assert status["release"] == "3.08.0"
    assert status["website"]["honest_readiness"] is True
    assert status["website"]["honest_readiness_live"] is False
    assert status["website"]["gold_is_launch"] is False
    assert status["website"]["twin_is_launch_day"] is False
    assert status["website"]["launch_day_certified"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.readiness.v1"
    assert review["gold_is_launch"] is False
    assert "Treat twin certified as launch day." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_306_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.05.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.06.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_readiness"] = False

    def live(cat):
        cat["programs"]["website"]["honest_readiness_live"] = True

    def gold(cat):
        cat["microsoft_stack"]["readiness"]["gold_is_launch"] = True

    def twin(cat):
        cat["microsoft_stack"]["readiness"]["twin_is_launch_day"] = True

    def site(cat):
        cat["microsoft_stack"]["readiness"]["site"] = "Ready on #agent-tools."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest readiness" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. Honest build sits on #agent-tools. This plane does not need full access."
        )

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "gold as launch" not in item.lower() and "launch day" not in item.lower()
        ]

    for mutator in (release, closed, flag_off, live, gold, twin, site, principles, ops, ciso):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["microsoft_stack"]["readiness"]["kind"] = "ainav.honest.readiness.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(hole, hole["plane_interface"])
    needed = copy.deepcopy(edge)
    needed["microsoft_stack"]["readiness"]["gold_is_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(needed, needed["plane_interface"])
    twin_flag = copy.deepcopy(edge)
    twin_flag["microsoft_stack"]["readiness"]["twin_is_launch_day"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(twin_flag, twin_flag["plane_interface"])
    day_flag = copy.deepcopy(edge)
    day_flag["microsoft_stack"]["readiness"]["launch_day_certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(day_flag, day_flag["plane_interface"])
    site_hole = copy.deepcopy(edge)
    site_hole["microsoft_stack"]["readiness"]["site"] = site_hole["microsoft_stack"]["readiness"]["site"].replace(
        "Gold is not launch. Twin certified is not launch day. Owner gaps stay owner-only. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(site_hole, site_hole["plane_interface"])
    honest = copy.deepcopy(edge)
    honest["microsoft_stack"]["readiness"]["honest"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(honest, honest["plane_interface"])
    site_gold = copy.deepcopy(edge)
    site_gold["programs"]["website"]["gold_is_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(site_gold, site_gold["plane_interface"])
    site_twin = copy.deepcopy(edge)
    site_twin["programs"]["website"]["twin_is_launch_day"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(site_twin, site_twin["plane_interface"])
    site_day = copy.deepcopy(edge)
    site_day["programs"]["website"]["launch_day_certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(site_day, site_day["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = "SKU attach chain. #agent-tools."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(ops_hole, ops_hole["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["honest_readiness"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    success_missing = copy.deepcopy(edge["expert_review"]["success"])
    success_missing.pop("honest_readiness")
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_missing)
    success_kind = copy.deepcopy(edge["expert_review"]["success"])
    success_kind["honest_readiness"]["kind"] = "ainav.honest.readiness.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_kind)
    success_href = copy.deepcopy(edge["expert_review"]["success"])
    success_href["honest_readiness"]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_href)
    for missing in (
        "Treat gold as launch",
        "Treat twin certified as launch day",
        "Treat simulation as production",
        "Treat an update as LIVE_PIN_OK",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
    site_mapped = copy.deepcopy(edge)
    site_mapped["microsoft_stack"]["readiness"]["site"] = (
        "Honest readiness on #agent-tools. Gold is not launch. Owner gaps stay owner-only."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(site_mapped, site_mapped["plane_interface"])
    site_owner = copy.deepcopy(edge)
    site_owner["microsoft_stack"]["readiness"]["site"] = (
        "Honest readiness on #agent-tools. Gold is not launch. Twin certified is not launch day."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(site_owner, site_owner["plane_interface"])
    principles_honest = copy.deepcopy(edge)
    principles_honest["expert_review"]["first_principles"] = [
        item.replace("Honest readiness", "Operator maps").replace("honest readiness", "operator maps")
        for item in principles_honest["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(principles_honest, principles_honest["plane_interface"])
    ops_sku = copy.deepcopy(edge)
    ops_sku["operations"]["note"] = "Honest readiness sits on #agent-tools."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(ops_sku, ops_sku["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest readiness."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_306(ops_href, ops_href["plane_interface"])
    first_gold = copy.deepcopy(edge["expert_review"]["first_principles"])
    first_gold = [item.replace("Gold is not launch.", "Gold stays mapped.") for item in first_gold]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(first_gold)
    first_twin = copy.deepcopy(edge["expert_review"]["first_principles"])
    first_twin = [
        item.replace("Twin certified is not launch day.", "Twin stays mapped.") for item in first_twin
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(first_twin)
    first_owner = copy.deepcopy(edge["expert_review"]["first_principles"])
    first_owner = [item.replace("Owner gaps stay owner-only.", "Owner gaps close.") for item in first_owner]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(first_owner)
