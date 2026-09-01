from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.business import public_business_plane
from ainav.catalog import load_catalog, validate_catalog


def test_business_plane_is_catalog_list_not_a_forecast():
    body = public_business_plane()
    assert body["kind"] == "ainav.institute.business_plane.v1"
    assert body["cms"] is False
    assert body["sku"] is False
    assert body["priced_round"] is False
    assert body["forecast"] is False
    assert body["recognized_revenue"] == 0
    assert body["signed_l1"] == 0
    assert body["named_customers"] == 0
    assert body["walk_away_recorded"] is False
    assert body["live_pin_ok"] is False
    assert body["close"]["closed"] is False
    assert body["close"]["named_dual_seats"] is False
    assert body["seat_b"]["entra_oid"] is None
    assert body["seat_b"]["seat_clicked"] is False
    assert body["seat_b"]["number_two"] is True
    assert body["seat_b"]["all_aspects"] is False
    assert body["number_two"]["scope"] == "other_aspects"
    assert body["number_two"]["all_aspects"] is False
    assert body["number_two"]["officer"] is False
    assert body["number_two"]["seat_clicked"] is False
    assert body["year_one_all_three"]["min"] == 88000
    assert body["year_one_all_three"]["max"] == 135000
    assert body["year_one_all_three"]["forecast"] is False
    assert {item["id"] for item in body["bake_off"]["we_win"]} >= {
        "independence",
        "consume_once",
        "fail_closed",
        "counterparty",
    }
    assert any("Workflow User Groups" in item for item in body["qualify"]["walk_away"])
    blob = json.dumps(body).lower()
    assert "nvidia inception member" not in blob
    assert "mailto:" not in blob


def test_catalog_requires_business_workspace():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    missing["plane_interface"]["floor"]["public_face"]["app"]["workspaces"] = [
        item
        for item in missing["plane_interface"]["floor"]["public_face"]["app"]["workspaces"]
        if item.get("id") != "business"
    ]
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(missing)
    assert exc.value.reason_code == "CATALOG_PLANE"


def test_app_html_paints_the_business_plane():
    app = Path("institute/app.html").read_text(encoding="utf-8")
    js = Path("institute/app.js").read_text(encoding="utf-8")
    assert 'id="workspace-business"' in app
    assert "If-then catalog list" in app
    assert "Operating company. Close is open." in app
    assert "Number two" in app
    assert "not all aspects" in app.lower()
    assert "plane-business.json" in js
    assert "paintBusiness" in js
    assert "nvidia inception member" not in app.lower()
