from __future__ import annotations

import io

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


def test_post_named_company_token_denied(monkeypatch):
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    from ainav.microsoft import bc_sandbox

    monkeypatch.setattr(bc_sandbox, "_token", lambda scope: {"ok": False, "status": "token_denied"})
    out = post_named_company({"record_type": "admit_ok", "proposal": {"sor_target": "bc.sandbox"}})
    assert out["ok"] is False
    assert out["sent"] is False
    assert out["reason"] == "token_denied"
    assert out["live_pin_ok"] is False


def test_post_named_company_refuses_non_sandbox_target():
    with pytest.raises(EffectBlocked):
        post_named_company(
            {
                "record_type": "admit_ok",
                "proposal": {"sor_target": "bc.other"},
            }
        )


def test_post_named_company_fail_closed_http(monkeypatch):
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    from ainav.microsoft import bc_sandbox

    monkeypatch.setattr(bc_sandbox, "_token", lambda scope: {"ok": True, "token": "lab"})

    def companies_denied(method, url, token, payload=None):
        return 403, {"error": {"code": "Denied"}}

    monkeypatch.setattr(bc_sandbox, "_request", companies_denied)
    denied = post_named_company({"record_type": "admit_ok", "proposal": {"sor_target": "bc.sandbox"}})
    assert denied["reason"] == "companies_denied"
    assert denied["live_pin_ok"] is False

    def no_company(method, url, token, payload=None):
        return 200, {"value": []}

    monkeypatch.setattr(bc_sandbox, "_request", no_company)
    missing = post_named_company({"record_type": "admit_ok", "proposal": {"sor_target": "bc.sandbox"}})
    assert missing["reason"] == "operating_company_missing"

    def journals_denied(method, url, token, payload=None):
        if url.endswith("/companies"):
            return 200, {"value": [{"id": "co-mine", "name": "My Company"}]}
        return 403, {}

    monkeypatch.setattr(bc_sandbox, "_request", journals_denied)
    journals = post_named_company({"record_type": "admit_ok", "proposal": {"sor_target": "bc.sandbox"}})
    assert journals["reason"] == "journals_denied"

    def no_default(method, url, token, payload=None):
        if url.endswith("/companies"):
            return 200, {"value": [{"id": "co-mine", "name": "My Company"}]}
        if url.endswith("/journals"):
            return 200, {"value": [{"id": "j-other", "code": "OTHER"}]}
        return 404, {}

    monkeypatch.setattr(bc_sandbox, "_request", no_default)
    journal = post_named_company({"record_type": "admit_ok", "proposal": {"sor_target": "bc.sandbox"}})
    assert journal["reason"] == "default_journal_missing"

    def line_denied(method, url, token, payload=None):
        if url.endswith("/companies"):
            return 200, {"value": [{"id": "co-mine", "name": "My Company"}]}
        if url.endswith("/journals"):
            return 200, {"value": [{"id": "j-default", "code": "DEFAULT"}]}
        return 400, {"error": {"message": "line refused"}}

    monkeypatch.setattr(bc_sandbox, "_request", line_denied)
    line = post_named_company({"record_type": "admit_ok", "proposal": {"sor_target": "bc.sandbox"}})
    assert line["reason"] == "journal_line_denied"
    assert line["sent"] is False
    assert line["live_pin_ok"] is False


def test_sandbox_request_json_plain_and_http_errors(monkeypatch):
    import urllib.error
    from ainav.microsoft import bc_sandbox

    class Resp:
        def __init__(self, body: str, status: int = 200):
            self.status = status
            self._body = body.encode()

        def read(self) -> bytes:
            return self._body

        def __enter__(self):
            return self

        def __exit__(self, *_exc) -> bool:
            return False

    def dispatch(req, timeout=45):
        url = req.full_url
        if url.endswith("/empty"):
            return Resp("")
        if url.endswith("/json"):
            return Resp('{"ok": true}')
        if url.endswith("/plain"):
            return Resp("not-json")
        if url.endswith("/err-json"):
            raise urllib.error.HTTPError(
                url, 403, "denied", hdrs=None, fp=io.BytesIO(b'{"error":{"code":"Denied"}}')
            )
        raise urllib.error.HTTPError(url, 500, "down", hdrs=None, fp=io.BytesIO(b"boom"))

    monkeypatch.setattr(bc_sandbox.urllib.request, "urlopen", dispatch)
    assert bc_sandbox._request("GET", "https://example.test/empty", "t") == (200, {})
    assert bc_sandbox._request("POST", "https://example.test/json", "t", {"a": 1}) == (200, {"ok": True})
    status, body = bc_sandbox._request("GET", "https://example.test/plain", "t")
    assert status == 200
    assert body == "not-json"
    status, body = bc_sandbox._request("GET", "https://example.test/err-json", "t")
    assert status == 403
    assert body["error"]["code"] == "Denied"
    status, body = bc_sandbox._request("GET", "https://example.test/err-plain", "t")
    assert status == 500
    assert body == "boom"


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
