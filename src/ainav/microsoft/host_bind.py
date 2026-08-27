"""Write Azure host binds only. Never SoR. Never LIVE_PIN_OK.

Creates the catalog Azure host landing zone: resource group ainav-inc,
Key Vault, and a Log Analytics workspace. Does not deploy master,
Institute, Sentinel, or a Business Central journal.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from ainav.errors import LivePinError
from ainav.microsoft.health import ARM_SCOPE, GRAPH_SCOPE, _entra, _get, _subscription_id, _token, entra_configured

RESOURCE_GROUP = "ainav-inc"
WORKSPACE = "ainav-mothership"
SECRET_NAME = "ainav-connection"
LOCATION = "eastus"
PROVIDERS = (
    "Microsoft.KeyVault",
    "Microsoft.OperationalInsights",
    "Microsoft.Insights",
)


def _request(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode()
            if not raw:
                return resp.status, {}
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw[:240]
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw[:240]


def _vault_name(subscription_id: str) -> str:
    compact = subscription_id.replace("-", "")[:8]
    return f"ainav{compact}"


def _refuse_sor() -> None:
    raise LivePinError(
        "Host bind cannot write a client SoR. G14 live SoR is open.",
        reason_code="LIVE_PIN_NOT_CLAIMED",
    )


def bind_host(*, write_sor: bool = False, deploy_institute: bool = False) -> dict[str, Any]:
    """PUT Azure host resources. Idempotent. Never a live pin."""
    if write_sor:
        _refuse_sor()
    if deploy_institute:
        raise LivePinError(
            "Azure deploy of AINAV.Institute is not claimed. Website files exist in-repo only.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )
    if not entra_configured():
        return {
            "kind": "ainav.host_bind.v1",
            "ok": False,
            "live": False,
            "live_pin_ok": False,
            "wrote_sor": False,
            "reason": "missing_env",
            "missing": ["ENTRA_TENANT_ID", "ENTRA_CLIENT_ID", "ENTRA_CLIENT_SECRET"],
        }
    arm = _token(ARM_SCOPE)
    if not arm.get("ok"):
        return {
            "kind": "ainav.host_bind.v1",
            "ok": False,
            "live": False,
            "live_pin_ok": False,
            "wrote_sor": False,
            "reason": str(arm.get("status")),
            "http": arm.get("http"),
        }
    token = arm["token"]
    sub = os.environ.get("AZURE_SUBSCRIPTION_ID") or _subscription_id(token)
    if not sub:
        return {
            "kind": "ainav.host_bind.v1",
            "ok": False,
            "live": False,
            "live_pin_ok": False,
            "wrote_sor": False,
            "reason": "no_azure_subscription_visible",
        }
    tenant = _entra()["tenant"]
    vault = _vault_name(sub)
    principal = os.environ.get("ENTRA_OBJECT_ID") or _service_principal_object_id()
    created: list[str] = []
    for provider in PROVIDERS:
        _request(
            "POST",
            f"https://management.azure.com/subscriptions/{sub}/providers/{provider}/register?api-version=2021-04-01",
            token,
        )
    status, body = _request(
        "PUT",
        f"https://management.azure.com/subscriptions/{sub}/resourcegroups/{RESOURCE_GROUP}?api-version=2021-04-01",
        token,
        {"location": LOCATION},
    )
    if status not in {200, 201}:
        return _fail("resource_group_denied", status, body, sub)
    created.append("resource_group")
    status, body = _request(
        "PUT",
        (
            f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{RESOURCE_GROUP}"
            f"/providers/Microsoft.KeyVault/vaults/{vault}?api-version=2022-07-01"
        ),
        token,
        {
            "location": LOCATION,
            "properties": {
                "tenantId": tenant,
                "sku": {"family": "A", "name": "standard"},
                "enableRbacAuthorization": False,
                "enableSoftDelete": True,
                "publicNetworkAccess": "Enabled",
                "accessPolicies": (
                    [
                        {
                            "tenantId": tenant,
                            "objectId": principal,
                            "permissions": {"secrets": ["get", "list", "set"]},
                        }
                    ]
                    if principal
                    else []
                ),
            },
        },
    )
    if status not in {200, 201}:
        return _fail("key_vault_denied", status, body, sub)
    created.append("key_vault")
    _wait_vault(sub, vault, token)
    secret_ok = _put_connection_secret(vault)
    status, body = _request(
        "PUT",
        (
            f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{RESOURCE_GROUP}"
            f"/providers/Microsoft.OperationalInsights/workspaces/{WORKSPACE}?api-version=2022-10-01"
        ),
        token,
        {
            "location": LOCATION,
            "properties": {"sku": {"name": "PerGB2018"}, "retentionInDays": 30},
        },
    )
    if status not in {200, 201}:
        return _fail("workspace_denied", status, body, sub)
    created.append("log_analytics")
    return {
        "kind": "ainav.host_bind.v1",
        "ok": True,
        "live": False,
        "live_pin_ok": False,
        "wrote_sor": False,
        "deployed_institute": False,
        "subscription_id": sub,
        "location": LOCATION,
        "resource_group": RESOURCE_GROUP,
        "key_vault": vault,
        "key_vault_uri": f"https://{vault}.vault.azure.net/",
        "workspace": WORKSPACE,
        "secret": SECRET_NAME,
        "secret_written": secret_ok,
        "created": created,
        "note": "Azure host bind is not LIVE_PIN_OK and not a Business Central write.",
    }


def _fail(reason: str, status: int, body: Any, sub: str) -> dict[str, Any]:
    detail = body
    if isinstance(body, dict):
        err = body.get("error") or body
        if isinstance(err, dict):
            detail = f"{err.get('code')} {err.get('message') or ''}".strip()
    return {
        "kind": "ainav.host_bind.v1",
        "ok": False,
        "live": False,
        "live_pin_ok": False,
        "wrote_sor": False,
        "reason": reason,
        "http": status,
        "detail": str(detail)[:240],
        "subscription_id": sub,
    }


def _wait_vault(sub: str, vault: str, token: str) -> None:
    url = (
        f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{RESOURCE_GROUP}"
        f"/providers/Microsoft.KeyVault/vaults/{vault}?api-version=2022-07-01"
    )
    for _ in range(12):
        status, body = _request("GET", url, token)
        state = ""
        if isinstance(body, dict):
            state = str((body.get("properties") or {}).get("provisioningState") or "")
        if status == 200 and state.lower() in {"succeeded", "success", ""}:
            return
        time.sleep(2)


def _service_principal_object_id() -> str:
    pinned = os.environ.get("ENTRA_OBJECT_ID") or ""
    if pinned:
        return pinned
    tok = _token(GRAPH_SCOPE)
    if not tok.get("ok"):
        return ""
    client = _entra()["client"]
    filt = urllib.parse.quote(f"appId eq '{client}'")
    status, body = _get(
        f"https://graph.microsoft.com/v1.0/servicePrincipals?$filter={filt}&$select=id",
        tok["token"],
    )
    if status == 200 and isinstance(body, dict) and body.get("value"):
        return str(body["value"][0].get("id") or "")
    return ""


def _put_connection_secret(vault: str) -> bool:
    vault_tok = _token("https://vault.azure.net/.default")
    if not vault_tok.get("ok"):
        return False
    payload = {
        "value": json.dumps(
            {"kind": "connection-secret", "live": False, "live_pin_ok": False, "wrote_sor": False}
        )
    }
    for _ in range(8):
        status, _body = _request(
            "PUT",
            f"https://{vault}.vault.azure.net/secrets/{SECRET_NAME}?api-version=7.4",
            vault_tok["token"],
            payload,
        )
        if status in {200, 201}:
            return True
        time.sleep(3)
    return False
