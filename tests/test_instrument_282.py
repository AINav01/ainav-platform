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


def test_release_is_282_what_youve_been_missing():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.82.0"
    assert cat["expert_review"]["success"]["what_was_missing"]["kind"] == "ainav.what_was_missing.v1"
    assert cat["expert_review"]["success"]["what_was_missing"]["fourth_sku"] is False
    assert cat["expert_review"]["success"]["what_was_missing"]["launch"] is False
    assert any("2.82.0" in item and "been missing" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 52
    assert upgrades[52]["who"] == "tree"
    assert upgrades[52]["done"] is True
    assert upgrades[52]["marks_live_pin"] is False
    blob = f"{upgrades[52]['title']} {upgrades[52]['do']}".lower()
    assert "been missing" in blob
    assert "live_pin_ok" in blob
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "what you've been missing" in principles
    assert "you already have" in principles
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert "2.82.0" in html
    assert 'id="have"' in html
    assert "paintWhatWasMissing" in js
    assert "index.html#have" in twin
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#have"' not in nav
    dash = public_dashboard()
    assert dash["release"] == "2.82.0"
    status = public_status()
    assert status["release"] == "2.82.0"
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_282_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.81.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.82.0" not in item
        ]

    def kind(cat):
        cat["expert_review"]["success"]["what_was_missing"]["kind"] = "ainav.wow.v1"

    def fourth(cat):
        cat["expert_review"]["success"]["what_was_missing"]["fourth_sku"] = True

    def launch(cat):
        cat["expert_review"]["success"]["what_was_missing"]["launch"] = True

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "what you've been missing" not in item.lower()
        ]

    for mutator in (release, closed, kind, fourth, launch, principles):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["entity"]["release"] = "2.81.0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_282(hole, hole["plane_interface"])
    hole = copy.deepcopy(edge)
    hole["expert_review"]["success"]["what_was_missing"]["fourth_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_282(hole, hole["plane_interface"])
    hole = copy.deepcopy(edge)
    hole["expert_review"]["success"]["what_was_missing"]["kind"] = "ainav.wow.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_282(hole, hole["plane_interface"])
    hole = copy.deepcopy(edge)
    hole["expert_review"]["success"]["what_was_missing"]["launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_282(hole, hole["plane_interface"])
    hole = copy.deepcopy(edge)
    hole["expert_review"]["first_principles"] = [
        item
        for item in hole["expert_review"]["first_principles"]
        if "what you've been missing" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_282(hole, hole["plane_interface"])
