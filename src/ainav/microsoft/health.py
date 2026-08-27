"""Honest Microsoft stack health. Probe is read-only. Never LIVE_PIN_OK.

Uses the same Entra app for Graph / ARM / BC tokens when present.
Missing env, 401/403, and empty Azure subscriptions are reported as
blocked — not connected. No SoR writes. No Teams send.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from ainav.microsoft.connections import COMPLEMENT_IDS, REQUIRED_IDS, spec


GRAPH_SCOPE = "https://graph.microsoft.com/.default"
ARM_SCOPE = "https://management.azure.com/.default"
BC_SCOPE = "https://api.businesscentral.dynamics.com/.default"


def _entra() -> dict[str, str]:
    return {
        "tenant": os.environ.get("ENTRA_TENANT_ID") or "",
        "client": os.environ.get("ENTRA_CLIENT_ID") or "",
        "secret": os.environ.get("ENTRA_CLIENT_SECRET") or "",
    }


def entra_configured() -> bool:
    body = _entra()
    return bool(body["tenant"] and body["client"] and body["secret"])


def _missing(names: list[str]) -> list[str]:
    return [name for name in names if not os.environ.get(name)]


def _token(scope: str) -> dict[str, Any]:
    creds = _entra()
    if not entra_configured():
        return {"ok": False, "status": "missing_env", "missing": ["ENTRA_TENANT_ID", "ENTRA_CLIENT_ID", "ENTRA_CLIENT_SECRET"]}
    data = urllib.parse.urlencode(
        {
            "client_id": creds["client"],
            "client_secret": creds["secret"],
            "scope": scope,
            "grant_type": "client_credentials",
        }
    ).encode()
    url = f"https://login.microsoftonline.com/{creds['tenant']}/oauth2/v2.0/token"
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode())
        return {"ok": True, "status": "token", "has_token": bool(body.get("access_token")), "token": body.get("access_token")}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": "token_denied", "http": exc.code}


def _get(url: str, token: str) -> tuple[int, Any]:
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw[:240]
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            err = json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw[:240]
        payload = err.get("error") or err
        if isinstance(payload, dict):
            return exc.code, f"{payload.get('code')} {payload.get('message') or ''}".strip()
        return exc.code, str(payload)[:240]


def _blocked(connection_id: str, *, reason: str, missing: list[str] | None = None, http: int | None = None) -> dict[str, Any]:
    item = spec(connection_id)
    out = {
        "id": connection_id,
        "product": item["product"],
        "connected": False,
        "live": False,
        "live_pin_ok": False,
        "sent": False,
        "reason": reason,
        "live_gap": item["live_gap"],
    }
    if missing:
        out["missing"] = missing
    if http is not None:
        out["http"] = http
    return out


def _connected(connection_id: str, *, detail: dict[str, Any]) -> dict[str, Any]:
    item = spec(connection_id)
    body = {
        "id": connection_id,
        "product": item["product"],
        "connected": True,
        "live": False,
        "live_pin_ok": False,
        "sent": False,
        "read_only": True,
        "live_gap": item["live_gap"],
    }
    body.update(detail)
    return body


def probe_graph() -> dict[str, Any]:
    tok = _token(GRAPH_SCOPE)
    if not tok.get("ok"):
        return _blocked("m365.e7", reason=str(tok.get("status")), missing=tok.get("missing"), http=tok.get("http"))
    status, org = _get("https://graph.microsoft.com/v1.0/organization?$select=displayName,verifiedDomains", tok["token"])
    if status != 200 or not isinstance(org, dict):
        return _blocked("m365.e7", reason="graph_org_denied", http=status)
    first = (org.get("value") or [{}])[0]
    domains = [d.get("name") for d in (first.get("verifiedDomains") or []) if d.get("name")]
    users_status, _users = _get("https://graph.microsoft.com/v1.0/users?$top=1&$select=id", tok["token"])
    sku_status, skus = _get("https://graph.microsoft.com/v1.0/subscribedSkus?$select=skuPartNumber,capabilityStatus", tok["token"])
    licenses = []
    if sku_status == 200 and isinstance(skus, dict):
        licenses = [
            item.get("skuPartNumber")
            for item in skus.get("value") or []
            if item.get("capabilityStatus") == "Enabled"
        ]
    entra = _connected(
        "entra.id",
        detail={"tenant": first.get("displayName"), "domains": domains, "users_read": users_status == 200},
    )
    e7 = _connected(
        "m365.e7",
        detail={"tenant": first.get("displayName"), "domains": domains, "licenses": licenses},
    )
    return {"entra.id": entra, "m365.e7": e7}


def probe_azure() -> dict[str, Any]:
    missing = _missing(["AZURE_SUBSCRIPTION_ID"])
    tok = _token(ARM_SCOPE)
    if not tok.get("ok"):
        return _blocked("azure.host", reason=str(tok.get("status")), missing=tok.get("missing"), http=tok.get("http"))
    status, body = _get("https://management.azure.com/subscriptions?api-version=2020-01-01", tok["token"])
    count = len((body or {}).get("value") or []) if isinstance(body, dict) else 0
    if status != 200:
        return _blocked("azure.host", reason="arm_denied", http=status)
    if count == 0:
        return _blocked(
            "azure.host",
            reason="no_azure_subscription_visible",
            missing=missing or ["AZURE_SUBSCRIPTION_ID"],
        )
    return _connected("azure.host", detail={"subscriptions": count})


def probe_bc() -> dict[str, Any]:
    tenant = _entra()["tenant"]
    env = os.environ.get("BC_ENVIRONMENT") or "sandbox"
    missing = _missing(["BC_ENVIRONMENT", "BC_COMPANY_ID"])
    tok = _token(BC_SCOPE)
    if not tok.get("ok"):
        return _blocked("bc.premium", reason=str(tok.get("status")), missing=tok.get("missing"), http=tok.get("http"))
    status, body = _get(
        f"https://api.businesscentral.dynamics.com/v2.0/{tenant}/{env}/api/v2.0/companies",
        tok["token"],
    )
    if status == 200 and isinstance(body, dict):
        return _connected("bc.premium", detail={"environment": env, "companies": len(body.get("value") or [])})
    reason = "bc_denied"
    if status == 404:
        reason = "bc_environment_missing"
    elif status == 401:
        reason = "bc_app_not_registered"
    return _blocked("bc.premium", reason=reason, missing=missing, http=status)


def probe_sales() -> dict[str, Any]:
    missing = _missing(["DATAVERSE_URL"])
    return _blocked("sales.enterprise", reason="missing_env", missing=missing)


def probe_teams(connection_id: str) -> dict[str, Any]:
    item = spec(connection_id)
    missing = _missing(list(item.get("env") or []))
    if missing:
        return _blocked(connection_id, reason="missing_env", missing=missing)
    return _blocked(connection_id, reason="graph_role_missing_Team_or_ChannelMessage")


def probe_complement(connection_id: str) -> dict[str, Any]:
    item = spec(connection_id)
    missing = _missing(list(item.get("env") or []))
    if connection_id == "entra.id":
        return None  # filled by probe_graph
    if missing:
        return _blocked(connection_id, reason="missing_env", missing=missing)
    return _blocked(connection_id, reason="graph_or_arm_role_missing")


def stack_health(*, probe: bool | None = None) -> dict[str, Any]:
    """Read-only health. probe=False never leaves the process (gold)."""
    if probe is None:
        probe = entra_configured()
    results: dict[str, Any] = {}
    if not probe:
        for cid in REQUIRED_IDS + COMPLEMENT_IDS:
            missing = _missing(list(spec(cid).get("env") or []))
            results[cid] = _blocked(cid, reason="not_probed", missing=missing or None)
    else:
        results.update(probe_graph())
        results["azure.host"] = probe_azure()
        results["bc.premium"] = probe_bc()
        results["sales.enterprise"] = probe_sales()
        results["teams.enterprise"] = probe_teams("teams.enterprise")
        results["teams.premium"] = probe_teams("teams.premium")
        for cid in COMPLEMENT_IDS:
            if cid in results:
                continue
            item = probe_complement(cid)
            if item is not None:
                results[cid] = item
    connected = [cid for cid, row in results.items() if row.get("connected")]
    blocked = [cid for cid, row in results.items() if not row.get("connected")]
    return {
        "kind": "ainav.connect.v1",
        "live": False,
        "live_pin_ok": False,
        "sent": False,
        "wrote_sor": False,
        "probed": bool(probe),
        "connected": connected,
        "blocked": blocked,
        "connections": results,
        "note": "Graph read is not LIVE_PIN_OK and not a Business Central write.",
    }
