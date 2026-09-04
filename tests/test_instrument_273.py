from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard


def test_release_is_273():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.81.0"
    assert "provision spine" in cat["equations"]["interface"]
    assert "duty hints" in cat["equations"]["interface"]
    assert "board packet" in cat["equations"]["interface"]
    assert "lab pin" in cat["equations"]["interface"]
    assert "edge quality" in cat["equations"]["interface"]
    assert any("2.73.0" in item and "floor" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("2.72.0" in item and "95" in item for item in cat["engineering"]["closed_in_tree"])
    assert cat["engineering"]["gold_ci"]["coverage_floor"] == 99


def test_view_shows_keep_client_lean_and_owner_packet():
    cat = load_catalog()
    floor = cat["plane_interface"]["proof_day_floor"]
    shows = floor["view_shows"]
    assert "gaps" not in shows["client"]
    assert "estate" not in shows["client"]
    assert "audit" not in shows["client"]
    assert "gaps" in shows["owner"]
    assert "gaps" in shows["entire"]
    assert "board_packet" in shows["owner"]
    assert "provision_path" in shows["provision"]
    assert "board_packet" in floor["owner_shows"]
    assert "provision_path" in floor["provision_shows"]
    dash = public_dashboard()
    assert dash["release"] == "2.81.0"
    assert "board_packet" in dash["proof_day_floor"]["view_shows"]["owner"]
    assert dash["board_packet"]["ask"].lower().startswith("seat b")
    assert dash["lab_vs_commercial"]["lab_pin"] == "AINAV-L1"
    assert dash["lab_vs_commercial"]["commercial_close"] is False


def test_duty_hints_cover_every_view():
    cat = load_catalog()
    hints = cat["plane_interface"]["proof_day_floor"]["duty_hints"]
    for view in ("client", "entire", "owner", "seats", "examiner", "remote", "it", "provision", "records"):
        assert hints[view].strip()
    html = Path("institute/app.html").read_text(encoding="utf-8")
    js = Path("institute/app.js").read_text(encoding="utf-8")
    assert "paintDutyHints" in js
    assert "data-duty" in js
    assert 'id="app-view-tabs"' in html


def test_examiner_demo_leaf_and_typed_id_are_honest():
    cat = load_catalog()
    demo = cat["plane_interface"]["examiner_walk"]["demo"]
    assert demo["record_id"] == "lab.demo.inclusion"
    assert demo["included"] is True
    assert demo["lab"] is True
    js = Path("institute/app.js").read_text(encoding="utf-8")
    assert "lab.demo.inclusion" in js or "demo.record_id" in js
    assert "not wired live" in js
    html = Path("institute/app.html").read_text(encoding="utf-8")
    assert 'id="app-prove-wired"' in html


def test_gaps_owner_only_walk_to_owner_steps():
    cat = load_catalog()
    hrefs = cat["plane_interface"]["gaps"]["owner_only_hrefs"]
    blob = " ".join(hrefs.values())
    assert "missing" in blob
    assert "twin" in blob
    assert "stack-walk" in blob
    assert "open" in blob
    js = Path("institute/app.js").read_text(encoding="utf-8")
    assert "owner_only_hrefs" in js
    html = Path("institute/app.html").read_text(encoding="utf-8")
    assert 'id="app-floor-gaps"' in html


def test_provision_spine_and_board_packet_sit_the_floor():
    html = Path("institute/app.html").read_text(encoding="utf-8")
    js = Path("institute/app.js").read_text(encoding="utf-8")
    assert 'id="app-floor-provision"' in html
    assert 'id="app-floor-packet"' in html
    assert 'id="app-lab-pin"' in html
    assert 'id="app-catalog-unavailable"' in html
    assert "paintProvision" in js
    assert "paintBoardPacket" in js
    assert "paintLabPin" in js
    assert "showCatalogUnavailable" in js
    assert "Console: freeze requested" in js or "freeze requested" in js
    assert "view_shows" in js
    offer = html.split('id="app-floor-offer"', 1)[1].split("</div>", 1)[0].lower()
    assert "estate — same plane" not in offer
    assert "audit — same plane" not in offer


def test_sale_site_has_one_owner_book_and_thirteen_maps():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert html.count("Owner book") == 1
    assert "popovertarget" in html
    assert "<details class=\"nav-more\">" not in html
    assert 'href="#stack-walk"' in html
    assert "13 / claimed=false" in html
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    assert "app.html#floor" in plane
    assert "pointer" in plane.lower()
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert app.count("Owner book") == 1
    assert "popovertarget" not in app


def test_upgrades_33_to_40_are_tree_done():
    cat = load_catalog()
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 51
    for number in range(33, 41):
        assert upgrades[number]["who"] == "tree"
        assert upgrades[number]["done"] is True
        assert upgrades[number]["marks_live_pin"] is False


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_instrument_273_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.72.0"

    def view_shows(cat):
        cat["plane_interface"]["proof_day_floor"]["view_shows"]["client"].append("gaps")

    def owner_packet(cat):
        cat["plane_interface"]["proof_day_floor"]["view_shows"]["owner"] = [
            item
            for item in cat["plane_interface"]["proof_day_floor"]["view_shows"]["owner"]
            if item != "board_packet"
        ]

    def duty(cat):
        cat["plane_interface"]["proof_day_floor"]["duty_hints"].pop("owner")

    def demo(cat):
        cat["plane_interface"]["examiner_walk"]["demo"]["record_id"] = "invented"

    def hrefs(cat):
        cat["plane_interface"]["gaps"]["owner_only_hrefs"] = {}

    def lab(cat):
        cat["plane_interface"]["lab_vs_commercial"]["commercial_close"] = True

    def packet(cat):
        cat["plane_interface"]["board_packet"]["tile_ids"] = ["must_have"]

    def ask(cat):
        cat["plane_interface"]["board_packet"]["ask"] = "Launch now"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.73.0" not in item
        ]

    for mutator in (
        release,
        view_shows,
        owner_packet,
        duty,
        demo,
        hrefs,
        lab,
        packet,
        ask,
        closed,
    ):
        _reject(mutator)
