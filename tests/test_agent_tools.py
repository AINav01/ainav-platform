from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.microsoft.agent_tools import public_review, validate_agent_tools


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


def test_cli_agent_tools(capsys):
    from ainav.__main__ import main

    assert main(["agent-tools"]) == 0
    out = capsys.readouterr().out
    assert "workiq.user" in out
    assert "dataverse.mcp" in out
    assert "false" in out
