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


def test_release_is_325_honest_rails():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.27.0"
    better = cat["honest_better"]
    assert better["rails_as_launch"] is False
    assert better["roster_as_wired"] is False
    assert better["flag_strip_as_admit"] is False
    assert "a 10/10 of the write rail, proof day, and bake-off is not launch" in better["note"].lower()
    assert "a polished microsoft roster is not a wired firm" in better["lede"].lower()
    assert "an identify flag strip is not admit" in better["site"].lower()
    site = cat["programs"]["website"]
    assert site["honest_rails"] is True
    assert site["honest_planes"] is True
    assert site["honest_rails_live"] is False
    assert site["rails_as_launch"] is False
    assert site["roster_as_wired"] is False
    assert site["flag_strip_as_admit"] is False
    assert any("3.25.0" in item and "honest rails" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.24.0" in item and "honest planes" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a 10/10 of the write rail, proof day, and bake-off as launch" in does_not
    assert "a polished microsoft roster as a wired firm" in does_not
    assert "an identify flag strip as admit" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "a 10/10 of the write rail, proof day, and bake-off is not launch" in principles
    assert "a polished microsoft roster is not a wired firm" in principles
    assert "an identify flag strip is not admit" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 97
    assert upgrades[95]["who"] == "tree"
    assert upgrades[95]["done"] is True
    assert upgrades[95]["marks_live_pin"] is False
    blob = f"{upgrades[95]['title']} {upgrades[95]['do']}".lower()
    assert "honest rails" in blob
    assert "write rail" in blob
    assert "bake-off" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    swa = json.loads(Path("institute/staticwebapp.config.json").read_text(encoding="utf-8"))
    assert "3.26.0" in html
    assert "3.25.0" in html
    assert "a 10/10 of the write rail, proof day, and bake-off is not launch" in html.lower()
    assert "a polished microsoft roster is not a wired firm" in html.lower() or "polished roster is a wired firm" in identify.lower()
    assert 'id="hero-rails-proof"' in html
    assert 'id="hero-write-rail"' in html
    assert 'id="hero-is-rails"' in html
    assert 'id="twin-day-proof"' in html
    assert 'id="twin-day-is-ten"' in html
    assert 'id="success-rails-proof"' in html
    assert html.index('id="join-consider"') < html.index('id="firm-console"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert "Honest rails" not in nav
    assert "Honest better" not in nav
    assert 'id="twin-rails-hops"' in twin
    assert "Digital twin · 3.27.0" in twin
    assert "A 10/10 of the write rail, proof day, and bake-off is not launch" in twin
    assert "The write rail is launch" in identify
    assert "A polished roster is a wired firm" in identify
    assert "Identify flag strip is admit" in identify
    assert 'id="identify-rails-proof"' in identify
    assert "The write rail is launch" in app
    assert "A polished roster is a wired firm" in app
    assert "Identify flag strip is admit" in app
    assert "Application · 3.27.0" in app
    assert "not a /firm" in lost.lower()
    assert "not a /proof" in lost.lower()
    assert "a 10/10 of the write rail, proof day, and bake-off is not launch" in lost.lower()
    assert "#hero-rails-proof" in css
    assert "#twin-day-proof" in css
    assert "#success-rails-proof" in css
    assert "#hero-write-rail" in css
    routes = [item.get("route") for item in swa["routes"] if isinstance(item, dict)]
    assert "/firm" in routes
    assert "/proof" in routes
    assert "/rails" in swa["navigationFallback"]["exclude"]
    assert any(item.get("route") == "/firm" and item.get("statusCode") == 404 for item in swa["routes"])
    assert html.count("Walk honest better") >= 4
    assert html.count("Owner book") == 1
    llms = public_llms().lower()
    assert "a 10/10 of the write rail, proof day, and bake-off is not launch" in llms or "honest rails" in llms
    search = public_search()
    sale_rec = next(item for item in search["records"] if item["id"] == "sale")
    demo_rec = next(item for item in search["records"] if item["id"] == "demo")
    better_rec = next(item for item in search["records"] if item["id"] == "better")
    assert "a 10/10 of the write rail, proof day, and bake-off is not launch" in sale_rec["text"].lower()
    assert "a 10/10 proof day is not launch" in demo_rec["text"].lower()
    assert "a 10/10 of the write rail, proof day, and bake-off is not launch" in better_rec["text"].lower()
    dash = public_dashboard()
    assert dash["release"] == "3.27.0"
    status = public_status()
    assert status["release"] == "3.27.0"
    assert status["website"]["honest_rails"] is True
    assert status["website"]["honest_rails_live"] is False
    assert status["website"]["rails_as_launch"] is False
    review = public_review()
    assert review["rails_as_launch"] is False
    assert "Treat a 10/10 of the write rail, proof day, and bake-off as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    managed = cat["expert_review"]["success"]["managed_face"]["managed"].lower()
    assert "not a 10/10-rails launch" in managed
    assert cat["expert_review"]["success"]["honest_better"]["rails_as_launch"] is False


def test_instrument_325_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.24.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.25.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_rails"] = False

    def live(cat):
        cat["programs"]["website"]["honest_rails_live"] = True

    def launch(cat):
        cat["programs"]["website"]["rails_as_launch"] = True

    def roster(cat):
        cat["programs"]["website"]["roster_as_wired"] = True

    def flags(cat):
        cat["programs"]["website"]["flag_strip_as_admit"] = True

    def body_launch(cat):
        cat["honest_better"]["rails_as_launch"] = True

    def site(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A 10/10 of the write rail, proof day, and bake-off is not launch.",
            "Rails are recorded.",
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "a 10/10 of the write rail, proof day, and bake-off is not launch" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = cat["operations"]["note"].replace(
            " 3.25.0 honest rails sit on the write rail, #twin, and #success. A 10/10 of the write rail, proof day, and bake-off is not launch. A polished Microsoft roster is not a wired firm. An identify flag strip is not admit.",
            "",
        )

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            cat["expert_review"]["success"]["managed_face"]["managed"].replace(
                " Not a 10/10-rails launch.",
                "",
            )
        )

    def hosted(cat):
        cat["expert_review"]["success"]["honest_better"]["rails_as_launch"] = True

    def body_roster(cat):
        cat["honest_better"]["roster_as_wired"] = True

    def body_flags(cat):
        cat["honest_better"]["flag_strip_as_admit"] = True

    def site_roster(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A polished Microsoft roster is not a wired firm.",
            "A polished roster is recorded.",
        )

    def site_flags(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "An identify flag strip is not admit.",
            "A flag strip is recorded.",
        )

    def principles_roster(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("A polished Microsoft roster is not a wired firm.", "A polished roster is recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def principles_flags(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("An identify flag strip is not admit.", "A flag strip is recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def hosted_roster(cat):
        cat["expert_review"]["success"]["honest_better"]["roster_as_wired"] = True

    def hosted_flags(cat):
        cat["expert_review"]["success"]["honest_better"]["flag_strip_as_admit"] = True

    def upgrade_n(cat):
        by_n = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
        by_n[95]["title"] = "Rooms"
        by_n[95]["do"] = "Ship 3.25.0. Not LIVE_PIN_OK."

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        roster,
        flags,
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
        body_roster,
        body_flags,
        site,
        site_roster,
        site_flags,
        principles_roster,
        principles_flags,
        hosted,
        hosted_roster,
        hosted_flags,
    ):
        hole = copy.deepcopy(edge)
        mutator(hole)
        with pytest.raises(IntegrityError):
            catmod._validate_instrument_325(hole, hole["plane_interface"])
    ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
    ciso_hole["ciso"]["does_not"] = [
        item
        for item in ciso_hole["ciso"]["does_not"]
        if item != "Treat a 10/10 of the write rail, proof day, and bake-off as launch"
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso_hole)
    for missing in (
        "Treat a polished Microsoft roster as a wired firm",
        "Treat an identify flag strip as admit",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [
            item for item in ciso_hole["ciso"]["does_not"] if item != missing
        ]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
