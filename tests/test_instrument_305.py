from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_BUILD_HREFS,
    HONEST_BUILD_IDS,
    HONEST_BUILD_REFUSE_IDS,
    HONEST_BUILD_REFUSE_TEXT,
    HONEST_BUILD_ROLES,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.build import public_review
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_305_honest_build():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.08.0"
    build = cat["microsoft_stack"]["build"]
    assert build["kind"] == "ainav.honest.build.v1"
    assert build["honest"] is True
    assert build["need_full"] is False
    assert build["full_access_needed"] is False
    assert build["more_secrets_needed"] is False
    assert build["twin_is_launch"] is False
    assert build["packs_are_skus"] is False
    assert build["is_admit_plane"] is False
    assert [item["id"] for item in build["three"]] == list(HONEST_BUILD_IDS)
    assert {item["id"]: item["role"] for item in build["three"]} == dict(HONEST_BUILD_ROLES)
    refuse = [item for item in build["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_BUILD_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_BUILD_REFUSE_TEXT[key] for key in HONEST_BUILD_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in build["three"]}
    hrefs.update({item["id"]: item["href"] for item in refuse})
    assert hrefs == HONEST_BUILD_HREFS
    assert all(item["installed"] is None and item["seat"] is not True for item in build["three"])
    assert "honest build" in build["note"].lower()
    assert "does not need full access" in build["note"].lower()
    assert "twin is not launch" in build["note"].lower()
    assert "packs, modules, and repositories are not skus" in build["note"].lower()
    assert "does not need full access" in build["lede"].lower()
    assert "twin is not launch" in build["lede"].lower()
    assert cat["programs"]["website"]["honest_build"] is True
    assert cat["programs"]["website"]["honest_operators"] is True
    assert cat["programs"]["website"]["honest_build_live"] is False
    assert cat["programs"]["website"]["full_access_needed"] is False
    assert cat["programs"]["website"]["twin_is_launch"] is False
    assert cat["programs"]["website"]["packs_are_skus"] is False
    assert "honest build" in cat["operations"]["note"].lower()
    assert any("3.05.0" in item and "honest build" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "full access as admit" in does_not
    assert "more secrets as build" in does_not
    assert "the twin as launch" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest build" in principles
    assert "does not need full access" in principles
    assert "twin is not launch" in principles
    assert "packs, modules, and repositories are not skus" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 78
    assert upgrades[75]["who"] == "tree"
    assert upgrades[75]["done"] is True
    assert upgrades[75]["marks_live_pin"] is False
    blob = f"{upgrades[75]['title']} {upgrades[75]['do']}".lower()
    assert "honest build" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    assert "3.08.0" in html
    assert "honest build" in html.lower()
    assert "does not need full access" in html.lower()
    assert "twin is not launch" in html.lower()
    assert "packs, modules, and repositories are not skus" in html.lower()
    assert 'id="build-three"' in html
    assert 'data-build-refuse="full_access_as_admit"' in html
    assert 'data-build-refuse="more_secrets_as_build"' in html
    assert 'data-build-refuse="twin_as_launch"' in html
    assert 'data-build-refuse="pack_as_sku"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#agent-tools"' not in nav
    assert 'href="/build"' not in nav
    assert 'href="/operators"' not in nav
    assert "bindBuildRefuses" in js
    assert "refuseBuild" in js
    assert "build-lede" not in js
    assert "operator-lede" not in js
    assert "access-lede" not in js
    assert "agent-tools-lede" not in js
    assert "honest build" in twin.lower()
    assert "does not need full access" in twin.lower()
    assert "build" in app.lower()
    assert "Full access" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.08.0"
    status = public_status()
    assert status["release"] == "3.08.0"
    assert status["website"]["honest_build"] is True
    assert status["website"]["honest_build_live"] is False
    assert status["website"]["full_access_needed"] is False
    assert status["website"]["twin_is_launch"] is False
    assert status["website"]["packs_are_skus"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.build.v1"
    assert review["need_full"] is False
    assert "Mark the twin as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_305_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.04.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.05.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_build"] = False

    def live(cat):
        cat["programs"]["website"]["honest_build_live"] = True

    def need(cat):
        cat["microsoft_stack"]["build"]["need_full"] = True

    def twin(cat):
        cat["microsoft_stack"]["build"]["twin_is_launch"] = True

    def site(cat):
        cat["microsoft_stack"]["build"]["site"] = "Build on #agent-tools."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest build" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            "SKU attach chain. Honest operators sit on #agent-tools. Cursor is recorded."
        )

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "full access" not in item.lower() and "twin as launch" not in item.lower()
        ]

    for mutator in (release, closed, flag_off, live, need, twin, site, principles, ops, ciso):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["microsoft_stack"]["build"]["kind"] = "ainav.honest.build.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(hole, hole["plane_interface"])
    needed = copy.deepcopy(edge)
    needed["microsoft_stack"]["build"]["need_full"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(needed, needed["plane_interface"])
    twin_flag = copy.deepcopy(edge)
    twin_flag["microsoft_stack"]["build"]["twin_is_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(twin_flag, twin_flag["plane_interface"])
    pack_flag = copy.deepcopy(edge)
    pack_flag["microsoft_stack"]["build"]["packs_are_skus"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(pack_flag, pack_flag["plane_interface"])
    site_hole = copy.deepcopy(edge)
    site_hole["microsoft_stack"]["build"]["site"] = site_hole["microsoft_stack"]["build"]["site"].replace(
        "This plane does not need full access. The twin is not launch. Packs, modules, and repositories are not SKUs.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(site_hole, site_hole["plane_interface"])
    honest = copy.deepcopy(edge)
    honest["microsoft_stack"]["build"]["honest"] = False
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(honest, honest["plane_interface"])
    site_need = copy.deepcopy(edge)
    site_need["programs"]["website"]["full_access_needed"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(site_need, site_need["plane_interface"])
    site_twin = copy.deepcopy(edge)
    site_twin["programs"]["website"]["twin_is_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(site_twin, site_twin["plane_interface"])
    site_packs = copy.deepcopy(edge)
    site_packs["programs"]["website"]["packs_are_skus"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(site_packs, site_packs["plane_interface"])
    ops_hole = copy.deepcopy(edge)
    ops_hole["operations"]["note"] = "SKU attach chain. #agent-tools."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(ops_hole, ops_hole["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["honest_build"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    success_missing = copy.deepcopy(edge["expert_review"]["success"])
    success_missing.pop("honest_build")
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_missing)
    success_kind = copy.deepcopy(edge["expert_review"]["success"])
    success_kind["honest_build"]["kind"] = "ainav.honest.build.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_kind)
    success_href = copy.deepcopy(edge["expert_review"]["success"])
    success_href["honest_build"]["href"] = "#fear"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_href)
    for missing in (
        "Treat full access as admit",
        "Treat more secrets as build",
        "Treat the twin as launch",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
    site_mapped = copy.deepcopy(edge)
    site_mapped["microsoft_stack"]["build"]["site"] = (
        "Honest build on #agent-tools. This plane does not need full access. Packs, modules, and repositories are not SKUs."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(site_mapped, site_mapped["plane_interface"])
    site_packs_note = copy.deepcopy(edge)
    site_packs_note["microsoft_stack"]["build"]["site"] = (
        "Honest build on #agent-tools. This plane does not need full access. The twin is not launch."
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(site_packs_note, site_packs_note["plane_interface"])
    principles_honest = copy.deepcopy(edge)
    principles_honest["expert_review"]["first_principles"] = [
        item.replace("Honest build", "Operator maps").replace("honest build", "operator maps")
        for item in principles_honest["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(principles_honest, principles_honest["plane_interface"])
    ops_sku = copy.deepcopy(edge)
    ops_sku["operations"]["note"] = "Honest build sits on #agent-tools."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(ops_sku, ops_sku["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest build."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_305(ops_href, ops_href["plane_interface"])
    first_full = copy.deepcopy(edge["expert_review"]["first_principles"])
    first_full = [item.replace("does not need full access", "needs full access") for item in first_full]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(first_full)
    first_twin = copy.deepcopy(edge["expert_review"]["first_principles"])
    first_twin = [item.replace("The twin is not launch.", "The twin stays mapped.") for item in first_twin]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(first_twin)
    first_packs = copy.deepcopy(edge["expert_review"]["first_principles"])
    first_packs = [
        item.replace("Packs, modules, and repositories are not SKUs.", "Packs stay maps.")
        for item in first_packs
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(first_packs)
