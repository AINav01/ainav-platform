"""Company narrative on #about stays a story, not an invented firm."""

from __future__ import annotations

from pathlib import Path

from ainav.face_kit import public_llms, public_search


def test_about_is_the_company_story():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    about = html[html.index('id="about"') : html.index('id="opportunity"')]
    assert 'id="about-lede"' in about
    assert "human failsafe" in about
    assert "not the AI" in about
    assert "Two distinct humans bind one action hash" in about
    assert "Microsoft is not the product" in about
    assert "Three SKUs only" in about
    assert "Complements stay eight" in about
    assert "James Hodnett is sole owner" in about
    assert "chodnett@ainav.institute recorded" in about
    assert "Entra oid and click still open" in about
    assert "Recognized revenue is $0" in about
    assert "Named customers are 0" in about
    assert "Signed L1 is 0" in about
    assert "Not a running firm" in about
    assert "This is not a patent" in about
    assert "A 10/10+ quality check is not launch" in about
    assert "Not a named design partner" in about
    assert "Walk the write" in about
    assert "Walk the join" in about
    assert about.count('data-fact=') == 6
    assert "LIVE_PIN_OK" in about
    assert "named client we do not have" not in about.lower()
    assert "nvidia inception member" not in about.lower()
    assert "licensed as wired" not in about.lower()
    assert html.count("Owner book") == 1
    assert "#about {" in css
    assert "#about-lede" in css
    assert ".pages-facts.about-facts" in css
    assert html.index('id="product"') < html.index('id="about"') < html.index('id="opportunity"')


def test_about_is_searchable_and_named_for_machines():
    llms = public_llms().lower()
    assert "about ainav sits on #about" in llms
    assert "failsafe, not the ai" in llms
    assert "not a running firm" in llms
    search = public_search()
    about = next(item for item in search["records"] if item["id"] == "about")
    assert about["href"] == "index.html#about"
    assert "human failsafe" in about["text"].lower()
    assert "not a running firm" in about["text"].lower()
    assert "a 10/10+ quality check is not launch" in about["text"].lower()
    assert "live" not in about
