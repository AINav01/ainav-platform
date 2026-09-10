"""Business, ops, and fulfillment stitch stay catalog-honest. 10/10 is not launch."""

from __future__ import annotations

from pathlib import Path

from ainav.catalog import load_catalog


def test_fulfillment_and_walks_stitch_without_launch():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    walk = html[html.index('id="qualify-walk"') : html.index("</ul>", html.index('id="qualify-walk"'))]
    catalog_walk = load_catalog()["expert_review"]["success"]["qualify"]["walk_away"]
    assert len(catalog_walk) == 20
    for item in catalog_walk:
        assert item in walk
    assert 'id="product-fulfill-hops"' in html
    assert 'id="product-walk"' in html
    assert 'id="path-join-walk"' in html
    assert 'id="firm-join-walk"' in html
    assert "The Job C plane runs in code" in html
    assert "The firm is not running" in html
    assert "Making all much better is not launch" in html
    assert "A 10/10 quality check is not launch" in html
    assert "A 10/10+ quality check is not launch" in html
    assert html.count("Owner book") == 1
    nav = html.split('aria-label="Primary"', 1)[1].split("</nav>", 1)[0]
    assert 'href="#buyer">The write</a>' in nav
    assert 'href="#twin">Proof day</a>' in nav
    assert 'href="#success">Bake-off</a>' in nav
    assert 'href="app.html">Dashboard</a>' in nav
    assert 'href="#missing">Owner</a>' in nav
    assert 'href="#packs"' not in nav
    assert 'href="#join-consider"' not in nav
    assert html.count("Walk the join") >= 8
    assert html.count("Walk the industry") >= 6
    assert html.count("Walk Agent Intent") >= 6
    for walk_id in (
        "whole-join-walk",
        "ten-join-walk",
        "close-join-walk",
        "prod-join-walk",
        "ops-join-walk",
        "fabric-join-walk",
        "operate-join-walk",
        "firm-ms-join-walk",
    ):
        strip = html[html.index(f'id="{walk_id}"') : html.index("</p>", html.index(f'id="{walk_id}"'))]
        assert "Walk the industry" in strip
        assert "Walk Agent Intent" in strip
    assert "#product-fulfill-hops" in css
    assert "#product-fulfill-hops { grid-template-columns: repeat(5" in css
    assert "#industry-area-hops { grid-template-columns: repeat(5" in css
    product = html[html.index('id="product"') : html.index('id="path"')]
    assert "L1 · Prove" in product
    assert "P-ADM · Keep" in product
    assert "U-DUAL · Deepen" in product
    assert "healthcare" not in product.lower()
