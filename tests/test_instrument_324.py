from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import public_dashboard
from ainav.face_kit import public_llms, public_search
from ainav.honest_better import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_324_honest_planes():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.25.0"
    better = cat["honest_better"]
    assert better["planes_as_launch"] is False
    assert better["industry_ten_as_launch"] is False
    assert better["client_ten_as_live_client"] is False
    assert better["twin_ten_as_launch"] is False
    assert better["named_vertical_as_sku"] is False
    assert better["institute_twin_is_assigned_sandbox"] is False
    assert better["shared_sandbox_is_production"] is False
    assert "a 10/10 of industry, client, and twin planes is not launch" in better["note"].lower()
    assert "a named vertical is not a sku" in better["lede"].lower()
    assert "the institute twin is not the assigned client sandbox" in better["site"].lower()
    site = cat["programs"]["website"]
    assert site["honest_planes"] is True
    assert site["please_make"] is True
    assert site["honest_planes_live"] is False
    assert site["planes_as_launch"] is False
    assert site["industry_ten_as_launch"] is False
    assert site["client_ten_as_live_client"] is False
    assert site["twin_ten_as_launch"] is False
    assert site["named_vertical_as_sku"] is False
    assert site["institute_twin_is_assigned_sandbox"] is False
    assert site["shared_sandbox_is_production"] is False
    assert any("3.24.0" in item and "honest planes" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.23.0" in item and "please make better" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a 10/10 of industry, client, and twin as launch" in does_not
    assert "a 10/10 industry as launch" in does_not
    assert "a 10/10 client as a live client" in does_not
    assert "a 10/10 twin as launch" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "a 10/10 of industry, client, and twin planes is not launch" in principles
    assert "a named vertical is not a sku" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 95
    assert upgrades[94]["who"] == "tree"
    assert upgrades[94]["done"] is True
    assert upgrades[94]["marks_live_pin"] is False
    blob = f"{upgrades[94]['title']} {upgrades[94]['do']}".lower()
    assert "honest planes" in blob
    assert "10/10" in blob
    assert "named vertical" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    swa = json.loads(Path("institute/staticwebapp.config.json").read_text(encoding="utf-8"))
    assert "3.24.0" in html
    assert "3.23.0" in html
    assert "a 10/10 of industry, client, and twin planes is not launch" in html.lower()
    assert "a 10/10 industry is not launch" in html.lower()
    assert "a 10/10 client is not a live client" in html.lower()
    assert 'id="industry-proof"' in html
    assert 'id="industry-is-ten"' in html
    assert 'id="industry-is-sku"' in html
    assert 'id="industry-is-route"' in html
    assert "Room 1 books" in html
    assert 'id="universe-proof"' in html
    assert 'id="universe-is-ten"' in html
    assert 'id="client-planes-proof"' in html
    assert html.index('id="join-consider"') < html.index('id="firm-console"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert "Honest planes" not in nav
    assert "10/10 industry" not in nav
    assert 'id="twin-planes-proof"' in twin
    assert 'id="twin-planes-hops"' in twin
    assert "Digital twin · 3.25.0" in twin
    assert "A 10/10 industry is not launch" in twin
    assert "A 10/10 industry is launch" in identify
    assert "A 10/10 client is a live client" in identify
    assert "A 10/10 twin is launch" in identify
    assert "Segregated industry is a SKU" in identify
    assert "A 10/10 industry is launch" in app
    assert "A 10/10 client is a live client" in app
    assert "A 10/10 twin is launch" in app
    assert "Application · 3.25.0" in app
    assert "not a /industry" in lost.lower()
    assert "not a /universe" in lost.lower()
    assert "a 10/10 of industry, client, and twin planes is not launch" in lost.lower()
    assert "#industry-proof" in css
    assert "#universe-proof" in css
    assert "#client-planes-proof" in css
    assert "#twin-planes-proof" in css
    routes = [item.get("route") for item in swa["routes"] if isinstance(item, dict)]
    assert "/industry" in routes
    assert "/universe" in routes
    assert "/crypto" in routes
    assert "/sandbox" in swa["navigationFallback"]["exclude"]
    assert any(item.get("route") == "/industry" and item.get("statusCode") == 404 for item in swa["routes"])
    assert html.count("Walk honest better") >= 4
    assert html.count("Owner book") == 1
    llms = public_llms().lower()
    assert "a 10/10 of industry, client, and twin planes is not launch" in llms or "honest planes" in llms
    search = public_search()
    industry_rec = next(item for item in search["records"] if item["id"] == "industry")
    universe_rec = next(item for item in search["records"] if item["id"] == "universe")
    assert "a 10/10 industry is not launch" in industry_rec["text"].lower()
    assert "a 10/10 client is not a live client" in universe_rec["text"].lower()
    dash = public_dashboard()
    assert dash["release"] == "3.25.0"
    status = public_status()
    assert status["release"] == "3.25.0"
    assert status["website"]["honest_planes"] is True
    assert status["website"]["honest_planes_live"] is False
    assert status["website"]["planes_as_launch"] is False
    review = public_review()
    assert review["planes_as_launch"] is False
    assert "Treat a 10/10 of industry, client, and twin as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    managed = cat["expert_review"]["success"]["managed_face"]["managed"].lower()
    assert "not a 10/10-planes launch" in managed
    assert cat["expert_review"]["success"]["honest_better"]["planes_as_launch"] is False
    drawer = cat["expert_review"]["success"]["industry_drawer"]
    assert drawer["industry_ten_as_launch"] is False
    assert "a 10/10 industry is not launch" in drawer["note"].lower()
    universe_body = cat["expert_review"]["success"]["client_universe"]
    assert universe_body["client_ten_as_live_client"] is False
    assert "a 10/10 client is not a live client" in universe_body["note"].lower()


def test_instrument_324_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.23.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.24.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_planes"] = False

    def live(cat):
        cat["programs"]["website"]["honest_planes_live"] = True

    def launch(cat):
        cat["programs"]["website"]["planes_as_launch"] = True

    def industry_ten(cat):
        cat["programs"]["website"]["industry_ten_as_launch"] = True

    def client_ten(cat):
        cat["programs"]["website"]["client_ten_as_live_client"] = True

    def twin_ten(cat):
        cat["programs"]["website"]["twin_ten_as_launch"] = True

    def vertical(cat):
        cat["programs"]["website"]["named_vertical_as_sku"] = True

    def assigned(cat):
        cat["programs"]["website"]["institute_twin_is_assigned_sandbox"] = True

    def shared(cat):
        cat["programs"]["website"]["shared_sandbox_is_production"] = True

    def body_launch(cat):
        cat["honest_better"]["planes_as_launch"] = True

    def site(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A 10/10 of industry, client, and twin planes is not launch.",
            "Planes are recorded.",
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "a 10/10 of industry, client, and twin planes is not launch" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = cat["operations"]["note"].replace(
            " 3.24.0 honest planes sit on #industry, #universe, #client-planes, and the twin. A 10/10 of industry, client, and twin planes is not launch. A named vertical is not a SKU. The Institute twin is not the assigned client sandbox. A shared sandbox is not production.",
            "",
        )

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            cat["expert_review"]["success"]["managed_face"]["managed"].replace(
                " Not a 10/10-planes launch.",
                "",
            )
        )

    def hosted(cat):
        cat["expert_review"]["success"]["honest_better"]["planes_as_launch"] = True

    def body_industry(cat):
        cat["honest_better"]["industry_ten_as_launch"] = True

    def body_client(cat):
        cat["honest_better"]["client_ten_as_live_client"] = True

    def body_twin(cat):
        cat["honest_better"]["twin_ten_as_launch"] = True

    def site_vertical(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A named vertical is not a SKU.",
            "A named vertical is recorded.",
        )

    def site_assigned(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "The Institute twin is not the assigned client sandbox.",
            "The Institute twin is recorded.",
        )

    def principles_vertical(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("A named vertical is not a SKU.", "A named vertical is recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def principles_assigned(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace(
                "The Institute twin is not the assigned client sandbox.",
                "The Institute twin is recorded.",
            )
            for item in cat["expert_review"]["first_principles"]
        ]

    def hosted_industry(cat):
        cat["expert_review"]["success"]["honest_better"]["industry_ten_as_launch"] = True

    def hosted_client(cat):
        cat["expert_review"]["success"]["honest_better"]["client_ten_as_live_client"] = True

    def hosted_twin(cat):
        cat["expert_review"]["success"]["honest_better"]["twin_ten_as_launch"] = True

    def drawer_ten(cat):
        cat["expert_review"]["success"]["industry_drawer"]["industry_ten_as_launch"] = True

    def universe_ten(cat):
        cat["expert_review"]["success"]["client_universe"]["client_ten_as_live_client"] = True

    def body_vertical(cat):
        cat["honest_better"]["named_vertical_as_sku"] = True

    def body_assigned(cat):
        cat["honest_better"]["institute_twin_is_assigned_sandbox"] = True

    def body_shared(cat):
        cat["honest_better"]["shared_sandbox_is_production"] = True

    def hosted_vertical(cat):
        cat["expert_review"]["success"]["honest_better"]["named_vertical_as_sku"] = True

    def drawer_vertical(cat):
        cat["expert_review"]["success"]["industry_drawer"]["named_vertical_as_sku"] = True

    def drawer_note(cat):
        drawer = cat["expert_review"]["success"]["industry_drawer"]
        for key in ("lede", "site", "note", "glance"):
            drawer[key] = str(drawer.get(key) or "").replace(
                "A 10/10 industry is not launch.",
                "Industry is recorded.",
            )

    def universe_assigned(cat):
        cat["expert_review"]["success"]["client_universe"]["institute_twin_is_assigned_sandbox"] = True

    def universe_note(cat):
        universe = cat["expert_review"]["success"]["client_universe"]
        for key in ("lede", "site", "note", "glance"):
            universe[key] = str(universe.get(key) or "").replace(
                "A 10/10 client is not a live client.",
                "Client is recorded.",
            )

    def upgrade_n(cat):
        by_n = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
        by_n[94]["title"] = "Rooms"
        by_n[94]["do"] = "Ship 3.24.0. Not LIVE_PIN_OK."

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        industry_ten,
        client_ten,
        twin_ten,
        vertical,
        assigned,
        shared,
        body_launch,
        site,
        principles,
        ops,
        managed,
        hosted,
        upgrade_n,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    for mutator in (
        body_launch,
        body_industry,
        body_client,
        body_twin,
        body_vertical,
        body_assigned,
        body_shared,
        site,
        site_vertical,
        site_assigned,
        principles_vertical,
        principles_assigned,
        hosted,
        hosted_industry,
        hosted_client,
        hosted_twin,
        hosted_vertical,
        drawer_ten,
        drawer_vertical,
        drawer_note,
        universe_ten,
        universe_assigned,
        universe_note,
    ):
        hole = copy.deepcopy(edge)
        mutator(hole)
        with pytest.raises(IntegrityError):
            catmod._validate_instrument_324(hole, hole["plane_interface"])
    ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
    ciso_hole["ciso"]["does_not"] = [
        item
        for item in ciso_hole["ciso"]["does_not"]
        if item != "Treat a 10/10 of industry, client, and twin as launch"
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso_hole)
    for missing in (
        "Treat a 10/10 industry as launch",
        "Treat a 10/10 client as a live client",
        "Treat a 10/10 twin as launch",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [
            item for item in ciso_hole["ciso"]["does_not"] if item != missing
        ]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
