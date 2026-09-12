from __future__ import annotations

import pytest

from ainav.errors import LivePinError
from ainav.microsoft import host_bind


def test_bind_host_refuses_sor_and_institute():
    with pytest.raises(LivePinError) as exc:
        host_bind.bind_host(write_sor=True)
    assert exc.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    with pytest.raises(LivePinError) as exc2:
        host_bind.bind_host(deploy_institute=True)
    assert exc2.value.reason_code == "LIVE_PIN_NOT_CLAIMED"


def test_bind_host_missing_entra(monkeypatch):
    monkeypatch.delenv("ENTRA_TENANT_ID", raising=False)
    monkeypatch.delenv("ENTRA_CLIENT_ID", raising=False)
    monkeypatch.delenv("ENTRA_CLIENT_SECRET", raising=False)
    body = host_bind.bind_host()
    assert body["ok"] is False
    assert body["live_pin_ok"] is False
    assert body["wrote_sor"] is False
    assert body["reason"] == "missing_env"


def test_bind_host_puts_rg_vault_and_workspace(monkeypatch):
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    monkeypatch.setenv("ENTRA_OBJECT_ID", "sp-1")

    def fake_token(scope: str):
        return {"ok": True, "status": "token", "has_token": True, "token": "lab"}

    def fake_request(method: str, url: str, token: str, payload=None):
        if method == "PUT" and "secrets/ainav-connection" in url:
            return 200, {}
        if method == "GET" and "vaults/ainav" in url:
            return 200, {"properties": {"provisioningState": "Succeeded"}}
        if method == "PUT":
            return 201, {"id": url}
        if method == "POST":
            return 200, {}
        return 200, {}

    monkeypatch.setattr(host_bind, "_token", fake_token)
    monkeypatch.setattr(host_bind, "_request", fake_request)
    monkeypatch.setattr(host_bind.time, "sleep", lambda _s: None)
    body = host_bind.bind_host()
    assert body["ok"] is True
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["wrote_sor"] is False
    assert body["resource_group"] == "ainav-inc"
    assert body["workspace"] == "ainav-mothership"
    assert body["secret_written"] is True
    assert "key_vault" in body["created"]


