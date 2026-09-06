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


def test_release_is_289_first_class_microsoft_run():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.92.0"
    firm = cat["expert_review"]["success"]["operating_company"]
    run = firm["microsoft_run"]
    assert run["kind"] == "ainav.microsoft_run.v1"
    assert run["sku"] is False
    assert run["wired_claimed"] is False
    assert run["microsoft_is_the_product"] is False
    assert run["ninth_complement"] is False
    assert run["live_pin_ok"] is False
    assert len(run["required_ids"]) == 6
    assert len(run["complement_ids"]) == 8
    assert [item["id"] for item in run["spine"]] == run["required_ids"] + run["complement_ids"]
    assert all(item["wired"] is False and item["live"] is False for item in run["spine"])
    assert cat["programs"]["website"]["microsoft_run"] is True
    assert cat["programs"]["website"]["microsoft_run_is_sku"] is False
    assert cat["programs"]["website"]["microsoft_is_the_product"] is False
    assert any(
        "2.89.0" in item and "microsoft run" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 62
    assert upgrades[59]["who"] == "tree"
    assert upgrades[59]["done"] is True
    assert upgrades[59]["marks_live_pin"] is False
    blob = f"{upgrades[59]['title']} {upgrades[59]['do']}".lower()
    assert "microsoft run" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert "2.92.0" in html
    assert 'id="firm-ms"' in html
    assert "firm-wire-teams" in html
    assert "firm-close-dataverse" in html
    assert "firm-trash-writes" in html
    assert "microsoft_run" in js
    assert "index.html#firm-ms" in twin
    dash = public_dashboard()
    assert dash["release"] == "2.92.0"
    status = public_status()
    assert status["release"] == "2.92.0"
    assert status["website"]["microsoft_run"] is True
    assert status["website"]["microsoft_is_the_product"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_289_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.88.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.89.0" not in item
        ]

    def run_off(cat):
        cat["programs"]["website"]["microsoft_run"] = False

    def run_sku(cat):
        cat["programs"]["website"]["microsoft_run_is_sku"] = True

    def product(cat):
        cat["programs"]["website"]["microsoft_is_the_product"] = True

    def kind(cat):
        cat["expert_review"]["success"]["operating_company"]["microsoft_run"]["kind"] = "ainav.crm.v1"

    def wired(cat):
        cat["expert_review"]["success"]["operating_company"]["microsoft_run"]["wired_claimed"] = True

    def ninth(cat):
        cat["expert_review"]["success"]["operating_company"]["microsoft_run"]["complement_ids"] = (
            cat["expert_review"]["success"]["operating_company"]["microsoft_run"]["complement_ids"] + ["cloudflare.dns"]
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "microsoft run" not in item.lower()
        ]

    for mutator in (
        release,
        closed,
        run_off,
        run_sku,
        product,
        kind,
        wired,
        ninth,
        principles,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    kind_hole = copy.deepcopy(edge)
    kind_hole["expert_review"]["success"]["operating_company"]["microsoft_run"]["kind"] = "ainav.crm.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_289(kind_hole, kind_hole["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "microsoft run" not in item.lower()
        and "eight complements" not in item.lower()
        and "not the product" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_289(principles_hole, principles_hole["plane_interface"])
    product_hole = copy.deepcopy(edge)
    product_hole["expert_review"]["success"]["operating_company"]["microsoft_run"]["microsoft_is_the_product"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_289(product_hole, product_hole["plane_interface"])
    site_hole = copy.deepcopy(edge)
    site_hole["programs"]["website"]["microsoft_is_the_product"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_289(site_hole, site_hole["plane_interface"])
    required_hole = copy.deepcopy(edge)
    required_hole["connections"]["required_ids"] = ["azure.host"]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_289(required_hole, required_hole["plane_interface"])
    complements_hole = copy.deepcopy(edge)
    complements_hole["connections"]["complements"] = complements_hole["connections"]["complements"][:7]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_289(complements_hole, complements_hole["plane_interface"])
    ninth_flag = copy.deepcopy(edge)
    ninth_flag["expert_review"]["success"]["operating_company"]["microsoft_run"]["ninth_complement"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_289(ninth_flag, ninth_flag["plane_interface"])
