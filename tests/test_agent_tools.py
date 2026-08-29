from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.microsoft.agent_tools import public_review, steps_markdown, validate_agent_tools


def test_agent_tools_review_is_not_the_admit_plane():
    body = public_review()
    assert body["kind"] == "ainav.institute.agent_tools.v1"
    assert body["is_admit_plane"] is False
    assert body["is_sku"] is False
    assert body["is_connection"] is False
    assert body["cloud_agent_can_approve"] is False
    assert body["live"] is False
    assert "admin.cloud.microsoft" in body["admin_url"]
    assert "workiq.teams" in [item["id"] for item in body["leave_available"]]
    assert "dataverse.mcp" in [item["id"] for item in body["block_until_dual"]]
    assert "Agent 365" in body["never_as_admit"]
    notes = {item["id"]: item["note"] for item in body["leave_available"]}
    assert notes["workiq.user"] == "Seat object ids. Not a seat."
    assert notes["workiq.teams"] == "Notify. A chat is not a seat."
    assert notes["workiq.sharepoint"] == "Kit evidence. Not dual."
    assert notes["workiq.mail"] == "Notify only. A mailbox is not a seat."
    assert notes["mcp.management"] == "Governs tools. Cannot weaken Job C."
    assert body["owner_playbook"]["actor"] == "DayTradingMarkets"
    assert body["owner_playbook"]["cannot_be_done_by"] == "cursor.cloud_agent"
    assert body["owner_playbook"]["steps"][0]["url"] == "https://admin.microsoft.com"
    on_disk = json.loads(Path("institute/agent-tools.json").read_text(encoding="utf-8"))
    assert on_disk == body


def test_catalog_refuses_agent_tools_as_admit_plane():
    cat = copy.deepcopy(load_catalog())
    cat["microsoft_stack"]["agent_tools"]["is_admit_plane"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(cat)
    assert exc.value.reason_code == "MICROSOFT_PRODUCT"
    missing = copy.deepcopy(load_catalog())
    missing["microsoft_stack"].pop("agent_tools")
    with pytest.raises(IntegrityError):
        validate_agent_tools(missing)
    wrong = copy.deepcopy(load_catalog())
    wrong["microsoft_stack"]["agent_tools"]["leave_available"] = []
    with pytest.raises(IntegrityError) as wrong_exc:
        validate_agent_tools(wrong)
    assert wrong_exc.value.reason_code == "MICROSOFT_PRODUCT"
    actor = copy.deepcopy(load_catalog())
    actor["microsoft_stack"]["agent_tools"]["owner_playbook"]["actor"] = "cursor.cloud_agent"
    with pytest.raises(IntegrityError):
        validate_agent_tools(actor)
    operator = copy.deepcopy(load_catalog())
    operator["microsoft_stack"]["agent_tools"]["owner_playbook"]["cannot_be_done_by"] = "DayTradingMarkets"
    with pytest.raises(IntegrityError):
        validate_agent_tools(operator)
    steps = copy.deepcopy(load_catalog())
    steps["microsoft_stack"]["agent_tools"]["owner_playbook"]["steps"] = []
    with pytest.raises(IntegrityError):
        validate_agent_tools(steps)
    approve = copy.deepcopy(load_catalog())
    approve["microsoft_stack"]["agent_tools"]["cloud_agent_can_approve"] = True
    with pytest.raises(IntegrityError) as approve_exc:
        validate_agent_tools(approve)
    assert approve_exc.value.reason_code == "MICROSOFT_PRODUCT"


def test_cli_agent_tools(capsys):
    from ainav.__main__ import main

    assert main(["agent-tools"]) == 0
    out = capsys.readouterr().out
    assert "workiq.user" in out
    assert "dataverse.mcp" in out
    assert "false" in out
    assert main(["agent-tools", "--steps"]) == 0
    steps = capsys.readouterr().out
    assert "Leave Available — owner playbook" in steps
    assert "https://admin.microsoft.com" in steps
    assert "Work IQ User" in steps
    assert "Seat object ids. Not a seat." in steps
    assert "This Cloud Agent cannot click Unblock" in steps
    assert steps_markdown() == steps
