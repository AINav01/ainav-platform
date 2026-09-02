from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard
from ainav.microsoft.dns import catalog_edge


def test_release_is_274():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.75.0"
    assert "edge quality" in cat["equations"]["interface"]
    assert any("2.74.0" in item and "quality" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("2.73.0" in item and "floor" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert cat["engineering"]["gold_ci"]["coverage_floor"] == 95
    dash = public_dashboard()
    assert dash["release"] == "2.75.0"


def test_quality_never_claims_full_or_launch():
    quality = catalog_edge()["quality"]
    assert quality["ssl_full_claimed"] is False
    assert quality["apex_is_institute"] is False
    assert quality["rocket_loader_claimed"] is False
    assert quality["live"] is False
    assert quality["live_pin_ok"] is False
    assert quality["from_this_plane"] is False
    verified = " ".join(quality["verified"]).lower()
    assert "tls" in verified
    assert "anycast" in verified
    assert "13/13" in verified
    gaps = load_catalog()["plane_interface"]["gaps"]
    owner = " ".join(gaps["owner_only_open"]).lower()
    assert "seat b" in owner
    assert "ssl full confirm" not in owner
    assert "rocket loader" in owner
    hrefs = " ".join(gaps["owner_only_hrefs"].values())
    assert "e7-cloudflare" in hrefs
    assert any("quality" in item.lower() and "anycast" in item.lower() for item in gaps["in_tree_closed"])


def test_upgrades_41_to_44_are_tree_done():
    cat = load_catalog()
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 45
    for number in range(41, 45):
        assert upgrades[number]["who"] == "tree"
        assert upgrades[number]["done"] is True
        assert upgrades[number]["marks_live_pin"] is False


def test_sale_site_quality_board_lists_tls_and_anycast():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert "not Cloudflare anycast" in html
    assert "not proof of Full" in html
    assert "TLS 1.2 and 1.3" in html
    assert "rocket_loader_claimed" in js
    assert "2.75.0" in html
    assert "Full (strict)" in html
    assert "e7-cloudflare-owner-recorded" in html


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_instrument_274_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.73.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.74.0" not in item
        ]

    def ssl_full(cat):
        cat["microsoft_stack"]["edge"]["quality"]["ssl_full_claimed"] = True

    def apex(cat):
        cat["microsoft_stack"]["edge"]["quality"]["apex_is_institute"] = True

    def verified(cat):
        cat["microsoft_stack"]["edge"]["quality"]["verified"] = [
            item
            for item in cat["microsoft_stack"]["edge"]["quality"]["verified"]
            if "tls" not in item.lower() and "anycast" not in item.lower()
        ]

    def hrefs(cat):
        cat["plane_interface"]["gaps"]["owner_only_hrefs"].pop("Rocket Loader confirm", None)

    def probe_closed(cat):
        cat["plane_interface"]["gaps"]["in_tree_closed"] = [
            item
            for item in cat["plane_interface"]["gaps"]["in_tree_closed"]
            if "quality" not in item.lower()
        ]

    def interface(cat):
        cat["equations"]["interface"] = cat["equations"]["interface"].replace(" × edge quality", "")

    def well(cat):
        cat["expert_review"]["working_well"] = [
            item
            for item in cat["expert_review"]["working_well"]
            if "quality probe" not in item.lower() and "live cloudflare quality" not in item.lower()
        ]

    def improve(cat):
        cat["expert_review"]["improve"] = [
            item for item in cat["expert_review"]["improve"] if "rocket" not in item.lower()
        ]

    def upgrade(cat):
        cat["expert_review"]["upgrades"] = [
            item for item in cat["expert_review"]["upgrades"] if item.get("n") != 41
        ]

    for mutator in (
        release,
        closed,
        ssl_full,
        apex,
        verified,
        hrefs,
        probe_closed,
        interface,
        well,
        improve,
        upgrade,
    ):
        _reject(mutator)
