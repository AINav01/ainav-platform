"""Admit-gated Business Central sandbox journal. Never production. Never LIVE_PIN_OK."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from agent_gov.errors import EffectBlocked
from ainav.errors import LivePinError
from ainav.microsoft.health import BC_SCOPE, _entra, _token, entra_configured

OPERATING_COMPANY = "My Company"
JOURNAL_CODE = "DEFAULT"
DEBIT_ACCOUNT = "11100"
CREDIT_ACCOUNT = "22100"
AMOUNT = 250.00
DOCUMENT = "AINAV-L1"
MEMO = "AINav L1 sandbox wedge"


def _request(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8-sig")
            if not raw:
                return resp.status, {}
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw[:240]
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8-sig", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw[:240]


def _require_admit(grant: dict[str, Any]) -> dict[str, Any]:
    if grant.get("record_type") != "admit_ok":
        raise EffectBlocked("sandbox journal refuses grant that is not admit_ok")
    proposal = grant.get("proposal") or {}
    target = str(proposal.get("sor_target") or "bc.sandbox")
    if "production" in target.lower() or target.lower().endswith(".prod"):
        raise LivePinError(
            "sandbox journal refuses production. G14 is open.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )
    if "sandbox" not in target.lower():
        raise EffectBlocked(f"sandbox journal refuses target {target!r}", reason_code="TWIN_TARGET")
    return proposal


def pick_operating_company(companies: list[dict[str, Any]]) -> dict[str, Any] | None:
    named = [item for item in companies if item.get("name") == OPERATING_COMPANY]
    if named:
        return named[0]
    return companies[0] if companies else None


def post_named_company(grant: dict[str, Any]) -> dict[str, Any]:
    """POST balanced lines to My Company DEFAULT, then post the batch. Sandbox only."""
    proposal = _require_admit(grant)
    if not entra_configured():
        return {"ok": False, "sent": False, "reason": "missing_env", "live_pin_ok": False}
    tok = _token(BC_SCOPE)
    if not tok.get("ok"):
        return {"ok": False, "sent": False, "reason": tok.get("status"), "live_pin_ok": False}
    tenant = _entra()["tenant"]
    token = str(tok["token"])
    base = f"https://api.businesscentral.dynamics.com/v2.0/{tenant}/sandbox/api/v2.0"
    status, body = _request("GET", f"{base}/companies", token)
    if status != 200 or not isinstance(body, dict):
        return {"ok": False, "sent": False, "http": status, "reason": "companies_denied", "live_pin_ok": False}
    companies = [item for item in (body.get("value") or []) if isinstance(item, dict)]
    company = pick_operating_company(companies)
    if not company or not company.get("id"):
        return {"ok": False, "sent": False, "reason": "operating_company_missing", "live_pin_ok": False}
    cid = company["id"]
    status, journals = _request("GET", f"{base}/companies({cid})/journals", token)
    if status != 200 or not isinstance(journals, dict):
        return {"ok": False, "sent": False, "http": status, "reason": "journals_denied", "live_pin_ok": False}
    journal = next((item for item in (journals.get("value") or []) if item.get("code") == JOURNAL_CODE), None)
    if not journal:
        return {"ok": False, "sent": False, "reason": "default_journal_missing", "live_pin_ok": False}
    jid = journal["id"]
    lines_url = f"{base}/companies({cid})/journals({jid})/journalLines"
    payload = proposal.get("payload") or {}
    amount = float(payload.get("amount") or AMOUNT)
    memo = str(payload.get("memo") or MEMO)
    debit = str(payload.get("account") or DEBIT_ACCOUNT)
    credit = str(payload.get("balancing_account") or CREDIT_ACCOUNT)
    created: list[dict[str, Any]] = []
    for line_number, account, signed in ((10000, debit, amount), (20000, credit, -amount)):
        status, line = _request(
            "POST",
            lines_url,
            token,
            {
                "lineNumber": line_number,
                "accountType": "G/L Account",
                "accountNumber": account,
                "documentNumber": DOCUMENT,
                "description": memo,
                "amount": signed,
            },
        )
        if status not in {200, 201} or not isinstance(line, dict):
            return {
                "ok": False,
                "sent": False,
                "http": status,
                "reason": "journal_line_denied",
                "company": company.get("name"),
                "journal": JOURNAL_CODE,
                "error": line,
                "live": False,
                "live_pin_ok": False,
            }
        created.append({"id": line.get("id"), "accountNumber": account, "amount": signed, "http": status})
    post_status, posted = _request("POST", f"{base}/companies({cid})/journals({jid})/Microsoft.NAV.post", token, {})
    return {
        "ok": post_status in {200, 204},
        "sent": True,
        "posted": post_status in {200, 204},
        "post_http": post_status,
        "post_body": posted if post_status not in {200, 204} else None,
        "company": company.get("name"),
        "company_id": cid,
        "journal": JOURNAL_CODE,
        "journal_id": jid,
        "lines": created,
        "grant_id": grant.get("grant_id"),
        "request_id": grant.get("request_id"),
        "live": False,
        "production": False,
        "live_pin_ok": False,
    }
