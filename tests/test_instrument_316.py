from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_TEN_HREFS,
    HONEST_TEN_REFUSE_IDS,
    HONEST_TEN_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.honest_ten import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_316_honest_ten():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.27.0"
    ten = cat["honest_ten"]
    assert ten["kind"] == "ainav.honest.ten.v1"
    assert ten["honest"] is True
    assert ten["considered"] is True
    assert ten["recorded"] is True
    assert ten["quality_ten_is_launch"] is False
    assert ten["gold_999_is_live_pin"] is False
    assert ten["compete_is_named_client"] is False
    assert ten["service_green_is_production"] is False
    assert ten["quality_is_seated"] is False
    assert ten["certified"] is False
    assert ten["created"] is False
    assert ten["href"] == "#success"
    refuse = [item for item in ten["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_TEN_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_TEN_REFUSE_TEXT[key] for key in HONEST_TEN_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_TEN_HREFS[key] for key in HONEST_TEN_REFUSE_IDS}
    assert "honest ten" in ten["note"].lower()
    assert "a 10/10 quality check is not launch" in ten["note"].lower()
    assert "gold 99.9 is not live_pin_ok" in ten["note"].lower()
    assert cat["programs"]["website"]["honest_ten"] is True
    assert cat["programs"]["website"]["honest_remainder"] is True
    assert cat["programs"]["website"]["honest_ten_live"] is False
    assert cat["programs"]["website"]["quality_ten_is_launch"] is False
    assert cat["programs"]["website"]["gold_999_is_live_pin"] is False
    assert cat["programs"]["website"]["compete_is_named_client"] is False
    assert cat["programs"]["website"]["service_green_is_production"] is False
    assert cat["programs"]["website"]["quality_is_seated"] is False
    assert "honest ten" in cat["operations"]["note"].lower()
    assert "#success" in cat["operations"]["note"]
    assert any("3.16.0" in item and "honest ten" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a 10/10 quality check as launch" in does_not
    assert "gold 99.9 as live_pin_ok" in does_not
    assert "a competitor analysis as a named client" in does_not
    assert "a green service as production" in does_not
    assert "a quality check as a seated second human" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest ten" in principles
    assert "a 10/10 quality check is not launch" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 97
    assert upgrades[86]["who"] == "tree"
    assert upgrades[86]["done"] is True
    assert upgrades[86]["marks_live_pin"] is False
    blob = f"{upgrades[86]['title']} {upgrades[86]['do']}".lower()
    assert "honest ten" in blob
    assert "live_pin_ok" in blob
    row_ids = [item["id"] for item in cat["plane_interface"]["competitive"]["rows"]]
    for needed in ("job_c", "teams_vote", "entra_mfa", "cursor_agent", "cloudflare_edge"):
        assert needed in row_ids
    substitutes = [
        item
        for item in cat["plane_interface"]["competitive"]["rows"]
        if item.get("id") != "job_c"
    ]
    assert all(
        item.get("consume_once") is not True
        and item.get("fail_closed_sor") is not True
        and item.get("counterparty_ai") is not True
        for item in substitutes
    )
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.16.0" in html
    assert "honest ten" in html.lower()
    assert "a 10/10 quality check is not launch" in html.lower()
    assert "gold 99.9 is not live_pin_ok" in html.lower()
    assert 'id="ten-consider"' in html
    assert 'id="ten-zeros"' in html
    assert 'id="ten-facts"' in html
    assert 'data-ten-refuse="ten_as_launch"' in html
    assert 'data-ten-refuse="gold_999_as_live_pin"' in html
    assert 'data-ten-refuse="compete_as_named_client"' in html
    assert 'data-ten-refuse="service_green_as_production"' in html
    assert 'data-ten-refuse="quality_as_seated"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/ten"' not in nav
    assert 'href="#ten"' not in nav
    assert 'href="#ten-consider"' not in nav
    assert "Honest ten" not in nav
    assert "bindTenRefuses" in js
    assert "refuseTen" in js
    assert "ten-lede" not in js
    assert "remain-lede" not in js
    assert "honest ten" in twin.lower()
    assert "a 10/10 quality check is not launch" in twin.lower()
    assert "Digital twin · 3.27.0" in twin
    assert "AINAV.Institute twin · 3.27.0" in twin
    assert "3.16.0" not in twin
    kit = Path("institute/kit.html").read_text(encoding="utf-8")
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    assert "Application kit · 3.27.0" in kit
    assert "Release 3.27.0" in lost
    assert "3.16.0" not in lost
    assert "Ultimate control plane · 3.27.0" in plane
    assert "3.16.0" not in plane
    assert 'href="index.html#ten-consider"' in plane
    assert 'href="index.html#ten-consider"' in app
    assert 'href="#ten-consider">Honest ten' in html
    assert "#ten-consider {" in css
    assert "#ten-zeros" in css
    assert ".ten-facts" in css
    assert "A 10/10 quality check is launch" in identify
    assert "Open ten" in identify
    assert "A 10/10 quality check is launch" in app
    dash = public_dashboard()
    assert dash["release"] == "3.27.0"
    status = public_status()
    assert status["release"] == "3.27.0"
    assert status["website"]["honest_ten"] is True
    assert status["website"]["honest_ten_live"] is False
    assert status["website"]["quality_ten_is_launch"] is False
    assert status["website"]["gold_999_is_live_pin"] is False
    assert status["website"]["compete_is_named_client"] is False
    assert status["website"]["service_green_is_production"] is False
    assert status["website"]["quality_is_seated"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.ten.v1"
    assert review["quality_ten_is_launch"] is False
    assert "Treat a 10/10 quality check as launch." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    owner_hrefs = [
        item.get("href")
        for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][1]["items"]
    ]
    assert owner_hrefs[:3] == ["#closed", "#missing", "#open"]
    assert "#ten-consider" in owner_hrefs
    services = ten["services"]
    assert services["claimed_as_production"] is False
    assert services["microsoft"]["graph_writes"] == "owner_revoked"
    assert services["cloudflare"]["ssl_full_claimed"] is False
    assert services["github"]["green_check_is_not_live_pin_ok"] is True
    assert services["cursor"]["cloud_agent_is_not_a_seat"] is True


def test_instrument_316_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.15.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.16.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_ten"] = False

    def live(cat):
        cat["programs"]["website"]["honest_ten_live"] = True

    def launch(cat):
        cat["programs"]["website"]["quality_ten_is_launch"] = True

    def gold(cat):
        cat["programs"]["website"]["gold_999_is_live_pin"] = True

    def compete(cat):
        cat["programs"]["website"]["compete_is_named_client"] = True

    def service(cat):
        cat["programs"]["website"]["service_green_is_production"] = True

    def seated(cat):
        cat["programs"]["website"]["quality_is_seated"] = True

    def site(cat):
        cat["honest_ten"]["site"] = "Ten board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest ten" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest remainder sits on #missing."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio. "
            "Not connected-as-live. Not a 10/10 launch. Not a shared sandbox. Not a production sim. "
            "Not a remainder close."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        launch,
        gold,
        compete,
        service,
        seated,
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
    hole["honest_ten"]["kind"] = "ainav.honest.ten.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_ten"]["site"] = site_name["honest_ten"]["site"].replace(
        "Honest ten",
        "Ten board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(site_name, site_name["plane_interface"])
    site_close = copy.deepcopy(edge)
    site_close["honest_ten"]["site"] = site_close["honest_ten"]["site"].replace(
        "A 10/10 quality check is not launch.",
        "Ten is recorded.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(site_close, site_close["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_ten"]["site"] = site_route["honest_ten"]["site"].replace(
        "Not a /ten route.",
        "A /ten route.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_ten"]["site"] = site_glance["honest_ten"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the ten board.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge)
    success["expert_review"]["success"]["honest_ten"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success)
    success_missing = copy.deepcopy(edge)
    success_missing["expert_review"]["success"].pop("honest_ten")
    with pytest.raises(IntegrityError):
        validate_catalog(success_missing)
    success_kind = copy.deepcopy(edge)
    success_kind["expert_review"]["success"]["honest_ten"]["kind"] = "ainav.honest.ten.v0"
    with pytest.raises(IntegrityError):
        validate_catalog(success_kind)
    success_href = copy.deepcopy(edge)
    success_href["expert_review"]["success"]["honest_ten"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_catalog(success_href)
    success_launch = copy.deepcopy(edge)
    success_launch["expert_review"]["success"]["honest_ten"]["quality_ten_is_launch"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_launch)
    success_gold = copy.deepcopy(edge)
    success_gold["expert_review"]["success"]["honest_ten"]["gold_999_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_gold)
    success_compete = copy.deepcopy(edge)
    success_compete["expert_review"]["success"]["honest_ten"]["compete_is_named_client"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_compete)
    success_service = copy.deepcopy(edge)
    success_service["expert_review"]["success"]["honest_ten"]["service_green_is_production"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_service)
    success_seated = copy.deepcopy(edge)
    success_seated["expert_review"]["success"]["honest_ten"]["quality_is_seated"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_seated)
    live_body = copy.deepcopy(edge)
    live_body["honest_ten"]["quality_ten_is_launch"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(live_body, live_body["plane_interface"])
    leftover_body = copy.deepcopy(edge)
    leftover_body["honest_ten"]["gold_999_is_live_pin"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(leftover_body, leftover_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_ten"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(certified, certified["plane_interface"])
    principles_name = copy.deepcopy(edge)
    principles_name["expert_review"]["first_principles"] = [
        item.replace("Honest ten sits on #success.", "Ten sits on #success.")
        for item in principles_name["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(principles_name, principles_name["plane_interface"])
    principles_close = copy.deepcopy(edge)
    principles_close["expert_review"]["first_principles"] = [
        item.replace("A 10/10 quality check is not launch.", "Ten is recorded done.")
        for item in principles_close["expert_review"]["first_principles"]
    ]
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(principles_close, principles_close["plane_interface"])
    ops_attach = copy.deepcopy(edge)
    ops_attach["operations"]["note"] = "Honest ten sits on #success."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(ops_attach, ops_attach["plane_interface"])
    ops_href = copy.deepcopy(edge)
    ops_href["operations"]["note"] = "SKU attach chain. Honest ten is recorded."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(ops_href, ops_href["plane_interface"])
    ops_name = copy.deepcopy(edge)
    ops_name["operations"]["note"] = "SKU attach chain. Ten sits on #success."
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(ops_name, ops_name["plane_interface"])
    managed_direct = copy.deepcopy(edge)
    managed_direct["expert_review"]["success"]["managed_face"]["managed"] = managed_direct[
        "expert_review"
    ]["success"]["managed_face"]["managed"].replace(" Not a 10/10 quality launch.", "")
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_316(managed_direct, managed_direct["plane_interface"])
    for missing in (
        "Treat a 10/10 quality check as launch",
        "Treat gold 99.9 as LIVE_PIN_OK",
        "Treat a competitor analysis as a named client",
        "Treat a green service as production",
        "Treat a quality check as a seated second human",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
