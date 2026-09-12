from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.catalog import (
    HONEST_PROTECT_HREFS,
    HONEST_PROTECT_REFUSE_IDS,
    HONEST_PROTECT_REFUSE_TEXT,
    load_catalog,
    validate_catalog,
)
from ainav.dashboard import public_dashboard
from ainav.honest_protect import public_review
from ainav.institute_status import public_status
from ainav.microsoft.institute_publish import publish_institute


def test_release_is_317_honest_protect():
    cat = load_catalog()
    assert cat["entity"]["release"] == "3.20.0"
    protect = cat["honest_protect"]
    assert protect["kind"] == "ainav.honest.protect.v1"
    assert protect["honest"] is True
    assert protect["considered"] is True
    assert protect["recorded"] is True
    assert protect["protect_as_patent"] is False
    assert protect["protect_as_uncopyable"] is False
    assert protect["client_license_as_assignment"] is False
    assert protect["kit_pass_as_source"] is False
    assert protect["g12_as_closed"] is False
    assert protect["certified"] is False
    assert protect["created"] is False
    assert protect["href"] == "#ip"
    refuse = [item for item in protect["refuse"] if item.get("refuse") is True]
    assert [item["id"] for item in refuse] == list(HONEST_PROTECT_REFUSE_IDS)
    assert {item["id"]: item["refuse_text"] for item in refuse} == {
        key: HONEST_PROTECT_REFUSE_TEXT[key] for key in HONEST_PROTECT_REFUSE_IDS
    }
    hrefs = {item["id"]: item["href"] for item in refuse}
    assert hrefs == {key: HONEST_PROTECT_HREFS[key] for key in HONEST_PROTECT_REFUSE_IDS}
    assert "honest protect" in protect["note"].lower()
    assert "an ip board is not a patent" in protect["note"].lower()
    assert "an l1 license is not an assignment of job c" in protect["note"].lower()
    assert cat["programs"]["website"]["honest_protect"] is True
    assert cat["programs"]["website"]["honest_ten"] is True
    assert cat["programs"]["website"]["honest_protect_live"] is False
    assert cat["programs"]["website"]["protect_as_patent"] is False
    assert cat["programs"]["website"]["protect_as_uncopyable"] is False
    assert cat["programs"]["website"]["client_license_as_assignment"] is False
    assert cat["programs"]["website"]["kit_pass_as_source"] is False
    assert cat["programs"]["website"]["g12_as_closed"] is False
    assert "honest protect" in cat["operations"]["note"].lower()
    assert "#ip" in cat["operations"]["note"]
    assert any("3.17.0" in item and "honest protect" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    does_not = " ".join(cat["expert_review"]["success"]["ciso"]["does_not"]).lower()
    assert "an ip board as a patent" in does_not
    assert "insulation as uncopyable" in does_not
    assert "an l1 license as an assignment of job c" in does_not
    assert "kit pass as a source license" in does_not
    assert "this board as closing g12" in does_not
    principles = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "honest protect" in principles
    assert "an ip board is not a patent" in principles
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 90
    assert upgrades[87]["who"] == "tree"
    assert upgrades[87]["done"] is True
    assert upgrades[87]["marks_live_pin"] is False
    blob = f"{upgrades[87]['title']} {upgrades[87]['do']}".lower()
    assert "honest protect" in blob
    assert "live_pin_ok" in blob
    ip = cat["ip"]
    assert ip["g12_open"] is True
    assert ip["no_patent_claim_in_this_tree"] is True
    assert ip["insulation"]["patent_claimed"] is False
    assert ip["insulation"]["uncopyable"] is False
    assert any(item.get("id") == "client" for item in ip["insulation"]["layers"])
    assert ip["client_protect"]["license_is_assignment"] is False
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    identify = Path("institute/identify.html").read_text(encoding="utf-8")
    app = Path("institute/app.html").read_text(encoding="utf-8")
    assert "3.17.0" in html
    assert "honest protect" in html.lower()
    assert "an ip board is not a patent" in html.lower()
    assert "an l1 license is not an assignment of job c" in html.lower()
    assert 'id="protect-consider"' in html
    assert 'id="protect-zeros"' in html
    assert 'id="protect-facts"' in html
    assert 'data-protect-refuse="protect_as_patent"' in html
    assert 'data-protect-refuse="protect_as_uncopyable"' in html
    assert 'data-protect-refuse="client_license_as_assignment"' in html
    assert 'data-protect-refuse="kit_pass_as_source"' in html
    assert 'data-protect-refuse="g12_as_closed"' in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="/protect"' not in nav
    assert 'href="#protect"' not in nav
    assert 'href="#protect-consider"' not in nav
    assert "Honest protect" not in nav
    assert "bindProtectRefuses" in js
    assert "refuseProtect" in js
    assert 'getElementById("protect-lede")' not in js
    assert "buyer-protect-lede" in js
    assert "ten-lede" not in js
    assert "honest protect" in twin.lower() or "3.17.0" in twin
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
    assert 'href="index.html#protect-consider"' in plane
    assert 'href="index.html#protect-consider"' in app
    assert 'href="#protect-consider">Honest protect' in html
    assert "#protect-consider {" in css
    assert "#protect-zeros" in css
    assert ".protect-facts" in css
    assert "An IP board is a patent" in identify
    assert "Open protect" in identify
    dash = public_dashboard()
    assert dash["release"] == "3.20.0"
    status = public_status()
    assert status["release"] == "3.20.0"
    assert status["website"]["honest_protect"] is True
    assert status["website"]["honest_protect_live"] is False
    assert status["website"]["protect_as_patent"] is False
    assert status["website"]["protect_as_uncopyable"] is False
    assert status["website"]["client_license_as_assignment"] is False
    assert status["website"]["kit_pass_as_source"] is False
    assert status["website"]["g12_as_closed"] is False
    review = public_review()
    assert review["kind"] == "ainav.honest.protect.v1"
    assert review["protect_as_patent"] is False
    assert "Treat an IP board as a patent." in " ".join(review["this_agent_cannot"])
    held = publish_institute()
    assert held["ok"] is False
    assert held["reason"] == "launch_not_ready"
    owner_hrefs = [
        item.get("href")
        for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][1]["items"]
    ]
    assert owner_hrefs[:3] == ["#closed", "#missing", "#open"]
    assert "#protect-consider" in owner_hrefs
    services = protect["services"]
    assert services["claimed_as_assignment"] is False
    assert services["microsoft"]["is_the_product"] is False
    assert services["client"]["license_is_assignment"] is False
    assert services["counsel"]["g12_closed"] is False


