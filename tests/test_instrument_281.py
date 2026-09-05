from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute, publish_twin


def test_release_is_281_twin_website_for_review():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.84.0"
    assert cat["programs"]["website"]["twin_review"] is True
    assert cat["programs"]["website"]["review_path"] == "twin.html"
    assert cat["programs"]["website"]["authorized_release"] is False
    assert cat["programs"]["website"]["launch_ready"] is False
    assert any("2.81.0" in item and "twin" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 54
    assert upgrades[51]["who"] == "tree"
    assert upgrades[51]["done"] is True
    assert upgrades[51]["marks_live_pin"] is False
    blob = f"{upgrades[51]['title']} {upgrades[51]['do']}".lower()
    assert "twin website" in blob
    assert "live_pin_ok" in blob
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "twin website" in principles
    assert "publish-twin" in principles
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert "2.84.0" in html
    assert 'id="twin-review"' in html
    assert 'href="twin.html"' in html
    assert "Twin review" in twin
    assert "publish-twin" in twin
    assert "launch_not_ready" in twin
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert "twin.html" not in nav
    assert 'href="#twin-review"' not in nav
    assert "twin-review-status" in js
    dash = public_dashboard()
    assert dash["release"] == "2.84.0"
    status = public_status()
    assert status["release"] == "2.84.0"
    assert status["website"]["twin_review"] is True
    assert status["website"]["review_path"] == "twin.html"
    assert status["website"]["authorized_release"] is False


def test_publish_institute_stays_held_publish_twin_is_not_launch():
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    assert held["uploaded"] is False
    assert held["live_pin_ok"] is False
    assert "publish-twin" in (held.get("note") or "")


def test_instrument_281_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.80.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.81.0" not in item
        ]

    def review(cat):
        cat["programs"]["website"]["twin_review"] = False

    def path(cat):
        cat["programs"]["website"]["review_path"] = "index.html"

    def launch(cat):
        cat["programs"]["website"]["launch_ready"] = True

    def authorized(cat):
        cat["programs"]["website"]["authorized_release"] = True

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "twin website" not in item.lower()
        ]

    for mutator in (release, closed, review, path, launch, authorized, principles):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["programs"]["website"]["twin_review"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_281(hole, hole["plane_interface"])
    hole = copy.deepcopy(edge)
    hole["programs"]["website"]["review_path"] = "app.html"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_281(hole, hole["plane_interface"])
    hole = copy.deepcopy(edge)
    hole["programs"]["website"]["authorized_release"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_281(hole, hole["plane_interface"])
    hole = copy.deepcopy(edge)
    hole["programs"]["website"]["launch_ready"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_281(hole, hole["plane_interface"])
