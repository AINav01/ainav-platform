from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import OPERATING_DAY_IDS, load_catalog, validate_catalog
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_290_microsoft_day_map():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.11.0"
    firm = cat["expert_review"]["success"]["operating_company"]
    run = firm["microsoft_run"]
    assert run["kind"] == "ainav.microsoft_run.v1"
    assert [item["id"] for item in run["day_map"]] == OPERATING_DAY_IDS
    assert all(item["wired"] is False and item["live"] is False for item in run["day_map"])
    assign = next(item for item in run["day_map"] if item["id"] == "assign")
    assert assign["on"] == ["azure.host"]
    assert "sandbox" in assign["note"].lower()
    azure = next(item for item in run["spine"] if item["id"] == "azure.host")
    assert azure["days"] == ["proof", "assign"]
    assert cat["programs"]["website"]["microsoft_day_map"] is True
    assert cat["programs"]["website"]["microsoft_day_map_is_sku"] is False
    assert any(
        "2.90.0" in item and "day map" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 81
    assert upgrades[60]["who"] == "tree"
    assert upgrades[60]["done"] is True
    assert upgrades[60]["marks_live_pin"] is False
    blob = f"{upgrades[60]['title']} {upgrades[60]['do']}".lower()
    assert "day map" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert "3.11.0" in html
    assert 'id="firm-ms-day"' in html
    assert "firm-wire-day" in html
    assert "firm-day-on-assign" in html
    assert "day_map" in js
    assert "index.html#firm-ms" in twin
    assert "day map" in twin.lower()
    dash = public_dashboard()
    assert dash["release"] == "3.11.0"
    status = public_status()
    assert status["release"] == "3.11.0"
    assert status["website"]["microsoft_day_map"] is True
    assert status["website"]["microsoft_day_map_is_sku"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_290_fail_closed():
    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.90.0" not in item
        ]

    def map_off(cat):
        cat["programs"]["website"]["microsoft_day_map"] = False

    def map_sku(cat):
        cat["programs"]["website"]["microsoft_day_map_is_sku"] = True

    def product(cat):
        cat["programs"]["website"]["microsoft_is_the_product"] = True

    def day_ids(cat):
        cat["expert_review"]["success"]["operating_company"]["microsoft_run"]["day_map"] = [
            {"id": "crm", "on": ["sales.enterprise"], "wired": False, "live": False, "note": "CRM"}
        ]

    def wired(cat):
        cat["expert_review"]["success"]["operating_company"]["microsoft_run"]["day_map"][0]["wired"] = True

    def live_map(cat):
        cat["expert_review"]["success"]["operating_company"]["microsoft_run"]["day_map"][3]["live"] = True

    def assign_off(cat):
        for item in cat["expert_review"]["success"]["operating_company"]["microsoft_run"]["day_map"]:
            if item.get("id") == "assign":
                item["on"] = ["sales.enterprise"]

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "day map" not in item.lower()
        ]

    for mutator in (
        closed,
        map_off,
        map_sku,
        product,
        day_ids,
        wired,
        live_map,
        assign_off,
        principles,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    map_hole = copy.deepcopy(edge)
    map_hole["programs"]["website"]["microsoft_day_map"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_290(map_hole, map_hole["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "day map" not in item.lower()
        and "assign sits on azure host" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_290(principles_hole, principles_hole["plane_interface"])
    assign_hole = copy.deepcopy(edge)
    for item in assign_hole["expert_review"]["success"]["operating_company"]["microsoft_run"]["day_map"]:
        if item.get("id") == "assign":
            item["on"] = ["sharepoint.kit"]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_290(assign_hole, assign_hole["plane_interface"])
    live_hole = copy.deepcopy(edge)
    live_hole["expert_review"]["success"]["operating_company"]["microsoft_run"]["day_map"][3]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_290(live_hole, live_hole["plane_interface"])
    ids_hole = copy.deepcopy(edge)
    ids_hole["expert_review"]["success"]["operating_company"]["microsoft_run"]["day_map"] = []
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_290(ids_hole, ids_hole["plane_interface"])
