from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard
from ainav.microsoft.dns import catalog_edge


def test_release_keeps_275_history():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.76.0"
    assert any("2.75.0" in item and "full (strict)" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("2.74.0" in item and "quality" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    dash = public_dashboard()
    assert dash["release"] == "2.76.0"


def test_owner_ssl_is_recorded_not_claimed():
    quality = catalog_edge()["quality"]
    assert quality["ssl_full_claimed"] is False
    assert quality["owner_ssl"]["kind"] == "ainav.edge.owner_ssl.v1"
    assert quality["owner_ssl"]["automatic"] is True
    assert quality["owner_ssl"]["mode"] == "full_strict"
    assert quality["owner_ssl"]["from_this_plane"] is False
    assert quality["owner_ssl"]["live_pin_ok"] is False
    assert quality["owner_ssl"]["visitor_cert_is_not_proof"] is True
    assert quality["owner_ssl"]["flexible"] is False
    assert quality["owner_ssl"]["off"] is False
    assert any("full (strict)" in item.lower() for item in quality["owner_recorded"])
    gaps = load_catalog()["plane_interface"]["gaps"]
    owner = " ".join(gaps["owner_only_open"]).lower()
    assert "seat b" in owner
    assert "rocket" in owner
    assert "ssl full confirm" not in owner
    assert any("owner recorded" in item.lower() and "full (strict)" in item.lower() for item in gaps["in_tree_closed"])


def test_upgrade_45_is_tree_done():
    cat = load_catalog()
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 46
    assert upgrades[45]["who"] == "tree"
    assert upgrades[45]["done"] is True
    assert upgrades[45]["marks_live_pin"] is False
    assert "full (strict)" in f"{upgrades[45]['title']} {upgrades[45]['do']}".lower()


def test_sale_site_paints_owner_recorded_full_strict():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert "e7-cloudflare-owner-recorded" in html
    assert "Full (strict)" in html
    assert "Do not downgrade Full (strict)" in html
    assert "owner_recorded" in js
    assert "owner_ssl" in js


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_instrument_275_fail_closed():
    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.75.0" not in item
        ]

    def claimed(cat):
        cat["microsoft_stack"]["edge"]["quality"]["ssl_full_claimed"] = True

    def mode(cat):
        cat["microsoft_stack"]["edge"]["quality"]["owner_ssl"]["mode"] = "full"

    def plane(cat):
        cat["microsoft_stack"]["edge"]["quality"]["owner_ssl"]["from_this_plane"] = True

    def recorded(cat):
        cat["microsoft_stack"]["edge"]["quality"]["owner_recorded"] = ["something else"]

    def reopen(cat):
        cat["plane_interface"]["gaps"]["owner_only_open"].append("SSL Full confirm")

    def drop_closed(cat):
        cat["plane_interface"]["gaps"]["in_tree_closed"] = [
            item
            for item in cat["plane_interface"]["gaps"]["in_tree_closed"]
            if "full (strict)" not in item.lower()
        ]

    def well(cat):
        cat["expert_review"]["working_well"] = [
            item for item in cat["expert_review"]["working_well"] if "full (strict)" not in item.lower()
        ]

    def upgrade(cat):
        cat["expert_review"]["upgrades"] = [
            item for item in cat["expert_review"]["upgrades"] if item.get("n") != 45
        ]

    for mutator in (
        closed,
        claimed,
        mode,
        plane,
        recorded,
        reopen,
        drop_closed,
        well,
        upgrade,
    ):
        _reject(mutator)
