"""Sandbox operating company. Display name is AINav; system name may stay My Company."""

from __future__ import annotations

from typing import Any

OPERATING_COMPANY = "AINav"
OPERATING_ALIASES = frozenset({"AINav", "My Company"})
OPERATING_COMPANY_ID = "9b8d1202-be8f-f111-8327-7ced8db3712c"


def company_label(item: dict[str, Any]) -> str:
    return str(item.get("displayName") or item.get("name") or "").strip()


def pick_operating_company(companies: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in companies:
        if item.get("id") == OPERATING_COMPANY_ID:
            return item
    for item in companies:
        if company_label(item) in OPERATING_ALIASES or item.get("name") in OPERATING_ALIASES:
            return item
    return companies[0] if companies else None
