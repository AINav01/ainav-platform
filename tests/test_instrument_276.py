from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import catalog_graph, load_catalog, validate_catalog
from ainav.dashboard import public_dashboard


def test_release_is_276():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.76.0"
    assert any("2.76.0" in item and "service principal" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("2.75.0" in item and "full (strict)" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    dash = public_dashboard()
    assert dash["release"] == "2.76.0"


def test_graph_consent_is_recorded_not_granted():
    graph = catalog_graph()
    assert graph["kind"] == "ainav.graph.owner_consent.v1"
    assert graph["from_this_plane"] is False
    assert graph["live"] is False
    assert graph["live_pin_ok"] is False
    assert graph["four_reads_granted"] is False
    assert graph["graph_write_claimed"] is False
    assert graph["tenant_wide_grant_ok"] is False
    assert graph["status"] == "owner_consent_open"
    assert graph["error"] == "no_subscription_or_service_principal"
    remove = " ".join(graph["remove_before_grant"]).lower()
    assert "speech" in remove
    assert "key vault" in remove
    assert "readwrite" in remove
    reads = " ".join(graph["four_reads"])
    assert "Team.ReadBasic.All" in reads
    assert "SecurityIncident.Read.All" in reads
    assert any("service principal" in item.lower() for item in graph["owner_recorded"])
    gaps = load_catalog()["plane_interface"]["gaps"]
    owner = " ".join(gaps["owner_only_open"]).lower()
    assert "graph read" in owner
    assert "seat b" in owner
    assert any("leftover" in item.lower() and "service principal" in item.lower() for item in gaps["in_tree_closed"])


def test_upgrade_46_is_tree_done():
    cat = load_catalog()
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 46
    assert upgrades[46]["who"] == "tree"
    assert upgrades[46]["done"] is True
    assert upgrades[46]["marks_live_pin"] is False
    blob = f"{upgrades[46]['title']} {upgrades[46]['do']}".lower()
    assert "leftover" in blob
    assert "service principal" in blob


def test_sale_site_walk_names_leftover_apis():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "leftover Speech" in html
    assert "service principal" in html
    assert "2.76.0" in html
    assert "Organization.ReadWrite.All" in html


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_instrument_276_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.75.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.76.0" not in item
        ]

    def granted(cat):
        cat["microsoft_stack"]["graph"]["four_reads_granted"] = True

    def writes(cat):
        cat["microsoft_stack"]["graph"]["graph_write_claimed"] = True

    def grant_ok(cat):
        cat["microsoft_stack"]["graph"]["tenant_wide_grant_ok"] = True

    def plane(cat):
        cat["microsoft_stack"]["graph"]["from_this_plane"] = True

    def recorded(cat):
        cat["microsoft_stack"]["graph"]["owner_recorded"] = ["something else"]

    def walk_status(cat):
        for item in cat["microsoft_stack"]["walk"]["path"]:
            if item.get("id") == "graph.read":
                item["status"] = "granted"

    def drop_graph_open(cat):
        cat["plane_interface"]["gaps"]["owner_only_open"] = [
            item for item in cat["plane_interface"]["gaps"]["owner_only_open"] if "Graph Read" not in item
        ]

    def drop_closed(cat):
        cat["plane_interface"]["gaps"]["in_tree_closed"] = [
            item
            for item in cat["plane_interface"]["gaps"]["in_tree_closed"]
            if "service principal" not in item.lower()
        ]

    def well(cat):
        cat["expert_review"]["working_well"] = [
            item for item in cat["expert_review"]["working_well"] if "service principal" not in item.lower()
        ]

    def upgrade(cat):
        cat["expert_review"]["upgrades"] = [
            item for item in cat["expert_review"]["upgrades"] if item.get("n") != 46
        ]

    def kind(cat):
        cat["microsoft_stack"]["graph"]["kind"] = "ainav.graph.v0"

    def sku(cat):
        cat["microsoft_stack"]["graph"]["sku"] = True

    def live(cat):
        cat["microsoft_stack"]["graph"]["live"] = True

    def remove(cat):
        cat["microsoft_stack"]["graph"]["remove_before_grant"] = ["Organization.ReadWrite.All"]

    def reads(cat):
        cat["microsoft_stack"]["graph"]["four_reads"] = ["Team.ReadBasic.All"]

    def note(cat):
        cat["microsoft_stack"]["graph"]["note"] = "owner recorded a portal error"

    def walk_owner(cat):
        for item in cat["microsoft_stack"]["walk"]["path"]:
            if item.get("id") == "graph.read":
                item["owner"] = "Grant the four Reads."
                item["in_tree"] = "Health probes report 403."

    def improve(cat):
        cat["expert_review"]["improve"] = [
            item for item in cat["expert_review"]["improve"] if "leftover" not in item.lower()
        ]

    def interface(cat):
        cat["equations"]["interface"] = cat["equations"]["interface"].replace(" × graph owner consent", "")

    def pin(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 46:
                item["marks_live_pin"] = True

    for mutator in (
        release,
        closed,
        granted,
        writes,
        grant_ok,
        plane,
        recorded,
        walk_status,
        drop_graph_open,
        drop_closed,
        well,
        upgrade,
        kind,
        sku,
        live,
        remove,
        reads,
        note,
        walk_owner,
        improve,
        interface,
        pin,
    ):
        _reject(mutator)
