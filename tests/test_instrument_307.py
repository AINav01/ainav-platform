from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_INDUSTRY_HREFS,
    HONEST_INDUSTRY_REFUSE_IDS,
    HONEST_INDUSTRY_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.industry_certify import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_307_honest_industry():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.13.0"
    industry = cat["industry_certify"]
    assert industry["kind"] == "ainav.honest.industry.v1"
    assert industry["honest"] is True
    assert industry["complete"] is True
    assert industry["packs_are_skus"] is False
    assert industry["industry_certified_launch"] is False
    assert industry["certified"] is False
    assert industry["is_admit_plane"] is False
    assert [item["id"] for item in industry["rows"]] == [item["id"] for item in cat["industry_packs"]]
    refuse = [item for item in industry["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_INDUSTRY_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_INDUSTRY_REFUSE_TEXT[key] for key in HONEST_INDUSTRY_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_INDUSTRY_HREFS[key] for key in HONEST_INDUSTRY_REFUSE_IDS}
    assert all(item["sku"] is False and item["seat"] is not True for item in industry["rows"])
    assert "honest industry" in industry["note"].lower()
    assert "packs are not skus" in industry["note"].lower()
    assert "industry certify is not launch" in industry["note"].lower()
    assert "industry certify is not launch" in industry["lede"].lower()
    assert cat["programs"]["website"]["honest_industry"] is True
    assert cat["programs"]["website"]["honest_readiness"] is True
    assert cat["programs"]["website"]["honest_industry_live"] is False
    assert cat["programs"]["website"]["industry_certified_launch"] is False
    assert cat["programs"]["website"]["packs_are_skus"] is False
    assert "honest industry" in cat["operations"]["note"].lower()
    assert any("3.07.0" in item and "honest industry" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "an industry pack as a sku" in does_not
    assert "a library as a sku" in does_not
    assert "a repository as a sku" in does_not
    assert "industry certify as launch" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest industry certify" in principles
    assert "industry certify is not launch" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 83
    assert upgrades[77]["who"] == "tree"
    assert upgrades[77]["done"] is True
    assert upgrades[77]["marks_live_pin"] is False
    blob = f"{upgrades[77]['title']} {upgrades[77]['do']}".lower()
    assert "honest industry" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.13.0" in html
    assert "honest industry" in html.lower()
    assert "industry certify is not launch" in html.lower()
    assert "packs are not skus" in html.lower()
    assert 'id="industry-cert-rows"' in html
    assert 'data-industry-refuse="industry_pack_as_sku"' in html
    assert 'data-industry-refuse="industry_lib_as_sku"' in html
    assert 'data-industry-refuse="industry_repo_as_sku"' in html
    assert 'data-industry-refuse="named_vertical_as_sku"' in html
    assert 'data-industry-refuse="industry_certify_as_launch"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#packs"' not in nav
    assert 'href="/industry"' not in nav
    assert 'href="/packs"' not in nav
    assert "bindIndustryRefuses" in js
    assert "refuseIndustry" in js
    assert "industry-cert-lede" not in js
    assert "ready-lede" not in js
    assert "build-lede" not in js
    assert "operator-lede" not in js
    assert "access-lede" not in js
    assert "agent-tools-lede" not in js
    assert "honest industry" in twin.lower()
    assert "industry certify is not launch" in twin.lower()
    assert "industry" in app.lower()
    assert "Packs are SKUs" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.13.0"
    status = public_status()
    assert status["release"] == "3.13.0"
    assert status["website"]["honest_industry"] is True
    assert status["website"]["honest_industry_live"] is False
    assert status["website"]["industry_certified_launch"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.industry.v1"
    assert review["packs_are_skus"] is False
    assert "Treat industry certify as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_307_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.06.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.07.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_industry"] = False

    def live(cat):
        cat["programs"]["website"]["honest_industry_live"] = True

    def packs(cat):
        cat["industry_certify"]["packs_are_skus"] = True

    def launch(cat):
        cat["industry_certify"]["industry_certified_launch"] = True

    def site(cat):
        cat["industry_certify"]["site"] = "Industry on #packs."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest industry certify" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. Honest readiness sits on #agent-tools. Gold is not launch."
        )

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "industry pack as a sku" not in item.lower() and "industry certify as launch" not in item.lower()
        ]

    for mutator in (release, closed, flag_off, live, packs, launch, site, principles, ops, ciso):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["industry_certify"]["kind"] = "ainav.honest.industry.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(hole, hole["plane_interface"])
    needed = copy.deepcopy(edge)
    needed["industry_certify"]["packs_are_skus"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(needed, needed["plane_interface"])
    day_flag = copy.deepcopy(edge)
    day_flag["industry_certify"]["industry_certified_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(day_flag, day_flag["plane_interface"])
    cert = copy.deepcopy(edge)
    cert["industry_certify"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(cert, cert["plane_interface"])
    site_hole = copy.deepcopy(edge)
    site_hole["industry_certify"]["site"] = site_hole["industry_certify"]["site"].replace(
        "Packs are not SKUs. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(site_hole, site_hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["industry_certify"]["site"] = site_name["industry_certify"]["site"].replace(
        "Honest industry certify",
        "Industry board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(site_name, site_name["plane_interface"])
    site_launch = copy.deepcopy(edge)
    site_launch["industry_certify"]["site"] = site_launch["industry_certify"]["site"].replace(
        "Industry certify is not launch. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(site_launch, site_launch["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["industry_certify"]["site"] = site_route["industry_certify"]["site"].replace(
        "Not a /industry route. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(site_route, site_route["plane_interface"])
    ready_off = copy.deepcopy(edge)
    ready_off["programs"]["website"]["honest_readiness"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(ready_off, ready_off["plane_interface"])
    honest = copy.deepcopy(edge)
    honest["industry_certify"]["honest"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(honest, honest["plane_interface"])
    site_launch = copy.deepcopy(edge)
    site_launch["programs"]["website"]["industry_certified_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(site_launch, site_launch["plane_interface"])
    site_packs = copy.deepcopy(edge)
    site_packs["programs"]["website"]["packs_are_skus"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(site_packs, site_packs["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = "SKU attach chain. #packs."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(ops_hole, ops_hole["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["honest_industry"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    success_missing = copy.deepcopy(edge["expert_review"]["success"])
    success_missing.pop("honest_industry")
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_missing)
    success_kind = copy.deepcopy(edge["expert_review"]["success"])
    success_kind["honest_industry"]["kind"] = "ainav.honest.industry.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_kind)
    success_href = copy.deepcopy(edge["expert_review"]["success"])
    success_href["honest_industry"]["href"] = "#industry"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_href)
    for missing in (
        "Treat an industry pack as a SKU",
        "Treat a library as a SKU",
        "Treat a repository as a SKU",
        "Treat industry certify as launch",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
    principles_honest = copy.deepcopy(edge)
    principles_honest["expert_review"]["first_principles"] = [
        item.replace("Honest industry certify", "Industry maps").replace(
            "honest industry certify", "industry maps"
        )
        for item in principles_honest["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(principles_honest, principles_honest["plane_interface"])
    ops_sku = copy.deepcopy(edge)
    ops_sku["operations"]["note"] = "Honest industry sits on #packs."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(ops_sku, ops_sku["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest industry."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(ops_href, ops_href["plane_interface"])
    first_launch = copy.deepcopy(edge["expert_review"]["first_principles"])
    first_launch = [
        item.replace("Industry certify is not launch.", "Industry certify is launch.") for item in first_launch
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(first_launch)
    principles_launch = copy.deepcopy(edge)
    principles_launch["expert_review"]["first_principles"] = [
        item.replace("Industry certify is not launch.", "Industry stays mapped.")
        for item in principles_launch["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_307(principles_launch, principles_launch["plane_interface"])
