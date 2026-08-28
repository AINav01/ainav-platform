"""Publish AINAV.Institute to Azure Static Web Apps. Host only.

Creates Microsoft.Web/staticSites/ainav-institute in ainav-inc and
uploads institute/. Never writes SoR. Never LIVE_PIN_OK. Never binds
ainav.institute. West Europe is refused.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from ainav.errors import LivePinError
from ainav.microsoft.health import ARM_SCOPE, _subscription_id, _token, entra_configured
from ainav.microsoft.host_bind import RESOURCE_GROUP, _fail, _request

SITE_NAME = "ainav-institute"
SWA_LOCATION = "eastus2"
BLOCKED_LOCATIONS = frozenset({"westeurope", "west europe"})
APP_LOCATION = Path("institute")


def publish_institute(*, custom_domain: str | None = None, location: str = SWA_LOCATION) -> dict[str, Any]:
    """PUT the Static Web App and deploy institute/. Not a live pin."""
    if custom_domain:
        raise LivePinError(
            "ainav.institute custom domain is not claimed. Publish the Azure hostname only.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )
    if location.lower().replace(" ", "") in BLOCKED_LOCATIONS:
        raise LivePinError(
            "West Europe is blocked by Azure Policy. Use eastus2.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )
    if not entra_configured():
        return {
            "kind": "ainav.institute_publish.v1",
            "ok": False,
            "live": False,
            "live_pin_ok": False,
            "custom_domain_claimed": False,
            "wrote_sor": False,
            "reason": "missing_env",
            "missing": ["ENTRA_TENANT_ID", "ENTRA_CLIENT_ID", "ENTRA_CLIENT_SECRET"],
        }
    if not (APP_LOCATION / "index.html").is_file():
        return _denied("institute_files_missing", 0, "institute/index.html missing", "")
    arm = _token(ARM_SCOPE)
    if not arm.get("ok"):
        return _denied(str(arm.get("status")), int(arm.get("http") or 0), "", "")
    token = arm["token"]
    sub = os.environ.get("AZURE_SUBSCRIPTION_ID") or _subscription_id(token)
    if not sub:
        return _denied("no_azure_subscription_visible", 0, "", "")
    _request(
        "POST",
        f"https://management.azure.com/subscriptions/{sub}/providers/Microsoft.Web/register?api-version=2021-04-01",
        token,
    )
    url = (
        f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{RESOURCE_GROUP}"
        f"/providers/Microsoft.Web/staticSites/{SITE_NAME}?api-version=2023-01-01"
    )
    status, body = _request(
        "PUT",
        url,
        token,
        {
            "location": location,
            "sku": {"name": "Free", "tier": "Free"},
            "properties": {"allowConfigFileUpdates": True, "stagingEnvironmentPolicy": "Disabled"},
        },
    )
    if status not in {200, 201}:
        return _denied("static_site_denied", status, body, sub)
    site = _wait_site(url, token)
    hostname = ""
    if isinstance(site, dict):
        hostname = str((site.get("properties") or {}).get("defaultHostname") or "")
    public_url = f"https://{hostname}" if hostname else ""
    api_key = _deployment_token(sub, token)
    uploaded = False
    upload_detail = ""
    if api_key:
        uploaded, upload_detail = _swa_deploy(api_key)
    return {
        "kind": "ainav.institute_publish.v1",
        "ok": bool(hostname) and uploaded,
        "live": False,
        "live_pin_ok": False,
        "custom_domain_claimed": False,
        "wrote_sor": False,
        "subscription_id": sub,
        "resource_group": RESOURCE_GROUP,
        "site": SITE_NAME,
        "location": location,
        "hostname": hostname or None,
        "url": public_url or None,
        "uploaded": uploaded,
        "upload_detail": upload_detail[:240],
        "note": "Azure hostname only. ainav.institute is not bound. Not LIVE_PIN_OK.",
    }


def _wait_site(url: str, token: str) -> dict[str, Any]:
    last: dict[str, Any] = {}
    for _ in range(20):
        status, body = _request("GET", url, token)
        if status == 200 and isinstance(body, dict):
            last = body
            state = str((body.get("properties") or {}).get("provisioningState") or "")
            host = str((body.get("properties") or {}).get("defaultHostname") or "")
            if host and state.lower() in {"succeeded", "success", ""}:
                return body
        time.sleep(3)
    return last


def _deployment_token(sub: str, token: str) -> str:
    status, body = _request(
        "POST",
        (
            f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{RESOURCE_GROUP}"
            f"/providers/Microsoft.Web/staticSites/{SITE_NAME}/listSecrets?api-version=2023-01-01"
        ),
        token,
        {},
    )
    if status != 200 or not isinstance(body, dict):
        return ""
    props = body.get("properties") or body
    if isinstance(props, dict):
        return str(props.get("apiKey") or props.get("api_key") or "")
    return ""


def _swa_deploy(api_key: str) -> tuple[bool, str]:
    cmd = [
        "npx",
        "--yes",
        "@azure/static-web-apps-cli",
        "deploy",
        str(APP_LOCATION.resolve()),
        "--deployment-token",
        api_key,
        "--env",
        "production",
        "--no-use-keychain",
    ]
    try:
        out = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    text = (out.stdout or "") + "\n" + (out.stderr or "")
    return out.returncode == 0, text[-240:]


def _denied(reason: str, status: int, body: Any, sub: str) -> dict[str, Any]:
    fail = _fail(reason, status, body, sub)
    fail["kind"] = "ainav.institute_publish.v1"
    fail["custom_domain_claimed"] = False
    fail["uploaded"] = False
    fail["url"] = None
    return fail
