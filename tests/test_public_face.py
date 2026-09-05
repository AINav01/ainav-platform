from __future__ import annotations

from pathlib import Path

from ainav.buyer import buyer_page
from ainav.catalog import load_catalog


def test_public_face_is_static_catalog_sale():
    cat = load_catalog()
    face = cat["plane_interface"]["floor"]["public_face"]
    assert face["sku"] is False
    assert face["live"] is False
    assert face["live_pin_ok"] is False
    assert face["launch"] is False
    assert face["cms"] is False
    assert face["application"] is True
    assert "static" in face["host"]
    assert "application" in face["thesis"].lower()
    assert face["app"]["cms"] is False
    assert face["app"]["href"] == "app.html"
    assert face["kit"]["cms"] is False
    assert face["kit"]["href"] == "kit.html"
    assert face["kit"]["auth_is_admit"] is False
    assert {item["id"] for item in face["app"]["workspaces"]} >= {"floor", "capital", "business", "programs"}
    assert face["primary"][3]["href"] == "app.html"
    assert [item["id"] for item in cat["skus"]] == ["L1", "P-ADM", "U-DUAL"]
    page = buyer_page()
    assert page["live"] is False
    assert page["live_pin_ok"] is False
    assert page["launch"] is False
    assert page["contact_email"] is None
    assert page["mailto"] is None
    assert [item["id"] for item in page["skus"]] == ["L1", "P-ADM", "U-DUAL"]
    assert page["public_face"]["primary"][2]["label"] == "Bake-off"
    html = Path("institute/index.html").read_text(encoding="utf-8")
    css = Path("institute/styles.css").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert "Owner book" in html
    assert 'class="hero-fold"' in html
    assert ".hero-fold" in css
    assert 'id="hero-write-rail"' in html
    assert 'class="write-rail"' in html
    assert 'data-step="seat_a"' in html
    assert 'data-step="seat_b"' in html
    assert 'data-step="hash"' in html
    assert 'data-step="write"' in html
    assert 'id="hero-rail-kicker"' in html
    assert 'data-lane="gate"' in html
    assert html.count('data-lane="copy"') >= 6
    assert ".write-rail" in css
    assert ".rail-kicker" in css
    assert 'data-lane="gate"' in css
    assert 'data-lane="copy"' in css
    assert 'setAttribute("data-lane", "gate")' in js
    assert 'setAttribute("data-lane", "copy")' in js
    assert "write_rail" in js
    assert "write rail" in face["thesis"].lower()
    dash_glance = cat["plane_interface"]["dashboard"]["first_glance"]
    assert [item["id"] for item in dash_glance["write_rail"]] == [
        "seat_a",
        "seat_b",
        "hash",
        "write",
    ]
    assert "one dashboard" in dash_glance["lede"].lower()
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    assert 'id="plane-write-rail"' in html
    assert 'id="app-write-rail"' in Path("institute/app.html").read_text(encoding="utf-8")
    assert 'id="plane-dash-lede"' in plane
    assert "app.html#floor" in plane
    assert "plane-write-rail" in js
    assert [item["id"] for item in page["first_glance"]["write_rail"]] == [
        "seat_a",
        "seat_b",
        "hash",
        "write",
    ]
    assert "gate" in page["first_glance"]["rail_kicker"].lower()
    assert face["cms"] is False
    assert html.count('href="#missing">Owner</a>') >= 2
    assert 'href="app.html">Dashboard</a>' in html
    assert "href=\"mailto:" not in html
    app = Path("institute/app.html").read_text(encoding="utf-8")
    js_app = Path("institute/app.js").read_text(encoding="utf-8")
    assert 'id="workspace-floor"' in app
    assert 'id="app-floor-board"' in app
    assert 'id="app-floor-attention"' in app
    assert 'id="app-floor-seats"' in app
    assert 'id="app-floor-offer"' in app
    assert 'id="app-floor-govern"' in app
    assert 'id="app-floor-assign"' in app
    assert 'id="app-floor-auth"' in app
    assert 'id="app-floor-mfa"' in app
    assert 'id="app-floor-legal"' in app
    assert 'id="app-floor-estate"' in app
    assert 'id="app-floor-estate-glance"' in app
    assert 'id="app-floor-audit"' in app
    assert 'id="app-floor-audit-glance"' in app
    assert 'id="app-floor-rooms12"' in app
    assert 'id="app-floor-regulated"' in app
    assert "paintRegulated" in js_app
    assert "paintRooms12" in js_app
    assert app.index('id="app-floor-estate"') < app.index('id="app-floor-audit"')
    assert app.index('id="app-floor-audit"') < app.index('id="app-floor-govern"')
    assert 'id="app-floor-failsafe"' in app
    assert 'id="app-floor-uses"' in app
    assert 'id="app-floor-maps"' in app
    assert app.index('id="app-floor-estate"') < app.index('id="app-floor-govern"')
    assert "paintUses" in js_app
    assert "paintOversee" in js_app
    assert "Wedge: " in js_app
    assert "app-floor-estate-glance" in js_app
    assert "AINav, Inc. disclaimers" in app
    assert "AI failsafe" in app
    assert "paintMaps" in js_app
    assert 'data-view="remote"' in app
    assert 'data-view="provision"' in app
    assert "paintAssignment" in js_app
    assert "paintMfa" in js_app
    assert "view_assignment" in js_app
    assert "Sit the plane" in app
    assert "Walk the full plane" in app
    assert 'data-walk="entire"' in app
    assert 'id="app-floor-inventory"' in app
    assert "paintInventory" in js_app
    assert "view_shows" in js_app
    assert "SECTION_ROOTS" in js_app
    assert "paintDutyHints" in js_app
    assert 'showGlance || id === "owner"' not in js_app
    assert app.index('id="app-write-rail"') < app.index('id="app-search"')
    assert app.count("Owner book") == 1
    assert 'data-view="client"' in app
    assert "paintFloor" in js_app
    assert "setView(initial, data)" in js_app
    assert "board.default_view || \"client\"" in js_app
    assert 'id="workspace-capital"' in app
    assert 'id="workspace-business"' in app
    assert 'id="workspace-programs"' in app
    assert "paintBusiness" in js_app
    assert "If-then catalog list" in app
    assert 'id="app-business-elevator-ten"' in app
    assert 'id="app-business-why-client"' in app
    assert 'id="app-capital-why-investor"' in app
    assert 'id="app-write-rail"' in app
    assert "Not a priced round" in app
    assert "Not LIVE_PIN_OK" in app
    assert "nvidia inception member" not in app.lower()
    assert "href=\"mailto:" not in app
    assert "control-plane.html" in app
    assert "workspaceFromHash" in js_app
    assert "paintCapital" in js_app
    assert "paintPrograms" in js_app
    assert ".app-shell" in css
    assert ".app-ladder" in css
    plane = Path("institute/control-plane.html").read_text(encoding="utf-8")
    assert plane.index("index.html#closed") < plane.index("index.html#missing")
    assert plane.index("index.html#missing") < plane.index("index.html#open")
    assert "app.html#floor" in plane
    assert "pointer" in plane.lower()
    assert "AINav, Inc. disclaimers" in Path("institute/app.html").read_text(encoding="utf-8")
