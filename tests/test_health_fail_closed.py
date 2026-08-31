from __future__ import annotations

import io
import json
import urllib.error

from ainav.microsoft import health


def _lab_env(monkeypatch) -> None:
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")


class _Resp:
    def __init__(self, body: str | bytes, status: int = 200):
        self.status = status
        self._body = body if isinstance(body, bytes) else body.encode()

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_Resp":
        return self

    def __exit__(self, *_exc) -> bool:
        return False


def _http_error(code: int, body: str) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "https://example.test",
        code,
        "denied",
        hdrs=None,
        fp=io.BytesIO(body.encode()),
    )


def test_token_ok_and_http_denied(monkeypatch):
    _lab_env(monkeypatch)

    def ok(req, timeout=20):
        return _Resp(json.dumps({"access_token": "lab"}))

    monkeypatch.setattr(health.urllib.request, "urlopen", ok)
    tok = health._token(health.GRAPH_SCOPE)
    assert tok["ok"] is True
    assert tok["token"] == "lab"

    def boom(req, timeout=20):
        raise _http_error(401, '{"error":"denied"}')

    monkeypatch.setattr(health.urllib.request, "urlopen", boom)
    denied = health._token(health.GRAPH_SCOPE)
    assert denied["ok"] is False
    assert denied["status"] == "token_denied"
    assert denied["http"] == 401


def test_get_json_plain_and_http_errors(monkeypatch):
    def dispatch(req, timeout=25):
        url = req.full_url
        if "json-ok" in url:
            return _Resp('{"ok": true}')
        if "plain-ok" in url:
            return _Resp("not-json")
        if "err-json" in url:
            raise _http_error(403, '{"error":{"code":"AccessDenied","message":"no"}}')
        if "err-str" in url:
            raise _http_error(403, '{"error":"plain"}')
        if "err-plain" in url:
            raise _http_error(500, "boom")
        raise _http_error(404, "{}")

    monkeypatch.setattr(health.urllib.request, "urlopen", dispatch)
    assert health._get("https://example.test/json-ok", "t") == (200, {"ok": True})
    status, body = health._get("https://example.test/plain-ok", "t")
    assert status == 200
    assert body == "not-json"
    status, body = health._get("https://example.test/err-json", "t")
    assert status == 403
    assert "AccessDenied" in body
    status, body = health._get("https://example.test/err-str", "t")
    assert status == 403
    assert body == "plain"
    status, body = health._get("https://example.test/err-plain", "t")
    assert status == 500
    assert body == "boom"


def test_subscription_id_uses_pinned_env(monkeypatch):
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "pinned-sub")
    assert health._subscription_id("unused") == "pinned-sub"


