from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_JOIN_FACT_IDS,
    HONEST_JOIN_HOP_HREFS,
    HONEST_JOIN_HOP_IDS,
    HONEST_JOIN_HREFS,
    HONEST_JOIN_REFUSE_IDS,
    HONEST_JOIN_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.face_kit import public_llms, public_search
from ainav.honest_join import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_320_honest_join():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.20.0"
    join = cat["honest_join"]
    assert join["kind"] == "ainav.honest.join.v1"
    assert join["honest"] is True
    assert join["considered"] is True
    assert join["recorded"] is True
    assert join["join_as_launch"] is False
    assert join["stitch_as_live_pin"] is False
    assert join["licensed_as_wired_firm"] is False
    assert join["manage_ops_as_closed"] is False
    assert join["certify_as_running"] is False
    assert join["certified"] is False
    assert join["created"] is False
    assert join["signed_l1"] is False
    assert join["named_client"] is False
    assert join["billing_provider"] is False
    assert join["href"] == "#firm"
    assert [item["id"] for item in join["hops"]] == list(HONEST_JOIN_HOP_IDS)
    hop_hrefs = {item["id"]: item["href"] for item in join["hops"]}
    assert hop_hrefs == {key: HONEST_JOIN_HOP_HREFS[key] for key in HONEST_JOIN_HOP_IDS}
    assert all(item.get("closed") is not True and item.get("live") is not True for item in join["hops"])
    assert [item["id"] for item in join["facts"]] == list(HONEST_JOIN_FACT_IDS)
    refuse = [item for item in join["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_JOIN_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_JOIN_REFUSE_TEXT[key] for key in HONEST_JOIN_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_JOIN_HREFS[key] for key in HONEST_JOIN_REFUSE_IDS}
    assert "honest join" in join["note"].lower()
    assert "the join is not launch" in join["note"].lower()
    assert "a certified simulation is not a running firm" in join["note"].lower()
    assert cat["programs"]["website"]["honest_join"] is True
    assert cat["programs"]["website"]["honest_close"] is True
    assert cat["programs"]["website"]["honest_join_live"] is False
    assert cat["programs"]["website"]["join_as_launch"] is False
    assert cat["programs"]["website"]["stitch_as_live_pin"] is False
    assert cat["programs"]["website"]["licensed_as_wired_firm"] is False
    assert cat["programs"]["website"]["manage_ops_as_closed"] is False
    assert cat["programs"]["website"]["certify_as_running"] is False
    assert "honest join" in cat["operations"]["note"].lower()
    assert "#firm" in cat["operations"]["note"]
    assert any("3.20.0" in item and "honest join" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.19.0" in item and "honest close" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "the join as launch" in does_not
    assert "the stitched firm as live_pin_ok" in does_not
    assert "licensed-not-wired as a wired firm" in does_not
    assert "management and operations as closed from this plane" in does_not
    assert "a certified simulation as a running firm" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest join" in principles
    assert "the join is not launch" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 90
    assert upgrades[90]["who"] == "tree"
    assert upgrades[90]["done"] is True
    assert upgrades[90]["marks_live_pin"] is False
    blob = f"{upgrades[90]['title']} {upgrades[90]['do']}".lower()
    assert "honest join" in blob
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
    assert "3.20.0" in html
    assert "3.19.0" in html
    assert "honest join" in html.lower()
    assert "the join is not launch" in html.lower()
    assert "a certified simulation is not a running firm" in html.lower()
    assert 'id="join-consider"' in html
    assert html.index('id="prod-consider"') < html.index('id="join-consider"')
    assert html.index('id="join-consider"') < html.index('id="firm-console"')
    assert 'id="join-zeros"' in html
    assert 'id="join-hops"' in html
    assert 'id="join-facts"' in html
    assert 'id="join-hops-kicker"' in html
    assert 'id="join-facts-kicker"' in html
    assert "Five facts" in html
    assert 'data-hop="write"' in html
    assert 'data-hop="certify"' in html
    join_board = html.split('id="join-consider"', 1)[1].split('id="firm-console"', 1)[0]
    assert 'data-hop="write"><a href="#buyer"' in join_board
    assert 'data-hop="plan"><a href="#business"' in join_board
    assert 'data-hop="close"><a href="#close-consider"' in join_board
    assert 'data-hop="fulfill"><a href="#path"' in join_board
    assert 'data-hop="produce"><a href="#firm"' in join_board
    assert 'data-hop="microsoft"><a href="#firm-ms"' in join_board
    assert 'data-hop="fabric"><a href="#fabric"' in join_board
    assert 'data-hop="website"><a href="#whole"' in join_board
    assert 'data-hop="operate"><a href="#agent-tools"' in join_board
    assert 'data-hop="keep"><a href="#ops"' in join_board
    assert 'data-hop="certify"><a href="#success"' in join_board
    assert 'href="/join"' not in join_board
    for hop in join["hops"]:
        assert hop["note"] in join_board
    assert "a 10/10 quality check is not launch" in join_board.lower()
    assert "a 10/10+ quality check is not launch" in join_board.lower()
    assert 'id="join-is-plus"' in join_board
    assert html.count("Walk the join") >= 8
    close_board = html.split('id="close-consider"', 1)[1].split('id="join-consider"', 1)[0]
    assert 'data-hop="qualify"><a href="#success"' in close_board
    assert 'data-hop="upsell"><a href="#commercial"' in close_board
    assert 'id="close-hops-kicker"' in close_board
    assert 'id="close-facts-kicker"' in close_board
    for hop in cat["honest_close"]["hops"]:
        assert hop["note"] in close_board
    assert 'data-join-refuse="join_as_launch"' in html
    assert 'data-join-refuse="stitch_as_live_pin"' in html
    assert 'data-join-refuse="licensed_as_wired_firm"' in html
    assert 'data-join-refuse="manage_ops_as_closed"' in html
    assert 'data-join-refuse="certify_as_running"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/join"' not in nav
    assert 'href="#join"' not in nav
    assert 'href="#join-consider"' not in nav
    assert "Honest join" not in nav
    assert "bindJoinRefuses" in js
    assert "refuseJoin" in js
    assert "JOIN_REFUSE" in js
    assert 'getElementById("join-lede")' not in js
    assert "honest join" in twin.lower()
    assert "Digital twin · 3.20.0" in twin
    assert "AINAV.Institute twin · 3.20.0" in twin
    assert "3.16.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    assert "Application kit · 3.20.0" in kit
    assert "Release 3.20.0" in lost
    assert "3.16.0" not in lost
    assert "Ultimate control plane · 3.20.0" in plane
    assert "3.16.0" not in plane
    assert 'href="index.html#join-consider"' in plane
    assert 'href="index.html#join-consider"' in app
    assert 'href="#join-consider">Honest join' in html
    assert "#join-consider {" in css
    assert "#close-consider {" in css
    assert "#hold-consider {" in css
    assert "#ten-consider {" in css
    assert "#protect-consider {" in css
    assert "#join-zeros" in css
    assert ".join-facts" in css
    assert "#join-hops a" in css
    assert "#close-hops a" in css
    assert ".pages-facts.join-facts" in css
    assert "[popover].owner-book a { white-space: nowrap; }" in css
    assert "data.manage_ops_as_closed || data.certify_as_running" in js
    llms = public_llms().lower()
    assert "honest join sits on #firm" in llms
    assert "the join is not launch" in llms
    assert "a certified simulation is not a running firm" in llms
    search = public_search()
    join_rec = next(item for item in search["records"] if item["id"] == "join")
    assert join_rec["href"] == "index.html#join-consider"
    assert "the join is not launch" in join_rec["text"].lower()
    assert "a 10/10+ quality check is not launch" in join_rec["text"].lower()
    assert "not a /join route" in join_rec["text"].lower()
    assert "a 10/10+ quality check is not launch" in llms
    assert "about ainav sits on #about" in llms
    about_rec = next(item for item in search["records"] if item["id"] == "about")
    assert about_rec["href"] == "index.html#about"
    assert "not a running firm" in about_rec["text"].lower()
    assert "The join is launch" in identify
    assert "10/10+ is launch" in identify
    assert "10/10+ is launch" in app
    assert "Open join" in identify
    assert 'href="index.html#join-consider">Open join' in identify
    assert "The join is launch" in app
    assert "Open close" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.20.0"
    status = public_status()
    assert status["release"] == "3.20.0"
    assert status["website"]["honest_join"] is True
    assert status["website"]["honest_join_live"] is False
    assert status["website"]["join_as_launch"] is False
    assert status["website"]["stitch_as_live_pin"] is False
    assert status["website"]["licensed_as_wired_firm"] is False
    assert status["website"]["manage_ops_as_closed"] is False
    assert status["website"]["certify_as_running"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.join.v1"
    assert review["join_as_launch"] is False
    assert "Treat the join as launch." in " ".join(review["this_agent_cannot"])
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
    assert "#join-consider" in sale_hrefs
    assert sale_hrefs[sale_hrefs.index("#firm") + 1] == "#join-consider"
    open_items = " ".join(cat["plane_interface"]["gaps"]["owner_only_open"])
    for stem in ("seat B click", "G12/G13", "billing", "launch"):
        assert stem in open_items
    assert html.count("Owner book") == 1
    assert cat["programs"]["website"]["managed"] is True


def test_instrument_320_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.19.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.20.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_join"] = False

    def live(cat):
        cat["programs"]["website"]["honest_join_live"] = True

    def launch(cat):
        cat["programs"]["website"]["join_as_launch"] = True

    def stitch(cat):
        cat["programs"]["website"]["stitch_as_live_pin"] = True

    def wired(cat):
        cat["programs"]["website"]["licensed_as_wired_firm"] = True

    def closed_ops(cat):
        cat["programs"]["website"]["manage_ops_as_closed"] = True

    def running(cat):
        cat["programs"]["website"]["certify_as_running"] = True

    def site(cat):
        cat["honest_join"]["site"] = "Join board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest join" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest close sits on #path."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio. "
            "Not connected-as-live. Not a 10/10 launch. Not a shared sandbox. Not a production sim. "
            "Not a remainder close. Not a 10/10 quality launch. Not a patent board. "
            "Not a client assignment. Not a vault live pin. Not a secret catalog. "
            "Not a booked close. Not a catalog collection."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        stitch,
        wired,
        closed_ops,
        running,
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
    hole["honest_join"]["kind"] = "ainav.honest.join.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_join"]["site"] = site_name["honest_join"]["site"].replace(
        "Honest join",
        "Join board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(site_name, site_name["plane_interface"])
    site_join = copy.deepcopy(edge)
    site_join["honest_join"]["site"] = site_join["honest_join"]["site"].replace(
        "The join is not launch.",
        "Join is recorded.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(site_join, site_join["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_join"]["site"] = site_route["honest_join"]["site"].replace(
        "Not a /join route.",
        "A /join route.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_join"]["site"] = site_glance["honest_join"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the join board.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge)
    success["expert_review"]["success"]["honest_join"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success)
    success_missing = copy.deepcopy(edge)
    success_missing["expert_review"]["success"].pop("honest_join")
    with pytest.raises(IntegrityError):
        validate_catalog(success_missing)
    success_kind = copy.deepcopy(edge)
    success_kind["expert_review"]["success"]["honest_join"]["kind"] = "ainav.honest.join.v0"
    with pytest.raises(IntegrityError):
        validate_catalog(success_kind)
    success_href = copy.deepcopy(edge)
    success_href["expert_review"]["success"]["honest_join"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_catalog(success_href)
    success_launch = copy.deepcopy(edge)
    success_launch["expert_review"]["success"]["honest_join"]["join_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_launch)
    live_body = copy.deepcopy(edge)
    live_body["honest_join"]["join_as_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(live_body, live_body["plane_interface"])
    leftover_body = copy.deepcopy(edge)
    leftover_body["honest_join"]["signed_l1"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(leftover_body, leftover_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_join"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(certified, certified["plane_interface"])
    for missing in (
        "Treat the join as launch",
        "Treat the stitched firm as LIVE_PIN_OK",
        "Treat licensed-not-wired as a wired firm",
        "Treat management and operations as closed from this plane",
        "Treat a certified simulation as a running firm",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
    hosted_booking = copy.deepcopy(edge)
    hosted_booking["expert_review"]["success"]["honest_close"]["booking_as_revenue"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(hosted_booking)
    hosted_list = copy.deepcopy(edge)
    hosted_list["expert_review"]["success"]["honest_close"]["custom_db_as_sku"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(hosted_list)
    hosted_stitch = copy.deepcopy(edge)
    hosted_stitch["expert_review"]["success"]["honest_join"]["stitch_as_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(hosted_stitch)
    hosted_ops = copy.deepcopy(edge)
    hosted_ops["expert_review"]["success"]["honest_join"]["manage_ops_as_closed"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(hosted_ops)
    principles_join = copy.deepcopy(edge)
    principles_join["expert_review"]["first_principles"] = [
        item
        for item in principles_join["expert_review"]["first_principles"]
        if "honest join" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(principles_join, principles_join["plane_interface"])
    principles_launch = copy.deepcopy(edge)
    principles_launch["expert_review"]["first_principles"] = [
        item.replace("The join is not launch.", "Join is recorded.")
        for item in principles_launch["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(principles_launch, principles_launch["plane_interface"])
    ops_sku = copy.deepcopy(edge)
    ops_sku["operations"]["note"] = "Honest join sits on #firm."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(ops_sku, ops_sku["plane_interface"])
    ops_firm = copy.deepcopy(edge)
    ops_firm["operations"]["note"] = "SKU attach chain. Honest join sits on #path."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(ops_firm, ops_firm["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. The operating day is #firm."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(ops_name, ops_name["plane_interface"])
    managed_run = copy.deepcopy(edge)
    managed_run["expert_review"]["success"]["managed_face"]["managed"] = (
        edge["expert_review"]["success"]["managed_face"]["managed"].replace(
            "Not a certified running firm.",
            "Certified running firm.",
        )
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_320(managed_run, managed_run["plane_interface"])
    wired_fp = copy.deepcopy(edge)
    wired_fp["expert_review"]["first_principles"] = [
        item.replace("Licensed-not-wired is not a wired firm.", "Licensed is visible.")
        .replace("A certified simulation is not a running firm.", "Simulation is recorded.")
        for item in wired_fp["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(wired_fp)
