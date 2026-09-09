from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_COPILOT_STUDIO_HREFS,
    HONEST_COPILOT_STUDIO_REFUSE_IDS,
    HONEST_COPILOT_STUDIO_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.copilot_studio import public_review
from ainav.dashboard import public_dashboard
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_310_honest_copilot_studio():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.16.0"
    studio = cat["honest_copilot_studio"]
    assert studio["kind"] == "ainav.honest.copilot_studio.v1"
    assert studio["honest"] is True
    assert studio["considered"] is True
    assert studio["is_job_c"] is False
    assert studio["is_sku"] is False
    assert studio["is_admit_plane"] is False
    assert studio["is_complement"] is False
    assert studio["is_seat"] is False
    assert studio["certified"] is False
    assert studio["created"] is False
    assert studio["href"] == "#success"
    refuse = [item for item in studio["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_COPILOT_STUDIO_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_COPILOT_STUDIO_REFUSE_TEXT[key] for key in HONEST_COPILOT_STUDIO_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_COPILOT_STUDIO_HREFS[key] for key in HONEST_COPILOT_STUDIO_REFUSE_IDS}
    assert "honest copilot studio" in studio["note"].lower()
    assert "copilot studio is not job c" in studio["note"].lower()
    assert "copilot studio is not a sku" in studio["note"].lower()
    assert cat["programs"]["website"]["honest_copilot_studio"] is True
    assert cat["programs"]["website"]["honest_power_pages"] is True
    assert cat["programs"]["website"]["honest_copilot_studio_live"] is False
    assert cat["programs"]["website"]["copilot_studio_is_job_c"] is False
    assert cat["programs"]["website"]["copilot_studio_is_sku"] is False
    assert cat["programs"]["website"]["copilot_studio_is_admit"] is False
    assert cat["programs"]["website"]["copilot_studio_is_complement"] is False
    assert cat["programs"]["website"]["copilot_studio_is_seat"] is False
    assert "honest copilot studio" in cat["operations"]["note"].lower()
    assert "#success" in cat["operations"]["note"]
    assert any("3.10.0" in item and "copilot studio" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "copilot studio as job c" in does_not
    assert "copilot studio as a sku" in does_not
    assert "copilot studio as the admit plane" in does_not
    assert "copilot studio as a complement" in does_not
    assert "copilot studio as seat b" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest copilot studio" in principles
    assert "copilot studio is not job c" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 86
    assert upgrades[80]["who"] == "tree"
    assert upgrades[80]["done"] is True
    assert upgrades[80]["marks_live_pin"] is False
    blob = f"{upgrades[80]['title']} {upgrades[80]['do']}".lower()
    assert "honest copilot studio" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.14.0" in html
    assert "honest copilot studio" in html.lower()
    assert "copilot studio is not job c" in html.lower()
    assert "copilot studio is not a sku" in html.lower()
    assert 'id="studio-consider"' in html
    assert 'id="studio-zeros"' in html
    assert 'id="studio-facts"' in html
    assert 'data-studio-refuse="studio_as_job_c"' in html
    assert 'data-studio-refuse="studio_as_sku"' in html
    assert 'data-studio-refuse="studio_as_admit"' in html
    assert 'data-studio-refuse="studio_as_complement"' in html
    assert 'data-studio-refuse="studio_as_seat"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/copilot-studio"' not in nav
    assert 'href="#studio"' not in nav
    assert 'href="#studio-consider"' not in nav
    assert "Copilot Studio" not in nav
    assert "bindStudioRefuses" in js
    assert "refuseStudio" in js
    assert "studio-lede" not in js
    assert "pages-lede" not in js
    assert "whole-lede" not in js
    assert "industry-cert-lede" not in js
    assert "ready-lede" not in js
    assert "build-lede" not in js
    assert "operator-lede" not in js
    assert "access-lede" not in js
    assert "honest copilot studio" in twin.lower()
    assert "copilot studio is not job c" in twin.lower()
    assert "Digital twin · 3.16.0" in twin
    assert "AINAV.Institute twin · 3.16.0" in twin
    assert "3.08.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    assert "Application kit · 3.16.0" in kit
    assert "Copilot Studio is Job C" in identify
    assert "Open Copilot Studio" in identify
    assert "Copilot Studio is Job C" in app
    dash = public_dashboard()
    assert dash["release"] == "3.16.0"
    status = public_status()
    assert status["release"] == "3.16.0"
    assert status["website"]["honest_copilot_studio"] is True
    assert status["website"]["honest_copilot_studio_live"] is False
    assert status["website"]["copilot_studio_is_job_c"] is False
    assert status["website"]["copilot_studio_is_sku"] is False
    assert status["website"]["copilot_studio_is_admit"] is False
    assert status["website"]["copilot_studio_is_complement"] is False
    assert status["website"]["copilot_studio_is_seat"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.copilot_studio.v1"
    assert review["is_job_c"] is False
    assert "Treat Copilot Studio as Job C." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_310_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.09.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.10.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_copilot_studio"] = False

    def live(cat):
        cat["programs"]["website"]["honest_copilot_studio_live"] = True

    def job_c(cat):
        cat["programs"]["website"]["copilot_studio_is_job_c"] = True

    def sku(cat):
        cat["programs"]["website"]["copilot_studio_is_sku"] = True

    def admit(cat):
        cat["programs"]["website"]["copilot_studio_is_admit"] = True

    def complement(cat):
        cat["programs"]["website"]["copilot_studio_is_complement"] = True

    def seat(cat):
        cat["programs"]["website"]["copilot_studio_is_seat"] = True

    def site(cat):
        cat["honest_copilot_studio"]["site"] = "Studio board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest copilot studio" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest Power Pages sits on #twin."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. Not a webmaster CMS. Not Squarespace. Not Power Pages."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        job_c,
        sku,
        admit,
        complement,
        seat,
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
    hole["honest_copilot_studio"]["kind"] = "ainav.honest.copilot_studio.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_copilot_studio"]["site"] = site_name["honest_copilot_studio"]["site"].replace(
        "Honest Copilot Studio",
        "Studio board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(site_name, site_name["plane_interface"])
    site_job = copy.deepcopy(edge)
    site_job["honest_copilot_studio"]["site"] = site_job["honest_copilot_studio"]["site"].replace(
        "Copilot Studio is not Job C. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(site_job, site_job["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_copilot_studio"]["site"] = site_route["honest_copilot_studio"]["site"].replace(
        "Not a /copilot-studio route. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_copilot_studio"]["site"] = site_glance["honest_copilot_studio"]["site"].replace(
        "First glance stays the write rail. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["honest_copilot_studio"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    success_missing = copy.deepcopy(edge["expert_review"]["success"])
    success_missing.pop("honest_copilot_studio")
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_missing)
    success_kind = copy.deepcopy(edge["expert_review"]["success"])
    success_kind["honest_copilot_studio"]["kind"] = "ainav.honest.copilot_studio.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_kind)
    success_href = copy.deepcopy(edge["expert_review"]["success"])
    success_href["honest_copilot_studio"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_href)
    success_job = copy.deepcopy(edge["expert_review"]["success"])
    success_job["honest_copilot_studio"]["is_job_c"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_job)
    success_sku = copy.deepcopy(edge["expert_review"]["success"])
    success_sku["honest_copilot_studio"]["is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_sku)
    success_admit = copy.deepcopy(edge["expert_review"]["success"])
    success_admit["honest_copilot_studio"]["is_admit_plane"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_admit)
    success_seat = copy.deepcopy(edge["expert_review"]["success"])
    success_seat["honest_copilot_studio"]["is_seat"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_seat)
    job_body = copy.deepcopy(edge)
    job_body["honest_copilot_studio"]["is_job_c"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(job_body, job_body["plane_interface"])
    sku_body = copy.deepcopy(edge)
    sku_body["honest_copilot_studio"]["is_sku"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(sku_body, sku_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_copilot_studio"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(certified, certified["plane_interface"])
    principles_direct = copy.deepcopy(edge)
    principles_direct["expert_review"]["first_principles"] = [
        item
        for item in principles_direct["expert_review"]["first_principles"]
        if "honest copilot studio" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(principles_direct, principles_direct["plane_interface"])
    principles_job = copy.deepcopy(edge)
    principles_job["expert_review"]["first_principles"] = [
        item.replace("Copilot Studio is not Job C.", "Copilot Studio is recorded.")
        for item in principles_job["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(principles_job, principles_job["plane_interface"])
    principles_first = copy.deepcopy(edge)
    principles_first["expert_review"]["first_principles"] = [
        item.replace("Honest Copilot Studio sits on #success.", "Studio sits on #success.")
        for item in principles_first["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_first["expert_review"]["first_principles"])
    ops_attach = copy.deepcopy(edge)
    ops_attach["operations"]["note"] = "Honest Copilot Studio sits on #success."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(ops_attach, ops_attach["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest Copilot Studio is recorded."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(ops_href, ops_href["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. Studio sits on #success."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(ops_name, ops_name["plane_interface"])
    managed_direct = copy.deepcopy(edge)
    managed_direct["expert_review"]["success"]["managed_face"]["managed"] = managed_direct["expert_review"]["success"]["managed_face"]["managed"].replace(
        " Not Copilot Studio.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_310(managed_direct, managed_direct["plane_interface"])
    for missing in (
        "Treat Copilot Studio as Job C",
        "Treat Copilot Studio as a SKU",
        "Treat Copilot Studio as the admit plane",
        "Treat Copilot Studio as a complement",
        "Treat Copilot Studio as seat B",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
