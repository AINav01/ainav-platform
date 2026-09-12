from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_REMAINDER_HREFS,
    HONEST_REMAINDER_REFUSE_IDS,
    HONEST_REMAINDER_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.honest_remainder import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_315_honest_remainder():
    cat = load_catalog()
    remainder = cat["honest_remainder"]
    assert remainder["kind"] == "ainav.honest.remainder.v1"
    assert remainder["honest"] is True
    assert remainder["considered"] is True
    assert remainder["recorded"] is True
    assert remainder["remainder_is_launch"] is False
    assert remainder["leftover_copy_is_live_pin"] is False
    assert remainder["owner_hrefs_are_clicks"] is False
    assert remainder["gold_995_is_production"] is False
    assert remainder["deep_remainder_is_seated"] is False
    assert remainder["certified"] is False
    assert remainder["created"] is False
    assert remainder["href"] == "#missing"
    refuse = [item for item in remainder["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_REMAINDER_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_REMAINDER_REFUSE_TEXT[key] for key in HONEST_REMAINDER_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_REMAINDER_HREFS[key] for key in HONEST_REMAINDER_REFUSE_IDS}
    assert "honest remainder" in remainder["note"].lower()
    assert "a remainder close is not launch" in remainder["note"].lower()
    assert "leftover copy is not live_pin_ok" in remainder["note"].lower()
    assert cat["programs"]["website"]["honest_remainder"] is True
    assert cat["programs"]["website"]["honest_production"] is True
    assert cat["programs"]["website"]["honest_remainder_live"] is False
    assert cat["programs"]["website"]["remainder_is_launch"] is False
    assert cat["programs"]["website"]["leftover_copy_is_live_pin"] is False
    assert cat["programs"]["website"]["owner_hrefs_are_clicks"] is False
    assert cat["programs"]["website"]["gold_995_is_production"] is False
    assert cat["programs"]["website"]["deep_remainder_is_seated"] is False
    assert "honest remainder" in cat["operations"]["note"].lower()
    assert "#missing" in cat["operations"]["note"]
    assert any("3.15.0" in item and "honest remainder" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    gaps = cat["plane_interface"]["gaps"]
    for item in gaps["owner_only_open"]:
        assert item in gaps["owner_only_hrefs"]
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a remainder close as launch" in does_not
    assert "leftover copy as live_pin_ok" in does_not
    assert "owner hrefs as owner clicks" in does_not
    assert "gold 99.5 as production" in does_not
    assert "a deep remainder as seated" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest remainder" in principles
    assert "a remainder close is not launch" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 90
    assert upgrades[85]["who"] == "tree"
    assert upgrades[85]["done"] is True
    assert upgrades[85]["marks_live_pin"] is False
    blob = f"{upgrades[85]['title']} {upgrades[85]['do']}".lower()
    assert "honest remainder" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.15.0" in html
    assert "honest remainder" in html.lower()
    assert "a remainder close is not launch" in html.lower()
    assert "leftover copy is not live_pin_ok" in html.lower()
    assert 'id="remain-consider"' in html
    assert 'id="remain-zeros"' in html
    assert 'id="remain-facts"' in html
    assert 'data-remain-refuse="remainder_as_launch"' in html
    assert 'data-remain-refuse="leftover_copy_as_live_pin"' in html
    assert 'data-remain-refuse="owner_hrefs_as_owner_clicks"' in html
    assert 'data-remain-refuse="gold_995_as_production"' in html
    assert 'data-remain-refuse="deep_remainder_as_seated"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/remainder"' not in nav
    assert 'href="#remain"' not in nav
    assert 'href="#remain-consider"' not in nav
    assert "Honest remainder" not in nav
    assert "bindRemainRefuses" in js
    assert "refuseRemain" in js
    assert "remain-lede" not in js
    assert "cycle-lede" not in js
    assert "operate-lede" not in js
    assert "connect-lede" not in js
    assert "studio-lede" not in js
    assert "pages-lede" not in js
    assert "honest remainder" in twin.lower()
    assert "a remainder close is not launch" in twin.lower()
    assert "Digital twin · 3.20.0" in twin
    assert "AINAV.Institute twin · 3.20.0" in twin
    assert "3.14.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    assert "Application kit · 3.20.0" in kit
    assert "Release 3.20.0" in lost
    assert "3.14.0" not in lost
    assert "Ultimate control plane · 3.20.0" in plane
    assert "3.14.0" not in plane
    assert 'href="index.html#remain-consider"' in plane
    assert 'href="index.html#remain-consider"' in app
    assert 'href="#remain-consider">Honest remainder' in html
    assert "#remain-consider {" in css
    assert "#remain-zeros" in css
    assert ".remain-facts" in css
    assert "A remainder close is launch" in identify
    assert "Open remainder" in identify
    assert "A remainder close is launch" in app
    dash = public_dashboard()
    assert dash["release"] == "3.20.0"
    status = public_status()
    assert status["release"] == "3.20.0"
    assert status["website"]["honest_remainder"] is True
    assert status["website"]["honest_remainder_live"] is False
    assert status["website"]["remainder_is_launch"] is False
    assert status["website"]["leftover_copy_is_live_pin"] is False
    assert status["website"]["owner_hrefs_are_clicks"] is False
    assert status["website"]["gold_995_is_production"] is False
    assert status["website"]["deep_remainder_is_seated"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.remainder.v1"
    assert review["remainder_is_launch"] is False
    assert "Treat a remainder close as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    quality = next(
        item
        for item in cat["microsoft_stack"]["readiness"]["lanes"]
        if item.get("id") == "quality"
    )
    assert quality["note"].startswith("Gold 99.5.")
    managed = next(
        item for item in cat["expert_review"]["success"]["objections"] if item.get("id") == "managed"
    )
    assert "Gold 99.5." in managed["answer"]
    assert "Gold 99." not in managed["answer"].replace("Gold 99.5.", "")
    now = next(
        item
        for lane in cat["expert_review"]["success"]["industry_drawer"]["control"]["lanes"]
        for item in lane.get("items") or []
        if item.get("id") == "now"
    )
    assert "Gold 99.5." in now["note"]
    assert "Gold 99." not in now["note"].replace("Gold 99.5.", "")
    owner_hrefs = [
        item.get("href")
        for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][1]["items"]
    ]
    assert owner_hrefs[:3] == ["#closed", "#missing", "#open"]
    assert "#remain-consider" in owner_hrefs


def test_instrument_315_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.14.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.15.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_remainder"] = False

    def live(cat):
        cat["programs"]["website"]["honest_remainder_live"] = True

    def launch(cat):
        cat["programs"]["website"]["remainder_is_launch"] = True

    def leftover(cat):
        cat["programs"]["website"]["leftover_copy_is_live_pin"] = True

    def hrefs(cat):
        cat["programs"]["website"]["owner_hrefs_are_clicks"] = True

    def gold(cat):
        cat["programs"]["website"]["gold_995_is_production"] = True

    def seated(cat):
        cat["programs"]["website"]["deep_remainder_is_seated"] = True

    def site(cat):
        cat["honest_remainder"]["site"] = "Remainder board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest remainder" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest production sits on #firm."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio. "
            "Not connected-as-live. Not a 10/10 launch. Not a shared sandbox. Not a production sim."
        )

    def missing_href(cat):
        cat["plane_interface"]["gaps"]["owner_only_hrefs"].pop("Teams team and channel ids", None)

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        leftover,
        hrefs,
        gold,
        seated,
        site,
        principles,
        ops,
        managed,
        missing_href,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["honest_remainder"]["kind"] = "ainav.honest.remainder.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_remainder"]["site"] = site_name["honest_remainder"]["site"].replace(
        "Honest remainder",
        "Remainder board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(site_name, site_name["plane_interface"])
    site_close = copy.deepcopy(edge)
    site_close["honest_remainder"]["site"] = site_close["honest_remainder"]["site"].replace(
        "A remainder close is not launch.",
        "Remainder is recorded.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(site_close, site_close["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_remainder"]["site"] = site_route["honest_remainder"]["site"].replace(
        "Not a /remainder route.",
        "A /remainder route.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_remainder"]["site"] = site_glance["honest_remainder"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the remainder board.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge)
    success["expert_review"]["success"]["honest_remainder"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success)
    success_missing = copy.deepcopy(edge)
    success_missing["expert_review"]["success"].pop("honest_remainder")
    with pytest.raises(IntegrityError):
        validate_catalog(success_missing)
    success_kind = copy.deepcopy(edge)
    success_kind["expert_review"]["success"]["honest_remainder"]["kind"] = "ainav.honest.remainder.v0"
    with pytest.raises(IntegrityError):
        validate_catalog(success_kind)
    success_href = copy.deepcopy(edge)
    success_href["expert_review"]["success"]["honest_remainder"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_catalog(success_href)
    success_launch = copy.deepcopy(edge)
    success_launch["expert_review"]["success"]["honest_remainder"]["remainder_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_launch)
    success_leftover = copy.deepcopy(edge)
    success_leftover["expert_review"]["success"]["honest_remainder"]["leftover_copy_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_leftover)
    success_clicks = copy.deepcopy(edge)
    success_clicks["expert_review"]["success"]["honest_remainder"]["owner_hrefs_are_clicks"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_clicks)
    success_gold = copy.deepcopy(edge)
    success_gold["expert_review"]["success"]["honest_remainder"]["gold_995_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_gold)
    success_seated = copy.deepcopy(edge)
    success_seated["expert_review"]["success"]["honest_remainder"]["deep_remainder_is_seated"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_seated)
    live_body = copy.deepcopy(edge)
    live_body["honest_remainder"]["remainder_is_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(live_body, live_body["plane_interface"])
    leftover_body = copy.deepcopy(edge)
    leftover_body["honest_remainder"]["leftover_copy_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(leftover_body, leftover_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_remainder"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(certified, certified["plane_interface"])
    principles_name = copy.deepcopy(edge)
    principles_name["expert_review"]["first_principles"] = [
        item.replace("Honest remainder sits on #missing.", "Remainder sits on #missing.")
        for item in principles_name["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(principles_name, principles_name["plane_interface"])
    principles_close = copy.deepcopy(edge)
    principles_close["expert_review"]["first_principles"] = [
        item.replace("A remainder close is not launch.", "Remainder is recorded done.")
        for item in principles_close["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(principles_close, principles_close["plane_interface"])
    principles_first = copy.deepcopy(edge)
    principles_first["expert_review"]["first_principles"] = [
        item.replace("Honest remainder sits on #missing.", "Remainder sits on #missing.")
        for item in principles_first["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_first["expert_review"]["first_principles"])
    ops_attach = copy.deepcopy(edge)
    ops_attach["operations"]["note"] = "Honest remainder sits on #missing."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(ops_attach, ops_attach["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest remainder is recorded."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(ops_href, ops_href["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. Remainder sits on #missing."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(ops_name, ops_name["plane_interface"])
    managed_direct = copy.deepcopy(edge)
    managed_direct["expert_review"]["success"]["managed_face"]["managed"] = managed_direct["expert_review"]["success"]["managed_face"]["managed"].replace(
        " Not a remainder close.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_315(managed_direct, managed_direct["plane_interface"])
    for missing in (
        "Treat a remainder close as launch",
        "Treat leftover copy as LIVE_PIN_OK",
        "Treat owner hrefs as owner clicks",
        "Treat gold 99.5 as production",
        "Treat a deep remainder as seated",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
