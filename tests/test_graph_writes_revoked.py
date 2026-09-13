from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import catalog_graph, load_catalog, validate_catalog


def test_graph_writes_revoked_is_owner_recorded():
    graph = catalog_graph()
    assert graph["status"] == "four_reads_granted_writes_revoked"
    assert not graph.get("error")
    assert graph["writes_revoked"] is True
    assert graph["writes_still_granted"] == []
    names = " ".join(graph["writes_revoked_names"])
    assert "Organization.ReadWrite.All" in names
    assert "User.ReadWrite.All" in names
    assert graph["four_reads_granted"] is True
    assert graph["graph_write_claimed"] is False
    assert graph["from_this_plane"] is False
    assert graph["live_pin_ok"] is False
    recorded = " ".join(graph["owner_recorded"]).lower()
    assert "owner revoked" in recorded
    assert "readwrite" in recorded
    note = graph["note"].lower()
    assert "owner-revoked" in note or "writes revoked" in note
    assert "not graph read closed" in note
    assert "not live_pin_ok" in note
    cat = load_catalog()
    owner = " ".join(cat["plane_interface"]["gaps"]["owner_only_open"]).lower()
    assert "graph write" not in owner
    assert "seat b" in owner
    assert cat["investor"]["executive_summary"]["opens"].lower().count("graph write") == 0
    assert "graph write" not in " ".join(cat["honest_missing"]).lower()
    assert "graph writes still granted" not in " ".join(cat["engineering"]["cannot_close"]).lower()
    assert any(
        "graph writes revoked" in item.lower() and "not graph write claimed" in item.lower()
        for item in cat["engineering"]["closed_in_tree"]
    )
    upgrades = {item["n"]: item for item in cat["expert_review"]["upgrades"]}
    assert len(cat["expert_review"]["upgrades"]) == 98
    assert upgrades[3]["who"] == "owner"
    assert upgrades[3]["done"] is True
    assert upgrades[3]["marks_live_pin"] is False
    blob = f"{upgrades[3]['title']} {upgrades[3]['do']}".lower()
    assert "revoked" in blob
    assert "do not add write" in blob
    walk = next(item for item in cat["microsoft_stack"]["walk"]["path"] if item["id"] == "graph.read")
    assert walk["status"] == "four_reads_granted_writes_revoked"
    depts = {item["id"]: item for item in cat["organization"]["departments"]}
    assert "Graph Write" not in " ".join(depts["dept.people"]["blocked_by"])
    assert "Graph Write" not in " ".join(depts["dept.compliance"]["blocked_by"])
    assert cat["entity"]["release"] == "3.28.0"


def _reject(mutator):
    cat = copy.deepcopy(load_catalog())
    mutator(cat)
    with pytest.raises(IntegrityError):
        validate_catalog(cat)


def test_graph_writes_revoked_fail_closed():
    def status(cat):
        cat["microsoft_stack"]["graph"]["status"] = "four_reads_granted_writes_open"

    def error(cat):
        cat["microsoft_stack"]["graph"]["error"] = "graph_writes_still_granted"

    def drop_revoked(cat):
        cat["microsoft_stack"]["graph"]["writes_revoked"] = False

    def restore_writes(cat):
        cat["microsoft_stack"]["graph"]["writes_still_granted"] = [
            "Organization.ReadWrite.All Application"
        ]

    def drop_recorded(cat):
        cat["microsoft_stack"]["graph"]["owner_recorded"] = [
            item
            for item in cat["microsoft_stack"]["graph"]["owner_recorded"]
            if "owner revoked" not in item.lower()
        ]

    def walk_status(cat):
        for item in cat["microsoft_stack"]["walk"]["path"]:
            if item.get("id") == "graph.read":
                item["status"] = "four_reads_granted_writes_open"

    def reopen_owner(cat):
        cat["plane_interface"]["gaps"]["owner_only_open"].append("Graph Writes revoke")
        cat["plane_interface"]["gaps"]["owner_only_hrefs"]["Graph Writes revoke"] = "index.html#stack-walk"

    def reopen_opens(cat):
        cat["investor"]["executive_summary"]["opens"] = (
            "Named dual seats. Graph Writes revoke. US Dataverse. Institute launch."
        )

    def reopen_missing(cat):
        cat["honest_missing"].append("Graph Writes still Granted on the same Entra app")

    def reopen_cannot(cat):
        cat["engineering"]["cannot_close"].append("Graph Writes still Granted on the same Entra app")

    def drop_closed(cat):
        cat["engineering"]["closed_in_tree"] = [
            item for item in cat["engineering"]["closed_in_tree"] if "graph writes revoked" not in item.lower()
        ]

    def upgrade_open(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 3:
                item["done"] = False

    def upgrade_stems(cat):
        for item in cat["expert_review"]["upgrades"]:
            if item.get("n") == 3:
                item["do"] = "Four Reads are Granted. Not LIVE_PIN_OK."

    def claimed(cat):
        cat["microsoft_stack"]["graph"]["graph_write_claimed"] = True

    def plane(cat):
        cat["microsoft_stack"]["graph"]["from_this_plane"] = True

    def ungrant(cat):
        cat["microsoft_stack"]["graph"]["four_reads_granted"] = False

    def note_open(cat):
        cat["microsoft_stack"]["graph"]["note"] = (
            "Four Reads Granted. Not Graph Read closed. Not LIVE_PIN_OK."
        )

    for mutator in (
        status,
        error,
        drop_revoked,
        restore_writes,
        drop_recorded,
        walk_status,
        reopen_owner,
        reopen_opens,
        reopen_missing,
        reopen_cannot,
        drop_closed,
        upgrade_open,
        upgrade_stems,
        claimed,
        plane,
        ungrant,
        note_open,
    ):
        _reject(mutator)
