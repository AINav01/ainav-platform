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
    assert "From proof to a client twin" in html
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
    assert [item["href"] for item in sale][-1] == "#path"


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_client_twin_fail_closed():
    def sku(cat):
        cat["expert_review"]["success"]["client_twin"]["sku"] = True

    def assigned(cat):
        cat["expert_review"]["success"]["client_twin"]["assigned"] = True

    def production(cat):
        cat["expert_review"]["success"]["client_twin"]["production"] = True

    def named(cat):
        cat["expert_review"]["success"]["client_twin"]["named_client"] = "Acme"

    def live(cat):
        cat["expert_review"]["success"]["client_twin"]["live_pin_ok"] = True

    def kind(cat):
        cat["expert_review"]["success"]["client_twin"]["kind"] = "ainav.fourth.sku.v1"

    def stages(cat):
        cat["expert_review"]["success"]["client_twin"]["stages"] = ["Demo only"]

    def count(cat):
        cat["expert_review"]["success"]["client_twin"]["count"] = 1

    for mutator in (sku, assigned, production, named, live, kind, stages, count):
        _reject(mutator)
