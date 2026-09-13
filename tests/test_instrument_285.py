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


def test_release_is_285_first_class_close_bench():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.26.0"
    bench = cat["expert_review"]["success"]["close_bench"]
    assert bench["kind"] == "ainav.close_bench.v1"
    assert bench["sku"] is False
    assert bench["assigned"] is False
    assert bench["production"] is False
    assert bench["live_pin_ok"] is False
    assert bench["named_client"] is None
    assert cat["programs"]["website"]["close_bench"] is True
    assert cat["programs"]["website"]["close_is_sku"] is False
    assert any("2.85.0" in item and "close bench" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 96
    assert upgrades[55]["who"] == "tree"
    assert upgrades[55]["done"] is True
    assert upgrades[55]["marks_live_pin"] is False
    blob = f"{upgrades[55]['title']} {upgrades[55]['do']}".lower()
    assert "close bench" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert 'id="close-console"' in html
    assert 'id="path-planes"' in html
    dash = public_dashboard()
    assert dash["release"] == "3.26.0"
    status = public_status()
    assert status["release"] == "3.26.0"
    assert status["website"]["close_bench"] is True
    assert status["website"]["close_is_sku"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_285_fail_closed():
    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.85.0" not in item
        ]

    def kind(cat):
        cat["expert_review"]["success"]["close_bench"]["kind"] = "ainav.cms.v1"

    def assigned(cat):
        cat["expert_review"]["success"]["close_bench"]["assigned"] = True

    def production(cat):
        cat["expert_review"]["success"]["close_bench"]["production"] = True

    def sku(cat):
        cat["expert_review"]["success"]["close_bench"]["sku"] = True

    def bench_off(cat):
        cat["programs"]["website"]["close_bench"] = False

    def bench_sku(cat):
        cat["programs"]["website"]["close_is_sku"] = True

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "close bench" not in item.lower()
        ]

    for mutator in (
        closed,
        kind,
        assigned,
        production,
        sku,
        bench_off,
        bench_sku,
        principles,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    kind_hole = copy.deepcopy(edge)
    kind_hole["expert_review"]["success"]["close_bench"]["kind"] = "ainav.cms.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_285(kind_hole, kind_hole["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "close bench" not in item.lower() and "three planes" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_285(principles_hole, principles_hole["plane_interface"])
    assigned_hole = copy.deepcopy(edge)
    assigned_hole["expert_review"]["success"]["close_bench"]["assigned"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_285(assigned_hole, assigned_hole["plane_interface"])
