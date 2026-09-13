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
    assert cat["entity"]["release"] == "3.28.0"
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
    assert len(cat["expert_review"]["upgrades"]) == 98
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
    assert "3.14.0" in html
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
    assert dash["release"] == "3.28.0"
    status = public_status()
    assert status["release"] == "3.28.0"
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
    brand_hole = copy.deepcopy(edge)
    kind_run = copy.deepcopy(edge)
    kind_run["expert_review"]["success"]["brand"]["kind"] = "ainav.brand.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(kind_run, kind_run["plane_interface"])
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
    for flag in (
        "fourth_sku",
        "cms",
        "live",
        "live_pin_ok",
        "launch",
        "trademark_filed",
        "microsoft_is_the_product",
    ):
        hole = copy.deepcopy(cat["expert_review"]["success"]["brand"])
        hole[flag] = True
        with pytest.raises(IntegrityError):
            catmod._validate_brand(hole)
    kind = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    kind["kind"] = "ainav.brand.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_brand(kind)
    lockflag = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    lockflag["lockfile_stays_job_c"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_brand(lockflag)
    legal = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    legal["marks"]["legal"] = "Fear, Inc."
    with pytest.raises(IntegrityError):
        catmod._validate_brand(legal)
    institute = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    institute["marks"]["institute"] = "Fear.Institute"
    with pytest.raises(IntegrityError):
        catmod._validate_brand(institute)
    job = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    job["marks"]["job"] = "Job D"
    with pytest.raises(IntegrityError):
        catmod._validate_brand(job)
    voice = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    voice["voice"] = {"ours": "authority", "not_ours": "something else"}
    with pytest.raises(IntegrityError):
        catmod._validate_brand(voice)
    surfaces = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    surfaces["surfaces"] = []
    with pytest.raises(IntegrityError):
        catmod._validate_brand(surfaces)
    stem = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    stem["surfaces"][0]["note"] = "A corporation."
    with pytest.raises(IntegrityError):
        catmod._validate_brand(stem)
    face = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    face["face"]["paper"] = "#ffffff"
    with pytest.raises(IntegrityError):
        catmod._validate_brand(face)
    gold = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    gold["face"]["gold"] = "#000000"
    with pytest.raises(IntegrityError):
        catmod._validate_brand(gold)
    void = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    void["face"]["void"] = "#000000"
    with pytest.raises(IntegrityError):
        catmod._validate_brand(void)
    fonts = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    fonts["face"]["display"] = "Comic Sans"
    with pytest.raises(IntegrityError):
        catmod._validate_brand(fonts)
    theme = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    theme["face"]["note"] = "A theme."
    with pytest.raises(IntegrityError):
        catmod._validate_brand(theme)
    refuse = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    refuse["refuse"] = ["something else"]
    with pytest.raises(IntegrityError):
        catmod._validate_brand(refuse)
    owner = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    owner["owner_only"] = ["something else"]
    with pytest.raises(IntegrityError):
        catmod._validate_brand(owner)
    firm_site = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    firm_site["site"] = "Brand system on #brand. Not a /brand route."
    with pytest.raises(IntegrityError):
        catmod._validate_brand(firm_site)
    note = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    note["note"] = "Marks stay catalog law."
    with pytest.raises(IntegrityError):
        catmod._validate_brand(note)
    lede = copy.deepcopy(cat["expert_review"]["success"]["brand"])
    lede["lede"] = "A mark set."
    with pytest.raises(IntegrityError):
        catmod._validate_brand(lede)
    marks_principles = list(cat["expert_review"]["first_principles"])
    marks_principles = [
        item.replace("Microsoft marks are theirs", "Marks stay mixed")
        if "brand system" in item.lower()
        else item
        for item in marks_principles
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(marks_principles)
    sandbox_principles = list(cat["expert_review"]["first_principles"])
    sandbox_principles = [
        item.replace("The sandbox is not a production brand", "The sandbox is a review surface")
        .replace("Not a fear brand", "Not a slogan")
        if "brand system" in item.lower()
        else item
        for item in sandbox_principles
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(sandbox_principles)
    href = copy.deepcopy(cat)
    href["programs"]["website"]["brand_href"] = "/brand"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(href, href["plane_interface"])
    cms = copy.deepcopy(cat)
    cms["expert_review"]["success"]["brand"]["cms"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(cms, cms["plane_interface"])
    lock_run = copy.deepcopy(cat)
    lock_run["expert_review"]["success"]["brand"]["lockfile_stays_job_c"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(lock_run, lock_run["plane_interface"])
    ip_mark = copy.deepcopy(cat)
    ip_mark["ip"]["institute_mark"] = "Fear.Institute"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(ip_mark, ip_mark["plane_interface"])
    product_ip = copy.deepcopy(cat)
    product_ip["ip"]["product_mark"] = "Fear Plane"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(product_ip, product_ip["plane_interface"])
    surfaces_run = copy.deepcopy(cat)
    surfaces_run["expert_review"]["success"]["brand"]["surfaces"] = []
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(surfaces_run, surfaces_run["plane_interface"])
    write = copy.deepcopy(cat)
    write["expert_review"]["first_principles"] = [
        item.replace("Write-fear", "Authority").replace("write-fear", "authority")
        for item in write["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(write, write["plane_interface"])
    ops_sku = copy.deepcopy(cat)
    ops_sku["operations"]["note"] = "The brand is #brand. The operating day is elsewhere."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(ops_sku, ops_sku["plane_interface"])
    ops_brand = copy.deepcopy(cat)
    ops_brand["operations"]["note"] = "SKU attach chain. The operating day is #firm."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(ops_brand, ops_brand["plane_interface"])
    apex = copy.deepcopy(cat)
    apex["honest_missing"] = [
        item if "trademark" not in item.lower() else "Trademark filing stays owner-only."
        for item in apex["honest_missing"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_292(apex, apex["plane_interface"])
