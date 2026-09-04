from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.errors import LivePinError
from ainav.microsoft.institute_publish import publish_institute, publish_twin


def test_publish_refuses_custom_domain_and_west_europe():
    with pytest.raises(LivePinError) as exc:
        publish_institute(custom_domain="ainav.institute")
    assert exc.value.reason_code == "LIVE_PIN_NOT_CLAIMED"
    with pytest.raises(LivePinError) as exc2:
        publish_institute(location="westeurope")
    assert exc2.value.reason_code == "LIVE_PIN_NOT_CLAIMED"


def test_publish_is_held_until_launch():
    body = publish_institute()
    assert body["ok"] is False
    assert body["reason"] == "launch_not_ready"
    assert body["uploaded"] is False
    assert body["custom_domain_claimed"] is False
    assert body["live_pin_ok"] is False
    assert body["launch"] is False


def test_publish_twin_skips_launch_hold_and_never_marks_launch(monkeypatch):
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish._token",
        lambda scope: {"ok": True, "token": "lab"},
    )

    def fake_request(method, url, token, payload=None):
        if method == "POST" and "listSecrets" in url:
            return 200, {"properties": {"apiKey": "tok"}}
        if method == "GET" and "staticSites" in url:
            return 200, {
                "properties": {
                    "provisioningState": "Succeeded",
                    "defaultHostname": "blue-river-010091a0f.7.azurestaticapps.net",
                }
            }
        return 201, {}

    monkeypatch.setattr("ainav.microsoft.institute_publish._request", fake_request)
    monkeypatch.setattr("ainav.microsoft.institute_publish._swa_deploy", lambda key: (True, "ok"))
    body = publish_twin()
    assert body["ok"] is True
    assert body["kind"] == "ainav.institute_twin_publish.v1"
    assert body["twin"] is True
    assert body["launch"] is False
    assert body["authorized_release"] is False
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["custom_domain_claimed"] is False
    assert body["uploaded"] is True
    assert "twin" in body["note"].lower()
    held = publish_institute()
    assert held["reason"] == "launch_not_ready"
    assert held["uploaded"] is False


def test_publish_missing_entra(monkeypatch):
    monkeypatch.setattr(
        "ainav.catalog.load_catalog",
        lambda: {"programs": {"website": {"launch_ready": True}}},
    )
    monkeypatch.delenv("ENTRA_TENANT_ID", raising=False)
    monkeypatch.delenv("ENTRA_CLIENT_ID", raising=False)
    monkeypatch.delenv("ENTRA_CLIENT_SECRET", raising=False)
    body = publish_institute()
    assert body["ok"] is False
    assert body["live_pin_ok"] is False
    assert body["custom_domain_claimed"] is False
    assert body["reason"] == "missing_env"


def test_publish_puts_swa_and_uploads(monkeypatch):
    monkeypatch.setattr(
        "ainav.catalog.load_catalog",
        lambda: {"programs": {"website": {"launch_ready": True}}},
    )
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish._token",
        lambda scope: {"ok": True, "token": "lab"},
    )

    def fake_request(method, url, token, payload=None):
        if method == "POST" and "listSecrets" in url:
            return 200, {"properties": {"apiKey": "tok"}}
        if method == "GET" and "staticSites" in url:
            return 200, {
                "properties": {
                    "provisioningState": "Succeeded",
                    "defaultHostname": "lab.azurestaticapps.net",
                }
            }
        return 201, {}

    monkeypatch.setattr("ainav.microsoft.institute_publish._request", fake_request)
    monkeypatch.setattr("ainav.microsoft.institute_publish._swa_deploy", lambda key: (True, "ok"))
    body = publish_institute()
    assert body["ok"] is True
    assert body["live"] is False
    assert body["live_pin_ok"] is False
    assert body["custom_domain_claimed"] is False
    assert body["url"] == "https://lab.azurestaticapps.net"
    assert body["uploaded"] is True


def test_catalog_records_azure_host_without_custom_domain():
    site = load_catalog()["programs"]["website"]
    assert site["public_deploy_claimed"] is False
    assert site["custom_domain_claimed"] is False
    assert site["launch_ready"] is False
    assert site["azure_url"].startswith("https://")
    claimed = copy.deepcopy(load_catalog())
    claimed["programs"]["website"]["custom_domain_claimed"] = True
    with pytest.raises(IntegrityError) as exc:
        validate_catalog(claimed)
    assert exc.value.reason_code == "PROGRAM_NOT_CLAIMED"
    launched = copy.deepcopy(load_catalog())
    launched["programs"]["website"]["launch_ready"] = True
    with pytest.raises(IntegrityError) as exc3:
        validate_catalog(launched)
    assert exc3.value.reason_code == "PROGRAM_NOT_CLAIMED"


