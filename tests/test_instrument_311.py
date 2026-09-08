from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_CONNECT_HREFS,
    HONEST_CONNECT_REFUSE_IDS,
    HONEST_CONNECT_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.honest_connect import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_311_honest_connect():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.12.0"
    connect = cat["honest_connect"]
    assert connect["kind"] == "ainav.honest.connect.v1"
    assert connect["honest"] is True
    assert connect["considered"] is True
    assert connect["recorded"] is True
    assert connect["connected_is_live"] is False
    assert connect["licensed_is_wired"] is False
    assert connect["available_is_seat"] is False
    assert connect["graph_read_is_live_pin"] is False
    assert connect["cursor_app_is_seat"] is False
    assert connect["certified"] is False
    assert connect["created"] is False
    assert connect["href"] == "#missing"
    refuse = [item for item in connect["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_CONNECT_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_CONNECT_REFUSE_TEXT[key] for key in HONEST_CONNECT_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_CONNECT_HREFS[key] for key in HONEST_CONNECT_REFUSE_IDS}
    assert "honest connect" in connect["note"].lower()
    assert "connected is not live" in connect["note"].lower()
    assert "licensed is not wired" in connect["note"].lower()
    assert cat["programs"]["website"]["honest_connect"] is True
    assert cat["programs"]["website"]["honest_copilot_studio"] is True
    assert cat["programs"]["website"]["honest_connect_live"] is False
    assert cat["programs"]["website"]["connected_is_live"] is False
    assert cat["programs"]["website"]["licensed_is_wired"] is False
    assert cat["programs"]["website"]["available_is_seat"] is False
    assert cat["programs"]["website"]["graph_read_is_live_pin"] is False
    assert cat["programs"]["website"]["cursor_app_is_seat"] is False
    assert "honest connect" in cat["operations"]["note"].lower()
    assert "#missing" in cat["operations"]["note"]
    assert any("3.11.0" in item and "honest connect" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "connected as live" in does_not
    assert "licensed as wired" in does_not
    assert "available as a seat" in does_not
    assert "graph read as live_pin_ok" in does_not
    assert "cursor app as a seat" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest connect" in principles
    assert "connected is not live" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 82
    assert upgrades[81]["who"] == "tree"
    assert upgrades[81]["done"] is True
    assert upgrades[81]["marks_live_pin"] is False
    blob = f"{upgrades[81]['title']} {upgrades[81]['do']}".lower()
    assert "honest connect" in blob
    assert "live_pin_ok" in blob
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.12.0" in html
    assert "honest connect" in html.lower()
    assert "connected is not live" in html.lower()
    assert "licensed is not wired" in html.lower()
    assert 'id="connect-consider"' in html
    assert 'id="connect-zeros"' in html
    assert 'id="connect-facts"' in html
    assert 'data-connect-refuse="connected_as_live"' in html
    assert 'data-connect-refuse="licensed_as_wired"' in html
    assert 'data-connect-refuse="available_as_seat"' in html
    assert 'data-connect-refuse="graph_read_as_live_pin"' in html
    assert 'data-connect-refuse="cursor_app_as_seat"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/connect"' not in nav
    assert 'href="#connect"' not in nav
    assert 'href="#connect-consider"' not in nav
    assert "Honest connect" not in nav
    assert "bindConnectRefuses" in js
    assert "refuseConnect" in js
    assert "connect-lede" not in js
    assert "operate-lede" not in js
    assert "studio-lede" not in js
    assert "pages-lede" not in js
    assert "whole-lede" not in js
    assert "industry-cert-lede" not in js
    assert "ready-lede" not in js
    assert "build-lede" not in js
    assert "operator-lede" not in js
    assert "access-lede" not in js
    assert "honest connect" in twin.lower()
    assert "connected is not live" in twin.lower()
    assert "Digital twin · 3.12.0" in twin
    assert "AINAV.Institute twin · 3.12.0" in twin
    assert "3.08.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    assert "Application kit · 3.12.0" in kit
    assert "Connected is live" in identify
    assert "Open connect" in identify
    assert "Connected is live" in app
    dash = public_dashboard()
    assert dash["release"] == "3.12.0"
    status = public_status()
    assert status["release"] == "3.12.0"
    assert status["website"]["honest_connect"] is True
    assert status["website"]["honest_connect_live"] is False
    assert status["website"]["connected_is_live"] is False
    assert status["website"]["licensed_is_wired"] is False
    assert status["website"]["available_is_seat"] is False
    assert status["website"]["graph_read_is_live_pin"] is False
    assert status["website"]["cursor_app_is_seat"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.connect.v1"
    assert review["connected_is_live"] is False
    assert "Treat connected as live." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"


def test_instrument_311_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.10.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.11.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_connect"] = False

    def live(cat):
        cat["programs"]["website"]["honest_connect_live"] = True

    def connected_live(cat):
        cat["programs"]["website"]["connected_is_live"] = True

    def wired(cat):
        cat["programs"]["website"]["licensed_is_wired"] = True

    def seat(cat):
        cat["programs"]["website"]["available_is_seat"] = True

    def pin(cat):
        cat["programs"]["website"]["graph_read_is_live_pin"] = True

    def app(cat):
        cat["programs"]["website"]["cursor_app_is_seat"] = True

    def site(cat):
        cat["honest_connect"]["site"] = "Connect board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest connect" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest Copilot Studio sits on #success."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        connected_live,
        wired,
        seat,
        pin,
        app,
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
    hole["honest_connect"]["kind"] = "ainav.honest.connect.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_connect"]["site"] = site_name["honest_connect"]["site"].replace(
        "Honest connect",
        "Connect board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(site_name, site_name["plane_interface"])
    site_live = copy.deepcopy(edge)
    site_live["honest_connect"]["site"] = site_live["honest_connect"]["site"].replace(
        "Connected is not live. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(site_live, site_live["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_connect"]["site"] = site_route["honest_connect"]["site"].replace(
        "Not a /connect route. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_connect"]["site"] = site_glance["honest_connect"]["site"].replace(
        "First glance stays the write rail. ",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge["expert_review"]["success"])
    success["honest_connect"]["live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success)
    success_missing = copy.deepcopy(edge["expert_review"]["success"])
    success_missing.pop("honest_connect")
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_missing)
    success_kind = copy.deepcopy(edge["expert_review"]["success"])
    success_kind["honest_connect"]["kind"] = "ainav.honest.connect.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_kind)
    success_href = copy.deepcopy(edge["expert_review"]["success"])
    success_href["honest_connect"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_href)
    success_live = copy.deepcopy(edge["expert_review"]["success"])
    success_live["honest_connect"]["connected_is_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_live)
    success_wired = copy.deepcopy(edge["expert_review"]["success"])
    success_wired["honest_connect"]["licensed_is_wired"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_wired)
    success_seat = copy.deepcopy(edge["expert_review"]["success"])
    success_seat["honest_connect"]["available_is_seat"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_seat)
    success_pin = copy.deepcopy(edge["expert_review"]["success"])
    success_pin["honest_connect"]["graph_read_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_pin)
    success_app = copy.deepcopy(edge["expert_review"]["success"])
    success_app["honest_connect"]["cursor_app_is_seat"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_success_program(success_app)
    live_body = copy.deepcopy(edge)
    live_body["honest_connect"]["connected_is_live"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(live_body, live_body["plane_interface"])
    wired_body = copy.deepcopy(edge)
    wired_body["honest_connect"]["licensed_is_wired"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(wired_body, wired_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_connect"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(certified, certified["plane_interface"])
    principles_direct = copy.deepcopy(edge)
    principles_direct["expert_review"]["first_principles"] = [
        item
        for item in principles_direct["expert_review"]["first_principles"]
        if "honest connect" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(principles_direct, principles_direct["plane_interface"])
    principles_live = copy.deepcopy(edge)
    principles_live["expert_review"]["first_principles"] = [
        item.replace("Connected is not live.", "Connected is recorded live.")
        for item in principles_live["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(principles_live, principles_live["plane_interface"])
    principles_first = copy.deepcopy(edge)
    principles_first["expert_review"]["first_principles"] = [
        item.replace("Honest connect sits on #missing.", "Connect sits on #missing.")
        for item in principles_first["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_first_principles(principles_first["expert_review"]["first_principles"])
    ops_attach = copy.deepcopy(edge)
    ops_attach["operations"]["note"] = "Honest connect sits on #missing."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(ops_attach, ops_attach["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest connect is recorded."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(ops_href, ops_href["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. Connect sits on #missing."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(ops_name, ops_name["plane_interface"])
    managed_direct = copy.deepcopy(edge)
    managed_direct["expert_review"]["success"]["managed_face"]["managed"] = managed_direct["expert_review"]["success"]["managed_face"]["managed"].replace(
        " Not connected-as-live.",
        "",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_311(managed_direct, managed_direct["plane_interface"])
    for missing in (
        "Treat connected as live",
        "Treat licensed as wired",
        "Treat available as a seat",
        "Treat a Graph read as LIVE_PIN_OK",
        "Treat a Cursor app as a seat",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
