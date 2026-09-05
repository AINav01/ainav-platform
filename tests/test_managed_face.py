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
    assert 'property="og:image"' in html
    assert "graphics/og.jpg" in html
    assert "graphics/write-rail.svg" in html
    assert "fonts/newsreader-500.woff2" in html
    assert html.index('id="class-glance"') < html.index('id="hero-contrast"')
    assert Path("institute/graphics/write-rail.svg").is_file()
    assert Path("institute/graphics/og.jpg").is_file()
    assert Path("institute/fonts/newsreader-500.woff2").is_file()
    assert Path("institute/fonts/source-sans-3-400.woff2").is_file()
    lost = Path("institute/404.html").read_text(encoding="utf-8")
    assert "This write did not land." in lost
    assert "graphics/write-rail.svg" in lost


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

    def ciso(cat):
        cat["expert_review"]["success"]["ciso"]["does_not"] = [
            item
            for item in cat["expert_review"]["success"]["ciso"]["does_not"]
            if "dynamic app" not in item.lower() and "calendly" not in item.lower()
        ]

    def lede(cat):
        cat["expert_review"]["success"]["managed_face"]["lede"] = "A nicer homepage."

    def product(cat):
        cat["expert_review"]["success"]["managed_face"]["product"] = "A nicer SKU page."

    def demo(cat):
        cat["expert_review"]["success"]["managed_face"]["demo"] = "Book a call."

    def managed(cat):
        cat["expert_review"]["success"]["managed_face"]["managed"] = "Hire a webmaster."

    def refuse(cat):
        cat["expert_review"]["success"]["managed_face"]["refuse"] = ["A CMS"]

    def site(cat):
        cat["expert_review"]["success"]["managed_face"]["site"] = "A nicer homepage."

    def note(cat):
        cat["expert_review"]["success"]["managed_face"]["note"] = "Looks finished."

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
        ciso,
        lede,
        product,
        demo,
        managed,
        refuse,
        site,
        note,
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
    for field, value in (
        ("lede", "A nicer homepage."),
        ("product", "A nicer SKU page."),
        ("demo", "Book a call."),
        ("managed", "Hire a webmaster."),
        ("site", "A nicer homepage."),
        ("note", "Looks finished."),
    ):
        hole = dict(good)
        hole[field] = value
        with pytest.raises(IntegrityError):
            catmod._validate_managed_face(hole)
    refuse = dict(good)
    refuse["refuse"] = ["A CMS"]
    with pytest.raises(IntegrityError):
        catmod._validate_managed_face(refuse)
    for stem in ("static", "cms", "admit plane", "three skus", "dashboard", "ninety-minute", "graph is not called", "calendly", "azure swa", "gold", "publish-twin", "write rail", "#twin", "/demo", "webflow", "live_pin_ok"):
        if stem in ("static", "cms"):
            hole = dict(good)
            hole["lede"] = "Managed first-class application. Not a shop."
            if stem == "cms":
                hole["lede"] = "Managed first-class static application."
            with pytest.raises(IntegrityError):
                catmod._validate_managed_face(hole)
        elif stem in ("admit plane", "three skus", "dashboard"):
            hole = dict(good)
            hole["product"] = "Prove, keep, deepen. Included dashboard. Three SKUs."
            if stem == "admit plane":
                hole["product"] = "Three SKUs. One dashboard."
            elif stem == "three skus":
                hole["product"] = "The admit plane. One dashboard."
            else:
                hole["product"] = "The admit plane. Three SKUs."
            with pytest.raises(IntegrityError):
                catmod._validate_managed_face(hole)
        elif stem in ("ninety-minute", "graph is not called", "calendly"):
            hole = dict(good)
            if stem == "ninety-minute":
                hole["demo"] = "Browser rehearsal. Graph is not called. Not Calendly."
            elif stem == "graph is not called":
                hole["demo"] = "Ninety-minute proof. Not Calendly."
            else:
                hole["demo"] = "Ninety-minute proof. Graph is not called."
            with pytest.raises(IntegrityError):
                catmod._validate_managed_face(hole)
        elif stem in ("azure swa", "gold", "publish-twin"):
            hole = dict(good)
            if stem == "azure swa":
                hole["managed"] = "Catalog plus gold plus --publish-twin."
            elif stem == "gold":
                hole["managed"] = "Azure SWA plus --publish-twin."
            else:
                hole["managed"] = "Azure SWA plus gold."
            with pytest.raises(IntegrityError):
                catmod._validate_managed_face(hole)
        elif stem in ("write rail", "#twin", "/demo"):
            hole = dict(good)
            if stem == "write rail":
                hole["site"] = "Demo is #twin. Not a /demo route."
            elif stem == "#twin":
                hole["site"] = "First glance stays the write rail. Not a /demo route."
            else:
                hole["site"] = "First glance stays the write rail. Demo is #twin."
            with pytest.raises(IntegrityError):
                catmod._validate_managed_face(hole)
        else:
            hole = dict(good)
            hole["note"] = "Not LIVE_PIN_OK." if stem == "webflow" else "Not Webflow."
            with pytest.raises(IntegrityError):
                catmod._validate_managed_face(hole)
    for missing in ("cms", "dynamic", "fourth sku", "/demo", "calendly", "launch", "live_pin"):
        hole = dict(good)
        hole["refuse"] = [item for item in good["refuse"] if missing not in item.lower()]
        with pytest.raises(IntegrityError):
            catmod._validate_managed_face(hole)
