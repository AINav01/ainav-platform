from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard


def test_release_is_279():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.80.0"
    assert any("2.79.0" in item and "first-principles" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("2.78.0" in item and "refus" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    principles = cat["expert_review"]["first_principles"]
    assert len(principles) >= 20
    blob = " ".join(principles).lower()
    assert "identify is not admit" in blob
    assert "assignment_live" in blob
    assert "claiming 99" in blob
    assert "mfa admits" not in blob
    dash = public_dashboard()
    assert dash["release"] == "2.80.0"


def test_first_principles_refuse_invented_live():
    cat = load_catalog()
    owner = " ".join(cat["plane_interface"]["gaps"]["owner_only_open"]).lower()
    for stem in ("seat b", "graph write", "dataverse", "g12", "billing", "launch"):
        assert stem in owner
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "2.80.0" in html
    assert cat["investor"]["executive_summary"]["opens"] in html


def test_upgrade_49_is_tree_done():
    cat = load_catalog()
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 50
    assert upgrades[49]["who"] == "tree"
    assert upgrades[49]["done"] is True
    assert upgrades[49]["marks_live_pin"] is False
    blob = f"{upgrades[49]['title']} {upgrades[49]['do']}".lower()
    assert "first-principles" in blob
    assert "live_pin_ok" in blob


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_instrument_279_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.78.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.79.0" not in item
        ]

    def short(cat):
        cat["expert_review"]["first_principles"] = cat["expert_review"]["first_principles"][:19]

    def stems(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("Identify is not admit", "Access is required").replace(
                "assignment_live stays false", "views are assigned"
            ).replace("Claiming 99 without coverage is a lie", "Coverage is closed")
            for item in cat["expert_review"]["first_principles"]
        ]

    def claim(cat):
        cat["expert_review"]["first_principles"].append("MFA admits. LIVE_PIN_OK is closed.")

    for mutator in (release, closed, short, stems, claim):
        _reject(mutator)
