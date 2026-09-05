from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard


def test_release_is_278():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.84.0"
    assert any("2.78.0" in item and "refus" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("2.78.0" in item and "refus" in item.lower() for item in cat["plane_interface"]["gaps"]["in_tree_closed"])
    assert any("2.77.0" in item and "four reads" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    dash = public_dashboard()
    assert dash["release"] == "2.84.0"


def test_owner_gaps_stay_open_after_quality_check():
    cat = load_catalog()
    owner = " ".join(cat["plane_interface"]["gaps"]["owner_only_open"]).lower()
    for stem in ("seat b", "graph write", "dataverse", "g12", "billing", "launch"):
        assert stem in owner
    assert cat["plane_interface"]["gaps"]["claimed"] is False
    assert cat["plane_interface"]["gaps"]["live_pin_ok"] is False
    opens = cat["investor"]["executive_summary"]["opens"].lower()
    assert "graph write" in opens
    assert "graph read on the same" not in opens
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "2.84.0" in html
    assert "Graph Writes still Granted on the same Entra app" in html
    assert cat["investor"]["executive_summary"]["opens"] in html
    assert "Named dual seats, Graph Read, Dataverse" not in html
    assert "Graph Read on the same Entra app" not in html


def test_upgrade_48_is_tree_done():
    cat = load_catalog()
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 54
    assert upgrades[48]["who"] == "tree"
    assert upgrades[48]["done"] is True
    assert upgrades[48]["marks_live_pin"] is False
    blob = f"{upgrades[48]['title']} {upgrades[48]['do']}".lower()
    assert "refus" in blob
    assert "live_pin_ok" in blob


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_instrument_278_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.77.0"  # 279 pins current release; 278 history stays

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.78.0" not in item
        ]

    def closed_gaps(cat):
        cat["plane_interface"]["gaps"]["in_tree_closed"] = [
            item for item in cat["plane_interface"]["gaps"]["in_tree_closed"] if "2.78.0" not in item
        ]

    def stale_opens(cat):
        cat["investor"]["executive_summary"]["opens"] = (
            "Named dual seats. Graph Read on the same Entra app. LIVE_PIN_OK cannot be marked from this plane."
        )

    for mutator in (release, closed, closed_gaps, stale_opens):
        _reject(mutator)
