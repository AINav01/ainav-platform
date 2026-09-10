from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_HOLD_DIRECTION_IDS,
    HONEST_HOLD_DIRECTION_LINKS,
    HONEST_HOLD_HREFS,
    HONEST_HOLD_REFUSE_IDS,
    HONEST_HOLD_REFUSE_TEXT,
    HONEST_HOLD_SECRET_NAMES,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.honest_hold import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_318_honest_hold():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.20.0"
    hold = cat["honest_hold"]
    assert hold["kind"] == "ainav.honest.hold.v1"
    assert hold["honest"] is True
    assert hold["considered"] is True
    assert hold["recorded"] is True
    assert hold["vault_as_live_pin"] is False
    assert hold["names_as_wired"] is False
    assert hold["secret_in_catalog"] is False
    assert hold["sentinel_as_admit"] is False
    assert hold["hold_as_seated"] is False
    assert hold["certified"] is False
    assert hold["created"] is False
    assert hold["values_in_tree"] is False
    assert hold["ids_in_plane"] is False
    assert hold["from_this_plane"] is False
    assert hold["href"] == "#missing"
    assert hold["vault_name"] == "ainavinc7bfcff"
    assert hold["law_name"] == "ainav-mothership"
    assert list(hold["secret_names"]) == list(HONEST_HOLD_SECRET_NAMES)
    assert [item["id"] for item in hold["directions"]] == list(HONEST_HOLD_DIRECTION_IDS)
    for item in hold["directions"]:
        assert item.get("wired") is not True
        assert item.get("values_in_tree") is not True
        assert item.get("is_admit_plane") is not True
        got = [(link["label"], link["url"]) for link in item["links"]]
        assert got == list(HONEST_HOLD_DIRECTION_LINKS[item["id"]])
    refuse = [item for item in hold["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_HOLD_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_HOLD_REFUSE_TEXT[key] for key in HONEST_HOLD_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_HOLD_HREFS[key] for key in HONEST_HOLD_REFUSE_IDS}
    assert "honest hold" in hold["note"].lower()
    assert "a vault hold is not live_pin_ok" in hold["note"].lower()
    assert "sentinel is not the admit plane" in hold["note"].lower()
    assert cat["programs"]["website"]["honest_hold"] is True
    assert cat["programs"]["website"]["honest_protect"] is True
    assert cat["programs"]["website"]["honest_hold_live"] is False
    assert cat["programs"]["website"]["vault_as_live_pin"] is False
    assert cat["programs"]["website"]["names_as_wired"] is False
    assert cat["programs"]["website"]["secret_in_catalog"] is False
    assert cat["programs"]["website"]["sentinel_as_admit"] is False
    assert cat["programs"]["website"]["hold_as_seated"] is False
    assert "honest hold" in cat["operations"]["note"].lower()
    assert "#missing" in cat["operations"]["note"]
    assert any("3.18.0" in item and "honest hold" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("3.17.0" in item and "honest protect" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "a vault hold as live_pin_ok" in does_not
    assert "secret names as wired notify" in does_not
    assert "secret values in the catalog" in does_not
    assert "sentinel as the admit plane" in does_not
    assert "a vault hold as a seated second human" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest hold" in principles
    assert "a vault hold is not live_pin_ok" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 90
    assert upgrades[88]["who"] == "tree"
    assert upgrades[88]["done"] is True
    assert upgrades[88]["marks_live_pin"] is False
    blob = f"{upgrades[88]['title']} {upgrades[88]['do']}".lower()
    assert "honest hold" in blob
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
    assert "3.18.0" in html
    assert "3.17.0" in html
    assert "honest hold" in html.lower()
    assert "a vault hold is not live_pin_ok" in html.lower()
    assert "a catalog must not hold secret values" in html.lower()
    assert 'id="hold-consider"' in html
    assert html.index('id="hold-consider"') < html.index('id="remain-consider"')
    assert 'id="hold-zeros"' in html
    assert 'id="hold-names"' in html
    assert 'id="hold-directions"' in html
    assert 'id="hold-facts"' in html
    assert "Secret names are not wired" in html
    assert "A catalog must not hold secret values" in html
    assert "Sentinel is not the admit plane" in html
    assert "https://portal.azure.com/#browse/Microsoft.KeyVault%2Fvaults" in html
    assert "https://admin.teams.microsoft.com" in html
    assert "https://ainav.sharepoint.com/sites/AINavInc" in html
    assert "https://portal.azure.com/#view/Microsoft_Azure_Security_Insights" in html
    assert 'href="#buyer">The write' in html
    assert "Owner directions and links sit on the hold board" in twin
    for name in HONEST_HOLD_SECRET_NAMES:
        assert name in html
    assert 'data-hold-refuse="vault_as_live_pin"' in html
    assert 'data-hold-refuse="names_as_wired"' in html
    assert 'data-hold-refuse="secret_in_catalog"' in html
    assert 'data-hold-refuse="sentinel_as_admit"' in html
    assert 'data-hold-refuse="hold_as_seated"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/hold"' not in nav
    assert 'href="#hold"' not in nav
    assert 'href="#hold-consider"' not in nav
    assert "Honest hold" not in nav
    assert "bindHoldRefuses" in js
    assert "refuseHold" in js
    assert 'getElementById("hold-lede")' not in js
    assert "honest hold" in twin.lower()
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
    assert 'href="index.html#hold-consider"' in plane
    assert 'href="index.html#hold-consider"' in app
    assert 'href="#hold-consider">Honest hold' in html
    assert "#hold-consider {" in css
    assert "#ten-consider {" in css
    assert "#protect-consider {" in css
    assert "#hold-zeros" in css
    assert "#hold-directions {" in css
    assert ".hold-facts" in css
    assert ".hold-directions" in css
    assert "A vault hold is LIVE_PIN_OK" in identify
    assert "Open hold" in identify
    assert 'href="index.html#hold-consider">Open hold' in identify
    assert "A vault hold is LIVE_PIN_OK" in app
    assert "Open protect" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.20.0"
    status = public_status()
    assert status["release"] == "3.20.0"
    assert status["website"]["honest_hold"] is True
    assert status["website"]["honest_hold_live"] is False
    assert status["website"]["vault_as_live_pin"] is False
    assert status["website"]["names_as_wired"] is False
    assert status["website"]["secret_in_catalog"] is False
    assert status["website"]["sentinel_as_admit"] is False
    assert status["website"]["hold_as_seated"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.hold.v1"
    assert review["vault_as_live_pin"] is False
    assert "Treat a vault hold as LIVE_PIN_OK." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    owner_hrefs = [
        item.get("href")
        for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][1]["items"]
    ]
    assert owner_hrefs[:3] == ["#closed", "#missing", "#open"]
    assert "#hold-consider" in owner_hrefs
    assert "#protect-consider" in owner_hrefs
    services = hold["services"]
    assert services["claimed_as_wired"] is False
    assert services["vault"]["values_in_tree"] is False
    assert services["sentinel"]["is_admit_plane"] is False
    assert services["sentinel"]["from_this_plane"] is False
    open_items = " ".join(cat["plane_interface"]["gaps"]["owner_only_open"])
    for stem in (
        "Teams team and channel ids",
        "SHAREPOINT_SITE_ID",
        "Sentinel on the existing LAW",
        "seat B click",
    ):
        assert stem in open_items


def test_instrument_318_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.17.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.18.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_hold"] = False

    def live(cat):
        cat["programs"]["website"]["honest_hold_live"] = True

    def pin(cat):
        cat["programs"]["website"]["vault_as_live_pin"] = True

    def wired(cat):
        cat["programs"]["website"]["names_as_wired"] = True

    def secret(cat):
        cat["programs"]["website"]["secret_in_catalog"] = True

    def sentinel(cat):
        cat["programs"]["website"]["sentinel_as_admit"] = True

    def seated(cat):
        cat["programs"]["website"]["hold_as_seated"] = True

    def site(cat):
        cat["honest_hold"]["site"] = "Hold board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest hold" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest protect sits on #ip."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio. "
            "Not connected-as-live. Not a 10/10 launch. Not a shared sandbox. Not a production sim. "
            "Not a remainder close. Not a 10/10 quality launch. Not a patent board. Not a client assignment."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        pin,
        wired,
        secret,
        sentinel,
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
    hole["honest_hold"]["kind"] = "ainav.honest.hold.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_318(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_hold"]["site"] = site_name["honest_hold"]["site"].replace(
        "Honest hold",
        "Hold board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_318(site_name, site_name["plane_interface"])
    site_close = copy.deepcopy(edge)
    site_close["honest_hold"]["site"] = site_close["honest_hold"]["site"].replace(
        "A vault hold is not LIVE_PIN_OK.",
        "Hold is recorded.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_318(site_close, site_close["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_hold"]["site"] = site_route["honest_hold"]["site"].replace(
        "Not a /hold route.",
        "A /hold route.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_318(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_hold"]["site"] = site_glance["honest_hold"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the hold board.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_318(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge)
    success["expert_review"]["success"]["honest_hold"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success)
    success_missing = copy.deepcopy(edge)
    success_missing["expert_review"]["success"].pop("honest_hold")
    with pytest.raises(IntegrityError):
        validate_catalog(success_missing)
    success_kind = copy.deepcopy(edge)
    success_kind["expert_review"]["success"]["honest_hold"]["kind"] = "ainav.honest.hold.v0"
    with pytest.raises(IntegrityError):
        validate_catalog(success_kind)
    success_href = copy.deepcopy(edge)
    success_href["expert_review"]["success"]["honest_hold"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_catalog(success_href)
    success_pin = copy.deepcopy(edge)
    success_pin["expert_review"]["success"]["honest_hold"]["vault_as_live_pin"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_pin)
    success_wired = copy.deepcopy(edge)
    success_wired["expert_review"]["success"]["honest_hold"]["names_as_wired"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_wired)
    success_secret = copy.deepcopy(edge)
    success_secret["expert_review"]["success"]["honest_hold"]["secret_in_catalog"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_secret)
    success_sentinel = copy.deepcopy(edge)
    success_sentinel["expert_review"]["success"]["honest_hold"]["sentinel_as_admit"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_sentinel)
    success_seated = copy.deepcopy(edge)
    success_seated["expert_review"]["success"]["honest_hold"]["hold_as_seated"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_seated)
    live_body = copy.deepcopy(edge)
    live_body["honest_hold"]["vault_as_live_pin"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_318(live_body, live_body["plane_interface"])
    leftover_body = copy.deepcopy(edge)
    leftover_body["honest_hold"]["values_in_tree"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_318(leftover_body, leftover_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_hold"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_318(certified, certified["plane_interface"])
    for missing in (
        "Treat a vault hold as LIVE_PIN_OK",
        "Treat secret names as wired notify",
        "Treat secret values in the catalog",
        "Treat Sentinel as the admit plane",
        "Treat a vault hold as a seated second human",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
