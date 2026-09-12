from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_CLOSE_FACT_IDS,
    HONEST_CLOSE_HOP_HREFS,
    HONEST_CLOSE_HOP_IDS,
    HONEST_CLOSE_HREFS,
    HONEST_CLOSE_REFUSE_IDS,
    HONEST_CLOSE_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.honest_close import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_319_honest_close():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.22.0"
    close = cat["honest_close"]
    assert close["kind"] == "ainav.honest.close.v1"
    assert close["honest"] is True
    assert close["considered"] is True
    assert close["recorded"] is True
    assert close["close_as_launch"] is False
    assert close["booking_as_revenue"] is False
    assert close["twin_as_assigned"] is False
    assert close["custom_db_as_sku"] is False
    assert close["list_as_collection"] is False
    assert close["certified"] is False
    assert close["created"] is False
    assert close["signed_l1"] is False
    assert close["named_client"] is False
    assert close["billing_provider"] is False
    assert close["href"] == "#path"
    assert [item["id"] for item in close["hops"]] == list(HONEST_CLOSE_HOP_IDS)
    hop_hrefs = {item["id"]: item["href"] for item in close["hops"]}
    assert hop_hrefs == {key: HONEST_CLOSE_HOP_HREFS[key] for key in HONEST_CLOSE_HOP_IDS}
    assert all(item.get("closed") is not True and item.get("live") is not True for item in close["hops"])
    assert [item["id"] for item in close["facts"]] == list(HONEST_CLOSE_FACT_IDS)
    refuse = [item for item in close["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_CLOSE_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_CLOSE_REFUSE_TEXT[key] for key in HONEST_CLOSE_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_CLOSE_HREFS[key] for key in HONEST_CLOSE_REFUSE_IDS}
    assert "honest close" in close["note"].lower()
    assert "a 10/10 close is not launch" in close["note"].lower()
    assert "a catalog list is not collection" in close["note"].lower()
    assert cat["programs"]["website"]["honest_close"] is True
    assert cat["programs"]["website"]["honest_hold"] is True
    assert cat["programs"]["website"]["honest_close_live"] is False
    assert cat["programs"]["website"]["close_as_launch"] is False
    assert cat["programs"]["website"]["booking_as_revenue"] is False
    assert cat["programs"]["website"]["twin_as_assigned"] is False
    assert cat["programs"]["website"]["custom_db_as_sku"] is False
    assert cat["programs"]["website"]["list_as_collection"] is False
    assert "honest close" in cat["operations"]["note"].lower()
    assert "#path" in cat["operations"]["note"]
    assert any("3.19.0" in item and "honest close" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.18.0" in item and "honest hold" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a 10/10 close as launch" in does_not
    assert "a booking as recognized revenue" in does_not
    assert "the institute twin as the assigned client sandbox" in does_not
    assert "a custom database as a fourth sku" in does_not
    assert "a catalog list as collection" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest close" in principles
    assert "a 10/10 close is not launch" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 92
    assert upgrades[89]["who"] == "tree"
    assert upgrades[89]["done"] is True
    assert upgrades[89]["marks_live_pin"] is False
    blob = f"{upgrades[89]['title']} {upgrades[89]['do']}".lower()
    assert "honest close" in blob
    assert "live_pin_ok" in blob
    ip = cat["ip"]
    assert ip["g12_open"] is True
    assert ip["no_patent_claim_in_this_tree"] is True
    assert ip["insulation"]["patent_claimed"] is False
    assert ip["insulation"]["uncopyable"] is False
    assert any(item.get("id") == "client" for item in ip["insulation"]["layers"])
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.19.0" in html
    assert "3.18.0" in html
    assert "honest close" in html.lower()
    assert "a 10/10 close is not launch" in html.lower()
    assert "a custom database is not a fourth sku" in html.lower()
    assert 'id="close-consider"' in html
    assert html.index('id="path-consider"') < html.index('id="close-consider"')
    assert html.index('id="close-consider"') < html.index('id="close-console"')
    assert 'id="close-zeros"' in html
    assert 'id="close-hops"' in html
    assert 'id="close-facts"' in html
    assert 'data-hop="qualify"' in html
    assert 'data-hop="upsell"' in html
    assert 'data-close-refuse="close_as_launch"' in html
    assert 'data-close-refuse="booking_as_revenue"' in html
    assert 'data-close-refuse="twin_as_assigned"' in html
    assert 'data-close-refuse="custom_db_as_sku"' in html
    assert 'data-close-refuse="list_as_collection"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/close"' not in nav
    assert 'href="#close"' not in nav
    assert 'href="#close-consider"' not in nav
    assert "Honest close" not in nav
    assert "bindCloseRefuses" in js
    assert "refuseClose" in js
    assert "CLOSE_REFUSE" in js
    assert 'getElementById("close-lede")' not in js
    assert "honest close" in twin.lower()
    assert "Digital twin · 3.22.0" in twin
    assert "AINAV.Institute twin · 3.22.0" in twin
    assert "3.16.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    assert "Application kit · 3.22.0" in kit
    assert "Release 3.22.0" in lost
    assert "3.16.0" not in lost
    assert "Ultimate control plane · 3.22.0" in plane
    assert "3.16.0" not in plane
    assert 'href="index.html#close-consider"' in plane
    assert 'href="index.html#close-consider"' in app
    assert 'href="#close-consider">Honest close' in html
    assert "#close-consider {" in css
    assert "#hold-consider {" in css
    assert "#ten-consider {" in css
    assert "#protect-consider {" in css
    assert "#close-zeros" in css
    assert ".close-facts" in css
    assert "A 10/10 close is launch" in identify
    assert "Open close" in identify
    assert 'href="index.html#close-consider">Open close' in identify
    assert "A 10/10 close is launch" in app
    assert "Open hold" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.22.0"
    status = public_status()
    assert status["release"] == "3.22.0"
    assert status["website"]["honest_close"] is True
    assert status["website"]["honest_close_live"] is False
    assert status["website"]["close_as_launch"] is False
    assert status["website"]["booking_as_revenue"] is False
    assert status["website"]["twin_as_assigned"] is False
    assert status["website"]["custom_db_as_sku"] is False
    assert status["website"]["list_as_collection"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.close.v1"
    assert review["close_as_launch"] is False
    assert "Treat a 10/10 close as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    owner_hrefs = [
        item.get("href")
        for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][1]["items"]
    ]
    assert owner_hrefs[:3] == ["#closed", "#missing", "#open"]
    sale_hrefs = [
        item.get("href")
        for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"]
    ]
    assert "#close-consider" in sale_hrefs
    assert sale_hrefs[sale_hrefs.index("#path") + 1] == "#close-consider"
    open_items = " ".join(cat["plane_interface"]["gaps"]["owner_only_open"])
    for stem in ("seat B click", "G12/G13", "billing", "launch"):
        assert stem in open_items
    assert html.count("Owner book") == 1
    assert cat["programs"]["website"]["managed"] is True


def test_instrument_319_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.18.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.19.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_close"] = False

    def live(cat):
        cat["programs"]["website"]["honest_close_live"] = True

    def launch(cat):
        cat["programs"]["website"]["close_as_launch"] = True

    def book(cat):
        cat["programs"]["website"]["booking_as_revenue"] = True

    def twin(cat):
        cat["programs"]["website"]["twin_as_assigned"] = True

    def sku(cat):
        cat["programs"]["website"]["custom_db_as_sku"] = True

    def collect(cat):
        cat["programs"]["website"]["list_as_collection"] = True

    def site(cat):
        cat["honest_close"]["site"] = "Close board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest close" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest hold sits on #missing."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio. "
            "Not connected-as-live. Not a 10/10 launch. Not a shared sandbox. Not a production sim. "
            "Not a remainder close. Not a 10/10 quality launch. Not a patent board. "
            "Not a client assignment. Not a vault live pin. Not a secret catalog."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        book,
        twin,
        sku,
        collect,
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
    hole["honest_close"]["kind"] = "ainav.honest.close.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_319(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_close"]["site"] = site_name["honest_close"]["site"].replace(
        "Honest close",
        "Close board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_319(site_name, site_name["plane_interface"])
    site_close = copy.deepcopy(edge)
    site_close["honest_close"]["site"] = site_close["honest_close"]["site"].replace(
        "A 10/10 close is not launch.",
        "Close is recorded.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_319(site_close, site_close["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_close"]["site"] = site_route["honest_close"]["site"].replace(
        "Not a /close route.",
        "A /close route.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_319(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_close"]["site"] = site_glance["honest_close"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the close board.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_319(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge)
    success["expert_review"]["success"]["honest_close"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success)
    success_missing = copy.deepcopy(edge)
    success_missing["expert_review"]["success"].pop("honest_close")
    with pytest.raises(IntegrityError):
        validate_catalog(success_missing)
    success_kind = copy.deepcopy(edge)
    success_kind["expert_review"]["success"]["honest_close"]["kind"] = "ainav.honest.close.v0"
    with pytest.raises(IntegrityError):
        validate_catalog(success_kind)
    success_href = copy.deepcopy(edge)
    success_href["expert_review"]["success"]["honest_close"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_catalog(success_href)
    success_launch = copy.deepcopy(edge)
    success_launch["expert_review"]["success"]["honest_close"]["close_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_launch)
    live_body = copy.deepcopy(edge)
    live_body["honest_close"]["close_as_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_319(live_body, live_body["plane_interface"])
    leftover_body = copy.deepcopy(edge)
    leftover_body["honest_close"]["signed_l1"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_319(leftover_body, leftover_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_close"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_319(certified, certified["plane_interface"])
    for missing in (
        "Treat a 10/10 close as launch",
        "Treat a booking as recognized revenue",
        "Treat the Institute twin as the assigned client sandbox",
        "Treat a custom database as a fourth SKU",
        "Treat a catalog list as collection",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
