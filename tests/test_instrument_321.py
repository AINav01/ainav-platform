from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_BETTER_FACT_IDS,
    HONEST_BETTER_HOP_HREFS,
    HONEST_BETTER_HOP_IDS,
    HONEST_BETTER_HREFS,
    HONEST_BETTER_REFUSE_IDS,
    HONEST_BETTER_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.face_kit import public_llms, public_search
from ainav.honest_better import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_321_honest_better():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.23.0"
    better = cat["honest_better"]
    assert better["kind"] == "ainav.honest.better.v1"
    assert better["honest"] is True
    assert better["considered"] is True
    assert better["recorded"] is True
    assert better["better_as_launch"] is False
    assert better["ten_as_seated"] is False
    assert better["systems_as_wired"] is False
    assert better["polish_as_production"] is False
    assert better["interpret_as_live_pin"] is False
    assert better["make_as_launch"] is False
    assert better["certified"] is False
    assert better["created"] is False
    assert better["signed_l1"] is False
    assert better["named_client"] is False
    assert better["billing_provider"] is False
    assert better["href"] == "#success"
    assert [item["id"] for item in better["hops"]] == list(HONEST_BETTER_HOP_IDS)
    hop_hrefs = {item["id"]: item["href"] for item in better["hops"]}
    assert hop_hrefs == {key: HONEST_BETTER_HOP_HREFS[key] for key in HONEST_BETTER_HOP_IDS}
    assert all(item.get("closed") is not True and item.get("live") is not True for item in better["hops"])
    assert [item["id"] for item in better["facts"]] == list(HONEST_BETTER_FACT_IDS)
    refuse = [item for item in better["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_BETTER_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_BETTER_REFUSE_TEXT[key] for key in HONEST_BETTER_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_BETTER_HREFS[key] for key in HONEST_BETTER_REFUSE_IDS}
    assert "honest better" in better["note"].lower()
    assert "a much better build and business is not launch" in better["note"].lower()
    assert "interpretability is not live_pin_ok" in better["note"].lower()
    assert "making better is not launch" in better["note"].lower()
    assert cat["programs"]["website"]["honest_better"] is True
    assert cat["programs"]["website"]["honest_join"] is True
    assert cat["programs"]["website"]["honest_better_live"] is False
    assert cat["programs"]["website"]["better_as_launch"] is False
    assert cat["programs"]["website"]["ten_as_seated"] is False
    assert cat["programs"]["website"]["systems_as_wired"] is False
    assert cat["programs"]["website"]["polish_as_production"] is False
    assert cat["programs"]["website"]["interpret_as_live_pin"] is False
    assert cat["programs"]["website"]["honest_make"] is True
    assert cat["programs"]["website"]["honest_make_live"] is False
    assert cat["programs"]["website"]["make_as_launch"] is False
    assert "honest better" in cat["operations"]["note"].lower()
    assert "#success" in cat["operations"]["note"]
    assert any("3.21.0" in item and "honest better" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.20.0" in item and "honest join" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a much better build and business as launch" in does_not
    assert "a 10/10 as a seated second human" in does_not
    assert "a systems review as a wired firm" in does_not
    assert "a polish pass as production" in does_not
    assert "interpretability as live_pin_ok" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest better" in principles
    assert "a much better build and business is not launch" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 93
    assert upgrades[91]["who"] == "tree"
    assert upgrades[91]["done"] is True
    assert upgrades[91]["marks_live_pin"] is False
    blob = f"{upgrades[91]['title']} {upgrades[91]['do']}".lower()
    assert "honest better" in blob
    assert "live_pin_ok" in blob
    ip = cat["ip"]
    assert ip["g12_open"] is True
    assert ip["no_patent_claim_in_this_tree"] is True
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.21.0" in html
    assert "3.22.0" in html
    assert "making better is not launch" in html.lower()
    assert "3.20.0" in html
    assert "honest better" in html.lower()
    assert "a much better build and business is not launch" in html.lower()
    assert "interpretability is not live_pin_ok" in html.lower()
    assert 'id="better-consider"' in html
    assert html.index('id="ten-consider"') < html.index('id="better-consider"')
    assert html.index('id="better-consider"') < html.index('id="studio-consider"')
    assert html.index('id="join-consider"') < html.index('id="firm-console"')
    assert 'id="better-zeros"' in html
    assert 'id="better-hops"' in html
    assert 'id="better-facts"' in html
    assert 'id="better-hops-kicker"' in html
    assert 'id="better-facts-kicker"' in html
    assert "Five facts" in html
    assert 'class="fact-stack"' in html.split('id="better-consider"', 1)[1].split('id="studio-consider"', 1)[0]
    better_board = html.split('id="better-consider"', 1)[1].split('id="studio-consider"', 1)[0]
    assert 'data-hop="systems"><a href="#buyer"' in better_board
    assert 'data-hop="build"><a href="#whole"' in better_board
    assert 'data-hop="business"><a href="#firm"' in better_board
    assert 'data-hop="services"><a href="#firm-ms"' in better_board
    assert 'data-hop="polish"><a href="#ten-consider"' in better_board
    assert 'data-hop="owner"><a href="#ten-consider"' in better_board
    assert 'href="/better"' not in better_board
    for hop in better["hops"]:
        assert hop["note"] in better_board
    assert "a systems review is not a wired firm" in better_board.lower()
    assert 'id="better-is-launch"' in better_board
    assert html.count("Walk honest better") >= 4
    join_board = html.split('id="join-consider"', 1)[1].split('id="firm-console"', 1)[0]
    assert 'data-hop="write"><a href="#buyer"' in join_board
    assert 'data-better-refuse="better_as_launch"' in html
    assert 'data-better-refuse="ten_as_seated"' in html
    assert 'data-better-refuse="systems_as_wired"' in html
    assert 'data-better-refuse="polish_as_production"' in html
    assert 'data-better-refuse="interpret_as_live_pin"' in html
    assert 'data-better-refuse="make_as_launch"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/better"' not in nav
    assert 'href="#better"' not in nav
    assert 'href="#better-consider"' not in nav
    assert "Honest better" not in nav
    assert "bindBetterRefuses" in js
    assert "refuseBetter" in js
    assert "BETTER_REFUSE" in js
    assert 'getElementById("better-lede")' not in js
    assert "honest better" in twin.lower()
    assert "Digital twin · 3.23.0" in twin
    assert "AINAV.Institute twin · 3.23.0" in twin
    assert "3.16.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    assert "Application kit · 3.23.0" in kit
    assert "Release 3.23.0" in lost
    assert "3.16.0" not in lost
    assert "Ultimate control plane · 3.23.0" in plane
    assert "3.16.0" not in plane
    assert 'href="index.html#better-consider"' in plane
    assert 'href="index.html#better-consider"' in app
    assert 'href="#better-consider">Honest better' in html
    assert "#better-consider {" in css
    assert "#ten-consider {" in css
    assert "#join-consider {" in css
    assert "#better-zeros" in css
    assert ".better-facts" in css
    assert "#better-hops a" in css
    assert ".pages-facts.better-facts" in css
    assert "data.better_as_launch || data.ten_as_seated" in js
    llms = public_llms().lower()
    assert "honest better sits on #success" in llms
    assert "a much better build and business is not launch" in llms
    assert "interpretability is not live_pin_ok" in llms
    search = public_search()
    better_rec = next(item for item in search["records"] if item["id"] == "better")
    assert better_rec["href"] == "index.html#better-consider"
    assert "a much better build and business is not launch" in better_rec["text"].lower()
    assert "not a /better route" in better_rec["text"].lower()
    assert "The join is launch" in identify
    assert "A much better build and business is launch" in identify
    assert "A much better build and business is launch" in app
    assert "Open better" in identify
    assert 'href="index.html#better-consider">Open better' in identify
    dash = public_dashboard()
    assert dash["release"] == "3.23.0"
    status = public_status()
    assert status["release"] == "3.23.0"
    assert status["website"]["honest_better"] is True
    assert status["website"]["honest_better_live"] is False
    assert status["website"]["better_as_launch"] is False
    assert status["website"]["ten_as_seated"] is False
    assert status["website"]["systems_as_wired"] is False
    assert status["website"]["polish_as_production"] is False
    assert status["website"]["interpret_as_live_pin"] is False
    assert status["website"]["honest_make"] is True
    assert status["website"]["make_as_launch"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.better.v1"
    assert review["better_as_launch"] is False
    assert "Treat a much better build and business as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    sale_hrefs = [
        item.get("href")
        for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"]
    ]
    assert "#better-consider" in sale_hrefs
    assert sale_hrefs[sale_hrefs.index("#join-consider") + 1] == "#better-consider"
    open_items = " ".join(cat["plane_interface"]["gaps"]["owner_only_open"])
    for stem in ("seat B click", "G12/G13", "billing", "launch"):
        assert stem in open_items
    assert html.count("Owner book") == 1
    assert cat["programs"]["website"]["managed"] is True


def test_instrument_321_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.20.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.21.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_better"] = False

    def live(cat):
        cat["programs"]["website"]["honest_better_live"] = True

    def launch(cat):
        cat["programs"]["website"]["better_as_launch"] = True

    def seated(cat):
        cat["programs"]["website"]["ten_as_seated"] = True

    def wired(cat):
        cat["programs"]["website"]["systems_as_wired"] = True

    def polish(cat):
        cat["programs"]["website"]["polish_as_production"] = True

    def interpret(cat):
        cat["programs"]["website"]["interpret_as_live_pin"] = True

    def site(cat):
        cat["honest_better"]["site"] = "Better board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest better" not in item.lower()
        ]

    def interpret_fp(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "interpretability is not live_pin_ok" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest join sits on #firm."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio. "
            "Not connected-as-live. Not a 10/10 launch. Not a shared sandbox. Not a production sim. "
            "Not a remainder close. Not a 10/10 quality launch. Not a patent board. "
            "Not a client assignment. Not a vault live pin. Not a secret catalog. "
            "Not a booked close. Not a catalog collection. Not a joined firm. "
            "Not a certified running firm."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        seated,
        wired,
        polish,
        interpret,
        site,
        principles,
        interpret_fp,
        ops,
        managed,
    ):
        cat = copy.deepcopy(load_catalog())
        mutator(cat)
        with pytest.raises(IntegrityError):
            validate_catalog(cat)
    edge = load_catalog()
    hole = copy.deepcopy(edge)
    hole["honest_better"]["kind"] = "ainav.honest.better.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_better"]["site"] = site_name["honest_better"]["site"].replace(
        "Honest better",
        "Better board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(site_name, site_name["plane_interface"])
    site_join = copy.deepcopy(edge)
    site_join["honest_better"]["site"] = site_join["honest_better"]["site"].replace(
        "A much better build and business is not launch.",
        "Better is recorded.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(site_join, site_join["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_better"]["site"] = site_route["honest_better"]["site"].replace(
        "Not a /better route.",
        "A /better route.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_better"]["site"] = site_glance["honest_better"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the better board.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge)
    success["expert_review"]["success"]["honest_better"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success)
    success_missing = copy.deepcopy(edge)
    success_missing["expert_review"]["success"].pop("honest_better")
    with pytest.raises(IntegrityError):
        validate_catalog(success_missing)
    success_kind = copy.deepcopy(edge)
    success_kind["expert_review"]["success"]["honest_better"]["kind"] = "ainav.honest.better.v0"
    with pytest.raises(IntegrityError):
        validate_catalog(success_kind)
    success_href = copy.deepcopy(edge)
    success_href["expert_review"]["success"]["honest_better"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_catalog(success_href)
    success_launch = copy.deepcopy(edge)
    success_launch["expert_review"]["success"]["honest_better"]["better_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_launch)
    live_body = copy.deepcopy(edge)
    live_body["honest_better"]["better_as_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(live_body, live_body["plane_interface"])
    leftover_body = copy.deepcopy(edge)
    leftover_body["honest_better"]["signed_l1"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(leftover_body, leftover_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_better"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(certified, certified["plane_interface"])
    for missing in (
        "Treat a much better build and business as launch",
        "Treat a 10/10 as a seated second human",
        "Treat a systems review as a wired firm",
        "Treat a polish pass as production",
        "Treat interpretability as LIVE_PIN_OK",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
    hosted_launch = copy.deepcopy(edge)
    hosted_launch["expert_review"]["success"]["honest_better"]["better_as_launch"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(hosted_launch)
    hosted_polish = copy.deepcopy(edge)
    hosted_polish["expert_review"]["success"]["honest_better"]["polish_as_production"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(hosted_polish)
    principles_better = copy.deepcopy(edge)
    principles_better["expert_review"]["first_principles"] = [
        item
        for item in principles_better["expert_review"]["first_principles"]
        if "honest better" not in item.lower()
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(principles_better, principles_better["plane_interface"])
    principles_launch = copy.deepcopy(edge)
    principles_launch["expert_review"]["first_principles"] = [
        item.replace("A much better build and business is not launch.", "Better is recorded.")
        for item in principles_launch["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(principles_launch, principles_launch["plane_interface"])
    ops_sku = copy.deepcopy(edge)
    ops_sku["operations"]["note"] = "Honest better sits on #success."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(ops_sku, ops_sku["plane_interface"])
    ops_success = copy.deepcopy(edge)
    ops_success["operations"]["note"] = "SKU attach chain. Honest better sits on #path."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(ops_success, ops_success["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. Honest ten sits on #success."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(ops_name, ops_name["plane_interface"])
    managed_run = copy.deepcopy(edge)
    managed_run["expert_review"]["success"]["managed_face"]["managed"] = (
        edge["expert_review"]["success"]["managed_face"]["managed"].replace(
            "Not a much-better launch.",
            "Much-better launch.",
        )
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_321(managed_run, managed_run["plane_interface"])
    wired_fp = copy.deepcopy(edge)
    wired_fp["expert_review"]["first_principles"] = [
        item.replace("A systems review is not a wired firm.", "Systems are visible.")
        .replace("Interpretability is not LIVE_PIN_OK.", "Interpretability is recorded.")
        for item in wired_fp["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        validate_catalog(wired_fp)
