"""Next pin: process twin → Microsoft Business Central sandbox.

Intended OData envelope only. Never HTTP. Never production.
Not LIVE_PIN_OK. G14 stays open.
"""

from __future__ import annotations

from typing import Any

from ainav.errors import LivePinError, ProvisionError


SANDBOX_ENV = "bc.microsoft.sandbox"
PRODUCTION_STEMS = ("production", ".prod", "live")


def next_pin_spec() -> dict[str, Any]:
    from ainav.catalog import load_catalog

    return dict(load_catalog()["next_pin"])


def _is_production(target: str) -> bool:
    lowered = target.lower()
    return any(stem in lowered for stem in PRODUCTION_STEMS)


def refuse_production(target: str) -> None:
    if _is_production(target):
        raise LivePinError(
            f"production Business Central is refused: {target!r}. G14 is open.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )


def sandbox_envelope(action: dict[str, Any] | None = None) -> dict[str, Any]:
    """Intended BC sandbox OData request. sent=False without tenant credentials."""
    action = dict(action or {})
    target = str(action.get("sor_target") or SANDBOX_ENV)
    refuse_production(target)
    if target not in {SANDBOX_ENV, "bc.sandbox"}:
        if "sandbox" not in target.lower():
            raise ProvisionError(
                f"next pin refuses non-sandbox target {target!r}",
                reason_code="TWIN_TARGET",
            )
    from ainav.microsoft.connections import intended_request, spec

    item = spec("bc.premium")
    payload = dict(action.get("payload") or {})
    intended = intended_request(
        "bc.premium",
        method="POST",
        path="/{tenant}/sandbox/api/v2.0/companies({company})/journals({journal})/journalLines",
        payload=payload,
    )
    return {
        "kind": "ainav.next_pin.v1",
        "environment": SANDBOX_ENV,
        "connection": "bc.premium",
        "product": item["product"],
        "from": "bc.sandbox",
        "to": SANDBOX_ENV,
        "action_class": action.get("action_class") or "bc.general_journal.post",
        "live": False,
        "production": False,
        "sent": False,
        "live_pin_ok": False,
        "reason": "no tenant credentials in this tree",
        "intended": intended,
    }


def send_sandbox(envelope: dict[str, Any] | None = None) -> None:
    raise LivePinError(
        "Microsoft Business Central sandbox HTTP is not claimed. G14 is open.",
        reason_code="LIVE_PIN_NOT_CLAIMED",
    )


def pin_from_twin(local: Any) -> dict[str, Any]:
    """Advance from an in-process twin journal to the intended sandbox envelope."""
    journals = getattr(getattr(getattr(local, "bc", None), "twin", None), "journals", None)
    if not journals:
        raise ProvisionError("next pin requires a twin journal", reason_code="NEXT_PIN")
    last = journals[-1]
    envelope = sandbox_envelope(
        {
            "action_class": last.get("action_class"),
            "payload": last.get("payload") or {},
            "sor_target": SANDBOX_ENV,
        }
    )
    envelope["from_twin"] = True
    envelope["twin_request_id"] = last.get("request_id")
    envelope["action_hash"] = last.get("action_hash")
    return envelope
