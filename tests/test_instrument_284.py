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


def test_release_is_284_client_assigned_sandbox_twin():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.84.0"
    twin = cat["expert_review"]["success"]["client_twin"]
    assert twin["kind"] == "ainav.client_twin.v1"
    assert twin["sku"] is False
    assert twin["fourth_sku"] is False
    assert twin["assigned"] is False
    assert twin["production"] is False
    assert twin["live_pin_ok"] is False
    assert twin["named_client"] is None
    assert twin["count"] == 0
    assert cat["programs"]["website"]["path_href"] == "#path"
    assert cat["programs"]["website"]["client_twin_is_sku"] is False
    assert any("2.84.0" in item and "client" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 54
    assert upgrades[54]["who"] == "tree"
    assert upgrades[54]["done"] is True
    assert upgrades[54]["marks_live_pin"] is False
    blob = f"{upgrades[54]['title']} {upgrades[54]['do']}".lower()
    assert "client twin" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "2.84.0" in html
    assert 'id="path"' in html
    assert 'id="path-console"' in html
    dash = public_dashboard()
    assert dash["release"] == "2.84.0"
    status = public_status()
    assert status["release"] == "2.84.0"
    assert status["website"]["path_href"] == "#path"
    assert status["website"]["client_twin_is_sku"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_284_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.83.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.84.0" not in item
        ]

    def kind(cat):
        cat["expert_review"]["success"]["client_twin"]["kind"] = "ainav.sandbox.sku.v1"

    def assigned(cat):
        cat["expert_review"]["success"]["client_twin"]["assigned"] = True

    def production(cat):
        cat["expert_review"]["success"]["client_twin"]["production"] = True

    def sku(cat):
        cat["expert_review"]["success"]["client_twin"]["sku"] = True

    def path_href(cat):
        cat["programs"]["website"]["path_href"] = "/demo"

    def twin_sku(cat):
        cat["programs"]["website"]["client_twin_is_sku"] = True

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "client-assigned" not in item.lower()
        ]

    for mutator in (
        release,
        closed,
        kind,
        assigned,
        production,
        sku,
        path_href,
        twin_sku,
        principles,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["entity"]["release"] = "2.83.0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_284(hole, hole["plane_interface"])
    kind_hole = copy.deepcopy(edge)
    kind_hole["expert_review"]["success"]["client_twin"]["kind"] = "ainav.sandbox.sku.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_284(kind_hole, kind_hole["plane_interface"])
    assigned_hole = copy.deepcopy(edge)
    assigned_hole["expert_review"]["success"]["client_twin"]["assigned"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_284(assigned_hole, assigned_hole["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "client-assigned" not in item.lower() and "segregated" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_284(principles_hole, principles_hole["plane_interface"])
