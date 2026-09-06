from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import BRAND_SURFACE_IDS, load_catalog, validate_catalog
from ainav.buyer import success_program
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_292_brand_system():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.92.0"
    brand = cat["expert_review"]["success"]["brand"]
    assert brand["kind"] == "ainav.brand.v1"
    assert brand["sku"] is False
    assert brand["cms"] is False
    assert brand["fear_brand"] is False
    assert brand["lockfile_stays_job_c"] is True
    assert brand["microsoft_is_the_product"] is False
    assert brand["trademark_filed"] is False
    assert [item["id"] for item in brand["surfaces"]] == BRAND_SURFACE_IDS
    assert brand["marks"]["legal"] == cat["entity"]["legal"]
    assert brand["marks"]["product"] == cat["entity"]["product"]
    assert brand["marks"]["institute"] == cat["entity"]["institute"]
    assert brand["marks"]["product"] == cat["ip"]["product_mark"]
    assert brand["marks"]["institute"] == cat["ip"]["institute_mark"]
    assert brand["marks"]["legal"] == cat["ip"]["owner"]
    assert brand["marks"]["lockfile"] == "job_c"
    assert "#brand" in brand["site"]
    assert "not a /brand route" in brand["site"].lower()
    assert cat["programs"]["website"]["brand"] is True
    assert cat["programs"]["website"]["brand_is_sku"] is False
    assert cat["programs"]["website"]["brand_href"] == "#brand"
    assert "#brand" in cat["operations"]["note"]
    assert any(
        "2.92.0" in item and "brand" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "brand system" in principles
    assert "lockfile stays job_c" in principles
    assert "write-fear" in principles
    assert "microsoft marks" in principles
    missing = " ".join(cat["honest_missing"]).lower()
    assert "trademark" in missing
    assert "apex brand" in missing
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 62
    assert upgrades[62]["who"] == "tree"
    assert upgrades[62]["done"] is True
    assert upgrades[62]["marks_live_pin"] is False
    blob = f"{upgrades[62]['title']} {upgrades[62]['do']}".lower()
    assert "brand" in blob
    assert "live_pin_ok" in blob
    exported = success_program()["brand"]
    assert exported["lede"] == brand["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "2.92.0" in html
    assert 'id="brand-surfaces"' in html
    assert 'id="brand-lede"' in html
    assert 'id="brand-status"' in html
    assert "brand-rebrand" in html
    assert "brand-fear" in html
    assert "brand-ms-product" in html
    assert "brand-teams-name" in html
    assert "brand-sandbox-prod" in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#brand"' not in nav
    assert 'href="/brand"' not in html
    assert "paintBrand" in js
    assert "#brand { scroll-margin-top" in css
    assert ".plane-strip a" in css
    assert "var(--gold-2)" in css.split(".plane-strip a", 1)[1]
    assert "index.html#brand" in twin
    assert "write-fear" in twin.lower()
    assert "not a fear brand" in twin.lower()
    assert 'id="app-floor-brand"' in app
    assert "index.html#brand" in app
    assert 'href="#brand"' in html.split('id="ops-note"', 1)[1].split("</p>", 1)[0]
    dash = public_dashboard()
    assert dash["release"] == "2.92.0"
    status = public_status()
    assert status["release"] == "2.92.0"
    assert status["website"]["brand"] is True
    assert status["website"]["brand_is_sku"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_292_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.91.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.92.0" not in item
        ]

    def brand_off(cat):
        cat["programs"]["website"]["brand"] = False

    def brand_sku(cat):
        cat["programs"]["website"]["brand_is_sku"] = True

    def product(cat):
        cat["programs"]["website"]["microsoft_is_the_product"] = True

    def kind(cat):
        cat["expert_review"]["success"]["brand"]["kind"] = "ainav.brand.v0"

    def fear(cat):
        cat["expert_review"]["success"]["brand"]["fear_brand"] = True

    def lockfile(cat):
        cat["expert_review"]["success"]["brand"]["lockfile_stays_job_c"] = False

    def marks(cat):
        cat["expert_review"]["success"]["brand"]["marks"]["product"] = "Fear Plane"

    def surfaces(cat):
        cat["expert_review"]["success"]["brand"]["surfaces"] = []

    def site(cat):
        cat["expert_review"]["success"]["brand"]["site"] = "Brand lives on /brand."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "brand system" not in item.lower()
        ]

    def missing(cat):
        cat["honest_missing"] = [
            item for item in cat["honest_missing"] if "trademark" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. The operating day is #firm."

    for mutator in (
        release,
        closed,
        brand_off,
        brand_sku,
        product,
        kind,
        fear,
        lockfile,
        marks,
        surfaces,
        site,
        principles,
        missing,
        ops,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["entity"]["release"] = "2.91.0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(hole, hole["plane_interface"])
    brand_hole = copy.deepcopy(edge)
    brand_hole["programs"]["website"]["brand"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(brand_hole, brand_hole["plane_interface"])
    fear_hole = copy.deepcopy(edge)
    fear_hole["expert_review"]["success"]["brand"]["fear_brand"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(fear_hole, fear_hole["plane_interface"])
    site_hole = copy.deepcopy(edge)
    site_hole["expert_review"]["success"]["brand"]["site"] = "Brand on /brand."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(site_hole, site_hole["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "brand system" not in item.lower() and "lockfile stays job_c" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(principles_hole, principles_hole["plane_interface"])
    missing_hole = copy.deepcopy(edge)
    missing_hole["honest_missing"] = [
        item for item in missing_hole["honest_missing"] if "trademark" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(missing_hole, missing_hole["plane_interface"])
    closed_hole = copy.deepcopy(edge)
    closed_hole["engineering"]["closed_in_tree"] = [
        item for item in closed_hole["engineering"]["closed_in_tree"] if "2.92.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(closed_hole, closed_hole["plane_interface"])
    sku_hole = copy.deepcopy(edge)
    sku_hole["programs"]["website"]["brand_is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(sku_hole, sku_hole["plane_interface"])
    mark_hole = copy.deepcopy(edge)
    mark_hole["expert_review"]["success"]["brand"]["marks"]["legal"] = "Fear, Inc."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(mark_hole, mark_hole["plane_interface"])


def test_brand_and_first_principles_fail_closed():
    cat = copy.deepcopy(load_catalog())
    brand = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    brand["sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_brand(brand)
    fear = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    fear["fear_brand"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_brand(fear)
    lock = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    lock["marks"]["lockfile"] = "fear_c"
    with pytest.raises(IntegrityError):
        catmod._validate_brand(lock)
    site = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    site["site"] = "Brand lives on /brand."
    with pytest.raises(IntegrityError):
        catmod._validate_brand(site)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "brand system" not in item.lower()
            ]
        )
    with pytest.raises(IntegrityError):
        catmod._validate_honest_missing(
            {
                **cat,
                "honest_missing": [
                    item for item in cat["honest_missing"] if "trademark" not in item.lower()
                ],
            }
        )
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item
        for item in ciso["ciso"]["does_not"]
        if "rebrand job c" not in item.lower() and "brand as a sku" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