def test_bind_host_arm_denied_and_resource_failures(monkeypatch):
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")

    monkeypatch.setattr(host_bind, "_token", lambda scope: {"ok": False, "status": "token_denied", "http": 401})
    denied = host_bind.bind_host()
    assert denied["ok"] is False
    assert denied["reason"] == "token_denied"

    monkeypatch.setattr(host_bind, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.setattr(host_bind, "_subscription_id", lambda token: None)
    empty = host_bind.bind_host()
    assert empty["reason"] == "no_azure_subscription_visible"

    monkeypatch.setattr(host_bind, "_subscription_id", lambda token: "sub-1")
    monkeypatch.setattr(host_bind, "_entra", lambda: {"tenant": "t", "client": "c", "secret": "s"})
    monkeypatch.setattr(
        host_bind,
        "_request",
        lambda method, url, token, payload=None: (403, {"error": {"code": "Denied", "message": "no"}}),
    )
    rg = host_bind.bind_host()
    assert rg["reason"] == "resource_group_denied"
    assert rg["live_pin_ok"] is False


def test_bind_host_vault_and_workspace_denied(monkeypatch):
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    monkeypatch.setattr(host_bind, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.setattr(host_bind, "_entra", lambda: {"tenant": "t", "client": "c", "secret": "s"})

    def vault_denied(method, url, token, payload=None):
        if "resourcegroups" in url and "providers" not in url:
            return 201, {}
        if "KeyVault/vaults" in url and method == "PUT":
            return 409, {"error": {"code": "Conflict", "message": "name"}}
        return 200, {}

    monkeypatch.setattr(host_bind, "_request", vault_denied)
    body = host_bind.bind_host()
    assert body["reason"] == "key_vault_denied"

    def workspace_denied(method, url, token, payload=None):
        if "OperationalInsights/workspaces" in url:
            return 400, "bad workspace"
        if method == "GET" and "vaults" in url:
            return 200, {"properties": {"provisioningState": "Succeeded"}}
        return 201, {}

    monkeypatch.setattr(host_bind, "_request", workspace_denied)
    monkeypatch.setattr(host_bind, "_put_connection_secret", lambda vault: False)
    monkeypatch.setattr(host_bind, "_service_principal_object_id", lambda: "")
    monkeypatch.setattr(host_bind.time, "sleep", lambda _s: None)
    body = host_bind.bind_host()
    assert body["reason"] == "workspace_denied"


def test_bind_host_keeps_existing_vault_when_model_locked(monkeypatch):
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    monkeypatch.setattr(host_bind, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.setattr(host_bind, "_entra", lambda: {"tenant": "t", "client": "c", "secret": "s"})
    monkeypatch.setattr(host_bind, "_service_principal_object_id", lambda: "sp-1")
    monkeypatch.setattr(host_bind, "_put_connection_secret", lambda vault: True)
    monkeypatch.setattr(host_bind.time, "sleep", lambda _s: None)

    def locked(method, url, token, payload=None):
        if "KeyVault/vaults" in url and method == "PUT":
            return 400, {"error": {"code": "InsufficientPermissions", "message": "permission model"}}
        if method == "GET" and "vaults" in url:
            return 200, {"properties": {"provisioningState": "Succeeded"}}
        return 201, {}

    monkeypatch.setattr(host_bind, "_request", locked)
    body = host_bind.bind_host()
    assert body["ok"] is True
    assert body["live_pin_ok"] is False
    assert "key_vault" in body["created"]


def test_request_and_secret_helpers(monkeypatch):
    class FakeResp:
        status = 200

        def read(self):
            return b'{"ok": true}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(host_bind.urllib.request, "urlopen", lambda req, timeout=45: FakeResp())
    status, body = host_bind._request("GET", "https://example.test", "tok")
    assert status == 200
    assert body["ok"] is True

    class Err(host_bind.urllib.error.HTTPError):
        def __init__(self):
            pass

        def read(self):
            return b'{"error":"no"}'

        code = 403

    def boom(req, timeout=45):
        raise Err()

    monkeypatch.setattr(host_bind.urllib.request, "urlopen", boom)
    status, body = host_bind._request("PUT", "https://example.test", "tok", {"a": 1})
    assert status == 403

    monkeypatch.setattr(host_bind, "_token", lambda scope: {"ok": False})
    assert host_bind._put_connection_secret("vault") is False
    monkeypatch.setattr(host_bind, "_token", lambda scope: {"ok": True, "token": "v"})
    monkeypatch.setattr(host_bind, "_request", lambda *a, **k: (500, {}))
    monkeypatch.setattr(host_bind.time, "sleep", lambda _s: None)
    assert host_bind._put_connection_secret("vault") is False

    monkeypatch.setattr(host_bind, "_token", lambda scope: {"ok": False})
    assert host_bind._service_principal_object_id() == ""
    monkeypatch.setenv("ENTRA_OBJECT_ID", "sp-9")
    assert host_bind._service_principal_object_id() == "sp-9"


def test_cli_bind_host(monkeypatch, capsys):
    from ainav.__main__ import main

    monkeypatch.setattr(
        "ainav.microsoft.host_bind.bind_host",
        lambda: {
            "ok": True,
            "live": False,
            "live_pin_ok": False,
            "wrote_sor": False,
        },
    )
    monkeypatch.setattr(
        "ainav.microsoft.health.stack_health",
        lambda probe=None: {"live_pin_ok": False, "connected": ["azure.host"]},
    )
    assert main(["connect", "--bind-host"]) == 0
    out = capsys.readouterr().out
    assert "live_pin_ok" in out
    assert "false" in out.lower()
