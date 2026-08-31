"""Microsoft stack connections. Wired, sandbox, fail-closed.

These six products host, identify, notify, and receive SoR writes.
They are not AINav SKUs. Live Graph / BC / Dataverse / Azure calls
are not claimed — G1/G10 and G14 stay open.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog
from ainav.errors import LivePinError, SoftDualError
from ainav.ip import refuse_claim, screen_pack_label

REQUIRED_IDS = (
    "azure.host",
    "m365.e7",
    "teams.enterprise",
    "teams.premium",
    "bc.premium",
    "sales.enterprise",
)
COMPLEMENT_IDS = (
    "entra.id",
    "azure.keyvault",
    "azure.monitor",
    "sharepoint.kit",
    "defender.xdr",
    "entra.pim",
    "sentinel.siem",
    "azure.policy",
)
SURFACES = frozenset({"ainav_inc", "ainav", "institute"})
FORBIDDEN_CONNECTION_STEMS = (
    "copilot",
    "agent_365",
    "agent365",
    "purview_plane",
    "soft_dual",
)


def validate_connections(catalog: dict[str, Any]) -> None:
    body = catalog.get("connections")
    if not isinstance(body, dict):
        raise IntegrityError("catalog missing connections", reason_code="CATALOG_CONNECTION")
    if body.get("live") is True:
        raise IntegrityError("connections cannot claim live", reason_code="LIVE_PIN_NOT_CLAIMED")
    items = body.get("items") or []
    ids = [item.get("id") for item in items]
    if ids != list(REQUIRED_IDS):
        raise IntegrityError(
            "connections must be the six Microsoft products in catalog order",
            reason_code="CATALOG_CONNECTION",
        )
    for item in items:
        screen_pack_label(str(item.get("id")), catalog=catalog)
        refuse_claim(str(item.get("product")), catalog=catalog)
        for stem in FORBIDDEN_CONNECTION_STEMS:
            blob = f"{item.get('id')} {item.get('product')}".lower()
            if stem.replace("_", " ") in blob or stem in blob.replace(" ", "_"):
                raise IntegrityError(
                    "Copilot / Agent 365 cannot be a stack connection",
                    reason_code="MICROSOFT_PRODUCT",
                )
        if not set(item.get("surfaces") or []) <= SURFACES:
            raise IntegrityError("unknown connection surface", reason_code="CATALOG_CONNECTION")
    complements = body.get("complements") or []
    if [item.get("id") for item in complements] != list(COMPLEMENT_IDS):
        raise IntegrityError(
            "complements must be the catalog Microsoft 10/10 set",
            reason_code="CATALOG_CONNECTION",
        )
    for item in complements:
        screen_pack_label(str(item.get("id")), catalog=catalog)
        refuse_claim(str(item.get("product")), catalog=catalog)
        blob = f"{item.get('id')} {item.get('product')}".lower()
        for stem in FORBIDDEN_CONNECTION_STEMS:
            if stem.replace("_", " ") in blob or stem in blob.replace(" ", "_"):
                raise IntegrityError(
                    "Copilot / Agent 365 cannot be a stack connection",
                    reason_code="MICROSOFT_PRODUCT",
                )


def connection_specs() -> list[dict[str, Any]]:
    return [dict(item) for item in load_catalog()["connections"]["items"]]


def complement_specs() -> list[dict[str, Any]]:
    return [dict(item) for item in load_catalog()["connections"].get("complements", [])]


def spec(connection_id: str) -> dict[str, Any]:
    for item in connection_specs() + complement_specs():
        if item["id"] == connection_id:
            return item
    raise IntegrityError(f"unknown connection {connection_id}", reason_code="CATALOG_CONNECTION")


def intended_request(connection_id: str, *, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    item = spec(connection_id)
    return {
        "connection": connection_id,
        "product": item["product"],
        "role": item["role"],
        "method": method,
        "url": f"{item['endpoint'].rstrip('/')}{path}",
        "payload": dict(payload),
        "live": False,
        "sent": False,
        "label": "SANDBOX",
    }


def stack_json() -> dict[str, Any]:
    cat = load_catalog()
    body = cat["connections"]
    return {
        "kind": "ainav.institute.stack.v1",
        "entity": cat["entity"]["legal"],
        "institute": cat["entity"]["institute"],
        "product": cat["entity"]["product"],
        "live": False,
        "not_the_product": cat["microsoft_stack"]["not_the_product"],
        "e7_not_the_product": list(cat["microsoft_stack"].get("e7_not_the_product") or []),
        "connections": [
            {
                "id": item["id"],
                "product": item["product"],
                "role": item["role"],
                "surfaces": list(item["surfaces"]),
                "binds": list(item.get("binds") or []),
                "mode": "sandbox",
                "live": False,
            }
            for item in body["items"]
        ],
        "complements": [
            {
                "id": item["id"],
                "product": item["product"],
                "role": item["role"],
                "surfaces": list(item["surfaces"]),
                "binds": list(item.get("binds") or []),
                "mode": "sandbox",
                "live": False,
            }
            for item in body.get("complements", [])
        ],
        "walk": {
            "thesis": (cat["microsoft_stack"].get("walk") or {}).get("thesis"),
            "implementation": (cat["microsoft_stack"].get("walk") or {}).get("implementation"),
            "cli": (cat["microsoft_stack"].get("walk") or {}).get("cli"),
            "cannot": list((cat["microsoft_stack"].get("walk") or {}).get("cannot") or []),
            "path": [dict(item) for item in (cat["microsoft_stack"].get("walk") or {}).get("path") or []],
            "complements": [
                dict(item) for item in (cat["microsoft_stack"].get("walk") or {}).get("complements") or []
            ],
        },
    }


class StackPlane:
    """Binds the six Microsoft connections onto a mothership. Never live."""

    live = False

    def __init__(self) -> None:
        self.receipts: list[dict[str, Any]] = []
        self.specs = {item["id"]: item for item in connection_specs() + complement_specs()}

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "ainav.stack.v1",
            "live": False,
            "connections": [self.health(cid) for cid in REQUIRED_IDS],
            "complements": [self.health(cid) for cid in COMPLEMENT_IDS],
            "not_the_product": load_catalog()["microsoft_stack"]["not_the_product"],
        }

    def health(self, connection_id: str) -> dict[str, Any]:
        item = self.specs[connection_id]
        return {
            "id": connection_id,
            "product": item["product"],
            "role": item["role"],
            "surfaces": list(item["surfaces"]),
            "mode": "sandbox",
            "configured": False,
            "live": False,
            "live_gap": item["live_gap"],
        }

    def live_connect(self, connection_id: str) -> None:
        item = spec(connection_id)
        raise LivePinError(
            f"{item['product']} live connect is not claimed. {item['live_gap']} is open.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )

    def after_effect(self, mothership: Any, effect: dict[str, Any]) -> list[dict[str, Any]]:
        if effect.get("record_type") != "effect_applied":
            return []
        receipts = [
            mothership.teams.notify(
                {
                    "request_id": effect.get("request_id"),
                    "record_type": effect.get("record_type"),
                    "action_hash": effect.get("action_hash"),
                },
                connection_id="teams.enterprise",
            ),
            mothership.teams.notify(
                {
                    "request_id": effect.get("request_id"),
                    "record_type": effect.get("record_type"),
                    "action_hash": effect.get("action_hash"),
                    "protection": "premium",
                },
                connection_id="teams.premium",
            ),
        ]
        if "P-ADM" in mothership.packs:
            receipts.append(
                mothership.compliance.export_audit(
                    {
                        "client_id": mothership.client_id,
                        "request_id": effect.get("request_id"),
                        "action_hash": effect.get("action_hash"),
                        "live": False,
                    }
                )
            )
        self.receipts.extend(receipts)
        return receipts
