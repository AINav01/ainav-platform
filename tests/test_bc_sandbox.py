from __future__ import annotations

import pytest
from agent_gov.errors import EffectBlocked
from ainav.errors import LivePinError
from ainav.microsoft.bc_company import pick_operating_company
from ainav.microsoft.bc_sandbox import post_named_company


def test_pick_operating_company_prefers_ainav():
    picked = pick_operating_company(
        [
            {"id": "cronus", "name": "CRONUS USA, Inc."},
            {"id": "9b8d1202-be8f-f111-8327-7ced8db3712c", "name": "My Company", "displayName": "AINav"},
        ]
    )
    assert picked["displayName"] == "AINav"
    assert pick_operating_company(
        [
            {"id": "cronus", "name": "CRONUS USA, Inc."},
            {"id": "mine", "name": "My Company"},
        ]
    ) == {"id": "mine", "name": "My Company"}


def test_post_named_company_requires_admit_ok():
    with pytest.raises(EffectBlocked):
        post_named_company({"record_type": "effect_applied", "proposal": {"sor_target": "bc.sandbox"}})


def test_post_named_company_refuses_production():
    with pytest.raises(LivePinError):
        post_named_company(
            {
                "record_type": "admit_ok",
                "proposal": {"sor_target": "bc.production", "action_class": "bc.general_journal.post"},
            }
        )


def test_post_named_company_http_success(monkeypatch):
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    from ainav.microsoft import bc_sandbox

    monkeypatch.setattr(bc_sandbox, "_token", lambda scope: {"ok": True, "token": "lab"})

    def fake_request(method, url, token, payload=None):
        if url.endswith("/companies"):
            return 200, {"value": [{"id": "co-mine", "name": "My Company"}]}
        if url.endswith("/journals"):
            return 200, {"value": [{"id": "j-default", "code": "DEFAULT"}]}
        if method == "POST" and "journalLines" in url:
            return 201, {"id": "line-1"}
        if url.endswith("/Microsoft.NAV.post"):
            return 204, {}
        return 404, {}

    monkeypatch.setattr(bc_sandbox, "_request", fake_request)
    out = post_named_company(
        {
            "record_type": "admit_ok",
            "grant_id": "g1",
            "request_id": "r1",
            "proposal": {
                "sor_target": "bc.sandbox",
                "payload": {"account": "11100", "balancing_account": "22100", "amount": "250.00"},
            },
        }
    )
    assert out["ok"] is True
    assert out["sent"] is True
    assert out["posted"] is True
    assert out["live_pin_ok"] is False
    assert out["production"] is False
    assert out["company"] == "My Company"
    assert len(out["lines"]) == 2


def test_post_named_company_missing_env(monkeypatch):
    monkeypatch.delenv("ENTRA_TENANT_ID", raising=False)
    monkeypatch.delenv("ENTRA_CLIENT_ID", raising=False)
    monkeypatch.delenv("ENTRA_CLIENT_SECRET", raising=False)
    out = post_named_company({"record_type": "admit_ok", "proposal": {"sor_target": "bc.sandbox"}})
    assert out["ok"] is False
    assert out["sent"] is False
    assert out["reason"] == "missing_env"


def test_cli_sandbox_wedge(monkeypatch, capsys):
    from ainav.__main__ import main
    from ainav.microsoft import bc_sandbox, health

    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    monkeypatch.setattr(
        bc_sandbox,
        "post_named_company",
        lambda grant: {
            "ok": True,
            "sent": True,
            "posted": True,
            "company": "My Company",
            "live_pin_ok": False,
        },
    )
    monkeypatch.setattr(
        health,
        "stack_health",
        lambda probe=None: {"live": False, "live_pin_ok": False, "connected": ["bc.premium"]},
    )
    assert main(["connect", "--sandbox-wedge"]) == 0
    out = capsys.readouterr().out
    assert "ainav.sandbox_wedge.v1" in out
    assert "live_pin_ok" in out
