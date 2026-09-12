from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.buyer import success_program
from ainav.catalog import load_catalog, validate_catalog


def test_close_bench_is_catalog_law_and_on_the_sale_site():
    cat = load_catalog()
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "close bench" in blob
    assert "three planes" in blob
    bench = cat["expert_review"]["success"]["close_bench"]
    assert bench["kind"] == "ainav.close_bench.v1"
    assert bench["sku"] is False
    assert bench["assigned"] is False
    assert bench["production"] is False
    assert bench["live_pin_ok"] is False
    assert bench["named_client"] is None
    assert [item["id"] for item in bench["planes"]] == ["institute", "client", "production"]
    exported = success_program()["close_bench"]
    assert exported["lede"] == bench["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    assert 'id="close-console"' in html
    assert 'id="path-planes"' in html
    assert "paintCloseBench" in js
    assert "Close on a client twin" in html
    assert "path-walk" in html
    assert "path-promote" in html
    assert "path-udual" in html
    assert 'href="/path"' not in html
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#path"' not in nav
    assert "index.html#path" in twin
    assert "Close bench" in twin
    objections = {item["id"] for item in cat["expert_review"]["success"]["objections"]}
    assert "close" in objections


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_close_bench_fail_closed():
    def sku(cat):
        cat["expert_review"]["success"]["close_bench"]["sku"] = True

    def assigned(cat):
        cat["expert_review"]["success"]["close_bench"]["assigned"] = True

    def production(cat):
        cat["expert_review"]["success"]["close_bench"]["production"] = True

    def named(cat):
        cat["expert_review"]["success"]["close_bench"]["named_client"] = "Acme"

    def pin(cat):
        cat["expert_review"]["success"]["close_bench"]["live_pin_ok"] = True

    def kind(cat):
        cat["expert_review"]["success"]["close_bench"]["kind"] = "ainav.fourth.sku.v1"

    def planes(cat):
        cat["expert_review"]["success"]["close_bench"]["planes"] = [{"id": "shared"}]

    def lede(cat):
        cat["expert_review"]["success"]["close_bench"]["lede"] = "Flip the demo live."

    def refuse(cat):
        cat["expert_review"]["success"]["close_bench"]["refuse"] = ["A blog"]

    def site(cat):
        cat["expert_review"]["success"]["close_bench"]["site"] = "A /demo route."

    def note(cat):
        cat["expert_review"]["success"]["close_bench"]["note"] = "Assigned later."

    def objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item for item in cat["expert_review"]["success"]["objections"] if item.get("id") != "close"
        ]

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "auto-promote" not in item.lower()
        ]

    def upgrade(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 55:
                item["do"] = "Ship a demo flip."

    for mutator in (
        sku,
        assigned,
        production,
        named,
        pin,
        kind,
        planes,
        lede,
        refuse,
        site,
        note,
        objection,
        ciso,
        upgrade,
    ):
        _reject(mutator)
