from __future__ import annotations

import copy

import pytest

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog
from ainav.errors import LivePinError
from ainav.microsoft.institute_publish import publish_institute


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
