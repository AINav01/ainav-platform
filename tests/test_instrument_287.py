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


def test_release_is_287_first_class_operating_day():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.92.0"
    firm = cat["expert_review"]["success"]["operating_company"]
    assert firm["kind"] == "ainav.operating_company.v1"
    assert firm["day"]["kind"] == "ainav.operating_day.v1"
    assert firm["gates"]["kind"] == "ainav.launch_gate.v1"
    assert firm["service"]["kind"] == "ainav.service_book.v1"
    assert firm["day"]["launch"] is False
    assert firm["gates"]["launch"] is False
    assert firm["gates"]["gold_is_not_launch"] is True
    assert firm["live_pin_ok"] is False
    assert [item["id"] for item in firm["day"]["stages"]] == [
        "qualify",
        "proof",
        "close",
        "assign",
        "service",
        "launch",
    ]
    assert all(item["ready"] is False for item in firm["gates"]["items"])
    assert cat["programs"]["website"]["operating_day"] is True
    assert cat["programs"]["website"]["operating_day_is_sku"] is False
    assert cat["programs"]["website"]["launch_gate"] is True
    assert cat["programs"]["website"]["launch_is_ready"] is False
    assert any(
        "2.87.0" in item and "operating day" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 62
    assert upgrades[57]["who"] == "tree"
    assert upgrades[57]["done"] is True
    assert upgrades[57]["marks_live_pin"] is False
    blob = f"{upgrades[57]['title']} {upgrades[57]['do']}".lower()
    assert "operating day" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "2.92.0" in html
    assert 'id="firm-console"' in html
    assert 'id="firm-day"' in html
    assert 'id="firm-gates"' in html
    assert 'id="firm-mark-launch"' in html
    dash = public_dashboard()
    assert dash["release"] == "2.92.0"
    status = public_status()
    assert status["release"] == "2.92.0"
    assert status["website"]["operating_day"] is True
    assert status["website"]["launch_is_ready"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_287_fail_closed():
    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.87.0" not in item
        ]

    def day_kind(cat):
        cat["expert_review"]["success"]["operating_company"]["day"]["kind"] = "ainav.crm.v1"

    def day_launch(cat):
        cat["expert_review"]["success"]["operating_company"]["day"]["launch"] = True

    def gate_kind(cat):
        cat["expert_review"]["success"]["operating_company"]["gates"]["kind"] = "ainav.cms.v1"

    def gate_ready(cat):
        cat["programs"]["website"]["launch_is_ready"] = True

    def day_off(cat):
        cat["programs"]["website"]["operating_day"] = False

    def day_sku(cat):
        cat["programs"]["website"]["operating_day_is_sku"] = True

    def gate_off(cat):
        cat["programs"]["website"]["launch_gate"] = False

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "operating day" not in item.lower()
        ]

    for mutator in (
        closed,
        day_kind,
        day_launch,
        gate_kind,
        gate_ready,
        day_off,
        day_sku,
        gate_off,
        principles,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    kind_hole = copy.deepcopy(edge)
    kind_hole["expert_review"]["success"]["operating_company"]["day"]["kind"] = "ainav.crm.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_287(kind_hole, kind_hole["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "operating day" not in item.lower() and "launch gate" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_287(principles_hole, principles_hole["plane_interface"])
    launch_hole = copy.deepcopy(edge)
    launch_hole["expert_review"]["success"]["operating_company"]["gates"]["launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_287(launch_hole, launch_hole["plane_interface"])
    ready_site = copy.deepcopy(edge)
    ready_site["programs"]["website"]["launch_is_ready"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_287(ready_site, ready_site["plane_interface"])
