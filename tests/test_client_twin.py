from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.buyer import success_program
from ainav.catalog import load_catalog, validate_catalog


def test_client_twin_is_catalog_law_and_on_the_sale_site():
    cat = load_catalog()
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "client-assigned" in blob
    assert "segregated" in blob
    assert "client twin" in blob
    twin = cat["expert_review"]["success"]["client_twin"]
    assert twin["kind"] == "ainav.client_twin.v1"
    assert twin["sku"] is False
    assert twin["fourth_sku"] is False
    assert twin["assigned"] is False
    assert twin["production"] is False
    assert twin["launch"] is False
    assert twin["live_pin_ok"] is False
    assert twin["named_client"] is None
    assert twin["do_not_invent_names"] is True
    stages = " ".join(twin["stages"]).lower()
    for stem in ("qualify", "remote proof", "close l1", "assigned sandbox", "paid enhance"):
        assert stem in stages
    exported = success_program()["client_twin"]
    assert exported["lede"] == twin["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin_html = Path("institute/twin.html").read_text(encoding="utf-8")
    assert 'id="path"' in html
    assert 'id="path-console"' in html
    assert "paintClientTwin" in js
    assert 'href="#path">Client twin</a>' in html
    assert "Close on a client twin" in html
    assert 'id="close-console"' in html
    assert "Assigned sandbox" in html
    assert "fourth SKU" in html
    assert 'href="/path"' not in html
    assert html.index('id="product"') < html.index('id="path"')
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#path"' not in nav
    assert "index.html#path" in twin_html
    walk = cat["expert_review"]["success"]["qualify"]["walk_away"]
    assert len(walk) == 20
    assert any("calendly" in item.lower() and "client twin" in item.lower() for item in walk)
    objections = {item["id"] for item in cat["expert_review"]["success"]["objections"]}
    assert "path" in objections
    sale = cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"]
    assert [item["href"] for item in sale][-1] == "#firm"
    assert [item["href"] for item in sale][-2] == "#path"


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_client_twin_fail_closed():
    def sku(cat):
        cat["expert_review"]["success"]["client_twin"]["sku"] = True

    def fourth(cat):
        cat["expert_review"]["success"]["client_twin"]["fourth_sku"] = True

    def assigned(cat):
        cat["expert_review"]["success"]["client_twin"]["assigned"] = True

    def production(cat):
        cat["expert_review"]["success"]["client_twin"]["production"] = True

    def launch(cat):
        cat["expert_review"]["success"]["client_twin"]["launch"] = True

    def named(cat):
        cat["expert_review"]["success"]["client_twin"]["named_client"] = "Acme"

    def live(cat):
        cat["expert_review"]["success"]["client_twin"]["live"] = True

    def pin(cat):
        cat["expert_review"]["success"]["client_twin"]["live_pin_ok"] = True

    def kind(cat):
        cat["expert_review"]["success"]["client_twin"]["kind"] = "ainav.fourth.sku.v1"

    def stages(cat):
        cat["expert_review"]["success"]["client_twin"]["stages"] = ["Demo only"]

    def count(cat):
        cat["expert_review"]["success"]["client_twin"]["count"] = 1

    def invent(cat):
        cat["expert_review"]["success"]["client_twin"]["do_not_invent_names"] = False

    def lede(cat):
        cat["expert_review"]["success"]["client_twin"]["lede"] = "A shared demo tenant."

    def is_yes(cat):
        cat["expert_review"]["success"]["client_twin"]["is"] = ["A product"]

    def is_not(cat):
        cat["expert_review"]["success"]["client_twin"]["is_not"] = ["A blog"]

    def enhance(cat):
        cat["expert_review"]["success"]["client_twin"]["enhance"] = "Free extras."

    def deploy(cat):
        cat["expert_review"]["success"]["client_twin"]["deploy"] = "Auto-promote."

    def site(cat):
        cat["expert_review"]["success"]["client_twin"]["site"] = "A /demo route."

    def note(cat):
        cat["expert_review"]["success"]["client_twin"]["note"] = "Assigned later."

    def walk(cat):
        cat["expert_review"]["success"]["qualify"]["walk_away"][-1] = "Calendly as the demo"

    def objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item for item in cat["expert_review"]["success"]["objections"] if item.get("id") != "path"
        ]

    def ciso_prod(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "institute twin" not in item.lower() and "client production" not in item.lower()
        ]

    def ciso_sku(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            "A fourth SKU as the sandbox" if "client twin" in item.lower() else item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
        ]

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "client-assigned" not in item.lower()
        ]

    def book(cat):
        cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"] = [
            item
            for item in cat["plane_interface"]["floor"]["public_face"]["owner_book"][0]["items"]
            if item.get("href") != "#path"
        ]

    def upgrade(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 55:
                item["do"] = "Ship a sandbox demo."

    for mutator in (
        sku,
        fourth,
        assigned,
        production,
        launch,
        named,
        live,
        pin,
        kind,
        stages,
        count,
        invent,
        lede,
        is_yes,
        is_not,
        enhance,
        deploy,
        site,
        note,
        walk,
        objection,
        ciso_prod,
        ciso_sku,
        principles,
        book,
        upgrade,
    ):
        _reject(mutator)