def test_probe_graph_org_denied(monkeypatch):
    _lab_env(monkeypatch)
    monkeypatch.setattr(health, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.setattr(health, "_get", lambda url, token: (403, "denied"))
    out = health.probe_graph()
    assert out["m365.e7"]["connected"] is False
    assert out["entra.id"]["connected"] is False
    assert out["m365.e7"]["reason"] == "graph_org_denied"
    assert out["m365.e7"]["live_pin_ok"] is False


def test_probe_graph_token_denied_keeps_connection_ids(monkeypatch):
    _lab_env(monkeypatch)
    monkeypatch.setattr(
        health,
        "_token",
        lambda scope: {"ok": False, "status": "token_denied", "http": 401},
    )
    out = health.probe_graph()
    assert set(out) == {"entra.id", "m365.e7"}
    assert out["m365.e7"]["reason"] == "token_denied"
    assert out["entra.id"]["reason"] == "token_denied"
    assert out["m365.e7"]["live_pin_ok"] is False


def test_probe_azure_token_and_arm_denied(monkeypatch):
    _lab_env(monkeypatch)
    monkeypatch.setattr(health, "_token", lambda scope: {"ok": False, "status": "token_denied", "http": 401})
    denied = health.probe_azure()
    assert denied["reason"] == "token_denied"
    assert denied["connected"] is False

    monkeypatch.setattr(health, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.setattr(health, "_get", lambda url, token: (403, "arm denied"))
    arm = health.probe_azure()
    assert arm["reason"] == "arm_denied"
    assert arm["http"] == 403


def test_probe_bc_token_404_and_denied(monkeypatch):
    _lab_env(monkeypatch)
    monkeypatch.setattr(health, "_token", lambda scope: {"ok": False, "status": "missing_env", "missing": ["ENTRA_TENANT_ID"]})
    missing = health.probe_bc()
    assert missing["reason"] == "missing_env"

    monkeypatch.setattr(health, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.setenv("BC_ENVIRONMENT", "sandbox")
    monkeypatch.setattr(health, "_get", lambda url, token: (404, "NoEnvironment"))
    gone = health.probe_bc()
    assert gone["reason"] == "bc_environment_missing"
    assert gone["http"] == 404

    monkeypatch.setattr(health, "_get", lambda url, token: (500, "down"))
    denied = health.probe_bc()
    assert denied["reason"] == "bc_denied"
    assert denied["http"] == 500


def test_probe_sales_denied_paths_and_discovery(monkeypatch):
    _lab_env(monkeypatch)
    monkeypatch.setenv("DATAVERSE_URL", "https://ainav.crm.dynamics.com")
    monkeypatch.setattr(health, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.setattr(health, "_get", lambda url, token: (403, "no"))
    denied = health.probe_sales()
    assert denied["reason"] == "dataverse_denied"
    assert denied["http"] == 403

    monkeypatch.setattr(health, "_token", lambda scope: {"ok": False, "status": "token_denied", "http": 401})
    tok = health.probe_sales()
    assert tok["reason"] == "token_denied"

    monkeypatch.delenv("DATAVERSE_URL", raising=False)
    monkeypatch.setattr(health, "_token", lambda scope: {"ok": False, "status": "missing_env", "missing": ["ENTRA_CLIENT_SECRET"]})
    disco_missing = health.probe_sales()
    assert disco_missing["reason"] == "missing_env"

    monkeypatch.setattr(health, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.setattr(
        health,
        "_get",
        lambda url, token: (200, {"value": [{"Url": "https://ainav.crm.dynamics.com"}]}),
    )
    found = health.probe_sales()
    assert found["connected"] is True
    assert found["discovered"] is True
    assert found["live_pin_ok"] is False


def test_probe_teams_token_denied_and_bound_read(monkeypatch):
    _lab_env(monkeypatch)
    monkeypatch.setattr(health, "_token", lambda scope: {"ok": False, "status": "token_denied", "http": 401})
    denied = health.probe_teams("teams.enterprise")
    assert denied["reason"] == "token_denied"

    monkeypatch.setenv("TEAMS_ENTERPRISE_TEAM_ID", "team-1")
    monkeypatch.setenv("TEAMS_ENTERPRISE_CHANNEL_ID", "chan-1")
    monkeypatch.setattr(health, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.setattr(
        health,
        "_get",
        lambda url, token: (200, {"value": [{"id": "team-1", "displayName": "Notify"}]}),
    )
    bound = health.probe_teams("teams.enterprise")
    assert bound["connected"] is True
    assert bound["teams_read"] is True
    assert bound["team_count"] == 1
    assert bound["live_pin_ok"] is False
    assert bound["sent"] is False

    monkeypatch.setattr(health, "_get", lambda url, token: (403, "missing Team.ReadBasic.All"))
    role = health.probe_teams("teams.enterprise")
    assert role["reason"] == "graph_role_missing_Team_or_ChannelMessage"
    assert role["http"] == 403


def test_probe_complement_fail_closed_and_sharepoint_bound(monkeypatch):
    _lab_env(monkeypatch)
    assert health.probe_complement("entra.id") is None

    monkeypatch.setattr(health, "_token", lambda scope: {"ok": False, "status": "token_denied", "http": 401})
    denied = health.probe_complement("azure.keyvault")
    assert denied["reason"] == "token_denied"

    monkeypatch.setattr(health, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.delenv("AZURE_SUBSCRIPTION_ID", raising=False)
    monkeypatch.setattr(health, "_arm_subscriptions", lambda token: (200, []))
    empty = health.probe_complement("azure.policy")
    assert empty["reason"] == "no_azure_subscription_visible"

    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    monkeypatch.setattr(health, "_get", lambda url, token: (403, "arm denied"))
    arm = health.probe_complement("azure.monitor")
    assert arm["reason"] == "arm_denied"

    monkeypatch.setattr(health, "_get", lambda url, token: (200, {"value": [{"id": "s1"}]}))
    monkeypatch.setenv("SHAREPOINT_SITE_ID", "site-1")
    sites = health.probe_complement("sharepoint.kit")
    assert sites["connected"] is True
    assert sites["sites_read"] is True
    assert sites["live_pin_ok"] is False

    monkeypatch.setattr(health, "_token", lambda scope: {"ok": False, "status": "token_denied", "http": 401})
    assert health.probe_complement("sharepoint.kit")["reason"] == "token_denied"
    assert health.probe_complement("defender.xdr")["reason"] == "token_denied"
    assert health.probe_complement("entra.pim")["reason"] == "token_denied"

    missing = health.probe_complement("teams.enterprise")
    assert missing["reason"] == "missing_env"
    monkeypatch.setenv("TEAMS_ENTERPRISE_TEAM_ID", "t")
    monkeypatch.setenv("TEAMS_ENTERPRISE_CHANNEL_ID", "c")
    leftover = health.probe_complement("teams.enterprise")
    assert leftover["reason"] == "graph_or_arm_role_missing"


def test_stack_health_graph_denied_does_not_pollute_results(monkeypatch):
    _lab_env(monkeypatch)
    monkeypatch.setattr(
        health,
        "_token",
        lambda scope: {"ok": False, "status": "token_denied", "http": 401},
    )
    body = health.stack_health(probe=True)
    assert "id" not in body["connections"]
    assert "m365.e7" in body["connections"]
    assert "entra.id" in body["connections"]
    assert body["connections"]["m365.e7"]["reason"] == "token_denied"
    assert body["live_pin_ok"] is False


def test_stack_health_defaults_to_probe_when_entra_configured(monkeypatch):
    _lab_env(monkeypatch)
    monkeypatch.setattr(health, "probe_graph", lambda: {"entra.id": {"connected": True}, "m365.e7": {"connected": True}})
    monkeypatch.setattr(health, "probe_azure", lambda: {"id": "azure.host", "connected": False})
    monkeypatch.setattr(health, "probe_bc", lambda: {"id": "bc.premium", "connected": False})
    monkeypatch.setattr(health, "probe_sales", lambda: {"id": "sales.enterprise", "connected": False})
    monkeypatch.setattr(health, "probe_teams", lambda cid: {"id": cid, "connected": False})
    monkeypatch.setattr(health, "probe_complement", lambda cid: None if cid == "entra.id" else {"id": cid, "connected": False})
    body = health.stack_health()
    assert body["probed"] is True
    assert body["live_pin_ok"] is False
    assert body["wrote_sor"] is False
