from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import catalog_graph, load_catalog, validate_catalog
from ainav.dashboard import public_dashboard


def test_release_is_277():
    cat = load_catalog()
    assert cat["entity"]["release"] == "2.77.0"
    assert any("2.77.0" in item and "four reads" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    assert any("2.76.0" in item and "service principal" in item.lower() for item in cat["engineering"]["closed_in_tree"])
    dash = public_dashboard()
    assert dash["release"] == "2.77.0"


def test_four_reads_granted_writes_still_open():
    graph = catalog_graph()
    assert graph["kind"] == "ainav.graph.owner_consent.v1"
    assert graph["from_this_plane"] is False
    assert graph["four_reads_granted"] is True
    assert graph["tenant_wide_grant_ok"] is True
    assert graph["graph_write_claimed"] is False
    assert graph["live_pin_ok"] is False
    assert graph["status"] == "four_reads_granted_writes_open"
    assert graph["error"] == "graph_writes_still_granted"
    writes = " ".join(graph["writes_still_granted"])
    assert "Organization.ReadWrite.All" in writes
    assert "User.ReadWrite.All" in writes
    assert any("successfully granted" in item.lower() for item in graph["owner_recorded"])
    gaps = load_catalog()["plane_interface"]["gaps"]
    owner = " ".join(gaps["owner_only_open"]).lower()
    assert "graph write" in owner
    assert "graph read" not in owner
    assert "seat b" in owner
    assert any("four reads" in item.lower() and "granted" in item.lower() for item in gaps["in_tree_closed"])


def test_upgrade_47_is_tree_done():
    cat = load_catalog()
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 47
    assert upgrades[47]["who"] == "tree"
    assert upgrades[47]["done"] is True
    assert upgrades[47]["marks_live_pin"] is False
    blob = f"{upgrades[47]['title']} {upgrades[47]['do']}".lower()
    assert "four reads" in blob
    assert "writes" in blob


def test_sale_site_walk_revokes_writes():
    html = Path("institute/index.html").read_text(encoding="utf-8")
    assert "Four Reads are Granted" in html
    assert "revokes the Writes" in html
    assert "2.77.0" in html
    assert "User.ReadWrite.All" in html


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_instrument_277_fail_closed():
    def release(cat):
        cat["entity"]["release"] = "2.76.0"

    def closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "2.77.0" not in item
        ]

    def ungrant(cat):
        cat["microsoft_stack"]["graph"]["four_reads_granted"] = False

    def writes(cat):
        cat["microsoft_stack"]["graph"]["graph_write_claimed"] = True

    def plane(cat):
        cat["microsoft_stack"]["graph"]["from_this_plane"] = True

    def status(cat):
        cat["microsoft_stack"]["graph"]["status"] = "owner_consent_open"

    def error(cat):
        cat["microsoft_stack"]["graph"]["error"] = "no_subscription_or_service_principal"

    def drop_writes(cat):
        cat["microsoft_stack"]["graph"]["writes_still_granted"] = []

    def recorded(cat):
        cat["microsoft_stack"]["graph"]["owner_recorded"] = [
            "Grant admin consent failed: leftover Speech has no service principal."
        ]

    def walk_status(cat):
        for item in cat["microsoft_stack"]["walk"]["path"]:
            if item.get("id") == "graph.read":
                item["status"] = "owner_consent_open"
                item["owner"] = "Grant the four Reads."
                item["in_tree"] = "Leftover Speech, Azure Service Management, and Key Vault."

    def drop_writes_open(cat):
        cat["plane_interface"]["gaps"]["owner_only_open"] = [
            item for item in cat["plane_interface"]["gaps"]["owner_only_open"] if "Graph Write" not in item
        ]

    def drop_closed(cat):
        cat["plane_interface"]["gaps"]["in_tree_closed"] = [
            item
            for item in cat["plane_interface"]["gaps"]["in_tree_closed"]
            if "four reads" not in item.lower()
        ]

    def well(cat):
        cat["expert_review"]["working_well"] = [
            item for item in cat["expert_review"]["working_well"] if "four reads" not in item.lower()
        ]

    def improve(cat):
        cat["expert_review"]["improve"] = [
            item for item in cat["expert_review"]["improve"] if "revoke" not in item.lower()
        ]

    def upgrade(cat):
        cat["expert_review"]["upgrades"] = [
            item for item in cat["expert_review"]["upgrades"] if item.get("n") != 47
        ]

    def pin(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 47:
                item["marks_live_pin"] = True

    def reopen_read(cat):
        cat["plane_interface"]["gaps"]["owner_only_open"].append("Graph Read")

    def drop_seat(cat):
        cat["plane_interface"]["gaps"]["owner_only_open"] = [
            item for item in cat["plane_interface"]["gaps"]["owner_only_open"] if "seat B" not in item
        ]

    def upgrade_stems(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 47:
                item["title"] = "Owner recorded Grant"
                item["do"] = "Record Grant succeeded. Not LIVE_PIN_OK."

    def upgrade_who(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 47:
                item["who"] = "owner"
                item["done"] = False

    def leftover_only(cat):
        cat["microsoft_stack"]["graph"]["owner_recorded"] = [
            "Grant admin consent failed: leftover Speech has no service principal."
        ]

    def note_closed(cat):
        cat["microsoft_stack"]["graph"]["note"] = "Four Reads Granted. Not LIVE_PIN_OK."

    for mutator in (
        release,
        closed,
        ungrant,
        writes,
        plane,
        status,
        error,
        drop_writes,
        recorded,
        walk_status,
        drop_writes_open,
        drop_closed,
        well,
        improve,
        upgrade,
        pin,
        reopen_read,
        drop_seat,
        upgrade_stems,
        upgrade_who,
        leftover_only,
        note_closed,
    ):
        _reject(mutator)
