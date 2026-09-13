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


def test_release_is_323_please_make_better():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.28.0"
    better = cat["honest_better"]
    assert better["please_as_launch"] is False
    assert better["twin_http_is_launch"] is False
    assert better["sandbox_http_is_g14"] is False
    assert "please make better is not launch" in better["note"].lower()
    assert "twin http 200 is not launch" in better["lede"].lower()
    assert "sandbox http is not g14" in better["site"].lower()
    site = cat["programs"]["website"]
    assert site["please_make"] is True
    assert site["honest_make"] is True
    assert site["please_make_live"] is False
    assert site["please_as_launch"] is False
    assert site["twin_http_is_launch"] is False
    assert site["sandbox_http_is_g14"] is False
    assert any("3.23.0" in item and "please make better" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.22.0" in item and "making better" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "please make better as launch" in does_not
    assert "twin http as launch" in does_not
    assert "sandbox http as g14" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "please make better is not launch" in principles
    assert "twin http 200 is not launch" in principles
    assert "sandbox http is not g14" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 98
    assert upgrades[93]["who"] == "tree"
    assert upgrades[93]["done"] is True
    assert upgrades[93]["marks_live_pin"] is False
    blob = f"{upgrades[93]['title']} {upgrades[93]['do']}".lower()
    assert "please make better" in blob
    assert "twin http" in blob
    assert "sandbox http" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    swa = json.loads(Path("institute/staticwebapp.config.json").read_text(encoding="utf-8"))
    assert "3.23.0" in html
    assert "3.22.0" in html
    assert "please make better is not launch" in html.lower()
    assert "twin http 200 is not launch" in html.lower()
    assert "sandbox http is not g14" in html.lower()
    better_board = html.split('id="better-consider"', 1)[1].split('id="studio-consider"', 1)[0]
    assert 'id="better-is-please"' in better_board
    assert 'id="better-proof"' in better_board
    assert 'id="better-is-twin-http"' in better_board
    assert 'id="better-is-sandbox-http"' in better_board
    assert "Please make better is launch" in better_board
    assert html.index('id="ten-consider"') < html.index('id="better-consider"')
    assert html.index('id="better-consider"') < html.index('id="studio-consider"')
    assert html.index('id="join-consider"') < html.index('id="firm-console"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#better-consider"' not in nav
    assert "Please make better" not in nav
    assert 'id="twin-sandbox-proof"' in twin
    assert "Sandbox HTTP is not G14" in twin
    assert "please make better is not launch" in twin.lower()
    assert "Digital twin · 3.28.0" in twin
    assert "Please make better is launch" in identify
    assert "Twin HTTP is launch" in identify
    assert "Sandbox HTTP is G14" in identify
    assert "Please make better is launch" in app
    assert "Twin HTTP is launch" in app
    assert "Sandbox HTTP is G14" in app
    assert "Application · 3.28.0" in app
    assert "not a /better" in lost.lower()
    assert "please make better is not launch" in lost.lower()
    assert "#better-proof {" in css
    assert "#twin-sandbox-proof" in css
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in css
    routes = [item.get("route") for item in swa["routes"] if isinstance(item, dict)]
    assert "/better" in routes
    assert "/join" in swa["navigationFallback"]["exclude"]
    assert any(item.get("route") == "/better" and item.get("statusCode") == 404 for item in swa["routes"])
    assert html.count("Walk honest better") >= 4
    assert html.count("Owner book") == 1
    llms = public_llms().lower()
    assert "please make better is not launch" in llms
    search = public_search()
    better_rec = next(item for item in search["records"] if item["id"] == "better")
    assert "please make better is not launch" in better_rec["text"].lower()
    assert "twin http 200 is not launch" in better_rec["text"].lower()
    dash = public_dashboard()
    assert dash["release"] == "3.28.0"
    status = public_status()
    assert status["release"] == "3.28.0"
    assert status["website"]["please_make"] is True
    assert status["website"]["please_make_live"] is False
    assert status["website"]["twin_http_is_launch"] is False
    review = public_review()
    assert review["please_as_launch"] is False
    assert "Treat please make better as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    managed = cat["expert_review"]["success"]["managed_face"]["managed"].lower()
    assert "not a please-make-better launch" in managed
    assert cat["expert_review"]["success"]["honest_better"]["please_as_launch"] is False


def test_instrument_323_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.22.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.23.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["please_make"] = False

    def live(cat):
        cat["programs"]["website"]["please_make_live"] = True

    def launch(cat):
        cat["programs"]["website"]["please_as_launch"] = True

    def twin_http(cat):
        cat["programs"]["website"]["twin_http_is_launch"] = True

    def sandbox_http(cat):
        cat["programs"]["website"]["sandbox_http_is_g14"] = True

    def body_launch(cat):
        cat["honest_better"]["please_as_launch"] = True

    def site(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "Please make better is not launch.",
            "Better is recorded.",
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "please make better is not launch" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = (
            cat["operations"]["note"]
            .replace(
                "3.23.0 please make better sits on the twin. Please make better is not launch. Twin HTTP 200 is not launch. Sandbox HTTP is not G14. ",
                "",
            )
            .replace("Please make better is not launch.", "")
        )

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            cat["expert_review"]["success"]["managed_face"]["managed"].replace(
                " Not a please-make-better launch.",
                "",
            )
        )

    def hosted(cat):
        cat["expert_review"]["success"]["honest_better"]["please_as_launch"] = True

    def body_twin(cat):
        cat["honest_better"]["twin_http_is_launch"] = True

    def body_sandbox(cat):
        cat["honest_better"]["sandbox_http_is_g14"] = True

    def site_twin(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "Twin HTTP 200 is not launch.",
            "Twin HTTP is recorded.",
        )

    def site_sandbox(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "Sandbox HTTP is not G14.",
            "Sandbox HTTP is recorded.",
        )

    def principles_twin(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("Twin HTTP 200 is not launch.", "Twin HTTP is recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def principles_sandbox(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("Sandbox HTTP is not G14.", "Sandbox HTTP is recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def hosted_twin(cat):
        cat["expert_review"]["success"]["honest_better"]["twin_http_is_launch"] = True

    def hosted_sandbox(cat):
        cat["expert_review"]["success"]["honest_better"]["sandbox_http_is_g14"] = True

    def upgrade_n(cat):
        by_n = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
        by_n[93]["title"] = "Rooms"
        by_n[93]["do"] = "Ship 3.23.0. Not LIVE_PIN_OK."

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        twin_http,
        sandbox_http,
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
        body_twin,
        body_sandbox,
        site,
        site_twin,
        site_sandbox,
        principles_twin,
        principles_sandbox,
        hosted_twin,
        hosted_sandbox,
    ):
        hole = copy.deepcopy(edge)
        mutator(hole)
        with pytest.raises(IntegrityError):
            catmod._validate_instrument_323(hole, hole["plane_interface"])
    ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
    ciso_hole["ciso"]["does_not"] = [
        item for item in ciso_hole["ciso"]["does_not"] if item != "Treat please make better as launch"
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso_hole)
    for missing in ("Treat twin HTTP as launch", "Treat sandbox HTTP as G14"):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [
            item for item in ciso_hole["ciso"]["does_not"] if item != missing
        ]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
