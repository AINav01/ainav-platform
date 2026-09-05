from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav import catalog as catmod
from ainav.buyer import success_program
from ainav.catalog import load_catalog, validate_catalog


def test_managed_face_is_catalog_law_and_on_the_sale_site():
    cat = load_catalog()
    blob = " ".join(cat["expert_review"]["first_principles"]).lower()
    assert "managed first-class" in blob
    assert "dynamic app" in blob
    assert "/demo" in blob
    face = cat["expert_review"]["success"]["managed_face"]
    assert face["kind"] == "ainav.managed_face.v1"
    assert face["sku"] is False
    assert face["cms"] is False
    assert face["dynamic"] is False
    assert face["launch"] is False
    assert face["live_pin_ok"] is False
    assert face["fourth_sku"] is False
    site = cat["programs"]["website"]
    assert site["managed"] is True
    assert site["first_class"] is True
    assert site["dynamic"] is False
    assert site["cms"] is False
    assert site["demo_path"] == "#twin"
    assert site["demo_is_sku"] is False
    exported = success_program()["managed_face"]
    assert exported["lede"] == face["lede"]
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    twin = Path("institute/twin.html").read_text(encoding="utf-8")
    assert 'id="class-glance"' in html
    assert 'id="demo-console"' in html
    assert 'id="product-stage"' in html
    assert "paintManagedFace" in js
    assert ".demo-console" in css
    assert "First-class demo" in html
    assert "First-class product" in html
    assert "Not a /demo route" in html
    assert 'href="/demo"' not in html
    assert "index.html#twin" in twin
    assert "First-class demo" in twin
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#class-glance"' not in nav
    assert html.index('id="twin"') < html.index('id="product"')


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_managed_face_fail_closed():
    def cms(cat):
        cat["expert_review"]["success"]["managed_face"]["cms"] = True

    def dynamic(cat):
        cat["expert_review"]["success"]["managed_face"]["dynamic"] = True

    def launch(cat):
        cat["expert_review"]["success"]["managed_face"]["launch"] = True

    def live(cat):
        cat["expert_review"]["success"]["managed_face"]["live_pin_ok"] = True

    def site_dynamic(cat):
        cat["programs"]["website"]["dynamic"] = True

    def demo_sku(cat):
        cat["programs"]["website"]["demo_is_sku"] = True

    def demo_path(cat):
        cat["programs"]["website"]["demo_path"] = "/demo"

    def principles(cat):
        cat["expert_review"]["first_principles"] = [
            item
            for item in cat["expert_review"]["first_principles"]
            if "managed first-class" not in item.lower()
        ]

    def walk(cat):
        cat["expert_review"]["success"]["qualify"]["walk_away"] = [
            item
            for item in cat["expert_review"]["success"]["qualify"]["walk_away"]
            if "dynamic" not in item.lower() and "calendly" not in item.lower()
        ]

    def managed_objection(cat):
        cat["expert_review"]["success"]["objections"] = [
            item
            for item in cat["expert_review"]["success"]["objections"]
            if item.get("id") != "managed"
        ]

    for mutator in (
        cms,
        dynamic,
        launch,
        live,
        site_dynamic,
        demo_sku,
        demo_path,
        principles,
        walk,
        managed_objection,
    ):
        _reject(mutator)


def test_validate_managed_face_direct_holes():
    good = dict(load_catalog()["expert_review"]["success"]["managed_face"])
    with pytest.raises(IntegrityError):
        catmod._validate_managed_face(None)
    for key in ("sku", "cms", "fourth_sku", "dynamic", "launch", "live", "live_pin_ok"):
        hole = dict(good)
        hole[key] = True
        with pytest.raises(IntegrityError):
            catmod._validate_managed_face(hole)
    kind = dict(good)
    kind["kind"] = "ainav.cms.v1"
    with pytest.raises(IntegrityError):
        catmod._validate_managed_face(kind)
