from __future__ import annotations

import copy
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


def test_release_is_322_making_better():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.28.0"
    better = cat["honest_better"]
    assert better["make_as_launch"] is False
    assert "making better is not launch" in better["note"].lower()
    assert "making better is not launch" in better["lede"].lower()
    assert "making better is not launch" in better["site"].lower()
    site = cat["programs"]["website"]
    assert site["honest_make"] is True
    assert site["honest_better"] is True
    assert site["honest_make_live"] is False
    assert site["make_as_launch"] is False
    assert any("3.22.0" in item and "making better" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.21.0" in item and "honest better" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "making better as launch" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "making better is not launch" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 98
    assert upgrades[92]["who"] == "tree"
    assert upgrades[92]["done"] is True
    assert upgrades[92]["marks_live_pin"] is False
    blob = f"{upgrades[92]['title']} {upgrades[92]['do']}".lower()
    assert "making better" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    assert "3.23.0" in html
    assert "3.22.0" in html
    assert "3.21.0" in html
    assert "making better is not launch" in html.lower()
    better_board = html.split('id="better-consider"', 1)[1].split('id="studio-consider"', 1)[0]
    assert 'id="better-is-make"' in better_board
    assert 'data-better-refuse="make_as_launch"' in better_board
    assert "Making better as launch" in better_board
    assert "Six hops scan" in better_board
    assert html.index('id="ten-consider"') < html.index('id="better-consider"')
    assert html.index('id="better-consider"') < html.index('id="studio-consider"')
    assert html.index('id="join-consider"') < html.index('id="firm-console"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#better-consider"' not in nav
    assert "Honest better" not in nav
    assert "Making better" not in nav
    assert "make_as_launch:" in js
    assert "data.make_as_launch" in js
    assert "#better-hops { grid-template-columns: repeat(6, minmax(0, 1fr)); }" in css
    assert "max-width: none; width: 100%;" in css
    assert '#better-facts [data-fact="business"]' in css
    section_css = css.split(".pages-facts.better-facts section {", 1)[1].split("}", 1)[0]
    assert "6.2rem minmax(0, 1fr)" in section_css
    assert "Making better is launch" in identify
    assert "Making better is launch" in app
    assert "making better is not launch" in twin.lower()
    assert "Application · 3.28.0" in app
    assert html.count("Walk honest better") >= 4
    assert html.count("Owner book") == 1
    llms = public_llms().lower()
    assert "making better is not launch" in llms
    search = public_search()
    better_rec = next(item for item in search["records"] if item["id"] == "better")
    assert "making better is not launch" in better_rec["text"].lower()
    dash = public_dashboard()
    assert dash["release"] == "3.28.0"
    status = public_status()
    assert status["release"] == "3.28.0"
    assert status["website"]["honest_make"] is True
    assert status["website"]["honest_make_live"] is False
    assert status["website"]["make_as_launch"] is False
    review = public_review()
    assert review["make_as_launch"] is False
    assert "Treat making better as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    managed = cat["expert_review"]["success"]["managed_face"]["managed"].lower()
    assert "not a make-better launch" in managed
    assert cat["expert_review"]["success"]["honest_better"]["make_as_launch"] is False


def test_instrument_322_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.21.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.22.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_make"] = False

    def live(cat):
        cat["programs"]["website"]["honest_make_live"] = True

    def launch(cat):
        cat["programs"]["website"]["make_as_launch"] = True

    def body_launch(cat):
        cat["honest_better"]["make_as_launch"] = True

    def site(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "Making better is not launch.",
            "Better is recorded.",
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "making better is not launch" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = cat["operations"]["note"].replace(
            "3.22.0 making better sits on #success. Making better is not launch. ",
            "",
        )

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            cat["expert_review"]["success"]["managed_face"]["managed"].replace(
                " Not a make-better launch.",
                "",
            )
        )

    def hosted(cat):
        cat["expert_review"]["success"]["honest_better"]["make_as_launch"] = True

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        body_launch,
        site,
        principles,
        ops,
        managed,
        hosted,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    for mutator in (body_launch, site, hosted):
        hole = copy.deepcopy(edge)
        mutator(hole)
        with pytest.raises(IntegrityError):
            catmod._validate_instrument_322(hole, hole["plane_interface"])
    ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
    ciso_hole["ciso"]["does_not"] = [
        item for item in ciso_hole["ciso"]["does_not"] if item != "Treat making better as launch"
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso_hole)
