"""Honest Microsoft stack health. Probe is read-only. Never LIVE_PIN_OK.

Uses the same Entra app for Graph / ARM / BC tokens when present.
Missing env, 401/403, and empty Azure subscriptions are reported as
blocked — not connected. No SoR writes. No Teams send.
"""

from __future__ import annotations

import base64
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
DISCO_SCOPE = "https://globaldisco.crm.dynamics.com/.default"
DISCO_URL = "https://globaldisco.crm.dynamics.com/api/discovery/v2.0/Instances"
ARM_SUBS_URL = "https://management.azure.com/subscriptions?api-version=2020-01-01"
BC_NEXT = (
    "Register the existing Entra app AINav Cloud Agent1 in the Business Central "
    "Sandbox (Microsoft Entra Applications). Do not create a new Entra app. "
    "https://businesscentral.dynamics.com/ainav.institute/Sandbox"
)
SALES_NEXT = (
    "Create a Dataverse / Dynamics 365 Sales environment, then set DATAVERSE_URL. "
    "https://admin.powerplatform.microsoft.com/environments"
)


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


def jwt_roles(token: str) -> list[str]:
    """Read-only roles claim. Never logs the token. Empty if not a JWT."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        body = json.loads(base64.urlsafe_b64decode(payload.encode()))
        return sorted(str(role) for role in (body.get("roles") or []) if role)
    except (IndexError, ValueError, json.JSONDecodeError):
        return []


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


def _blocked(
    connection_id: str,
    *,
    reason: str,
    missing: list[str] | None = None,
    http: int | None = None,
    next_step: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
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
    if next_step:
        out["next"] = next_step
    out.update(extra)
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


def _arm_subscriptions(token: str) -> tuple[int, list[dict[str, Any]]]:
    status, body = _get(ARM_SUBS_URL, token)
    if status != 200 or not isinstance(body, dict):
        return status, []
    return status, [item for item in (body.get("value") or []) if isinstance(item, dict)]


def _subscription_id(token: str) -> str | None:
    pinned = os.environ.get("AZURE_SUBSCRIPTION_ID") or ""
    if pinned:
        return pinned
    _status, subs = _arm_subscriptions(token)
    if len(subs) == 1:
        return subs[0].get("subscriptionId") or None
    return None


def probe_azure() -> dict[str, Any]:
    missing = _missing(["AZURE_SUBSCRIPTION_ID"])
    tok = _token(ARM_SCOPE)
    if not tok.get("ok"):
        return _blocked("azure.host", reason=str(tok.get("status")), missing=tok.get("missing"), http=tok.get("http"))
    status, subs = _arm_subscriptions(tok["token"])
    if status != 200:
        return _blocked("azure.host", reason="arm_denied", http=status)
    if not subs:
        return _blocked(
            "azure.host",
            reason="no_azure_subscription_visible",
            missing=missing or ["AZURE_SUBSCRIPTION_ID"],
        )
    return _connected(
        "azure.host",
        detail={
            "subscriptions": len(subs),
            "subscription_ids": [item.get("subscriptionId") for item in subs if item.get("subscriptionId")],
        },
    )


def probe_bc() -> dict[str, Any]:
    tenant = _entra()["tenant"]
    pinned = os.environ.get("BC_ENVIRONMENT") or ""
    names = [pinned] if pinned else ["sandbox", "production"]
    missing = _missing(["BC_ENVIRONMENT", "BC_COMPANY_ID"])
    tok = _token(BC_SCOPE)
    if not tok.get("ok"):
        return _blocked("bc.premium", reason=str(tok.get("status")), missing=tok.get("missing"), http=tok.get("http"))
    last_status = 0
    hits: dict[str, int] = {}
    for env in names:
        status, body = _get(
            f"https://api.businesscentral.dynamics.com/v2.0/{tenant}/{env}/api/v2.0/companies",
            tok["token"],
        )
        last_status = status
        hits[env] = status
        if status == 200 and isinstance(body, dict):
            from ainav.microsoft.bc_company import company_label, pick_operating_company

            rows = [item for item in (body.get("value") or []) if isinstance(item, dict)]
            names = [company_label(item) or str(item.get("name") or "") for item in rows]
            names = [name for name in names if name]
            operating = pick_operating_company(rows) or {}
            return _connected(
                "bc.premium",
                detail={
                    "environment": env,
                    "companies": len(rows),
                    "company_names": names,
                    "operating_company": company_label(operating) or operating.get("name") or None,
                    "operating_company_id": operating.get("id") or None,
                },
            )
    saw_401 = next((env for env in ("sandbox", "production") if hits.get(env) == 401), None)
    if saw_401 is None:
        saw_401 = next((env for env, status in hits.items() if status == 401), None)
    if saw_401:
        return _blocked(
            "bc.premium",
            reason="bc_app_not_registered",
            missing=missing,
            http=401,
            next_step=BC_NEXT,
            environment=saw_401,
            sandbox_missing=hits.get("sandbox") == 404,
            environments=hits,
            entra_scopes=jwt_roles(str(tok.get("token") or "")),
        )
    saw_404 = next((env for env, status in hits.items() if status == 404), None)
    if saw_404:
        return _blocked(
            "bc.premium",
            reason="bc_environment_missing",
            missing=missing,
            http=404,
            next_step=BC_NEXT,
            environment=saw_404,
            environments=hits,
        )
    return _blocked("bc.premium", reason="bc_denied", missing=missing, http=last_status or None, next_step=BC_NEXT)


def probe_sales() -> dict[str, Any]:
    missing = _missing(["DATAVERSE_URL"])
    url = os.environ.get("DATAVERSE_URL") or ""
    if url:
        tok = _token(f"{url.rstrip('/')}/.default")
        if tok.get("ok"):
            status, body = _get(f"{url.rstrip('/')}/api/data/v9.2/WhoAmI", tok["token"])
            if status == 200 and isinstance(body, dict):
                return _connected("sales.enterprise", detail={"url": url, "whoami": True})
            return _blocked("sales.enterprise", reason="dataverse_denied", missing=missing, http=status, next_step=SALES_NEXT)
        return _blocked(
            "sales.enterprise",
            reason=str(tok.get("status")),
            missing=tok.get("missing") or missing,
            http=tok.get("http"),
            next_step=SALES_NEXT,
        )
    tok = _token(DISCO_SCOPE)
    if not tok.get("ok"):
        return _blocked(
            "sales.enterprise",
            reason=str(tok.get("status")) if tok.get("status") != "missing_env" else "missing_env",
            missing=missing,
            http=tok.get("http"),
            next_step=SALES_NEXT,
        )
    status, body = _get(DISCO_URL, tok["token"])
    if status != 200 or not isinstance(body, dict):
        return _blocked(
            "sales.enterprise",
            reason="discovery_denied",
            missing=missing,
            http=status,
            next_step=SALES_NEXT,
        )
    instances = [item.get("Url") or item.get("ApiUrl") for item in (body.get("value") or []) if isinstance(item, dict)]
    instances = [item for item in instances if item]
    if instances:
        return _connected("sales.enterprise", detail={"instances": instances, "discovered": True})
    return _blocked(
        "sales.enterprise",
        reason="no_dataverse_instance",
        missing=missing,
        next_step=SALES_NEXT,
    )


def probe_teams(connection_id: str) -> dict[str, Any]:
    item = spec(connection_id)
    missing = _missing(list(item.get("env") or []))
    tok = _token(GRAPH_SCOPE)
    if not tok.get("ok"):
        return _blocked(
            connection_id,
            reason=str(tok.get("status")),
            missing=tok.get("missing") or missing,
            http=tok.get("http"),
        )
    status, body = _get("https://graph.microsoft.com/v1.0/teams?$top=5&$select=id,displayName", tok["token"])
    if status == 200 and isinstance(body, dict):
        teams = body.get("value") or []
        if missing:
            return _blocked(
                connection_id,
                reason="teams_unbound",
                missing=missing,
                team_count=len(teams),
                next_step="Set TEAMS_*_TEAM_ID and TEAMS_*_CHANNEL_ID. A chat is not a seat.",
            )
        return _blocked(connection_id, reason="graph_role_missing_Team_or_ChannelMessage")
    return _blocked(
        connection_id,
        reason="graph_role_missing_Team_or_ChannelMessage",
        missing=missing or None,
        http=status,
        next_step="Grant Team.ReadBasic.All on the existing Entra app, or set TEAMS_* IDs. Do not create a new app.",
    )


def _probe_arm_list(connection_id: str, *, path: str, empty_reason: str, next_step: str) -> dict[str, Any]:
    tok = _token(ARM_SCOPE)
    if not tok.get("ok"):
        return _blocked(connection_id, reason=str(tok.get("status")), missing=tok.get("missing"), http=tok.get("http"))
    sub = _subscription_id(tok["token"])
    if not sub:
        return _blocked(connection_id, reason="no_azure_subscription_visible", missing=["AZURE_SUBSCRIPTION_ID"])
    status, body = _get(
        f"https://management.azure.com/subscriptions/{sub}/providers/{path}",
        tok["token"],
    )
    if status != 200 or not isinstance(body, dict):
        return _blocked(connection_id, reason="arm_denied", http=status)
    items = body.get("value") or []
    if not items:
        return _blocked(connection_id, reason=empty_reason, next_step=next_step, subscription_id=sub)
    return _connected(connection_id, detail={"subscription_id": sub, "count": len(items)})


def probe_complement(connection_id: str) -> dict[str, Any] | None:
    if connection_id == "entra.id":
        return None
    if connection_id == "azure.policy":
        return _probe_arm_list(
            connection_id,
            path="Microsoft.Authorization/policyAssignments?api-version=2023-04-01",
            empty_reason="no_policy_assignment",
            next_step="Azure Policy is reachable; no assignment required to keep connecting.",
        )
    if connection_id == "azure.keyvault":
        return _probe_arm_list(
            connection_id,
            path="Microsoft.KeyVault/vaults?api-version=2022-07-01",
            empty_reason="no_key_vault",
            next_step="Create a Key Vault on the visible Azure subscription, or set AZURE_KEYVAULT_URI.",
        )
    if connection_id == "azure.monitor":
        return _probe_arm_list(
            connection_id,
            path="Microsoft.OperationalInsights/workspaces?api-version=2022-10-01",
            empty_reason="no_log_analytics_workspace",
            next_step="Create a Log Analytics workspace before Sentinel/Monitor can bind.",
        )
    if connection_id == "sentinel.siem":
        return _probe_arm_list(
            connection_id,
            path="Microsoft.OperationsManagement/solutions?api-version=2015-11-01-preview",
            empty_reason="no_sentinel",
            next_step="A Log Analytics workspace is not Sentinel. Do not mark LIVE_PIN_OK.",
        )
    if connection_id == "sharepoint.kit":
        tok = _token(GRAPH_SCOPE)
        if not tok.get("ok"):
            return _blocked(connection_id, reason=str(tok.get("status")), missing=tok.get("missing"), http=tok.get("http"))
        status, _body = _get("https://graph.microsoft.com/v1.0/sites?search=*&$top=1", tok["token"])
        if status == 200:
            missing = _missing(["SHAREPOINT_SITE_ID"])
            if missing:
                return _blocked(
                    connection_id,
                    reason="sharepoint_unbound",
                    missing=missing,
                    next_step="Set SHAREPOINT_SITE_ID for Acceptance Kit evidence. Not a seat.",
                )
            return _connected(connection_id, detail={"sites_read": True})
        return _blocked(
            connection_id,
            reason="graph_role_missing_Sites",
            missing=_missing(["SHAREPOINT_SITE_ID"]) or None,
            http=status,
            next_step="Grant Sites.Read.All on the existing Entra app, or set SHAREPOINT_SITE_ID.",
        )
    if connection_id == "defender.xdr":
        tok = _token(GRAPH_SCOPE)
        if not tok.get("ok"):
            return _blocked(connection_id, reason=str(tok.get("status")), missing=tok.get("missing"), http=tok.get("http"))
        status, _body = _get("https://graph.microsoft.com/v1.0/security/incidents?$top=1", tok["token"])
        if status == 200:
            return _connected(connection_id, detail={"incidents_read": True})
        return _blocked(
            connection_id,
            reason="graph_role_missing_SecurityIncident",
            http=status,
            next_step="Grant SecurityIncident.Read.All on the existing Entra app. Do not create a new app.",
        )
    if connection_id == "entra.pim":
        tok = _token(GRAPH_SCOPE)
        if not tok.get("ok"):
            return _blocked(connection_id, reason=str(tok.get("status")), missing=tok.get("missing"), http=tok.get("http"))
        status, _body = _get(
            "https://graph.microsoft.com/v1.0/roleManagement/directory/roleEligibilityScheduleInstances?$top=1",
            tok["token"],
        )
        if status == 200:
            return _connected(connection_id, detail={"eligibility_read": True})
        return _blocked(
            connection_id,
            reason="graph_role_missing_PIM",
            http=status,
            next_step="Grant RoleEligibilitySchedule.Read.Directory on the existing Entra app. A PIM activation is not dual admit.",
        )
    missing = _missing(list(spec(connection_id).get("env") or []))
    if missing:
        return _blocked(connection_id, reason="missing_env", missing=missing)
    return _blocked(connection_id, reason="graph_or_arm_role_missing")


def _next_steps(results: dict[str, Any]) -> list[str]:
    steps: list[str] = []
    bc_next = (results.get("bc.premium") or {}).get("next")
    if bc_next:
        steps.append(bc_next)
    for cid in REQUIRED_IDS + COMPLEMENT_IDS:
        if cid == "bc.premium":
            continue
        row = results.get(cid) or {}
        step = row.get("next")
        if step and step not in steps:
            steps.append(step)
    return steps


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
        "next": _next_steps(results),
        "connections": results,
        "note": "Graph read is not LIVE_PIN_OK and not a Business Central write.",
    }
