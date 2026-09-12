from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_POWER_PAGES_HREFS,
    HONEST_POWER_PAGES_REFUSE_IDS,
    HONEST_POWER_PAGES_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute
from ainav.power_pages import public_review


def test_release_is_309_honest_power_pages():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.21.0"
    pages = cat["honest_power_pages"]
    assert pages["kind"] == "ainav.honest.power_pages.v1"
    assert pages["honest"] is True
    assert pages["considered"] is True
    assert pages["is_host"] is False
    assert pages["is_sku"] is False
    assert pages["cms"] is False
    assert pages["closes_dataverse"] is False
    assert pages["certified"] is False
    assert pages["is_admit_plane"] is False
    assert pages["created"] is False
    assert pages["href"] == "#twin"
    refuse = [item for item in pages["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_POWER_PAGES_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_POWER_PAGES_REFUSE_TEXT[key] for key in HONEST_POWER_PAGES_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_POWER_PAGES_HREFS[key] for key in HONEST_POWER_PAGES_REFUSE_IDS}
    assert "honest power pages" in pages["note"].lower()
    assert "power pages is not the institute host" in pages["note"].lower()
    assert "power pages is not a sku" in pages["note"].lower()
    assert cat["programs"]["website"]["honest_power_pages"] is True
    assert cat["programs"]["website"]["honest_whole"] is True
    assert cat["programs"]["website"]["honest_power_pages_live"] is False
    assert cat["programs"]["website"]["power_pages_is_host"] is False
    assert cat["programs"]["website"]["power_pages_is_sku"] is False
    assert cat["programs"]["website"]["power_pages_is_cms"] is False
    assert cat["programs"]["website"]["power_pages_closes_dataverse"] is False
    assert "honest power pages" in cat["operations"]["note"].lower()
    assert "#twin" in cat["operations"]["note"]
    assert any("3.09.0" in item and "power pages" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "power pages as the institute host" in does_not
    assert "power pages as a sku" in does_not
    assert "power pages as the cms" in does_not
    assert "power pages as the institute apex" in does_not
    assert "power pages as a dataverse close" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest power pages" in principles
    assert "power pages is not the institute host" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 91
    assert upgrades[79]["who"] == "tree"
    assert upgrades[79]["done"] is True
    assert upgrades[79]["marks_live_pin"] is False
    blob = f"{upgrades[79]['title']} {upgrades[79]['do']}".lower()
    assert "honest power pages" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert "honest power pages" in html.lower()
    assert "power pages is not the institute host" in html.lower()
    assert "power pages is not a sku" in html.lower()
    assert 'id="pages-consider"' in html
    assert 'id="pages-zeros"' in html
    assert 'id="pages-facts"' in html
    assert 'data-pages-refuse="power_pages_as_host"' in html
    assert 'data-pages-refuse="power_pages_as_sku"' in html
    assert 'data-pages-refuse="power_pages_as_cms"' in html
    assert 'data-pages-refuse="power_pages_as_apex"' in html
    assert 'data-pages-refuse="power_pages_as_dataverse_close"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/power-pages"' not in nav
    assert 'href="#pages"' not in nav
    assert 'href="#pages-consider"' not in nav
    assert "Power Pages" not in nav
    assert "bindPagesRefuses" in js
    assert "refusePages" in js
    assert "pages-lede" not in js
    assert "whole-lede" not in js
    assert "industry-cert-lede" not in js
    assert "ready-lede" not in js
    assert "build-lede" not in js
    assert "operator-lede" not in js
    assert "access-lede" not in js
    assert "honest power pages" in twin.lower()
    assert "power pages is not the institute host" in twin.lower()
    assert "Digital twin · 3.21.0" in twin
    assert "AINAV.Institute twin · 3.21.0" in twin
    assert "3.07.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    assert "Application kit · 3.21.0" in kit
    assert "Power Pages is host" in identify
    assert "Open Power Pages" in identify
    assert "Power Pages is host" in app
    dash = public_dashboard()
    assert dash["release"] == "3.21.0"
    status = public_status()
    assert status["release"] == "3.21.0"
    assert status["website"]["honest_power_pages"] is True
    assert status["website"]["honest_power_pages_live"] is False
    assert status["website"]["power_pages_is_host"] is False
    assert status["website"]["power_pages_is_sku"] is False
    assert status["website"]["power_pages_is_cms"] is False
    assert status["website"]["power_pages_closes_dataverse"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.power_pages.v1"
    assert review["is_host"] is False
    assert "Treat Power Pages as the Institute host." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_309_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.08.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.09.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_power_pages"] = False

    def live(cat):
        cat["programs"]["website"]["honest_power_pages_live"] = True

    def host(cat):
        cat["programs"]["website"]["power_pages_is_host"] = True

    def sku(cat):
        cat["programs"]["website"]["power_pages_is_sku"] = True

    def cms(cat):
        cat["programs"]["website"]["power_pages_is_cms"] = True

    def dataverse(cat):
        cat["programs"]["website"]["power_pages_closes_dataverse"] = True

    def site(cat):
        cat["honest_power_pages"]["site"] = "Pages board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest power pages" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest whole sits on #whole."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. Not a webmaster CMS. Not Squarespace."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        host,
        sku,
        cms,
        dataverse,
        site,
        principles,
        ops,
        managed,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["honest_power_pages"]["kind"] = "ainav.honest.power_pages.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_power_pages"]["site"] = site_name["honest_power_pages"]["site"].replace(
        "Honest Power Pages",
        "Pages board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(site_name, site_name["plane_interface"])
    site_host = copy.deepcopy(edge)
    site_host["honest_power_pages"]["site"] = site_host["honest_power_pages"]["site"].replace(
        "Power Pages is not the Institute host. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(site_host, site_host["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_power_pages"]["site"] = site_route["honest_power_pages"]["site"].replace(
        "Not a /power-pages route. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_power_pages"]["site"] = site_glance["honest_power_pages"]["site"].replace(
        "First glance stays the write rail. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["honest_power_pages"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    success_missing = copy.deepcopy(edge["expert_review"]["success"])
    success_missing.pop("honest_power_pages")
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_missing)
    success_kind = copy.deepcopy(edge["expert_review"]["success"])
    success_kind["honest_power_pages"]["kind"] = "ainav.honest.power_pages.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_kind)
    success_href = copy.deepcopy(edge["expert_review"]["success"])
    success_href["honest_power_pages"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_href)
    success_host = copy.deepcopy(edge["expert_review"]["success"])
    success_host["honest_power_pages"]["is_host"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_host)
    success_sku = copy.deepcopy(edge["expert_review"]["success"])
    success_sku["honest_power_pages"]["is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_sku)
    success_cms = copy.deepcopy(edge["expert_review"]["success"])
    success_cms["honest_power_pages"]["cms"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_cms)
    success_dv = copy.deepcopy(edge["expert_review"]["success"])
    success_dv["honest_power_pages"]["closes_dataverse"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_dv)
    host_body = copy.deepcopy(edge)
    host_body["honest_power_pages"]["is_host"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(host_body, host_body["plane_interface"])
    sku_body = copy.deepcopy(edge)
    sku_body["honest_power_pages"]["is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(sku_body, sku_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_power_pages"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(certified, certified["plane_interface"])
    principles_direct = copy.deepcopy(edge)
    principles_direct["expert_review"]["first_principles"] = [
        item
        for item in principles_direct["expert_review"]["first_principles"]
        if "honest power pages" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(principles_direct, principles_direct["plane_interface"])
    principles_host = copy.deepcopy(edge)
    principles_host["expert_review"]["first_principles"] = [
        item.replace("Power Pages is not the Institute host.", "Power Pages is recorded.")
        for item in principles_host["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(principles_host, principles_host["plane_interface"])
    principles_first = copy.deepcopy(edge)
    principles_first["expert_review"]["first_principles"] = [
        item.replace("Honest Power Pages sits on #twin.", "Pages sit on #twin.")
        for item in principles_first["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_first["expert_review"]["first_principles"])
    ops_attach = copy.deepcopy(edge)
    ops_attach["operations"]["note"] = "Honest Power Pages sits on #twin."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(ops_attach, ops_attach["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest Power Pages is recorded."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(ops_href, ops_href["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. Pages sit on #twin."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(ops_name, ops_name["plane_interface"])
    managed_direct = copy.deepcopy(edge)
    managed_direct["expert_review"]["success"]["managed_face"]["managed"] = managed_direct["expert_review"]["success"]["managed_face"]["managed"].replace(
        " Not Power Pages.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_309(managed_direct, managed_direct["plane_interface"])
    for missing in (
        "Treat Power Pages as the Institute host",
        "Treat Power Pages as a SKU",
        "Treat Power Pages as the CMS",
        "Treat Power Pages as the Institute apex",
        "Treat Power Pages as a Dataverse close",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
