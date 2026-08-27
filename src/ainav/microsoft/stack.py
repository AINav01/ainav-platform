"""Declared Microsoft stack. Live Graph/BC is not claimed. Catalog wins."""

from __future__ import annotations

from typing import Any

from ainav.catalog import microsoft_stack as catalog_stack
from ainav.errors import SoftDualError

TEAMS_PREFIXES = ("teams:", "msteams:", "chat:")


def declared_stack() -> dict[str, Any]:
    return catalog_stack()


# Compatibility snapshot. Prefer declared_stack() for new callers.
MICROSOFT_STACK = declared_stack()


def assert_not_a_seat(principal: str) -> None:
    """A Teams thread, chat, or Adaptive Card is not a dual seat."""
    lowered = principal.strip().lower()
    if lowered.startswith(TEAMS_PREFIXES) or lowered in {"teams", "msteams"}:
        raise SoftDualError(
            "Teams is notify-only; it cannot be seat_a or seat_b",
            reason_code="SOFT_DUAL",
        )
