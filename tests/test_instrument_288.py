from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_288_operating_day_quality_review():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.91.0"
    firm = cat["expert_review"]["success"]["operating_company"]
    gold = next(item for item in firm["gates"]["items"] if item["id"] == "gold")
    assert gold["held"] is True
    assert gold["ready"] is False
    assert "floor held" in gold["note"].lower()
    assert all(item["ready"] is False for item in firm["gates"]["items"])
    assert all(item.get("held") is not True for item in firm["gates"]["items"] if item["id"] != "gold")
    assert "#firm" in cat["operations"]["note"]
    assert "sku attach" in cat["operations"]["note"].lower()
    assert any(
        "2.88.0" in item and "quality review" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 61
    assert upgrades[58]["who"] == "tree"
    assert upgrades[58]["done"] is True
    assert upgrades[58]["marks_live_pin"] is False
    blob = f"{upgrades[58]['title']} {upgrades[58]['do']}".lower()
    assert "quality review" in blob
    assert "live_pin_ok" in blob
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "quality review" in principles
    assert "403 challenge" in principles
    assert "sku attach" in principles
    confirm = " ".join(cat["microsoft_stack"]["edge"]["quality"]["confirm"]).lower()
    assert "403-vs-404" in confirm
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert "2.91.0" in html
    assert 'src="site.js?v=2.91.0"' in html
    assert 'src="site.js?v=2.91.0"' in twin
    assert "Held. Floor held. Gold is not launch." in html
    assert 'id="ops-note"' in html
    assert "SKU attach chain" in html
    assert 'item.held ? "Held. "' in js
    dash = public_dashboard()
    assert dash["release"] == "2.91.0"
    status = public_status()
    assert status["release"] == "2.91.0"
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_288_fail_closed():
    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.88.0" not in item
        ]

    def gold_held(cat):
        for item in cat["expert_review"]["success"]["operating_company"]["gates"]["items"]:
            if item.get("id") == "gold":
                item["held"] = False

    def gold_ready(cat):
        for item in cat["expert_review"]["success"]["operating_company"]["gates"]["items"]:
            if item.get("id") == "gold":
                item["ready"] = True

    def ops_note(cat):
        cat["operations"]["note"] = "A second company."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "quality review" not in item.lower()
        ]

    def confirm(cat):
        cat["microsoft_stack"]["edge"]["quality"]["confirm"] = [
            item
            for item in cat["microsoft_stack"]["edge"]["quality"]["confirm"]
            if "403-vs-404" not in item.lower()
        ]

    for mutator in (
        closed,
        gold_held,
        gold_ready,
        ops_note,
        principles,
        confirm,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    held_hole = copy.deepcopy(edge)
    for item in held_hole["expert_review"]["success"]["operating_company"]["gates"]["items"]:
        if item.get("id") == "gold":
            item["held"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_288(held_hole, held_hole["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "quality review" not in item.lower()
        and "403 challenge" not in item.lower()
        and "sku attach" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_288(principles_hole, principles_hole["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = "A second company."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_288(ops_hole, ops_hole["plane_interface"])
    confirm_hole = copy.deepcopy(edge)
    confirm_hole["microsoft_stack"]["edge"]["quality"]["confirm"] = [
        item
        for item in confirm_hole["microsoft_stack"]["edge"]["quality"]["confirm"]
        if "403-vs-404" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_288(confirm_hole, confirm_hole["plane_interface"])
