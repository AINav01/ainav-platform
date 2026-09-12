from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_PRODUCTION_HREFS,
    HONEST_PRODUCTION_REFUSE_IDS,
    HONEST_PRODUCTION_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.honest_production import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_314_honest_production():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.21.0"
    production = cat["honest_production"]
    assert production["kind"] == "ainav.honest.production.v1"
    assert production["honest"] is True
    assert production["considered"] is True
    assert production["recorded"] is True
    assert production["production_sim_is_production"] is False
    assert production["fix_all_is_this_plane"] is False
    assert production["elements_are_live"] is False
    assert production["better_is_launch"] is False
    assert production["rehearsal_is_live_pin"] is False
    assert production["certified"] is False
    assert production["created"] is False
    assert production["href"] == "#firm"
    refuse = [item for item in production["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_PRODUCTION_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_PRODUCTION_REFUSE_TEXT[key] for key in HONEST_PRODUCTION_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_PRODUCTION_HREFS[key] for key in HONEST_PRODUCTION_REFUSE_IDS}
    assert "honest production" in production["note"].lower()
    assert "a production sim is not production" in production["note"].lower()
    assert "fixing all is not this plane" in production["note"].lower()
    assert cat["programs"]["website"]["honest_production"] is True
    assert cat["programs"]["website"]["honest_path"] is True
    assert cat["programs"]["website"]["honest_production_live"] is False
    assert cat["programs"]["website"]["production_sim_is_production"] is False
    assert cat["programs"]["website"]["fix_all_is_this_plane"] is False
    assert cat["programs"]["website"]["elements_are_live"] is False
    assert cat["programs"]["website"]["better_is_launch"] is False
    assert cat["programs"]["website"]["rehearsal_is_live_pin"] is False
    assert "honest production" in cat["operations"]["note"].lower()
    assert "#firm" in cat["operations"]["note"]
    assert any("3.14.0" in item and "honest production" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a production sim as production" in does_not
    assert "fixing all as this plane" in does_not
    assert "rehearsed elements as live" in does_not
    assert "making all much better as launch" in does_not
    assert "a rehearsal as live_pin_ok" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest production" in principles
    assert "a production sim is not production" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 91
    assert upgrades[84]["who"] == "tree"
    assert upgrades[84]["done"] is True
    assert upgrades[84]["marks_live_pin"] is False
    blob = f"{upgrades[84]['title']} {upgrades[84]['do']}".lower()
    assert "honest production" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert "honest production" in html.lower()
    assert "a production sim is not production" in html.lower()
    assert "fixing all is not this plane" in html.lower()
    assert 'id="prod-consider"' in html
    assert 'id="prod-zeros"' in html
    assert 'id="prod-facts"' in html
    assert 'data-prod-refuse="production_sim_as_production"' in html
    assert 'data-prod-refuse="fix_all_as_this_plane"' in html
    assert 'data-prod-refuse="elements_as_live"' in html
    assert 'data-prod-refuse="better_as_launch"' in html
    assert 'data-prod-refuse="rehearsal_as_live_pin"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/firm"' not in nav
    assert 'href="#prod"' not in nav
    assert 'href="#prod-consider"' not in nav
    assert "Honest production" not in nav
    assert "bindProdRefuses" in js
    assert "refuseProd" in js
    assert "prod-lede" not in js
    assert "cycle-lede" not in js
    assert "operate-lede" not in js
    assert "connect-lede" not in js
    assert "studio-lede" not in js
    assert "pages-lede" not in js
    assert "honest production" in twin.lower()
    assert "a production sim is not production" in twin.lower()
    assert "Digital twin · 3.21.0" in twin
    assert "AINAV.Institute twin · 3.21.0" in twin
    assert "3.13.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    assert "Application kit · 3.21.0" in kit
    assert "A production sim is production" in identify
    assert "Open production" in identify
    assert "A production sim is production" in app
    dash = public_dashboard()
    assert dash["release"] == "3.21.0"
    status = public_status()
    assert status["release"] == "3.21.0"
    assert status["website"]["honest_production"] is True
    assert status["website"]["honest_production_live"] is False
    assert status["website"]["production_sim_is_production"] is False
    assert status["website"]["fix_all_is_this_plane"] is False
    assert status["website"]["elements_are_live"] is False
    assert status["website"]["better_is_launch"] is False
    assert status["website"]["rehearsal_is_live_pin"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.production.v1"
    assert review["production_sim_is_production"] is False
    assert "Treat a production sim as production." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_314_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.13.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.14.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_production"] = False

    def live(cat):
        cat["programs"]["website"]["honest_production_live"] = True

    def sim(cat):
        cat["programs"]["website"]["production_sim_is_production"] = True

    def fix(cat):
        cat["programs"]["website"]["fix_all_is_this_plane"] = True

    def elements(cat):
        cat["programs"]["website"]["elements_are_live"] = True

    def better(cat):
        cat["programs"]["website"]["better_is_launch"] = True

    def rehearsal(cat):
        cat["programs"]["website"]["rehearsal_is_live_pin"] = True

    def site(cat):
        cat["honest_production"]["site"] = "Production board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest production" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest path sits on #path."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio. "
            "Not connected-as-live. Not a 10/10 launch. Not a shared sandbox."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        sim,
        fix,
        elements,
        better,
        rehearsal,
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
    hole["honest_production"]["kind"] = "ainav.honest.production.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_production"]["site"] = site_name["honest_production"]["site"].replace(
        "Honest production",
        "Production board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(site_name, site_name["plane_interface"])
    site_sim = copy.deepcopy(edge)
    site_sim["honest_production"]["site"] = site_sim["honest_production"]["site"].replace(
        "A production sim is not production.",
        "Production is recorded.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(site_sim, site_sim["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_production"]["site"] = site_route["honest_production"]["site"].replace(
        "Not a /firm route.",
        "A /firm route.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_production"]["site"] = site_glance["honest_production"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the production board.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge)
    success["expert_review"]["success"]["honest_production"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success)
    success_missing = copy.deepcopy(edge)
    success_missing["expert_review"]["success"].pop("honest_production")
    with pytest.raises(IntegrityError):
        validate_catalog(success_missing)
    success_kind = copy.deepcopy(edge)
    success_kind["expert_review"]["success"]["honest_production"]["kind"] = "ainav.honest.production.v0"
    with pytest.raises(IntegrityError):
        validate_catalog(success_kind)
    success_href = copy.deepcopy(edge)
    success_href["expert_review"]["success"]["honest_production"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_catalog(success_href)
    success_sim = copy.deepcopy(edge)
    success_sim["expert_review"]["success"]["honest_production"]["production_sim_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_sim)
    success_fix = copy.deepcopy(edge)
    success_fix["expert_review"]["success"]["honest_production"]["fix_all_is_this_plane"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_fix)
    success_elements = copy.deepcopy(edge)
    success_elements["expert_review"]["success"]["honest_production"]["elements_are_live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_elements)
    success_better = copy.deepcopy(edge)
    success_better["expert_review"]["success"]["honest_production"]["better_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_better)
    success_rehearsal = copy.deepcopy(edge)
    success_rehearsal["expert_review"]["success"]["honest_production"]["rehearsal_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_rehearsal)
    live_body = copy.deepcopy(edge)
    live_body["honest_production"]["production_sim_is_production"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(live_body, live_body["plane_interface"])
    fix_body = copy.deepcopy(edge)
    fix_body["honest_production"]["fix_all_is_this_plane"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(fix_body, fix_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_production"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(certified, certified["plane_interface"])
    principles_name = copy.deepcopy(edge)
    principles_name["expert_review"]["first_principles"] = [
        item.replace("Honest production sits on #firm.", "Production sits on #firm.")
        for item in principles_name["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(principles_name, principles_name["plane_interface"])
    principles_sim = copy.deepcopy(edge)
    principles_sim["expert_review"]["first_principles"] = [
        item.replace("A production sim is not production.", "Production is recorded done.")
        for item in principles_sim["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(principles_sim, principles_sim["plane_interface"])
    principles_first = copy.deepcopy(edge)
    principles_first["expert_review"]["first_principles"] = [
        item.replace("Honest production sits on #firm.", "Production sits on #firm.")
        for item in principles_first["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_first["expert_review"]["first_principles"])
    ops_attach = copy.deepcopy(edge)
    ops_attach["operations"]["note"] = "Honest production sits on #firm."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(ops_attach, ops_attach["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest production is recorded."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(ops_href, ops_href["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. Production sits on #firm."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(ops_name, ops_name["plane_interface"])
    managed_direct = copy.deepcopy(edge)
    managed_direct["expert_review"]["success"]["managed_face"]["managed"] = managed_direct["expert_review"]["success"]["managed_face"]["managed"].replace(
        " Not a production sim.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_314(managed_direct, managed_direct["plane_interface"])
    for missing in (
        "Treat a production sim as production",
        "Treat fixing all as this plane",
        "Treat rehearsed elements as live",
        "Treat making all much better as launch",
        "Treat a rehearsal as LIVE_PIN_OK",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
