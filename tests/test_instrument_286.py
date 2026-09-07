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


def test_release_is_286_first_class_operating_company():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.01.0"
    firm = cat["expert_review"]["success"]["operating_company"]
    assert firm["kind"] == "ainav.operating_company.v1"
    assert firm["sku"] is False
    assert firm["crm"] is False
    assert firm["sales_team_claimed"] is False
    assert firm["payouts_booked"] is False
    assert firm["live_pin_ok"] is False
    assert firm["capacity"]["live"] == 0
    assert firm["capacity"]["pipeline"] == 0
    assert cat["programs"]["website"]["operating_company"] is True
    assert cat["programs"]["website"]["firm_is_sku"] is False
    assert cat["programs"]["website"]["firm_href"] == "#firm"
    assert any("2.86.0" in item and "operating company" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 71
    assert upgrades[56]["who"] == "tree"
    assert upgrades[56]["done"] is True
    assert upgrades[56]["marks_live_pin"] is False
    blob = f"{upgrades[56]['title']} {upgrades[56]['do']}".lower()
    assert "operating company" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "3.01.0" in html
    assert 'id="firm-console"' in html
    assert 'id="firm-rails"' in html
    dash = public_dashboard()
    assert dash["release"] == "3.01.0"
    status = public_status()
    assert status["release"] == "3.01.0"
    assert status["website"]["operating_company"] is True
    assert status["website"]["firm_is_sku"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_286_fail_closed():
    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.86.0" not in item
        ]

    def kind(cat):
        cat["expert_review"]["success"]["operating_company"]["kind"] = "ainav.crm.v1"

    def team(cat):
        cat["expert_review"]["success"]["operating_company"]["sales_team_claimed"] = True

    def pay(cat):
        cat["expert_review"]["success"]["operating_company"]["payouts_booked"] = True

    def sku(cat):
        cat["expert_review"]["success"]["operating_company"]["sku"] = True

    def firm_off(cat):
        cat["programs"]["website"]["operating_company"] = False

    def firm_sku(cat):
        cat["programs"]["website"]["firm_is_sku"] = True

    def href(cat):
        cat["programs"]["website"]["firm_href"] = "/firm"

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "operating company" not in item.lower()
        ]

    for mutator in (
        closed,
        kind,
        team,
        pay,
        sku,
        firm_off,
        firm_sku,
        href,
        principles,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    kind_hole = copy.deepcopy(edge)
    kind_hole["expert_review"]["success"]["operating_company"]["kind"] = "ainav.crm.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_286(kind_hole, kind_hole["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "operating company" not in item.lower() and "five hundred" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_286(principles_hole, principles_hole["plane_interface"])
    pay_hole = copy.deepcopy(edge)
    pay_hole["expert_review"]["success"]["operating_company"]["payouts_booked"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_286(pay_hole, pay_hole["plane_interface"])
    crm_site = copy.deepcopy(edge)
    crm_site["programs"]["website"]["firm_is_crm"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_286(crm_site, crm_site["plane_interface"])
