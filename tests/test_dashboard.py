from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.dashboard import (
    dashboard_html,
    dashboard_markdown,
    public_dashboard,
    write_dashboard,
)


def test_dashboard_is_honest_and_not_a_sku():
    body = public_dashboard()
    assert body["kind"] == "ainav.plane.interface.v1"
    assert body["sku"] is False
    assert body["live"] is False
    assert body["certified"] is False
    assert body["real_time_claimed"] is False
    assert body["forecast"] is False
    assert body["recorded"] is False
    assert body["invited"] == "Cynthia Hodnett"
    assert {item["id"] for item in body["levels"]} >= {
        "owner",
        "board",
        "seat_a",
        "seat_b",
        "remote",
        "agent",
    }
    assert body["access"]["same_plane"] is True
    assert body["access"]["second_remote_plane"] is False
    assert body["access"]["vpn_sku"] is False
    tiles = {item["id"]: item for item in body["tiles"]}
    assert tiles["recognized_revenue"]["value"] == "$0"
    assert tiles["named_customers"]["value"] == "0"
    assert tiles["signed_l1"]["value"] == "0"
    assert "claimed=false" in tiles["compliance_maps"]["value"]
    md = dashboard_markdown()
    assert "humans sit from the top" in md.lower()
    assert "not a sku" in md.lower()
    assert "$0" in md
    assert "same entra" in md.lower() or "same plane" in md.lower()
    html = dashboard_html()
    assert "Executive control-plane dashboard" in html
    assert "OPEN" in html
    path = write_dashboard()
    assert path.exists()
    assert Path("docs/CONTROL_PLANE.md").exists()


def test_plane_interface_validators_refuse_fiction():
    cat = load_catalog()
    missing = copy.deepcopy(cat)
    del missing["plane_interface"]
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(missing)
    assert exc.value.reason_code == "CATALOG_PLANE"
    live = copy.deepcopy(cat)
    live["plane_interface"]["live"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(live)
    sku = copy.deepcopy(cat)
    sku["plane_interface"]["sku"] = True
    with pytest.raises(IntegrityError) as sku_exc:
        validate_catalog(sku)
    assert sku_exc.value.reason_code == "CATALOG_SKU"
    vpn = copy.deepcopy(cat)
    vpn["plane_interface"]["access"]["vpn_sku"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(vpn)
    remote = copy.deepcopy(cat)
    remote["plane_interface"]["access"]["second_remote_plane"] = True
    with pytest.raises(IntegrityError):
        validate_catalog(remote)


def test_institute_control_plane_matches_catalog():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    js = Path("institute/site.js").read_text(encoding="utf-8")
    assert 'id="control-plane"' in html
    assert "control-plane.json" in js
    on_disk = json.loads(Path("institute/control-plane.json").read_text(encoding="utf-8"))
    assert on_disk == public_dashboard()
