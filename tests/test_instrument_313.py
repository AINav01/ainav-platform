from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_PATH_HREFS,
    HONEST_PATH_REFUSE_IDS,
    HONEST_PATH_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.honest_path import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_313_honest_path():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.17.0"
    path = cat["honest_path"]
    assert path["kind"] == "ainav.honest.path.v1"
    assert path["honest"] is True
    assert path["considered"] is True
    assert path["recorded"] is True
    assert path["industry_is_named_client"] is False
    assert path["shared_sandbox_is_production"] is False
    assert path["hours_is_sku"] is False
    assert path["rollback_is_live_pin"] is False
    assert path["redeploy_is_launch"] is False
    assert path["certified"] is False
    assert path["created"] is False
    assert path["href"] == "#path"
    refuse = [item for item in path["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_PATH_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_PATH_REFUSE_TEXT[key] for key in HONEST_PATH_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_PATH_HREFS[key] for key in HONEST_PATH_REFUSE_IDS}
    assert "honest path" in path["note"].lower()
    assert "an industry is not a named client" in path["note"].lower()
    assert "a shared sandbox is not production" in path["note"].lower()
    assert cat["programs"]["website"]["honest_path"] is True
    assert cat["programs"]["website"]["honest_operate"] is True
    assert cat["programs"]["website"]["honest_path_live"] is False
    assert cat["programs"]["website"]["industry_is_named_client"] is False
    assert cat["programs"]["website"]["shared_sandbox_is_production"] is False
    assert cat["programs"]["website"]["hours_is_sku"] is False
    assert cat["programs"]["website"]["rollback_is_live_pin"] is False
    assert cat["programs"]["website"]["redeploy_is_launch"] is False
    assert "honest path" in cat["operations"]["note"].lower()
    assert "#path" in cat["operations"]["note"]
    assert any("3.13.0" in item and "honest path" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "an industry as a named client" in does_not
    assert "a shared sandbox as production" in does_not
    assert "hours as a sku" in does_not
    assert "rollback as live_pin_ok" in does_not
    assert "a redeploy as launch" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest path" in principles
    assert "an industry is not a named client" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 87
    assert upgrades[83]["who"] == "tree"
    assert upgrades[83]["done"] is True
    assert upgrades[83]["marks_live_pin"] is False
    blob = f"{upgrades[83]['title']} {upgrades[83]['do']}".lower()
    assert "honest path" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert "honest path" in html.lower()
    assert "an industry is not a named client" in html.lower()
    assert "a shared sandbox is not production" in html.lower()
    assert 'id="path-consider"' in html
    assert 'id="cycle-zeros"' in html
    assert 'id="cycle-facts"' in html
    assert 'data-cycle-refuse="industry_as_named_client"' in html
    assert 'data-cycle-refuse="shared_sandbox_as_production"' in html
    assert 'data-cycle-refuse="hours_as_sku"' in html
    assert 'data-cycle-refuse="rollback_as_live_pin"' in html
    assert 'data-cycle-refuse="redeploy_as_launch"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/path"' not in nav
    assert 'href="#cycle"' not in nav
    assert 'href="#path-consider"' not in nav
    assert "Honest path" not in nav
    assert "bindCycleRefuses" in js
    assert "refuseCycle" in js
    assert "cycle-lede" not in js
    assert "operate-lede" not in js
    assert "connect-lede" not in js
    assert "studio-lede" not in js
    assert "pages-lede" not in js
    assert "honest path" in twin.lower()
    assert "an industry is not a named client" in twin.lower()
    assert "Digital twin · 3.16.0" in twin
    assert "AINAV.Institute twin · 3.16.0" in twin
    assert "3.12.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    assert "Application kit · 3.16.0" in kit
    assert "An industry is a named client" in identify
    assert "Open path" in identify
    assert "An industry is a named client" in app
    dash = public_dashboard()
    assert dash["release"] == "3.17.0"
    status = public_status()
    assert status["release"] == "3.17.0"
    assert status["website"]["honest_path"] is True
    assert status["website"]["honest_path_live"] is False
    assert status["website"]["industry_is_named_client"] is False
    assert status["website"]["shared_sandbox_is_production"] is False
    assert status["website"]["hours_is_sku"] is False
    assert status["website"]["rollback_is_live_pin"] is False
    assert status["website"]["redeploy_is_launch"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.path.v1"
    assert review["industry_is_named_client"] is False
    assert "Treat an industry as a named client." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_313_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.12.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.13.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_path"] = False

    def live(cat):
        cat["programs"]["website"]["honest_path_live"] = True

    def industry(cat):
        cat["programs"]["website"]["industry_is_named_client"] = True

    def shared(cat):
        cat["programs"]["website"]["shared_sandbox_is_production"] = True

    def hours(cat):
        cat["programs"]["website"]["hours_is_sku"] = True

    def rollback(cat):
        cat["programs"]["website"]["rollback_is_live_pin"] = True

    def redeploy(cat):
        cat["programs"]["website"]["redeploy_is_launch"] = True

    def site(cat):
        cat["honest_path"]["site"] = "Path board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest path" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest operate sits on #agent-tools."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio. "
            "Not connected-as-live. Not a 10/10 launch."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        industry,
        shared,
        hours,
        rollback,
        redeploy,
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
    hole["honest_path"]["kind"] = "ainav.honest.path.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_path"]["site"] = site_name["honest_path"]["site"].replace(
        "Honest path",
        "Path board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(site_name, site_name["plane_interface"])
    site_industry = copy.deepcopy(edge)
    site_industry["honest_path"]["site"] = site_industry["honest_path"]["site"].replace(
        "An industry is not a named client.",
        "Industry is recorded.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(site_industry, site_industry["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_path"]["site"] = site_route["honest_path"]["site"].replace(
        "Not a /path route.",
        "A /path route.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_path"]["site"] = site_glance["honest_path"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the path board.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge)
    success["expert_review"]["success"]["honest_path"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success)
    success_missing = copy.deepcopy(edge)
    success_missing["expert_review"]["success"].pop("honest_path")
    with pytest.raises(IntegrityError):
        validate_catalog(success_missing)
    success_kind = copy.deepcopy(edge)
    success_kind["expert_review"]["success"]["honest_path"]["kind"] = "ainav.honest.path.v0"
    with pytest.raises(IntegrityError):
        validate_catalog(success_kind)
    success_href = copy.deepcopy(edge)
    success_href["expert_review"]["success"]["honest_path"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_catalog(success_href)
    success_industry = copy.deepcopy(edge)
    success_industry["expert_review"]["success"]["honest_path"]["industry_is_named_client"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_industry)
    success_shared = copy.deepcopy(edge)
    success_shared["expert_review"]["success"]["honest_path"]["shared_sandbox_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_shared)
    success_hours = copy.deepcopy(edge)
    success_hours["expert_review"]["success"]["honest_path"]["hours_is_sku"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_hours)
    success_rollback = copy.deepcopy(edge)
    success_rollback["expert_review"]["success"]["honest_path"]["rollback_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_rollback)
    success_redeploy = copy.deepcopy(edge)
    success_redeploy["expert_review"]["success"]["honest_path"]["redeploy_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_redeploy)
    live_body = copy.deepcopy(edge)
    live_body["honest_path"]["industry_is_named_client"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(live_body, live_body["plane_interface"])
    shared_body = copy.deepcopy(edge)
    shared_body["honest_path"]["shared_sandbox_is_production"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(shared_body, shared_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_path"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(certified, certified["plane_interface"])
    principles_name = copy.deepcopy(edge)
    principles_name["expert_review"]["first_principles"] = [
        item.replace("Honest path sits on #path.", "Path sits on #path.")
        for item in principles_name["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(principles_name, principles_name["plane_interface"])
    principles_industry = copy.deepcopy(edge)
    principles_industry["expert_review"]["first_principles"] = [
        item.replace("An industry is not a named client.", "Industry is recorded done.")
        for item in principles_industry["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(principles_industry, principles_industry["plane_interface"])
    principles_first = copy.deepcopy(edge)
    principles_first["expert_review"]["first_principles"] = [
        item.replace("Honest path sits on #path.", "Path sits on #path.")
        for item in principles_first["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_first["expert_review"]["first_principles"])
    ops_attach = copy.deepcopy(edge)
    ops_attach["operations"]["note"] = "Honest path sits on #path."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(ops_attach, ops_attach["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest path is recorded."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(ops_href, ops_href["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. Path sits on #path."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(ops_name, ops_name["plane_interface"])
    managed_direct = copy.deepcopy(edge)
    managed_direct["expert_review"]["success"]["managed_face"]["managed"] = managed_direct["expert_review"]["success"]["managed_face"]["managed"].replace(
        " Not a shared sandbox.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_313(managed_direct, managed_direct["plane_interface"])
    for missing in (
        "Treat an industry as a named client",
        "Treat a shared sandbox as production",
        "Treat hours as a SKU",
        "Treat rollback as LIVE_PIN_OK",
        "Treat a redeploy as launch",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
