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


def test_release_is_326_honest_craft():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.27.0"
    better = cat["honest_better"]
    assert better["craft_as_launch"] is False
    assert better["look_as_production"] is False
    assert better["graphic_as_launch"] is False
    assert "a 10/10 of quality, content, format, and graphics is not launch" in better["note"].lower()
    assert "a 10/10 look is not production" in better["lede"].lower()
    assert "a polished graphic is not launch" in better["site"].lower()
    site = cat["programs"]["website"]
    assert site["honest_craft"] is True
    assert site["honest_rails"] is True
    assert site["honest_craft_live"] is False
    assert site["craft_as_launch"] is False
    assert site["look_as_production"] is False
    assert site["graphic_as_launch"] is False
    assert any("3.26.0" in item and "honest craft" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.25.0" in item and "honest rails" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a 10/10 of quality, content, format, and graphics as launch" in does_not
    assert "a 10/10 look as production" in does_not
    assert "a polished graphic as launch" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "a 10/10 of quality, content, format, and graphics is not launch" in principles
    assert "a 10/10 look is not production" in principles
    assert "a polished graphic is not launch" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 97
    assert upgrades[96]["who"] == "tree"
    assert upgrades[96]["done"] is True
    assert upgrades[96]["marks_live_pin"] is False
    blob = f"{upgrades[96]['title']} {upgrades[96]['do']}".lower()
    assert "honest craft" in blob
    assert "write-rail diagram" in blob or "write rail" in blob
    assert "#brand" in blob or "brand" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    swa = json.loads(Path("institute/staticwebapp.config.json").read_text(encoding="utf-8"))
    manifest = json.loads(Path("institute/site.webmanifest").read_text(encoding="utf-8"))
    assert "3.26.0" in html
    assert "3.25.0" in html
    assert "a 10/10 of quality, content, format, and graphics is not launch" in html.lower()
    assert "a 10/10 look is not production" in html.lower()
    assert "a polished graphic is not launch" in html.lower()
    assert 'id="hero-diagram"' in html
    assert 'src="graphics/write-rail.svg"' in html
    assert 'id="brand-craft-proof"' in html
    assert 'id="ten-craft-proof"' in html
    assert "graphics/emblem.svg" in html
    assert html.index('id="join-consider"') < html.index('id="firm-console"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert "Honest craft" not in nav
    assert "Honest better" not in nav
    assert "Honest rails" not in nav
    assert 'id="twin-craft-hops"' in twin
    assert "Digital twin · 3.27.0" in twin
    assert "A 10/10 of quality, content, format, and graphics is not launch" in twin
    assert "A 10/10 of quality, content, format, and graphics is launch" in identify
    assert "A 10/10 look is production" in identify
    assert "A polished graphic is launch" in identify
    assert 'id="identify-craft-proof"' in identify
    assert "A 10/10 of quality, content, format, and graphics is launch" in app
    assert "A 10/10 look is production" in app
    assert "A polished graphic is launch" in app
    assert "Application · 3.27.0" in app
    assert "not a /brand" in lost.lower()
    assert "not a /craft" in lost.lower()
    assert "a 10/10 of quality, content, format, and graphics is not launch" in lost.lower()
    assert "#hero-diagram" in css
    assert "#brand-craft-proof" in css
    assert "#ten-craft-proof" in css
    assert "color: var(--void-ink)" in css.split("#hero-contrast article[data-pin=\"job-c\"] h3", 1)[1][:280]
    assert "color: var(--gold-ink)" in css.split(".plane-strip.plane-page-first b", 1)[1][:180]
    assert ".band .not" in css
    assert ".band .kicker" in css
    routes = [item.get("route") for item in swa["routes"] if isinstance(item, dict)]
    assert "/brand" in routes
    assert "/craft" in routes
    assert "/look" in routes
    assert "/graphics" in routes
    assert "/brand" in swa["navigationFallback"]["exclude"]
    assert "/craft" in swa["navigationFallback"]["exclude"]
    assert any(item.get("route") == "/brand" and item.get("statusCode") == 404 for item in swa["routes"])
    assert html.count("Walk honest better") >= 4
    assert html.count("Owner book") == 1
    assert not any(icon.get("sizes") == "512x512" for icon in manifest["icons"])
    assert any(icon.get("src") == "graphics/emblem.svg" for icon in manifest["icons"])
    assert "twitter:image" in html
    assert "og:image:alt" in html
    assert "graphics/emblem.svg" in kit
    assert "Application kit · 3.27.0" in kit
    search_js = Path("institute/search.js").read_text(encoding="utf-8")
    assert "RESULT_CAP" in search_js
    assert "aria-expanded" in search_js
    assert 'role="combobox"' in html
    assert 'role="combobox"' in app
    assert 'role="combobox"' in kit
    assert 'aria-haspopup="listbox"' in html
    assert 'aria-haspopup="listbox"' in app
    assert 'aria-haspopup="listbox"' in kit
    assert 'id="twin-ribbon"' in app
    assert "Escape" in search_js
    llms = public_llms().lower()
    assert "a 10/10 of quality, content, format, and graphics is not launch" in llms or "honest craft" in llms
    search = public_search()
    sale_rec = next(item for item in search["records"] if item["id"] == "sale")
    brand_rec = next(item for item in search["records"] if item["id"] == "brand")
    ten_rec = next(item for item in search["records"] if item["id"] == "ten")
    better_rec = next(item for item in search["records"] if item["id"] == "better")
    assert "a 10/10 of quality, content, format, and graphics is not launch" in sale_rec["text"].lower()
    assert "a 10/10 look is not production" in brand_rec["text"].lower()
    assert "a 10/10 of quality, content, format, and graphics is not launch" in ten_rec["text"].lower()
    assert "a 10/10 of quality, content, format, and graphics is not launch" in better_rec["text"].lower()
    dash = public_dashboard()
    assert dash["release"] == "3.27.0"
    status = public_status()
    assert status["release"] == "3.27.0"
    assert status["website"]["honest_craft"] is True
    assert status["website"]["honest_craft_live"] is False
    assert status["website"]["craft_as_launch"] is False
    review = public_review()
    assert review["craft_as_launch"] is False
    assert "Treat a 10/10 of quality, content, format, and graphics as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    managed = cat["expert_review"]["success"]["managed_face"]["managed"].lower()
    assert "not a 10/10-craft launch" in managed
    assert cat["expert_review"]["success"]["honest_better"]["craft_as_launch"] is False


def test_instrument_326_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.25.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.26.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_craft"] = False

    def live(cat):
        cat["programs"]["website"]["honest_craft_live"] = True

    def launch(cat):
        cat["programs"]["website"]["craft_as_launch"] = True

    def look(cat):
        cat["programs"]["website"]["look_as_production"] = True

    def graphic(cat):
        cat["programs"]["website"]["graphic_as_launch"] = True

    def body_launch(cat):
        cat["honest_better"]["craft_as_launch"] = True

    def site(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A 10/10 of quality, content, format, and graphics is not launch.",
            "Craft is recorded.",
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "a 10/10 of quality, content, format, and graphics is not launch" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = cat["operations"]["note"].replace(
            " 3.26.0 honest craft sits on the write-rail diagram, #brand, and #ten-proof. A 10/10 of quality, content, format, and graphics is not launch. A 10/10 look is not production. A polished graphic is not launch.",
            "",
        )

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            cat["expert_review"]["success"]["managed_face"]["managed"].replace(
                " Not a 10/10-craft launch.",
                "",
            )
        )

    def hosted(cat):
        cat["expert_review"]["success"]["honest_better"]["craft_as_launch"] = True

    def body_look(cat):
        cat["honest_better"]["look_as_production"] = True

    def body_graphic(cat):
        cat["honest_better"]["graphic_as_launch"] = True

    def site_look(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A 10/10 look is not production.",
            "A look is recorded.",
        )

    def site_graphic(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A polished graphic is not launch.",
            "A graphic is recorded.",
        )

    def principles_look(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("A 10/10 look is not production.", "A look is recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def principles_graphic(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("A polished graphic is not launch.", "A graphic is recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def hosted_look(cat):
        cat["expert_review"]["success"]["honest_better"]["look_as_production"] = True

    def hosted_graphic(cat):
        cat["expert_review"]["success"]["honest_better"]["graphic_as_launch"] = True

    def upgrade_n(cat):
        by_n = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
        by_n[96]["title"] = "Rooms"
        by_n[96]["do"] = "Ship 3.26.0. Not LIVE_PIN_OK."

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        look,
        graphic,
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
        body_look,
        body_graphic,
        site,
        site_look,
        site_graphic,
        principles_look,
        principles_graphic,
        hosted,
        hosted_look,
        hosted_graphic,
    ):
        hole = copy.deepcopy(edge)
        mutator(hole)
        with pytest.raises(IntegrityError):
            catmod._validate_instrument_326(hole, hole["plane_interface"])
    ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
    ciso_hole["ciso"]["does_not"] = [
        item
        for item in ciso_hole["ciso"]["does_not"]
        if item != "Treat a 10/10 of quality, content, format, and graphics as launch"
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso_hole)
    for missing in (
        "Treat a 10/10 look as production",
        "Treat a polished graphic as launch",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [
            item for item in ciso_hole["ciso"]["does_not"] if item != missing
        ]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
