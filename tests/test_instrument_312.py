from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_OPERATE_HREFS,
    HONEST_OPERATE_REFUSE_IDS,
    HONEST_OPERATE_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.honest_operate import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_312_honest_operate():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.13.0"
    operate = cat["honest_operate"]
    assert operate["kind"] == "ainav.honest.operate.v1"
    assert operate["honest"] is True
    assert operate["considered"] is True
    assert operate["recorded"] is True
    assert operate["close_gaps_is_this_plane"] is False
    assert operate["outlook_is_click"] is False
    assert operate["grok_login_is_this_plane"] is False
    assert operate["operate_sim_is_production"] is False
    assert operate["polish_ten_is_launch"] is False
    assert operate["certified"] is False
    assert operate["created"] is False
    assert operate["href"] == "#agent-tools"
    refuse = [item for item in operate["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_OPERATE_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_OPERATE_REFUSE_TEXT[key] for key in HONEST_OPERATE_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_OPERATE_HREFS[key] for key in HONEST_OPERATE_REFUSE_IDS}
    assert "honest operate" in operate["note"].lower()
    assert "closing all gaps is not this plane" in operate["note"].lower()
    assert "outlook mail is not a click" in operate["note"].lower()
    assert cat["programs"]["website"]["honest_operate"] is True
    assert cat["programs"]["website"]["honest_connect"] is True
    assert cat["programs"]["website"]["honest_operate_live"] is False
    assert cat["programs"]["website"]["close_gaps_is_this_plane"] is False
    assert cat["programs"]["website"]["outlook_is_click"] is False
    assert cat["programs"]["website"]["grok_login_is_this_plane"] is False
    assert cat["programs"]["website"]["operate_sim_is_production"] is False
    assert cat["programs"]["website"]["polish_ten_is_launch"] is False
    assert "honest operate" in cat["operations"]["note"].lower()
    assert "#agent-tools" in cat["operations"]["note"]
    assert any("3.12.0" in item and "honest operate" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "closing all gaps as this plane" in does_not
    assert "outlook mail as a click" in does_not
    assert "grok login as this plane" in does_not
    assert "an operate sim as production" in does_not
    assert "a 10/10 polish as launch" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest operate" in principles
    assert "closing all gaps is not this plane" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 83
    assert upgrades[82]["who"] == "tree"
    assert upgrades[82]["done"] is True
    assert upgrades[82]["marks_live_pin"] is False
    blob = f"{upgrades[82]['title']} {upgrades[82]['do']}".lower()
    assert "honest operate" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.13.0" in html
    assert "honest operate" in html.lower()
    assert "closing all gaps is not this plane" in html.lower()
    assert "outlook mail is not a click" in html.lower()
    assert 'id="operate-consider"' in html
    assert 'id="operate-zeros"' in html
    assert 'id="operate-facts"' in html
    assert 'data-operate-refuse="close_gaps_as_this_plane"' in html
    assert 'data-operate-refuse="outlook_as_click"' in html
    assert 'data-operate-refuse="grok_login_as_this_plane"' in html
    assert 'data-operate-refuse="operate_sim_as_production"' in html
    assert 'data-operate-refuse="polish_ten_as_launch"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/operate"' not in nav
    assert 'href="#operate"' not in nav
    assert 'href="#operate-consider"' not in nav
    assert "Honest operate" not in nav
    assert "bindOperateRefuses" in js
    assert "refuseOperate" in js
    assert "operate-lede" not in js
    assert "connect-lede" not in js
    assert "studio-lede" not in js
    assert "pages-lede" not in js
    assert "whole-lede" not in js
    assert "industry-cert-lede" not in js
    assert "ready-lede" not in js
    assert "build-lede" not in js
    assert "operator-lede" not in js
    assert "access-lede" not in js
    assert "honest operate" in twin.lower()
    assert "closing all gaps is not this plane" in twin.lower()
    assert "Digital twin · 3.13.0" in twin
    assert "AINAV.Institute twin · 3.13.0" in twin
    assert "3.11.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    assert "Application kit · 3.13.0" in kit
    assert "Closing all gaps is this plane" in identify
    assert "Open operate" in identify
    assert "Closing all gaps is this plane" in app
    dash = public_dashboard()
    assert dash["release"] == "3.13.0"
    status = public_status()
    assert status["release"] == "3.13.0"
    assert status["website"]["honest_operate"] is True
    assert status["website"]["honest_operate_live"] is False
    assert status["website"]["close_gaps_is_this_plane"] is False
    assert status["website"]["outlook_is_click"] is False
    assert status["website"]["grok_login_is_this_plane"] is False
    assert status["website"]["operate_sim_is_production"] is False
    assert status["website"]["polish_ten_is_launch"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.operate.v1"
    assert review["close_gaps_is_this_plane"] is False
    assert "Treat closing all gaps as this plane." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_312_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.11.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.12.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_operate"] = False

    def live(cat):
        cat["programs"]["website"]["honest_operate_live"] = True

    def gaps(cat):
        cat["programs"]["website"]["close_gaps_is_this_plane"] = True

    def outlook(cat):
        cat["programs"]["website"]["outlook_is_click"] = True

    def grok(cat):
        cat["programs"]["website"]["grok_login_is_this_plane"] = True

    def sim(cat):
        cat["programs"]["website"]["operate_sim_is_production"] = True

    def ten(cat):
        cat["programs"]["website"]["polish_ten_is_launch"] = True

    def site(cat):
        cat["honest_operate"]["site"] = "Operate board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest operate" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest connect sits on #missing."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio. Not connected-as-live."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        gaps,
        outlook,
        grok,
        sim,
        ten,
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
    hole["honest_operate"]["kind"] = "ainav.honest.operate.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_operate"]["site"] = site_name["honest_operate"]["site"].replace(
        "Honest operate",
        "Operate board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(site_name, site_name["plane_interface"])
    site_gaps = copy.deepcopy(edge)
    site_gaps["honest_operate"]["site"] = site_gaps["honest_operate"]["site"].replace(
        "Closing all gaps is not this plane. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(site_gaps, site_gaps["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_operate"]["site"] = site_route["honest_operate"]["site"].replace(
        "Not a /operate route. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_operate"]["site"] = site_glance["honest_operate"]["site"].replace(
        "First glance stays the write rail. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["honest_operate"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    success_missing = copy.deepcopy(edge["expert_review"]["success"])
    success_missing.pop("honest_operate")
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_missing)
    success_kind = copy.deepcopy(edge["expert_review"]["success"])
    success_kind["honest_operate"]["kind"] = "ainav.honest.operate.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_kind)
    success_href = copy.deepcopy(edge["expert_review"]["success"])
    success_href["honest_operate"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_href)
    success_gaps = copy.deepcopy(edge["expert_review"]["success"])
    success_gaps["honest_operate"]["close_gaps_is_this_plane"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_gaps)
    success_outlook = copy.deepcopy(edge["expert_review"]["success"])
    success_outlook["honest_operate"]["outlook_is_click"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_outlook)
    success_grok = copy.deepcopy(edge["expert_review"]["success"])
    success_grok["honest_operate"]["grok_login_is_this_plane"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_grok)
    success_sim = copy.deepcopy(edge["expert_review"]["success"])
    success_sim["honest_operate"]["operate_sim_is_production"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_sim)
    success_ten = copy.deepcopy(edge["expert_review"]["success"])
    success_ten["honest_operate"]["polish_ten_is_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_ten)
    live_body = copy.deepcopy(edge)
    live_body["honest_operate"]["close_gaps_is_this_plane"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(live_body, live_body["plane_interface"])
    click_body = copy.deepcopy(edge)
    click_body["honest_operate"]["outlook_is_click"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(click_body, click_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_operate"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(certified, certified["plane_interface"])
    principles_direct = copy.deepcopy(edge)
    principles_direct["expert_review"]["first_principles"] = [
        item
        for item in principles_direct["expert_review"]["first_principles"]
        if "honest operate" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(principles_direct, principles_direct["plane_interface"])
    principles_gaps = copy.deepcopy(edge)
    principles_gaps["expert_review"]["first_principles"] = [
        item.replace("Closing all gaps is not this plane.", "Closing all gaps is recorded done.")
        for item in principles_gaps["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(principles_gaps, principles_gaps["plane_interface"])
    principles_first = copy.deepcopy(edge)
    principles_first["expert_review"]["first_principles"] = [
        item.replace("Honest operate sits on #agent-tools.", "Operate sits on #agent-tools.")
        for item in principles_first["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_first["expert_review"]["first_principles"])
    ops_attach = copy.deepcopy(edge)
    ops_attach["operations"]["note"] = "Honest operate sits on #agent-tools."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(ops_attach, ops_attach["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest operate is recorded."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(ops_href, ops_href["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. Operate sits on #agent-tools."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(ops_name, ops_name["plane_interface"])
    managed_direct = copy.deepcopy(edge)
    managed_direct["expert_review"]["success"]["managed_face"]["managed"] = managed_direct["expert_review"]["success"]["managed_face"]["managed"].replace(
        " Not a 10/10 launch.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_312(managed_direct, managed_direct["plane_interface"])
    for missing in (
        "Treat closing all gaps as this plane",
        "Treat Outlook mail as a click",
        "Treat grok login as this plane",
        "Treat an operate sim as production",
        "Treat a 10/10 polish as launch",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
