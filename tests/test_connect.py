from __future__ import annotations

from ainav.microsoft.connections import COMPLEMENT_IDS, REQUIRED_IDS
from ainav.microsoft.health import entra_configured, stack_health


def test_stack_health_offline_never_claims_live():
    body = stack_health(probe=False)
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wrote_sor"] is False
    assert body["probed"] is False
    assert set(body["connections"]) == set(REQUIRED_IDS + COMPLEMENT_IDS)
    assert all(row["connected"] is False for row in body["connections"].values())
    assert all(row["sent"] is False for row in body["connections"].values())


def test_cli_connect_offline(monkeypatch, capsys):
    from ainav.__main__ import main

    monkeypatch.delenv("ENTRA_TENANT_ID", raising=False)
    monkeypatch.delenv("ENTRA_CLIENT_ID", raising=False)
    monkeypatch.delenv("ENTRA_CLIENT_SECRET", raising=False)
    assert entra_configured() is False
    assert main(["connect"]) == 0
    out = capsys.readouterr().out
    assert "live_pin_ok" in out
    assert "false" in out.lower()


def test_probe_graph_connected(monkeypatch):
    from ainav.microsoft import health

    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")

    def fake_token(scope: str):
        return {"ok": True, "status": "token", "has_token": True, "token": "lab"}

    def fake_get(url: str, token: str):
        if "organization" in url:
            return 200, {"value": [{"displayName": "AINav Inc", "verifiedDomains": [{"name": "ainav.institute"}]}]}
        if "subscribedSkus" in url:
            return 200, {"value": [{"skuPartNumber": "MICROSOFT_365_E7", "capabilityStatus": "Enabled"}]}
        if "users" in url:
            return 200, {"value": [{"id": "x"}]}
        if "subscriptions" in url:
            return 200, {"value": []}
        if "businesscentral" in url:
            return 401, "Authentication_InvalidCredentials"
        return 403, "denied"

    monkeypatch.setattr(health, "_token", fake_token)
    monkeypatch.setattr(health, "_get", fake_get)
    body = health.stack_health(probe=True)
    assert body["live_pin_ok"] is False
    assert "m365.e7" in body["connected"]
    assert "entra.id" in body["connected"]
    assert body["connections"]["azure.host"]["reason"] == "no_azure_subscription_visible"
    assert body["connections"]["bc.premium"]["reason"] == "bc_app_not_registered"
    assert body["connections"]["sales.enterprise"]["reason"] == "missing_env"
