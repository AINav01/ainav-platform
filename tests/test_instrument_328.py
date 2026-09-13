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


def test_release_is_328_honest_certified():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.28.0"
    better = cat["honest_better"]
    assert better["use_as_launch"] is False
    assert better["certified_as_launch"] is False
    assert better["packs_as_sku"] is False
    assert "a 10/10 of operability, interoperability, and usability is not launch" in better["note"].lower()
    assert "a 10/10 of prebuilt certified day-one is not launch" in better["lede"].lower()
    assert "packs, modules, and custom builds are not a fourth sku" in better["site"].lower()
    site = cat["programs"]["website"]
    assert site["honest_certified"] is True
    assert site["honest_face"] is True
    assert site["honest_certified_live"] is False
    assert site["use_as_launch"] is False
    assert site["certified_as_launch"] is False
    assert site["packs_as_sku"] is False
    assert any("3.28.0" in item and "honest certified" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.27.0" in item and "honest face" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a 10/10 of operability, interoperability, and usability as launch" in does_not
    assert "a 10/10 of prebuilt certified day-one as launch" in does_not
    assert "packs as a fourth sku" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "a 10/10 of operability, interoperability, and usability is not launch" in principles
    assert "a 10/10 of prebuilt certified day-one is not launch" in principles
    assert "packs, modules, and custom builds are not a fourth sku" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 98
    assert upgrades[98]["who"] == "tree"
    assert upgrades[98]["done"] is True
    assert upgrades[98]["marks_live_pin"] is False
    blob = f"{upgrades[98]['title']} {upgrades[98]['do']}".lower()
    assert "honest certified" in blob
    assert "packs" in blob or "kit" in blob or "client-planes" in blob
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
    assert "a 10/10 of operability, interoperability, and usability is not launch" in html.lower()
    assert "a 10/10 of prebuilt certified day-one is not launch" in html.lower()
    assert "packs, modules, and custom builds are not a fourth sku" in html.lower()
    assert 'id="ten-certified-proof"' in html
    assert 'id="ten-proof-is-use"' in html
    assert 'id="ten-proof-is-certified"' in html
    assert 'id="ten-proof-is-packs"' in html
    assert 'id="offer-certified-proof"' in html
    assert html.index('id="join-consider"') < html.index('id="firm-console"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert "Honest certified" not in nav
    assert "Honest better" not in nav
    assert "Please make better" not in nav
    assert 'id="twin-certified-hops"' in twin
    assert "Digital twin · 3.28.0" in twin
    assert "A 10/10 of prebuilt certified day-one is not launch" in twin
    assert "Packs are a fourth SKU" in identify
    assert "Prebuilt certified day-one is launch" in identify
    assert 'id="identify-certified-proof"' in identify
    assert 'id="twin-ribbon"' in identify
    assert 'id="app-certified-proof"' in app
    assert "Packs are a fourth SKU" in app
    assert "Application · 3.28.0" in app
    assert "not a /certified" in lost.lower()
    assert "a 10/10 of prebuilt certified day-one is not launch" in lost.lower()
    assert "packs, modules, and custom builds are not a fourth sku" in lost.lower()
    assert "#ten-certified-proof" in css
    routes = [item.get("route") for item in swa["routes"] if isinstance(item, dict)]
    assert "/certified" in routes
    assert "/use" in routes
    assert "/certified" in swa["navigationFallback"]["exclude"]
    assert any(item.get("route") == "/certified" and item.get("statusCode") == 404 for item in swa["routes"])
    assert "Application kit · 3.28.0" in kit
    assert "a 10/10 of prebuilt certified day-one is not launch" in kit.lower()
    assert 'id="kit-certified-proof"' in kit
    assert 'src="site.js?v=3.28.0"' in html
    assert 'src="search.js?v=3.28.0"' in html
    llms = public_llms().lower()
    assert "honest certified" in llms or "prebuilt certified day-one" in llms
    search = public_search()
    sale_rec = next(item for item in search["records"] if item["id"] == "sale")
    brand_rec = next(item for item in search["records"] if item["id"] == "brand")
    ten_rec = next(item for item in search["records"] if item["id"] == "ten")
    better_rec = next(item for item in search["records"] if item["id"] == "better")
    kit_rec = next(item for item in search["records"] if item["id"] == "kit")
    assert "a 10/10 of prebuilt certified day-one is not launch" in sale_rec["text"].lower()
    assert "a 10/10 of prebuilt certified day-one is not launch" in brand_rec["text"].lower()
    assert "a 10/10 of operability, interoperability, and usability is not launch" in ten_rec["text"].lower()
    assert "packs, modules, and custom builds are not a fourth sku" in better_rec["text"].lower()
    assert "a 10/10 of prebuilt certified day-one is not launch" in kit_rec["text"].lower()
    dash = public_dashboard()
    assert dash["release"] == "3.28.0"
    status = public_status()
    assert status["release"] == "3.28.0"
    assert status["website"]["honest_certified"] is True
    assert status["website"]["honest_certified_live"] is False
    assert status["website"]["use_as_launch"] is False
    review = public_review()
    assert review["use_as_launch"] is False
    assert review["certified_as_launch"] is False
    assert review["packs_as_sku"] is False
    cannot = " ".join(review["this_agent_cannot"])
    assert "Treat a 10/10 of operability, interoperability, and usability as launch." in cannot
    assert "Treat a 10/10 of prebuilt certified day-one as launch." in cannot
    assert "Treat packs as a fourth SKU." in cannot
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    managed = cat["expert_review"]["success"]["managed_face"]["managed"].lower()
    assert "not a 10/10-certified launch" in managed
    assert cat["expert_review"]["success"]["honest_better"]["use_as_launch"] is False
    assert cat["expert_review"]["success"]["honest_better"]["certified_as_launch"] is False


def test_instrument_328_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.27.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.28.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_certified"] = False

    def live(cat):
        cat["programs"]["website"]["honest_certified_live"] = True

    def launch(cat):
        cat["programs"]["website"]["use_as_launch"] = True

    def certified(cat):
        cat["programs"]["website"]["certified_as_launch"] = True

    def packs(cat):
        cat["programs"]["website"]["packs_as_sku"] = True

    def body_launch(cat):
        cat["honest_better"]["use_as_launch"] = True

    def site(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A 10/10 of operability, interoperability, and usability is not launch.",
            "Use is recorded.",
        )

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "a 10/10 of operability, interoperability, and usability is not launch" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = cat["operations"]["note"].replace(
            " 3.28.0 honest certified sits on kit, #packs, #client-planes, and #ten-proof. A 10/10 of operability, interoperability, and usability is not launch. A 10/10 of prebuilt certified day-one is not launch. Packs, modules, and custom builds are not a fourth SKU.",
            "",
        )

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            cat["expert_review"]["success"]["managed_face"]["managed"].replace(
                " Not a 10/10-certified launch.",
                "",
            )
        )

    def hosted(cat):
        cat["expert_review"]["success"]["honest_better"]["use_as_launch"] = True

    def body_certified(cat):
        cat["honest_better"]["certified_as_launch"] = True

    def body_packs(cat):
        cat["honest_better"]["packs_as_sku"] = True

    def site_certified(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "A 10/10 of prebuilt certified day-one is not launch.",
            "Certified is recorded.",
        )

    def site_packs(cat):
        cat["honest_better"]["site"] = cat["honest_better"]["site"].replace(
            "Packs, modules, and custom builds are not a fourth SKU.",
            "Packs are recorded.",
        )

    def principles_certified(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("A 10/10 of prebuilt certified day-one is not launch.", "Certified is recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def principles_packs(cat):
        cat["expert_review"]["first_principles"] = [
            item.replace("Packs, modules, and custom builds are not a fourth SKU.", "Packs are recorded.")
            for item in cat["expert_review"]["first_principles"]
        ]

    def hosted_certified(cat):
        cat["expert_review"]["success"]["honest_better"]["certified_as_launch"] = True

    def hosted_packs(cat):
        cat["expert_review"]["success"]["honest_better"]["packs_as_sku"] = True

    def upgrade_n(cat):
        by_n = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
        by_n[98]["title"] = "Rooms"
        by_n[98]["do"] = "Ship 3.28.0. Not LIVE_PIN_OK."

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        certified,
        packs,
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
    hole = copy.deepcopy(edge)
    hole["entity"]["release"] = "3.27.0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_328(hole, hole["plane_interface"])
    for mutator in (
        body_launch,
        body_certified,
        body_packs,
        site,
        site_certified,
        site_packs,
        principles_certified,
        principles_packs,
        hosted,
        hosted_certified,
        hosted_packs,
    ):
        hole = copy.deepcopy(edge)
        mutator(hole)
        with pytest.raises(IntegrityError):
            catmod._validate_instrument_328(hole, hole["plane_interface"])
    ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
    ciso_hole["ciso"]["does_not"] = [
        item
        for item in ciso_hole["ciso"]["does_not"]
        if item != "Treat a 10/10 of operability, interoperability, and usability as launch"
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(ciso_hole)
    for missing in (
        "Treat a 10/10 of prebuilt certified day-one as launch",
        "Treat packs as a fourth SKU",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [
            item for item in ciso_hole["ciso"]["does_not"] if item != missing
        ]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
