"""AINav, Inc. operating organization. Departments are not SKUs.

The map is complete out of the gate. That is not a claim that Sales,
Teams, Institute, legal, or programs are live — or that LIVE_PIN_OK is closed.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import ALLOWED_SKUS, load_catalog

REQUIRED_DEPT_IDS = (
    "dept.treasury",
    "dept.identity",
    "dept.sales",
    "dept.people",
    "dept.compliance",
    "dept.institute",
    "dept.legal",
    "dept.product",
    "dept.delivery",
    "dept.programs",
)
ALLOWED_DEPT_STATUS = frozenset(
    {
        "running_sandbox",
        "running_code",
        "licensed_not_wired",
        "in_repo_not_public",
        "azure_hosted_not_custom",
        "open_gap",
        "qualify_not_claimed",
    }
)
RUNNING_STATUSES = frozenset({"running_sandbox", "running_code"})
EXTRA_SYSTEMS = frozenset(
    {
        "repo.agent_gov",
        "repo.catalog",
        "repo.institute",
        "programs",
        "catalog.legal",
        "delivery",
    }
)


def _connection_systems() -> frozenset[str]:
    from ainav.microsoft.connections import COMPLEMENT_IDS, REQUIRED_IDS

    return frozenset(REQUIRED_IDS + COMPLEMENT_IDS)


def validate_organization(catalog: dict[str, Any]) -> None:
    body = catalog.get("organization")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing organization", reason_code="CATALOG_ORG")
    if body.get("sku") is True:
        raise IntegrityError("organization is not a SKU", reason_code="CATALOG_SKU")
    if body.get("all_wired_claimed") is True:
        raise IntegrityError("do not claim every department is wired", reason_code="ORG_NOT_WIRED")
    if body.get("live") is True or body.get("live_pin_ok") is True:
        raise IntegrityError("organization cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    if body.get("second_officer"):
        raise IntegrityError("do not invent a second officer", reason_code="ORG_SECOND_OFFICER")
    if body.get("incorporation_date"):
        raise IntegrityError("incorporation date is not stored in this tree", reason_code="ORG_INCORPORATION")
    contacts = body.get("contacts") or {}
    if contacts.get("second_unique_human") is True:
        raise IntegrityError("do not invent a second unique human", reason_code="ORG_SECOND_OFFICER")
    if contacts.get("developer") or contacts.get("business_executive"):
        raise IntegrityError("do not invent Inception contacts", reason_code="ORG_SECOND_OFFICER")
    invited = contacts.get("invited") or {}
    if invited.get("second_unique_human") is True:
        raise IntegrityError("mailbox is not the second unique human", reason_code="ORG_SECOND_OFFICER")
    if invited.get("equity") is True:
        raise IntegrityError("invited human is not a stockholder", reason_code="ORG_SECOND_OFFICER")
    if invited.get("officer") is True:
        raise IntegrityError("number two is not an officer", reason_code="ORG_SECOND_OFFICER")
    if invited.get("all_aspects") is True:
        raise IntegrityError("number two is other aspects, not all aspects", reason_code="ORG_SECOND_OFFICER")
    if invited.get("seat_clicked") is True:
        raise IntegrityError("do not invent a seat B click", reason_code="ORG_SECOND_OFFICER")
    if invited.get("entra_oid"):
        raise IntegrityError("do not invent an Entra object id", reason_code="ORG_SECOND_OFFICER")
    name = str(invited.get("name") or "").strip()
    if not name:
        raise IntegrityError("invited human name is required while invite is open", reason_code="CATALOG_ORG")
    email = str(invited.get("email") or "").strip().lower()
    if invited.get("recorded") is True:
        if invited.get("agreed") is not True:
            raise IntegrityError("recorded invite must be the owner-confirmed agreement", reason_code="ORG_SECOND_OFFICER")
        if name != "Cynthia Hodnett":
            raise IntegrityError("recorded invite name is Cynthia Hodnett", reason_code="ORG_SECOND_OFFICER")
        if email != "chodnett@ainav.institute":
            raise IntegrityError(
                "recorded invite must be the owner-sent institute mailbox",
                reason_code="ORG_SECOND_OFFICER",
            )
        if "gmail" in email or email.split("@")[0] in {"james", "jhodnett", "daytradingmarkets"}:
            raise IntegrityError("recorded invite cannot be an alias or Gmail", reason_code="ORG_SECOND_OFFICER")
        if invited.get("number_two") is not True:
            raise IntegrityError("recorded invite is number two", reason_code="ORG_SECOND_OFFICER")
        _validate_number_two(body.get("number_two"), name=name, email=email)
    else:
        if email:
            raise IntegrityError("do not invent an invited email", reason_code="ORG_SECOND_OFFICER")
        if invited.get("agreed") is True:
            raise IntegrityError("agreed invite must record the owner-sent mailbox", reason_code="ORG_SECOND_OFFICER")
    departments = body.get("departments") or []
    ids = [item.get("id") for item in departments]
    if ids != list(REQUIRED_DEPT_IDS):
        raise IntegrityError("organization departments must be the full-service set", reason_code="CATALOG_ORG")
    allowed_systems = _connection_systems() | EXTRA_SYSTEMS
    for item in departments:
        ident = item.get("id")
        if ident in ALLOWED_SKUS or item.get("sku"):
            raise IntegrityError(f"department {ident} is not a SKU", reason_code="CATALOG_SKU")
        if item.get("status") not in ALLOWED_DEPT_STATUS:
            raise IntegrityError(
                f"unknown department status {item.get('status')!r}",
                reason_code="CATALOG_ORG",
            )
        if item.get("production") is True:
            raise IntegrityError("department cannot claim production", reason_code="LIVE_PIN_NOT_CLAIMED")
        for system in item.get("systems") or []:
            if system not in allowed_systems:
                raise IntegrityError(f"unknown org system {system}", reason_code="CATALOG_ORG")


def _validate_number_two(body: Any, *, name: str, email: str) -> None:
    if not isinstance(body, dict):
        raise IntegrityError("number two must be catalog law", reason_code="ORG_SECOND_OFFICER")
    if body.get("sku") is True:
        raise IntegrityError("number two is not a SKU", reason_code="CATALOG_SKU")
    if str(body.get("name") or "") != name or str(body.get("mailbox") or "").lower() != email:
        raise IntegrityError("number two is the recorded invite", reason_code="ORG_SECOND_OFFICER")
    if str(body.get("role") or "") != "number_two" or str(body.get("scope") or "") != "other_aspects":
        raise IntegrityError("number two scope is other aspects", reason_code="ORG_SECOND_OFFICER")
    if body.get("all_aspects") is True:
        raise IntegrityError("number two is other aspects, not all aspects", reason_code="ORG_SECOND_OFFICER")
    if body.get("officer") is True or body.get("second_officer") is True or body.get("equity") is True:
        raise IntegrityError("number two is not an officer or stockholder", reason_code="ORG_SECOND_OFFICER")
    if body.get("seated") is True or body.get("seat_clicked") is True or body.get("entra_oid"):
        raise IntegrityError("number two is not a click", reason_code="ORG_SECOND_OFFICER")
    if body.get("second_unique_human") is True:
        raise IntegrityError("mailbox is not the second unique human", reason_code="ORG_SECOND_OFFICER")
    note = str(body.get("note") or "").lower()
    if "other aspects" not in note or "not all aspects" not in note:
        raise IntegrityError("number two note must keep other aspects, not all aspects", reason_code="ORG_SECOND_OFFICER")
    if "not an officer" not in note or "not a click" not in note:
        raise IntegrityError("number two note must keep not an officer and not a click", reason_code="ORG_SECOND_OFFICER")
    manages = " ".join(str(item).lower() for item in body.get("manages") or [])
    cannot = " ".join(str(item).lower() for item in body.get("cannot") or [])
    if "walk away" not in manages or "seat b" not in manages:
        raise IntegrityError("number two manages seat B and the walk-away", reason_code="ORG_SECOND_OFFICER")
    if "all aspects" not in cannot or "officer" not in cannot or "live_pin_ok" not in cannot:
        raise IntegrityError("number two cannot list must keep all aspects, officer, and LIVE_PIN_OK", reason_code="ORG_SECOND_OFFICER")


def organization() -> dict[str, Any]:
    return dict(load_catalog()["organization"])


def human_gates() -> list[str]:
    gates = load_catalog().get("owner_gates") or []
    return [item["do"] for item in gates]


def _wired_now(dept: dict[str, Any], connected: set[str] | None) -> bool:
    status = dept.get("status")
    if status not in RUNNING_STATUSES:
        return False
    systems = [item for item in dept.get("systems") or [] if item in _connection_systems()]
    if connected is None or not systems:
        return True
    return all(item in connected for item in systems)


def org_report(*, probe: bool = False) -> dict[str, Any]:
    cat = load_catalog()
    body = organization()
    health = None
    connected: set[str] | None = None
    if probe:
        from ainav.microsoft.health import stack_health

        health = stack_health(probe=True)
        connected = set(health.get("connected") or [])
    departments: list[dict[str, Any]] = []
    wired: list[str] = []
    blocked: list[str] = []
    for item in body["departments"]:
        row = dict(item)
        systems = [sys_id for sys_id in item.get("systems") or [] if sys_id in _connection_systems()]
        row["wired_now"] = _wired_now(item, connected)
        if connected is not None:
            row["systems_connected"] = [sys_id for sys_id in systems if sys_id in connected]
            row["systems_blocked"] = [sys_id for sys_id in systems if sys_id not in connected]
        if row["wired_now"]:
            wired.append(item["id"])
        else:
            blocked.append(item["id"])
        departments.append(row)
    return {
        "kind": "ainav.org.v1",
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "operating": dict(cat["operating"]),
        "full_service": True,
        "all_wired_claimed": False,
        "all_running_claimed": False,
        "live": False,
        "live_pin_ok": False,
        "second_officer": None,
        "incorporation_date": None,
        "contacts": dict(body["contacts"]),
        "number_two": dict(body.get("number_two") or {}),
        "departments": departments,
        "wired_now": wired,
        "blocked_now": blocked,
        "programs": {
            "application_order": list(cat["programs"]["application_order"]),
            "membership_claimed": False,
            "ready_to_apply": False,
        },
        "human_gates": human_gates(),
        "open_gaps": list(cat["open_gaps"]),
        "health": health,
        "probed": bool(probe),
        "note": body["note"],
    }


def public_org() -> dict[str, Any]:
    report = org_report(probe=False)
    report.pop("health", None)
    report.pop("operating", None)
    return report
