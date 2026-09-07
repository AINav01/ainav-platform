from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    INDUSTRY_DRAWER_AREA_HREFS,
    INDUSTRY_DRAWER_AREA_IDS,
    INDUSTRY_DRAWER_HREFS,
    INDUSTRY_DRAWER_LANE_IDS,
    INDUSTRY_DRAWER_PAPER_HREFS,
    INDUSTRY_DRAWER_PAPER_IDS,
    load_catalog,
    validate_catalog,
)
from ainav.buyer import success_program
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_296_sit_down_industry():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.97.0"
    drawer = cat["expert_review"]["success"]["industry_drawer"]
    assert drawer["kind"] == "ainav.industry_drawer.v1"
    assert drawer["sit_down"] is True
    assert drawer["drawer_is_live"] is False
    assert drawer["drawer_invented"] is False
    assert drawer["certified"] is False
    assert drawer["sku"] is False
    assert drawer["named_vertical"] is False
    assert drawer["filing"] is False
    assert [item["id"] for item in drawer["lanes"]] == INDUSTRY_DRAWER_LANE_IDS
    hrefs = {
        row["id"]: row["href"]
        for lane in drawer["lanes"]
        for row in lane["items"]
    }
    assert hrefs == INDUSTRY_DRAWER_HREFS
    assert [item["id"] for item in drawer["papers"]] == INDUSTRY_DRAWER_PAPER_IDS
    assert {item["id"]: item["href"] for item in drawer["papers"]} == INDUSTRY_DRAWER_PAPER_HREFS
    assert [item["id"] for item in drawer["areas"]] == INDUSTRY_DRAWER_AREA_IDS
    assert {item["id"]: item["href"] for item in drawer["areas"]} == INDUSTRY_DRAWER_AREA_HREFS
    assert "sit / maps / attach / refuse" in drawer["site"].lower()
    assert "not a /industry route" in drawer["site"].lower()
    assert cat["programs"]["website"]["industry_drawer"] is True
    assert cat["programs"]["website"]["industry_drawer_live"] is False
    assert cat["programs"]["website"]["industry_certified"] is False
    assert cat["programs"]["website"]["industry_href"] == "#industry"
    assert "sit-down industry drawer" in cat["operations"]["note"].lower()
    assert "#industry" in cat["operations"]["note"].lower()
    assert any(
        "2.96.0" in item and "sit-down" in item.lower() and "industry" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "sit-down industry drawer" in principles
    assert "maps stay claimed=false" in principles
    assert "not a /industry route" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 67
    assert upgrades[66]["who"] == "tree"
    assert upgrades[66]["done"] is True
    assert upgrades[66]["marks_live_pin"] is False
    blob = f"{upgrades[66]['title']} {upgrades[66]['do']}".lower()
    assert "sit-down industry" in blob
    assert "live_pin_ok" in blob
    exported = success_program()["industry_drawer"]
    assert exported["drawer_is_live"] is False
    html = Path("institute/index.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "2.97.0" in html
    assert 'id="industry-day"' in html
    assert 'data-lane="sit"' in html
    assert 'data-lane="maps"' in html
    assert 'data-lane="attach"' in html
    assert 'data-lane="refuse"' in html
    assert 'id="industry-papers"' in html
    assert 'id="industry-areas"' in html
    assert 'id="industry-refuse"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#industry"' not in nav
    assert 'href="#universe"' not in nav
    assert "paintIndustryDrawer" in js
    assert "refuseIndustry" in js
    assert ".industry-day" in css
    assert "sit-down industry" in twin.lower() or "sit / maps / attach" in twin.lower()
    assert "mfa identifies" in twin.lower()
    assert 'id="app-floor-industry"' in app
    assert "not SKUs" in app or "not skus" in app.lower()
    assert 'id="identify-industry"' in identify
    dash = public_dashboard()
    assert dash["release"] == "2.97.0"
    status = public_status()
    assert status["release"] == "2.97.0"
    assert status["website"]["industry_drawer"] is True
    assert status["website"]["industry_drawer_live"] is False
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_296_fail_closed():
    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.96.0" not in item
        ]

    def drawer_off(cat):
        cat["programs"]["website"]["industry_drawer"] = False

    def drawer_live(cat):
        cat["programs"]["website"]["industry_drawer_live"] = True

    def certified(cat):
        cat["programs"]["website"]["industry_certified"] = True

    def href_off(cat):
        cat["programs"]["website"]["industry_href"] = "/industry"

    def sku_on(cat):
        cat["programs"]["website"]["industry_is_sku"] = True

    def invented(cat):
        cat["expert_review"]["success"]["industry_drawer"]["drawer_invented"] = True

    def lanes(cat):
        cat["expert_review"]["success"]["industry_drawer"]["lanes"] = []

    def site(cat):
        cat["expert_review"]["success"]["industry_drawer"]["site"] = (
            "Industry drawer on #industry. Packs is #packs. Not a /industry route."
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "sit-down industry drawer" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. The operating day is #firm. Brand is #brand. "
            "The client universe is #universe. Sit-down client day."
        )

    for mutator in (
        closed,
        drawer_off,
        drawer_live,
        certified,
        href_off,
        sku_on,
        invented,
        lanes,
        site,
        principles,
        ops,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["engineering"]["closed_in_tree"] = [
        item for item in hole["engineering"]["closed_in_tree"] if "2.96.0" not in item
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_296(hole, hole["plane_interface"])
    live = copy.deepcopy(edge)
    live["expert_review"]["success"]["industry_drawer"]["drawer_is_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_296(live, live["plane_interface"])
    empty = copy.deepcopy(edge)
    empty["expert_review"]["success"]["industry_drawer"]["lanes"] = []
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_296(empty, empty["plane_interface"])
    site_note = copy.deepcopy(edge)
    site_note["expert_review"]["success"]["industry_drawer"]["site"] = (
        "Industry drawer on #industry. Packs is #packs. Maps is #governance. Not a /industry route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_296(site_note, site_note["plane_interface"])
    principles_hole = copy.deepcopy(edge)
    principles_hole["expert_review"]["first_principles"] = [
        item
        for item in principles_hole["expert_review"]["first_principles"]
        if "sit-down industry drawer" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_296(principles_hole, principles_hole["plane_interface"])
    certified_drawer = copy.deepcopy(edge)
    certified_drawer["expert_review"]["success"]["industry_drawer"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_296(certified_drawer, certified_drawer["plane_interface"])
    sit_note = copy.deepcopy(edge)
    sit_note["expert_review"]["success"]["industry_drawer"]["site"] = (
        "Packs is #packs. Maps is #governance. Sit / maps / attach / refuse. Not a /industry route."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_296(sit_note, sit_note["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = (
        "SKU attach chain. The industry bench is #industry. Packs are not SKUs."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_296(ops_hole, ops_hole["plane_interface"])


def test_industry_drawer_fail_closed():
    cat = copy.deepcopy(load_catalog())
    hole = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    hole["sit_down"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(hole)
    live = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    live["drawer_is_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(live)
    certified = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    certified["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(certified)
    named = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    named["lanes"][0]["items"][0]["href"] = "/healthcare"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(named)
    papers = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    papers["papers"] = []
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(papers)
    areas = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    areas["areas"][0]["href"] = "/industry"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(areas)
    site = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    site["site"] = "Industry drawer on #industry. Not a /industry route."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(site)
    lede = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    lede["lede"] = "Who we sit and what we attach."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(lede)
    glance = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    glance["glance"] = "Maps claimed=false. Not LIVE_PIN_OK."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(glance)
    note = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    note["note"] = "Packs are not SKUs. Maps stay claimed=false."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(note)
    refuse = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    refuse["refuse"] = ["Treat maps as certificates"]
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(refuse)
    owner = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    owner["owner_only"] = ["Signed L1"]
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(owner)
    paper_href = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    paper_href["papers"][0]["href"] = "/whitepaper"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(paper_href)
    paper_note = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    paper_note["papers"][0]["note"] = "A paper."
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(paper_note)
    flag = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    flag["sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(flag)
    kind = copy.deepcopy(cat["expert_review"]["success"]["industry_drawer"])
    kind["kind"] = "ainav.industry.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_industry_drawer(kind)
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(
            [
                item
                for item in cat["expert_review"]["first_principles"]
                if "sit-down industry drawer" not in item.lower()
            ]
        )
    ciso = copy.deepcopy(cat["expert_review"]["success"])
    ciso["ciso"]["does_not"] = [
        item
        for item in ciso["ciso"]["does_not"]
        if "industry drawer as a live filing" not in item.lower()
        and "named vertical as a sku" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso)
