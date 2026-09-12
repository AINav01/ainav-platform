from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_WHOLE_HREFS,
    HONEST_WHOLE_REFUSE_IDS,
    HONEST_WHOLE_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.honest_whole import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_308_honest_whole():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.25.0"
    whole = cat["honest_whole"]
    assert whole["kind"] == "ainav.honest.whole.v1"
    assert whole["honest"] is True
    assert whole["complete"] is True
    assert whole["whole_is_launch"] is False
    assert whole["ten_is_launch"] is False
    assert whole["stitch_is_sku"] is False
    assert whole["certified"] is False
    assert whole["is_admit_plane"] is False
    refuse = [item for item in whole["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_WHOLE_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_WHOLE_REFUSE_TEXT[key] for key in HONEST_WHOLE_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_WHOLE_HREFS[key] for key in HONEST_WHOLE_REFUSE_IDS}
    assert "honest whole" in whole["note"].lower()
    assert "the whole firm is not launch" in whole["note"].lower()
    assert "10/10 review is not launch" in whole["note"].lower()
    assert cat["programs"]["website"]["honest_whole"] is True
    assert cat["programs"]["website"]["honest_industry"] is True
    assert cat["programs"]["website"]["honest_whole_live"] is False
    assert cat["programs"]["website"]["whole_is_launch"] is False
    assert "honest whole" in cat["operations"]["note"].lower()
    assert any("3.08.0" in item and "honest whole" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "the whole firm as launch" in does_not
    assert "a 10/10 review as launch" in does_not
    assert "the stitch as a sku" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest whole" in principles
    assert "the whole firm is not launch" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 95
    assert upgrades[78]["who"] == "tree"
    assert upgrades[78]["done"] is True
    assert upgrades[78]["marks_live_pin"] is False
    blob = f"{upgrades[78]['title']} {upgrades[78]['do']}".lower()
    assert "honest whole" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert "honest whole" in html.lower()
    assert "the whole firm is not launch" in html.lower()
    assert "a 10/10 review is not launch" in html.lower()
    assert 'id="whole-lanes"' in html
    assert 'data-whole-refuse="whole_as_launch"' in html
    assert 'data-whole-refuse="ten_as_launch"' in html
    assert 'data-whole-refuse="stitch_as_sku"' in html
    assert 'data-whole-refuse="website_as_apex"' in html
    assert 'data-whole-refuse="ci_as_launch"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#whole"' not in nav
    assert 'href="/whole"' not in nav
    assert "bindWholeRefuses" in js
    assert "refuseWhole" in js
    assert "whole-lede" not in js
    assert "industry-cert-lede" not in js
    assert "ready-lede" not in js
    assert "honest whole" in twin.lower()
    assert "the whole firm is not launch" in twin.lower()
    assert "Digital twin · 3.25.0" in twin
    assert "AINAV.Institute twin · 3.25.0" in twin
    assert "3.07.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    assert "Application kit · 3.25.0" in kit
    assert "Whole is launch" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.25.0"
    status = public_status()
    assert status["release"] == "3.25.0"
    assert status["website"]["honest_whole"] is True
    assert status["website"]["honest_whole_live"] is False
    assert status["website"]["whole_is_launch"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.whole.v1"
    assert review["whole_is_launch"] is False
    assert "Treat the whole firm as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_308_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.07.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.08.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_whole"] = False

    def live(cat):
        cat["programs"]["website"]["honest_whole_live"] = True

    def launch(cat):
        cat["honest_whole"]["whole_is_launch"] = True

    def ten(cat):
        cat["honest_whole"]["ten_is_launch"] = True

    def site(cat):
        cat["honest_whole"]["site"] = "Whole board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest whole" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest industry sits on #packs."

    for mutator in (release, closed, flag_off, live, launch, ten, site, principles, ops):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["honest_whole"]["kind"] = "ainav.honest.whole.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_whole"]["site"] = site_name["honest_whole"]["site"].replace(
        "Honest whole",
        "Firm board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(site_name, site_name["plane_interface"])
    site_launch = copy.deepcopy(edge)
    site_launch["honest_whole"]["site"] = site_launch["honest_whole"]["site"].replace(
        "The whole firm is not launch. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(site_launch, site_launch["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_whole"]["site"] = site_route["honest_whole"]["site"].replace(
        "Not a /whole route. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(site_route, site_route["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["honest_whole"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    success_missing = copy.deepcopy(edge["expert_review"]["success"])
    success_missing.pop("honest_whole")
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_missing)
    success_kind = copy.deepcopy(edge["expert_review"]["success"])
    success_kind["honest_whole"]["kind"] = "ainav.honest.whole.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_kind)
    success_href = copy.deepcopy(edge["expert_review"]["success"])
    success_href["honest_whole"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_href)
    success_stitch = copy.deepcopy(edge["expert_review"]["success"])
    success_stitch["honest_whole"]["stitch_is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_stitch)
    stitch_site = copy.deepcopy(edge)
    stitch_site["programs"]["website"]["stitch_is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(stitch_site, stitch_site["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_whole"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(certified, certified["plane_interface"])
    whole_launch = copy.deepcopy(edge)
    whole_launch["honest_whole"]["whole_is_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(whole_launch, whole_launch["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_whole"]["site"] = site_glance["honest_whole"]["site"].replace(
        "First glance stays the write rail. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(site_glance, site_glance["plane_interface"])
    principles_direct = copy.deepcopy(edge)
    principles_direct["expert_review"]["first_principles"] = [
        item
        for item in principles_direct["expert_review"]["first_principles"]
        if "honest whole" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(principles_direct, principles_direct["plane_interface"])
    principles_firm = copy.deepcopy(edge)
    principles_firm["expert_review"]["first_principles"] = [
        item.replace("The whole firm is not launch.", "The stitch is recorded.")
        for item in principles_firm["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(principles_firm, principles_firm["plane_interface"])
    principles_ten = copy.deepcopy(edge)
    principles_ten["expert_review"]["first_principles"] = [
        item.replace("A 10/10 review is not launch.", "Review is recorded.")
        for item in principles_ten["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_ten["expert_review"]["first_principles"])
    ops_attach = copy.deepcopy(edge)
    ops_attach["operations"]["note"] = "Honest whole sits on #whole."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(ops_attach, ops_attach["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest whole is recorded."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(ops_href, ops_href["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. The stitch sits on #whole."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_308(ops_name, ops_name["plane_interface"])
    for missing in (
        "Treat the whole firm as launch",
        "Treat a 10/10 review as launch",
        "Treat the stitch as a SKU",
        "Treat the twin as the Institute apex",
        "Treat a green check as launch",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
