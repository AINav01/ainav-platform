from __future__ import annotations

from pathlib import Path

from ainav.microsoft.connections import stack_json
from ainav.stack_walk import stack_walk, stack_walk_markdown


def test_stack_walk_is_catalog_honest_with_https_links():
    body = stack_walk()
    assert body["kind"] == "ainav.stack.walk.v1"
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["sku"] is False
    assert body["is_admit_plane"] is False
    assert body["release"] == "2.70.0"
    assert "failsafe" in (body.get("estate_equation") or "")
    assert "other uses" in (body.get("estate_equation") or "")
    assert "internal audit" in (body.get("audit_equation") or "")
    assert "room 2" in (body.get("audit_equation") or "").lower()
    ids = [item["id"] for item in body["path"]]
    assert ids == [
        "cloudflare.dns",
        "azure.host",
        "entra.id",
        "admit",
        "bc.premium",
        "sales.enterprise",
        "teams.enterprise",
        "graph.read",
        "agent_tools",
        "institute.launch",
    ]
    assert all(item["url"].startswith("https://") for item in body["path"])
    assert all(item["url"].startswith("https://") for item in body["complements"])
    assert body["path"][0]["url"] == "https://dash.cloudflare.com"
    assert "chodnett@ainav.institute" in body["path"][2]["in_tree"]
    assert "create users" in " ".join(body["cannot"])
    md = stack_walk_markdown()
    assert "stack walk" in md.lower()
    assert "dash.cloudflare.com" in md
    assert "businesscentral.dynamics.com" in md
    assert "admin.powerplatform.microsoft.com" in md
    assert "LIVE_PIN_OK" in md
    assert "Estate:" in md
    assert "same dashboard" in md.lower()
    assert "Audit:" in md
    assert "room 1" in md.lower()
    page = stack_json()
    assert page["walk"]["path"][0]["id"] == "cloudflare.dns"
    assert page["live"] is False


def test_cli_stack_and_generated_doc(capsys):
    from ainav.__main__ import main

    assert main(["stack"]) == 0
    out = capsys.readouterr().out
    assert "Privileged-write path" in out
    assert "Complements" in out
    on_disk = Path("docs/STACK_WALK.md").read_text(encoding="utf-8")
    assert on_disk == out