def test_instrument_317_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "3.16.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "3.17.0" not in item
        ]

    def flag_off(cat):
        cat["programs"]["website"]["honest_protect"] = False

    def live(cat):
        cat["programs"]["website"]["honest_protect_live"] = True

    def patent(cat):
        cat["programs"]["website"]["protect_as_patent"] = True

    def uncopyable(cat):
        cat["programs"]["website"]["protect_as_uncopyable"] = True

    def assign(cat):
        cat["programs"]["website"]["client_license_as_assignment"] = True

    def source(cat):
        cat["programs"]["website"]["kit_pass_as_source"] = True

    def g12(cat):
        cat["programs"]["website"]["g12_as_closed"] = True

    def site(cat):
        cat["honest_protect"]["site"] = "Protect board."

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "honest protect" not in item.lower()
        ]

    def ops(cat):
        cat["operations"]["note"] = "SKU attach chain. Honest ten sits on #success."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = (
            "Azure SWA hosts. Catalog regen. Gold CI. --publish-twin. Owner authorizes launch. "
            "Not a webmaster CMS. Not Squarespace. Not Power Pages. Not Copilot Studio. "
            "Not connected-as-live. Not a 10/10 launch. Not a shared sandbox. Not a production sim. "
            "Not a remainder close. Not a 10/10 quality launch."
        )

    for mutator in (
        release,
        closed,
        flag_off,
        live,
        patent,
        uncopyable,
        assign,
        source,
        g12,
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
    hole["honest_protect"]["kind"] = "ainav.honest.protect.v0"
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_317(hole, hole["plane_interface"])
    site_name = copy.deepcopy(edge)
    site_name["honest_protect"]["site"] = site_name["honest_protect"]["site"].replace(
        "Honest protect",
        "Protect board",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_317(site_name, site_name["plane_interface"])
    site_close = copy.deepcopy(edge)
    site_close["honest_protect"]["site"] = site_close["honest_protect"]["site"].replace(
        "An IP board is not a patent.",
        "Protect is recorded.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_317(site_close, site_close["plane_interface"])
    site_route = copy.deepcopy(edge)
    site_route["honest_protect"]["site"] = site_route["honest_protect"]["site"].replace(
        "Not a /protect route.",
        "A /protect route.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_317(site_route, site_route["plane_interface"])
    site_glance = copy.deepcopy(edge)
    site_glance["honest_protect"]["site"] = site_glance["honest_protect"]["site"].replace(
        "First glance stays the write rail.",
        "First glance is the protect board.",
    )
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_317(site_glance, site_glance["plane_interface"])
    success = copy.deepcopy(edge)
    success["expert_review"]["success"]["honest_protect"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success)
    success_missing = copy.deepcopy(edge)
    success_missing["expert_review"]["success"].pop("honest_protect")
    with pytest.raises(IntegrityError):
        validate_catalog(success_missing)
    success_kind = copy.deepcopy(edge)
    success_kind["expert_review"]["success"]["honest_protect"]["kind"] = "ainav.honest.protect.v0"
    with pytest.raises(IntegrityError):
        validate_catalog(success_kind)
    success_href = copy.deepcopy(edge)
    success_href["expert_review"]["success"]["honest_protect"]["href"] = "#buyer"
    with pytest.raises(IntegrityError):
        validate_catalog(success_href)
    success_patent = copy.deepcopy(edge)
    success_patent["expert_review"]["success"]["honest_protect"]["protect_as_patent"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_patent)
    success_copy = copy.deepcopy(edge)
    success_copy["expert_review"]["success"]["honest_protect"]["protect_as_uncopyable"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_copy)
    success_assign = copy.deepcopy(edge)
    success_assign["expert_review"]["success"]["honest_protect"]["client_license_as_assignment"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_assign)
    success_source = copy.deepcopy(edge)
    success_source["expert_review"]["success"]["honest_protect"]["kit_pass_as_source"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_source)
    success_g12 = copy.deepcopy(edge)
    success_g12["expert_review"]["success"]["honest_protect"]["g12_as_closed"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(success_g12)
    live_body = copy.deepcopy(edge)
    live_body["honest_protect"]["protect_as_patent"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_317(live_body, live_body["plane_interface"])
    leftover_body = copy.deepcopy(edge)
    leftover_body["honest_protect"]["protect_as_uncopyable"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_317(leftover_body, leftover_body["plane_interface"])
    certified = copy.deepcopy(edge)
    certified["honest_protect"]["certified"] = True
    with pytest.raises(IntegrityError):
        catmod._validate_instrument_317(certified, certified["plane_interface"])
    for missing in (
        "Treat an IP board as a patent",
        "Treat insulation as uncopyable",
        "Treat an L1 license as an assignment of Job C",
        "Treat kit PASS as a source license",
        "Treat this board as closing G12",
    ):
        ciso_hole = copy.deepcopy(edge["expert_review"]["success"])
        ciso_hole["ciso"]["does_not"] = [item for item in ciso_hole["ciso"]["does_not"] if item != missing]
        with pytest.raises(IntegrityError):
            catmod._validate_success_program(ciso_hole)
