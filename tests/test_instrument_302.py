from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    AGENTS_ALL_URL,
    MICROSOFT_AGENT_AROUND_IDS,
    MICROSOFT_AGENT_DRAFT_IDS,
    MICROSOFT_AGENT_LANE_IDS,
    MICROSOFT_AGENT_REFUSE_IDS,
    MICROSOFT_AGENT_REFUSE_TEXT,
    MICROSOFT_AGENT_TYPE_IDS,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.agents import public_review
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_302_honest_agents():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.14.0"
    agents = cat["microsoft_stack"]["agents"]
    assert agents["kind"] == "ainav.microsoft.agents.v1"
    assert agents["honest"] is True
    assert agents["admin_url"] == AGENTS_ALL_URL
    assert agents["inventory_claimed"] is False
    assert agents["census"] is False
    assert agents["agent_365_is_product"] is False
    assert agents["is_admit_plane"] is False
    assert agents["cloud_agent_can_approve"] is False
    assert [item["id"] for item in agents["types"]] == list(MICROSOFT_AGENT_TYPE_IDS)
    assert [item["id"] for item in agents["draft"]] == list(MICROSOFT_AGENT_DRAFT_IDS)
    assert [item["id"] for item in agents["around"]] == list(MICROSOFT_AGENT_AROUND_IDS)
    assert all(item["installed"] is None for item in agents["draft"])
    assert all(item["claimed"] is False and item["installed"] is None for item in agents["around"])
    assert [lane["id"] for lane in agents["lanes"]] == list(MICROSOFT_AGENT_LANE_IDS)
    refuse = next(lane for lane in agents["lanes"] if lane["id"] == "refuse")
    assert [item["id"] for item in refuse["items"]] == list(MICROSOFT_AGENT_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse["items"]} == {
        key: MICROSOFT_AGENT_REFUSE_TEXT[key] for key in MICROSOFT_AGENT_REFUSE_IDS
    }
    assert "honest agents" in agents["note"].lower()
    assert "around the write" in agents["note"].lower()
    assert "total agents" in agents["note"].lower()
    assert "agent is not a seat" in agents["lede"].lower()
    assert "workiq.user" in [item["id"] for item in cat["microsoft_stack"]["agent_tools"]["leave_available"]]
    assert cat["programs"]["website"]["microsoft_agents"] is True
    assert cat["programs"]["website"]["microsoft_agents_honest"] is True
    assert cat["programs"]["website"]["microsoft_agents_live"] is False
    assert cat["programs"]["website"]["microsoft_census"] is False
    assert cat["programs"]["website"]["agent_365_is_product"] is False
    assert "honest agents" in cat["operations"]["note"].lower()
    assert "around the write" in cat["operations"]["note"].lower()
    assert any("3.02.0" in item and "honest agents" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "agent 365 as ainav" in does_not
    assert "total agents" in does_not
    assert "ownerless" in does_not
    assert "unmanaged" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest agents" in principles
    assert "agent is not a seat" in principles
    assert "around the write" in principles
    assert "total agents" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 84
    assert upgrades[72]["who"] == "tree"
    assert upgrades[72]["done"] is True
    assert upgrades[72]["marks_live_pin"] is False
    blob = f"{upgrades[72]['title']} {upgrades[72]['do']}".lower()
    assert "honest agents" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert "honest agents" in html.lower()
    assert 'href="https://admin.cloud.microsoft/?#/agents/all"' in html
    assert 'id="agents-board"' in html
    assert 'id="agent-around"' in html
    assert 'data-around="github_copilot"' in html
    assert 'data-around="ownerless_unmanaged"' in html
    assert 'data-agent-refuse="agent_as_seat"' in html
    assert 'data-agent-refuse="copilot_studio_as_job_c"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#agent-tools"' not in nav
    assert 'href="/agents"' not in nav
    assert "bindAgentRefuses" in js
    assert "agent-tools-lede" not in js
    assert "honest agents" in twin.lower()
    assert "around the write" in twin.lower()
    assert "Honest" in app
    assert "Around" in app
    assert "agents" in identify.lower()
    assert "Around" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.14.0"
    status = public_status()
    assert status["release"] == "3.14.0"
    assert status["website"]["microsoft_agents"] is True
    assert status["website"]["microsoft_agents_live"] is False
    assert status["website"]["agent_365_is_product"] is False
    review = public_review()
    assert review["kind"] == "ainav.microsoft.agents.v1"
    assert review["inventory_claimed"] is False
    assert "Paste Total agents" in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_302_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.01.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.02.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["microsoft_agents"] = False

    def live(cat):
        cat["programs"]["website"]["microsoft_agents_live"] = True

    def census(cat):
        cat["microsoft_stack"]["agents"]["inventory_claimed"] = True

    def product(cat):
        cat["microsoft_stack"]["agents"]["agent_365_is_product"] = True

    def site(cat):
        cat["microsoft_stack"]["agents"]["site"] = "Agent Tools on #agent-tools."

    def around(cat):
        cat["microsoft_stack"]["agents"]["around"][0]["claimed"] = True

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest agents" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. The sit-down industry drawer is sit / maps / attach / refuse on #industry."
        )

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "Total agents" not in item and "ownerless" not in item.lower()
        ]

    for mutator in (release, closed, flag_off, live, census, product, site, around, principles, ops, ciso):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["microsoft_stack"]["agents"]["kind"] = "ainav.microsoft.agents.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_302(hole, hole["plane_interface"])
    census_hole = copy.deepcopy(edge)
    census_hole["microsoft_stack"]["agents"]["admin_url"] = "https://example.com"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_302(census_hole, census_hole["plane_interface"])
    around_site = copy.deepcopy(edge)
    around_site["microsoft_stack"]["agents"]["site"] = around_site["microsoft_stack"]["agents"]["site"].replace(
        "Around the write stays maps. Total agents is a Microsoft card.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_302(around_site, around_site["plane_interface"])
    honest = copy.deepcopy(edge)
    honest["microsoft_stack"]["agents"]["honest"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_302(honest, honest["plane_interface"])
    product_flag = copy.deepcopy(edge)
    product_flag["programs"]["website"]["agent_365_is_product"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_302(product_flag, product_flag["plane_interface"])
    census_flag = copy.deepcopy(edge)
    census_flag["programs"]["website"]["microsoft_census"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_302(census_flag, census_flag["plane_interface"])
    inventory = copy.deepcopy(edge)
    inventory["microsoft_stack"]["agents"]["inventory_claimed"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_302(inventory, inventory["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = "SKU attach chain. #agent-tools."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_302(ops_hole, ops_hole["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["microsoft_agents"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    for missing in (
        "Treat Agent 365 as AINav",
        "Treat an agent as a seat",
        "Claim a live agent census from this plane",
        "Treat a pinned agent as dual admit",
        "Paste Total agents into the catalog",
        "Treat ownerless or unmanaged agents as a census",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
    principles_around = copy.deepcopy(edge["expert_review"]["first_principles"])
    principles_around = [
        item.replace("Around the write stays maps. Total agents is a Microsoft card.", "")
        for item in principles_around
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_around)