def test_publish_fail_closed_after_launch(monkeypatch, tmp_path):
    from ainav.microsoft import institute_publish as pub

    monkeypatch.setattr(
        "ainav.catalog.load_catalog",
        lambda: {"programs": {"website": {"launch_ready": True}}},
    )
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")

    monkeypatch.setattr(pub, "APP_LOCATION", tmp_path)
    missing = publish_institute()
    assert missing["ok"] is False
    assert missing["reason"] == "institute_files_missing"
    assert missing["live_pin_ok"] is False
    assert missing["custom_domain_claimed"] is False

    (tmp_path / "index.html").write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(pub, "_token", lambda scope: {"ok": False, "status": "token_denied", "http": 401})
    denied = publish_institute()
    assert denied["reason"] == "token_denied"
    assert denied["ok"] is False

    monkeypatch.setattr(pub, "_token", lambda scope: {"ok": True, "token": "lab"})
    monkeypatch.delenv("AZURE_SUBSCRIPTION_ID", raising=False)
    monkeypatch.setattr(pub, "_subscription_id", lambda token: None)
    no_sub = publish_institute()
    assert no_sub["reason"] == "no_azure_subscription_visible"

    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    monkeypatch.setattr(pub, "_request", lambda method, url, token, payload=None: (400, {"error": {"code": "Denied", "message": "no"}}))
    site = publish_institute()
    assert site["reason"] == "static_site_denied"
    assert site["uploaded"] is False
    assert site["url"] is None


def test_publish_helpers_fail_closed(monkeypatch):
    from ainav.microsoft import institute_publish as pub

    monkeypatch.setattr(pub.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(pub, "_request", lambda method, url, token, payload=None: (200, {"properties": {"provisioningState": "Creating"}}))
    waiting = pub._wait_site("https://example.test/site", "lab")
    assert waiting["properties"]["provisioningState"] == "Creating"

    monkeypatch.setattr(pub, "_request", lambda method, url, token, payload=None: (404, "gone"))
    assert pub._deployment_token("sub-1", "lab") == ""

    monkeypatch.setattr(pub, "_request", lambda method, url, token, payload=None: (200, {"properties": {"apiKey": ""}}))
    assert pub._deployment_token("sub-1", "lab") == ""

    monkeypatch.setattr(pub, "_request", lambda method, url, token, payload=None: (200, "not-a-dict"))
    assert pub._deployment_token("sub-1", "lab") == ""

    def boom(*_args, **_kwargs):
        raise OSError("npx missing")

    monkeypatch.setattr(pub.subprocess, "run", boom)
    ok, detail = pub._swa_deploy("key")
    assert ok is False
    assert "npx missing" in detail

    class Result:
        returncode = 0
        stdout = "uploaded"
        stderr = ""

    monkeypatch.setattr(pub.subprocess, "run", lambda *args, **kwargs: Result())
    ok, detail = pub._swa_deploy("key")
    assert ok is True
    assert "uploaded" in detail


def test_publish_twin_hostname_without_token(monkeypatch):
    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    monkeypatch.setattr(
        "ainav.microsoft.institute_publish._token",
        lambda scope: {"ok": True, "token": "lab"},
    )

    def fake_request(method, url, token, payload=None):
        if method == "POST" and "listSecrets" in url:
            return 200, {"properties": "not-a-dict"}
        if method == "GET" and "staticSites" in url:
            return 200, {
                "properties": {
                    "provisioningState": "Succeeded",
                    "defaultHostname": "blue-river-010091a0f.7.azurestaticapps.net",
                }
            }
        return 201, {}

    monkeypatch.setattr("ainav.microsoft.institute_publish._request", fake_request)
    body = publish_twin()
    assert body["ok"] is False
    assert body["twin"] is True
    assert body["launch"] is False
    assert body["uploaded"] is False
    assert body["hostname"] == "blue-river-010091a0f.7.azurestaticapps.net"


def test_cli_publish_twin(monkeypatch, capsys):
    from ainav.__main__ import main

    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_twin",
        lambda: {
            "ok": True,
            "twin": True,
            "launch": False,
            "live": False,
            "live_pin_ok": False,
            "custom_domain_claimed": False,
            "url": "https://blue-river-010091a0f.7.azurestaticapps.net",
        },
    )
    monkeypatch.setattr(
        "ainav.microsoft.health.stack_health",
        lambda probe=None: {"live_pin_ok": False},
    )
    assert main(["connect", "--publish-twin"]) == 0
    out = capsys.readouterr().out
    assert "blue-river" in out
    assert "live_pin_ok" in out


def test_cli_publish_institute(monkeypatch, capsys):
    from ainav.__main__ import main

    monkeypatch.setattr(
        "ainav.microsoft.institute_publish.publish_institute",
        lambda: {
            "ok": True,
            "live": False,
            "live_pin_ok": False,
            "custom_domain_claimed": False,
            "url": "https://lab.azurestaticapps.net",
        },
    )
    monkeypatch.setattr(
        "ainav.microsoft.health.stack_health",
        lambda probe=None: {"live_pin_ok": False},
    )
    assert main(["connect", "--publish-institute"]) == 0
    out = capsys.readouterr().out
    assert "lab.azurestaticapps.net" in out
    assert "live_pin_ok" in out
