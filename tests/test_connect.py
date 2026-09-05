from __future__ import annotations

import base64
import json

from ainav.microsoft.connections import COMPLEMENT_IDS, REQUIRED_IDS
from ainav.microsoft.health import entra_configured, jwt_roles, stack_health


def _lab_jwt(*roles: str) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"roles": list(roles)}).encode()).decode().rstrip("=")
    return f"lab.{payload}.sig"


def test_jwt_roles_reads_claim_without_logging_token():
    assert jwt_roles(_lab_jwt("API.ReadWrite.All", "Automation.ReadWrite.All")) == [
        "API.ReadWrite.All",
        "Automation.ReadWrite.All",
    ]
    assert jwt_roles("not-a-jwt") == []
    assert jwt_roles("") == []


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
        if "businesscentral" in scope:
            return {
                "ok": True,
                "status": "token",
                "has_token": True,
                "token": _lab_jwt("API.ReadWrite.All", "Automation.ReadWrite.All"),
            }
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
    assert body["connections"]["bc.premium"]["entra_scopes"] == [
        "API.ReadWrite.All",
        "Automation.ReadWrite.All",
    ]
    assert body["next"][0].startswith("Register the existing Entra app")
    assert body["connections"]["sales.enterprise"]["reason"] == "discovery_denied"
    assert body["wrote_sor"] is False


def test_probe_discovers_azure_policy_and_empty_sales(monkeypatch):
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
        if url.endswith("subscriptions?api-version=2020-01-01"):
            return 200, {"value": [{"subscriptionId": "sub-1", "displayName": "Azure subscription 1"}]}
        if "policyAssignments" in url:
            return 200, {"value": [{"name": "sys.blockwesteurope"}]}
        if "Microsoft.KeyVault/vaults" in url:
            return 200, {"value": []}
        if "Microsoft.OperationalInsights/workspaces" in url:
            return 200, {"value": []}
        if "Microsoft.OperationsManagement/solutions" in url:
            return 200, {"value": []}
        if "businesscentral" in url and "/production/" in url:
            return 401, "Authentication_InvalidCredentials"
        if "businesscentral" in url:
            return 404, "NoEnvironment"
        if "globaldisco" in url:
            return 200, {"value": []}
        if "teams" in url:
            return 403, "missing Team.ReadBasic.All"
        if "sites" in url:
            return 403, "accessDenied"
        if "security/incidents" in url:
            return 403, "missing SecurityIncident.Read.All"
        if "roleEligibilityScheduleInstances" in url:
            return 403, "missing PIM"
        return 403, "denied"

    monkeypatch.setattr(health, "_token", fake_token)
    monkeypatch.setattr(health, "_get", fake_get)
    body = health.stack_health(probe=True)
    assert body["live_pin_ok"] is False
    assert "azure.host" in body["connected"]
    assert "azure.policy" in body["connected"]
    assert body["connections"]["azure.host"]["subscription_ids"] == ["sub-1"]
    assert body["connections"]["bc.premium"]["reason"] == "bc_app_not_registered"
    assert body["connections"]["bc.premium"]["environment"] == "production"
    assert body["connections"]["bc.premium"]["sandbox_missing"] is True
    assert body["connections"]["bc.premium"]["environments"]["sandbox"] == 404
    assert body["next"][0].startswith("Register the existing Entra app")
    assert body["connections"]["sales.enterprise"]["reason"] == "no_dataverse_instance"
    assert body["connections"]["azure.keyvault"]["reason"] == "no_key_vault"
    assert body["connections"]["sentinel.siem"]["reason"] == "no_sentinel"
    assert "Register the existing Entra app" in body["connections"]["bc.premium"]["next"]
    assert body["wrote_sor"] is False


def test_probe_sales_whoami_and_bc_companies(monkeypatch):
    from ainav.microsoft import health

    monkeypatch.setenv("ENTRA_TENANT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_CLIENT_ID", "00000000-0000-0000-0000-000000000002")
    monkeypatch.setenv("ENTRA_CLIENT_SECRET", "lab-secret")
    monkeypatch.setenv("DATAVERSE_URL", "https://ainav.crm.dynamics.com")
    monkeypatch.setenv("BC_ENVIRONMENT", "sandbox")

    def fake_token(scope: str):
        return {"ok": True, "status": "token", "has_token": True, "token": "lab"}

    def fake_get(url: str, token: str):
        if "organization" in url:
            return 200, {"value": [{"displayName": "AINav Inc", "verifiedDomains": []}]}
        if "subscribedSkus" in url:
            return 200, {"value": []}
        if "users" in url:
            return 200, {"value": []}
        if "subscriptions?" in url:
            return 200, {"value": [{"subscriptionId": "sub-1"}]}
        if "businesscentral" in url:
            return 200, {"value": [{"id": "co-1", "name": "CRONUS", "displayName": "CRONUS"}]}
        if "WhoAmI" in url:
            return 200, {"UserId": "u1"}
        if "policyAssignments" in url:
            return 200, {"value": [{"name": "p1"}]}
        if "vaults" in url or "workspaces" in url or "solutions" in url:
            return 200, {"value": [{"name": "lab"}]}
        if "teams" in url:
            return 200, {"value": [{"id": "t1", "displayName": "Notify"}]}
        if "sites" in url:
            return 200, {"value": [{"id": "s1"}]}
        if "security/incidents" in url:
            return 200, {"value": []}
        if "roleEligibilityScheduleInstances" in url:
            return 200, {"value": []}
        return 403, "denied"

    monkeypatch.setattr(health, "_token", fake_token)
    monkeypatch.setattr(health, "_get", fake_get)
    body = health.stack_health(probe=True)
    assert body["live_pin_ok"] is False
    assert body["connections"]["bc.premium"]["connected"] is True
    assert body["connections"]["bc.premium"]["companies"] == 1
    assert body["connections"]["bc.premium"]["company_names"] == ["CRONUS"]
    assert body["connections"]["bc.premium"]["operating_company"] == "CRONUS"
    assert body["connections"]["sales.enterprise"]["connected"] is True
    assert body["connections"]["sales.enterprise"]["whoami"] is True
    assert body["connections"]["azure.keyvault"]["connected"] is True
    assert body["connections"]["teams.enterprise"]["reason"] == "teams_unbound"
    assert body["connections"]["sharepoint.kit"]["reason"] == "sharepoint_unbound"
    assert "defender.xdr" in body["connected"]
    assert "entra.pim" in body["connected"]
