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


def test_release_is_283_managed_first_class_face():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.83.0"
    assert cat["expert_review"]["success"]["managed_face"]["kind"] == "ainav.managed_face.v1"
    assert cat["programs"]["website"]["managed"] is True
    assert cat["programs"]["website"]["first_class"] is True
    assert cat["programs"]["website"]["dynamic"] is False
    assert any("2.83.0" in item and "first-class" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 53
    assert upgrades[53]["who"] == "tree"
    assert upgrades[53]["done"] is True
    assert upgrades[53]["marks_live_pin"] is False
    blob = f"{upgrades[53]['title']} {upgrades[53]['do']}".lower()
    assert "first-class" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "2.83.0" in html
    assert 'id="demo-console"' in html
    assert 'id="product-stage"' in html
    dash = public_dashboard()
    assert dash["release"] == "2.83.0"
    status = public_status()
    assert status["release"] == "2.83.0"
    assert status["website"]["managed"] is True
    assert status["website"]["first_class"] is True
    assert status["website"]["dynamic"] is False
    assert status["website"]["demo_path"] == "#twin"
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_283_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.82.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.83.0" not in item
        ]

    def managed(cat):
        cat["programs"]["website"]["managed"] = False

    def dynamic(cat):
        cat["programs"]["website"]["dynamic"] = True

    def kind(cat):
        cat["expert_review"]["success"]["managed_face"]["kind"] = "ainav.cms.v1"

    for mutator in (release, closed, managed, dynamic, kind):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["entity"]["release"] = "2.82.0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_283(hole, hole["plane_interface"])
