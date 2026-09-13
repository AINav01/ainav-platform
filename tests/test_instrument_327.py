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


def test_release_is_327_honest_face():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.28.0"
    better = cat["honest_better"]
    assert better["kit_as_launch"] is False
    assert better["face_as_launch"] is False
    assert better["type_as_launch"] is False
    assert "please make better is not launch" in better["note"].lower()
    assert "a green kit check is not launch" in better["lede"].lower()
    assert "a 10/10 face is not production" in better["site"].lower()
    assert "readable type is not launch" in better["site"].lower()
    site = cat["programs"]["website"]
    assert site["honest_face"] is True
    assert site["honest_craft"] is True
    assert site["honest_face_live"] is False
    assert site["kit_as_launch"] is False
    assert site["face_as_launch"] is False
    assert site["type_as_launch"] is False
    assert any("3.27.0" in item and "honest face" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.26.0" in item and "honest craft" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a green kit check as launch" in does_not
    assert "a 10/10 face as production" in does_not
    assert "readable type as launch" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "a green kit check is not launch" in principles
    assert "a 10/10 face is not production" in principles
    assert "readable type is not launch" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 98
    assert upgrades[97]["who"] == "tree"
    assert upgrades[97]["done"] is True
    assert upgrades[97]["marks_live_pin"] is False
    blob = f"{upgrades[97]['title']} {upgrades[97]['do']}".lower()
    assert "honest face" in blob
    assert "search" in blob or "kit" in blob or "identify" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    swa = json.loads(Path("institute/staticwebapp.config.json").read_text(encoding="utf-8"))
    assert "3.28.0" in html
    assert "3.27.0" in html
    assert "3.26.0" in html
    assert "please make better is not launch" in html.lower()
    assert "a green kit check is not launch" in html.lower()
    assert "a 10/10 face is not production" in html.lower()
    assert "readable type is not launch" in html.lower()
    assert 'id="ten-face-proof"' in html
    assert 'id="ten-proof-is-please"' in html
    assert 'id="ten-proof-is-kit"' in html
    assert 'id="ten-proof-is-face"' in html
    assert html.index('id="join-consider"') < html.index('id="firm-console"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert "Honest face" not in nav
    assert "Honest better" not in nav
    assert "Please make better" not in nav
    assert 'id="twin-face-hops"' in twin
    assert "Digital twin · 3.28.0" in twin
    assert "A green kit check is not launch" in twin
    assert "A green kit check is launch" in identify
    assert "A 10/10 face is production" in identify
    assert "Readable type is launch" in identify
    assert 'id="identify-face-proof"' in identify
    assert 'id="twin-ribbon"' in identify
    assert 'id="app-face-proof"' in app
    assert "A 10/10 face is production" in app
    assert "Application · 3.28.0" in app
    assert "not a /face" in lost.lower()
    assert "a green kit check is not launch" in lost.lower()
    assert "a 10/10 face is not production" in lost.lower()
    assert "#ten-face-proof" in css
    assert "aria-activedescendant" in Path("institute/search.js").read_text(encoding="utf-8")
    assert "ArrowDown" in Path("institute/search.js").read_text(encoding="utf-8")
    assert "ArrowUp" in Path("institute/search.js").read_text(encoding="utf-8")
    routes = [item.get("route") for item in swa["routes"] if isinstance(item, dict)]
    assert "/face" in routes
    assert "/please" in routes
    assert "/face" in swa["navigationFallback"]["exclude"]
    assert any(item.get("route") == "/face" and item.get("statusCode") == 404 for item in swa["routes"])
    assert "Application kit · 3.28.0" in kit
    assert "a green kit check is not launch" in kit.lower()
    search_js = Path("institute/search.js").read_text(encoding="utf-8")
    assert 'src="site.js?v=3.28.0"' in html
    assert 'src="search.js?v=3.28.0"' in html
    assert "is-active" in search_js
    llms = public_llms().lower()
    assert "a green kit check is not launch" in llms or "honest face" in llms
    search = public_search()
    sale_rec = next(item for item in search["records"] if item["id"] == "sale")
    brand_rec = next(item for item in search["records"] if item["id"] == "brand")
    ten_rec = next(item for item in search["records"] if item["id"] == "ten")
    better_rec = next(item for item in search["records"] if item["id"] == "better")
    kit_rec = next(item for item in search["records"] if item["id"] == "kit")
    assert "a green kit check is not launch" in sale_rec["text"].lower()
    assert "a 10/10 face is not production" in brand_rec["text"].lower()
    assert "readable type is not launch" in ten_rec["text"].lower()
    assert "a green kit check is not launch" in better_rec["text"].lower()
    assert "a green kit check is not launch" in kit_rec["text"].lower()
    dash = public_dashboard()
    assert dash["release"] == "3.28.0"
    status = public_status()
    assert status["release"] == "3.28.0"
    assert status["website"]["honest_face"] is True
    assert status["website"]["honest_face_live"] is False
    assert status["website"]["kit_as_launch"] is False
    review = public_review()
    assert review["kit_as_launch"] is False
    assert review["face_as_launch"] is False
    assert review["type_as_launch"] is False
    cannot = " ".join(review["this_agent_cannot"])
    assert "Treat a green kit check as launch." in cannot
    assert "Treat a 10/10 face as production." in cannot
    assert "Treat readable type as launch." in cannot
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    managed = cat["expert_review"]["success"]["managed_face"]["managed"].lower()
    assert "not a 10/10-face launch" in managed
    assert cat["expert_review"]["success"]["honest_better"]["kit_as_launch"] is False
    assert cat["expert_review"]["success"]["honest_better"]["face_as_launch"] is False


def test_instrument_327_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.26.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.27.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_face"] = False

    def live(cat):
        cat["programs"]["website"]["honest_face_live"] = True

    def launch(cat):
        cat["programs"]["website"]["kit_as_launch"] = True

    def face(cat):
        cat["programs"]["website"]["face_as_launch"] = True

    def typography(cat):
        cat["programs"]["website"]["type_as_launch"] = True

    def body_launch(cat):
        cat["honest_better"]["kit_as_launch"] = True

    def site(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A green kit check is not launch.",
            "Kit is recorded.",
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "a green kit check is not launch" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = cat["operations"]["note"].replace(
            " 3.27.0 honest face sits on search, identify, kit, and #ten-proof. Please make better is not launch. A green kit check is not launch. A 10/10 face is not production. Readable type is not launch.",
            "",
        )

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            cat["expert_review"]["success"]["managed_face"]["managed"].replace(
                " Not a 10/10-face launch.",
                "",
            )
        )

    def hosted(cat):
        cat["expert_review"]["success"]["honest_better"]["kit_as_launch"] = True

    def body_face(cat):
        cat["honest_better"]["face_as_launch"] = True

    def body_type(cat):
        cat["honest_better"]["type_as_launch"] = True

    def site_face(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A 10/10 face is not production.",
            "A face is recorded.",
        )

    def site_type(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "Readable type is not launch.",
            "Type is recorded.",
        )

    def principles_face(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("A 10/10 face is not production.", "A face is recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def principles_type(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("Readable type is not launch.", "Type is recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def hosted_face(cat):
        cat["expert_review"]["success"]["honest_better"]["face_as_launch"] = True

    def hosted_type(cat):
        cat["expert_review"]["success"]["honest_better"]["type_as_launch"] = True

    def upgrade_n(cat):
        by_n = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
        by_n[97]["title"] = "Rooms"
        by_n[97]["do"] = "Ship 3.27.0. Not LIVE_PIN_OK."

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        face,
        typography,
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
        body_face,
        body_type,
        site,
        site_face,
        site_type,
        principles_face,
        principles_type,
        hosted,
        hosted_face,
        hosted_type,
    ):
        hole = copy.deepcopy(edge)
        mutator(hole)
        with pytest.raises(IntegrityError):
            catmod._validate_instrument_327(hole, hole["plane_interface"])
    ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
    ciso_hole["ciso"]["does_not"] = [
        item
        for item in ciso_hole["ciso"]["does_not"]
        if item != "Treat a green kit check as launch"
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso_hole)
    for missing in (
        "Treat a 10/10 face as production",
        "Treat readable type as launch",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [
            item for item in ciso_hole["ciso"]["does_not"] if item != missing
        ]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
