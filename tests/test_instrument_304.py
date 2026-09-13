from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_OPERATOR_HREFS,
    HONEST_OPERATOR_IDS,
    HONEST_OPERATOR_REFUSE_IDS,
    HONEST_OPERATOR_REFUSE_TEXT,
    HONEST_OPERATOR_ROLES,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute
from ainav.microsoft.operators import public_review


def test_release_is_304_honest_operators():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.28.0"
    ops = cat["microsoft_stack"]["operators"]
    assert ops["kind"] == "ainav.honest.operators.v1"
    assert ops["honest"] is True
    assert ops["swap"] is False
    assert ops["grok_is_recorded"] is False
    assert ops["bot_is_operator"] is False
    assert ops["bot_is_admit"] is False
    assert ops["owner_is_operator"] is False
    assert ops["is_admit_plane"] is False
    assert [item["id"] for item in ops["three"]] == list(HONEST_OPERATOR_IDS)
    assert {item["id"]: item["role"] for item in ops["three"]} == dict(HONEST_OPERATOR_ROLES)
    refuse = [item for item in ops["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_OPERATOR_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_OPERATOR_REFUSE_TEXT[key] for key in HONEST_OPERATOR_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in ops["three"]}
    hrefs.update({item["id"]: item["href"] for item in refuse})
    assert hrefs == HONEST_OPERATOR_HREFS
    cursor = next(item for item in ops["three"] if item["id"] == "cursor")
    assert cursor["recorded"] is True
    assert all(item["id"] == "cursor" or item["recorded"] is not True for item in ops["three"])
    assert all(item["installed"] is None and item["seat"] is not True for item in ops["three"])
    grok_bot = next(item for item in ops["three"] if item["id"] == "grok_bot")
    assert grok_bot["operator"] is not True
    assert "honest operators" in ops["note"].lower()
    assert "cursor is recorded" in ops["note"].lower()
    assert "grok build is mapped" in ops["note"].lower()
    assert "grok bot is not admit" in ops["note"].lower()
    assert "cursor is recorded" in ops["lede"].lower()
    assert "grok build is mapped" in ops["lede"].lower()
    assert "grok bot is not admit" in ops["lede"].lower()
    assert cat["programs"]["website"]["honest_operators"] is True
    assert cat["programs"]["website"]["honest_access"] is True
    assert cat["programs"]["website"]["honest_operators_live"] is False
    assert cat["programs"]["website"]["operator_swap"] is False
    assert cat["programs"]["website"]["grok_is_recorded"] is False
    assert cat["programs"]["website"]["bot_is_operator"] is False
    assert "honest operators" in cat["operations"]["note"].lower()
    assert any("3.04.0" in item and "honest operators" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "grok build as the recorded operator" in does_not
    assert "grok bot as the operator" in does_not
    assert "swap cursor for grok" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest operators" in principles
    assert "cursor is recorded" in principles
    assert "grok build is mapped" in principles
    assert "grok bot is not admit" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 98
    assert upgrades[74]["who"] == "tree"
    assert upgrades[74]["done"] is True
    assert upgrades[74]["marks_live_pin"] is False
    blob = f"{upgrades[74]['title']} {upgrades[74]['do']}".lower()
    assert "honest operators" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert "honest operators" in html.lower()
    assert "cursor is recorded" in html.lower()
    assert "grok build is mapped" in html.lower()
    assert "grok bot is not admit" in html.lower()
    assert 'id="operator-three"' in html
    assert 'data-operator-refuse="swap_operator"' in html
    assert 'data-operator-refuse="grok_as_recorded"' in html
    assert 'data-operator-refuse="bot_as_operator"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#agent-tools"' not in nav
    assert 'href="/operators"' not in nav
    assert 'href="/grok"' not in nav
    assert "bindOperatorRefuses" in js
    assert "refuseOperator" in js
    assert "operator-lede" not in js
    assert "access-lede" not in js
    assert "agent-tools-lede" not in js
    assert "honest operators" in twin.lower()
    assert "cursor is recorded" in twin.lower()
    assert "Grok Build" in app
    assert "operators" in app.lower()
    assert "Grok bot" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.28.0"
    status = public_status()
    assert status["release"] == "3.28.0"
    assert status["website"]["honest_operators"] is True
    assert status["website"]["honest_operators_live"] is False
    assert status["website"]["operator_swap"] is False
    assert status["website"]["grok_is_recorded"] is False
    assert status["website"]["bot_is_operator"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.operators.v1"
    assert review["swap"] is False
    assert "Treat a Grok bot as the operator or as dual admit." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_304_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.03.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.04.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_operators"] = False

    def live(cat):
        cat["programs"]["website"]["honest_operators_live"] = True

    def swap(cat):
        cat["microsoft_stack"]["operators"]["swap"] = True

    def grok(cat):
        cat["microsoft_stack"]["operators"]["grok_is_recorded"] = True

    def site(cat):
        cat["microsoft_stack"]["operators"]["site"] = "Operators on #agent-tools."

    def recorded(cat):
        cat["microsoft_stack"]["operators"]["three"][1]["recorded"] = True

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest operators" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. Honest access sits on #agent-tools. Grok Build is not a seat."
        )

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "Grok Build as the recorded" not in item and "Swap Cursor" not in item
        ]

    for mutator in (release, closed, flag_off, live, swap, grok, site, recorded, principles, ops, ciso):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["microsoft_stack"]["operators"]["kind"] = "ainav.honest.operators.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(hole, hole["plane_interface"])
    swapped = copy.deepcopy(edge)
    swapped["microsoft_stack"]["operators"]["swap"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(swapped, swapped["plane_interface"])
    grok_flag = copy.deepcopy(edge)
    grok_flag["microsoft_stack"]["operators"]["grok_is_recorded"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(grok_flag, grok_flag["plane_interface"])
    bot_flag = copy.deepcopy(edge)
    bot_flag["microsoft_stack"]["operators"]["bot_is_operator"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(bot_flag, bot_flag["plane_interface"])
    site_hole = copy.deepcopy(edge)
    site_hole["microsoft_stack"]["operators"]["site"] = site_hole["microsoft_stack"]["operators"]["site"].replace(
        "Cursor is recorded. Grok Build is mapped. Grok bot is not admit.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(site_hole, site_hole["plane_interface"])
    honest = copy.deepcopy(edge)
    honest["microsoft_stack"]["operators"]["honest"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(honest, honest["plane_interface"])
    recorded_flag = copy.deepcopy(edge)
    recorded_flag["programs"]["website"]["grok_is_recorded"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(recorded_flag, recorded_flag["plane_interface"])
    bot_site = copy.deepcopy(edge)
    bot_site["programs"]["website"]["bot_is_operator"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(bot_site, bot_site["plane_interface"])
    swapped_site = copy.deepcopy(edge)
    swapped_site["programs"]["website"]["operator_swap"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(swapped_site, swapped_site["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = "SKU attach chain. #agent-tools."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(ops_hole, ops_hole["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["honest_operators"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    success_missing = copy.deepcopy(edge["expert_review"]["success"])
    success_missing.pop("honest_operators")
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_missing)
    success_kind = copy.deepcopy(edge["expert_review"]["success"])
    success_kind["honest_operators"]["kind"] = "ainav.honest.operators.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_kind)
    success_href = copy.deepcopy(edge["expert_review"]["success"])
    success_href["honest_operators"]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_href)
    success_swap = copy.deepcopy(edge["expert_review"]["success"])
    success_swap["honest_operators"]["swap"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_swap)
    for missing in (
        "Treat Grok Build as the recorded operator",
        "Treat a Grok bot as the operator",
        "Swap Cursor for Grok",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
    principles_ops = copy.deepcopy(edge["expert_review"]["first_principles"])
    principles_ops = [
        item.replace("Honest operators is catalog law: Cursor is recorded.", "").replace(
            "Grok Build is mapped.", ""
        )
        for item in principles_ops
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_ops)
    site_mapped = copy.deepcopy(edge)
    site_mapped["microsoft_stack"]["operators"]["site"] = (
        "Honest operators on #agent-tools. Cursor is recorded. Grok bot is not admit."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(site_mapped, site_mapped["plane_interface"])
    site_bot = copy.deepcopy(edge)
    site_bot["microsoft_stack"]["operators"]["site"] = (
        "Honest operators on #agent-tools. Cursor is recorded. Grok Build is mapped."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(site_bot, site_bot["plane_interface"])
    principles_honest = copy.deepcopy(edge)
    principles_honest["expert_review"]["first_principles"] = [
        item.replace("Honest operators", "Operator maps").replace("honest operators", "operator maps")
        for item in principles_honest["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(principles_honest, principles_honest["plane_interface"])
    ops_sku = copy.deepcopy(edge)
    ops_sku["operations"]["note"] = "Honest operators sit on #agent-tools."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(ops_sku, ops_sku["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest operators."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(ops_href, ops_href["plane_interface"])
    principles_cursor = copy.deepcopy(edge)
    principles_cursor["expert_review"]["first_principles"] = [
        item.replace("Cursor is recorded.", "Cursor is mapped.")
        for item in principles_cursor["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_304(principles_cursor, principles_cursor["plane_interface"])
    first_mapped = copy.deepcopy(edge["expert_review"]["first_principles"])
    first_mapped = [item.replace("Grok Build is mapped.", "Grok Build is recorded.") for item in first_mapped]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(first_mapped)
