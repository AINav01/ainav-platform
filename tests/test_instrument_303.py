from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_ACCESS_HREFS,
    HONEST_ACCESS_LANE_IDS,
    HONEST_ACCESS_OPERATOR_IDS,
    HONEST_ACCESS_REFUSE_IDS,
    HONEST_ACCESS_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.access import public_review
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_303_honest_access():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.13.0"
    access = cat["microsoft_stack"]["access"]
    assert access["kind"] == "ainav.honest.access.v1"
    assert access["honest"] is True
    assert access["need_more"] is False
    assert access["additional_access_needed"] is False
    assert access["grok_is_product"] is False
    assert access["grok_is_seat"] is False
    assert access["grok_installed"] is None
    assert access["is_admit_plane"] is False
    assert [item["id"] for item in access["operators"]] == list(HONEST_ACCESS_OPERATOR_IDS)
    assert [lane["id"] for lane in access["lanes"]] == list(HONEST_ACCESS_LANE_IDS)
    refuse = next(lane for lane in access["lanes"] if lane["id"] == "refuse")
    assert [item["id"] for item in refuse["items"]] == list(HONEST_ACCESS_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse["items"]} == {
        key: HONEST_ACCESS_REFUSE_TEXT[key] for key in HONEST_ACCESS_REFUSE_IDS
    }
    hrefs = {row["id"]: row["href"] for lane in access["lanes"] for row in lane["items"]}
    assert hrefs == HONEST_ACCESS_HREFS
    cursor = next(item for item in access["operators"] if item["id"] == "cursor")
    assert cursor["recorded"] is True
    assert all(item["id"] == "cursor" or item["recorded"] is not True for item in access["operators"])
    assert all(item["installed"] is None and item["seat"] is not True for item in access["operators"])
    assert "honest access" in access["note"].lower()
    assert "does not need" in access["note"].lower()
    assert "grok build" in access["note"].lower()
    assert "not a seat" in access["note"].lower()
    assert "does not need additional access" in access["lede"].lower()
    assert "grok build is not a seat" in access["lede"].lower()
    assert cat["programs"]["website"]["honest_access"] is True
    assert cat["programs"]["website"]["honest_access_live"] is False
    assert cat["programs"]["website"]["additional_access_needed"] is False
    assert cat["programs"]["website"]["grok_is_product"] is False
    assert cat["programs"]["website"]["grok_is_seat"] is False
    assert "honest access" in cat["operations"]["note"].lower()
    assert any("3.03.0" in item and "honest access" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "grok build as a seat" in does_not
    assert "grok bot as dual admit" in does_not
    assert "microsoft admin as this cloud agent" in does_not
    assert "additional access as admit" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest access" in principles
    assert "does not need additional access" in principles
    assert "grok build is not a seat" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 83
    assert upgrades[73]["who"] == "tree"
    assert upgrades[73]["done"] is True
    assert upgrades[73]["marks_live_pin"] is False
    blob = f"{upgrades[73]['title']} {upgrades[73]['do']}".lower()
    assert "honest access" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.13.0" in html
    assert "honest access" in html.lower()
    assert "does not need additional access" in html.lower()
    assert "grok build is not a seat" in html.lower()
    assert 'id="access-board"' in html
    assert 'data-access-refuse="ask_admin"' in html
    assert 'data-access-refuse="grok_as_seat"' in html
    assert 'data-access-refuse="grok_as_product"' in html
    assert 'data-access-refuse="bot_as_admit"' in html
    assert 'data-access-refuse="more_access_as_admit"' in html
    assert 'id="access-need-more-btn"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#agent-tools"' not in nav
    assert 'href="/access"' not in nav
    assert 'href="/grok"' not in nav
    assert "bindAccessRefuses" in js
    assert "refuseAccess" in js
    assert "access-lede" not in js
    assert "agent-tools-lede" not in js
    assert "honest access" in twin.lower()
    assert "grok build is not a seat" in twin.lower()
    assert "Honest" in app
    assert "access" in app.lower()
    assert "Grok" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.13.0"
    status = public_status()
    assert status["release"] == "3.13.0"
    assert status["website"]["honest_access"] is True
    assert status["website"]["honest_access_live"] is False
    assert status["website"]["additional_access_needed"] is False
    assert status["website"]["grok_is_product"] is False
    assert status["website"]["grok_is_seat"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.access.v1"
    assert review["need_more"] is False
    assert review["grok_is_product"] is False
    assert "Treat Grok Build as a seat" in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_303_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.02.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.03.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_access"] = False

    def live(cat):
        cat["programs"]["website"]["honest_access_live"] = True

    def need_more(cat):
        cat["microsoft_stack"]["access"]["need_more"] = True

    def product(cat):
        cat["microsoft_stack"]["access"]["grok_is_product"] = True

    def site(cat):
        cat["microsoft_stack"]["access"]["site"] = "Access on #agent-tools."

    def recorded(cat):
        cat["microsoft_stack"]["access"]["operators"][1]["recorded"] = True

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest access" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. Honest agents sit on #agent-tools. An agent is not a seat."
        )

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "Grok Build" not in item and "additional access" not in item.lower()
        ]

    for mutator in (release, closed, flag_off, live, need_more, product, site, recorded, principles, ops, ciso):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["microsoft_stack"]["access"]["kind"] = "ainav.honest.access.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(hole, hole["plane_interface"])
    more = copy.deepcopy(edge)
    more["microsoft_stack"]["access"]["need_more"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(more, more["plane_interface"])
    grok = copy.deepcopy(edge)
    grok["microsoft_stack"]["access"]["grok_is_product"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(grok, grok["plane_interface"])
    site_hole = copy.deepcopy(edge)
    site_hole["microsoft_stack"]["access"]["site"] = site_hole["microsoft_stack"]["access"]["site"].replace(
        "This plane does not need additional access. Grok Build is not a seat.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(site_hole, site_hole["plane_interface"])
    honest = copy.deepcopy(edge)
    honest["microsoft_stack"]["access"]["honest"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(honest, honest["plane_interface"])
    product_flag = copy.deepcopy(edge)
    product_flag["programs"]["website"]["grok_is_product"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(product_flag, product_flag["plane_interface"])
    seat_flag = copy.deepcopy(edge)
    seat_flag["programs"]["website"]["grok_is_seat"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(seat_flag, seat_flag["plane_interface"])
    needed = copy.deepcopy(edge)
    needed["programs"]["website"]["additional_access_needed"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(needed, needed["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = "SKU attach chain. #agent-tools."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(ops_hole, ops_hole["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["honest_access"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    for missing in (
        "Treat Grok Build as a seat",
        "Treat a Grok bot as dual admit",
        "Request Microsoft admin as this Cloud Agent",
        "Treat additional access as admit",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
    principles_access = copy.deepcopy(edge["expert_review"]["first_principles"])
    principles_access = [
        item.replace("Honest access does not need additional access.", "").replace("Grok Build is not a seat.", "")
        for item in principles_access
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_access)
    site_grok = copy.deepcopy(edge)
    site_grok["microsoft_stack"]["access"]["site"] = (
        "Honest access on #agent-tools. This plane does not need additional access."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(site_grok, site_grok["plane_interface"])
    principles_grok = copy.deepcopy(edge)
    principles_grok["expert_review"]["first_principles"] = [
        item.replace("Grok Build is not a seat.", "Grok Build is mapped.")
        for item in principles_grok["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_303(principles_grok, principles_grok["plane_interface"])
    first_grok = copy.deepcopy(edge["expert_review"]["first_principles"])
    first_grok = [item.replace("Grok Build is not a seat.", "Grok Build is mapped.") for item in first_grok]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(first_grok)
