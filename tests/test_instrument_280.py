from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard


def test_release_is_280_and_gold_99_is_the_floor():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.83.0"
    assert cat["engineering"]["gold_ci"]["coverage_floor"] == 99
    assert cat["plane_interface"]["gaps"]["gold_floor"] == 99
    assert "fail_under = 99" in Path("pyproject.toml").read_text(encoding="utf-8")
    assert any("2.80.0" in item and "99" in item for item in cat["engineering"]["closed_in_tree"])
    assert any("2.79.0" in item and "first-principles" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("gold floor 95" in item.lower() for item in cat["plane_interface"]["gaps"]["in_tree_closed"])
    principles = cat["expert_review"]["first_principles"]
    assert len(principles) >= 20
    blob = " ".join(principles).lower()
    assert "identify is not admit" in blob
    assert "assignment_live" in blob
    assert "claiming 99" in blob
    assert "gold coverage floor is 99" in blob
    dash = public_dashboard()
    assert dash["release"] == "2.83.0"
    assert dash["gaps"]["gold_floor"] == 99


def test_upgrade_50_is_tree_done():
    cat = load_catalog()
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 53
    assert upgrades[50]["who"] == "tree"
    assert upgrades[50]["done"] is True
    assert upgrades[50]["marks_live_pin"] is False
    blob = f"{upgrades[50]['title']} {upgrades[50]['do']}".lower()
    assert "gold 99" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "2.83.0" in html
    assert "Gold floor 99" in Path("institute/app.html").read_text(encoding="utf-8")


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_instrument_280_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.79.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.80.0" not in item
        ]

    def floor(cat):
        cat["plane_interface"]["gaps"]["gold_floor"] = 95
        cat["engineering"]["gold_ci"]["coverage_floor"] = 95

    for mutator in (release, closed, floor):
        _reject(mutator)
