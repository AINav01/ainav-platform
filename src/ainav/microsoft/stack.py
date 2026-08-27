"""Declared Microsoft stack. Live Graph/BC is not claimed."""

from __future__ import annotations

from ainav.errors import SoftDualError

MICROSOFT_STACK = {
    "identity": "Microsoft Entra ID",
    "notify_only": ("Microsoft Teams Enterprise", "Microsoft Teams Premium"),
    "sor_l1": "Dynamics 365 Business Central Premium",
    "sor_udual": "Dynamics 365 Sales Enterprise",
    "compliance": ("Microsoft 365 E7", "Microsoft Purview", "Microsoft Sentinel"),
    "hosting": "Microsoft Azure",
}

TEAMS_PREFIXES = ("teams:", "msteams:", "chat:")


def assert_not_a_seat(principal: str) -> None:
    """A Teams thread, chat, or Adaptive Card is not a dual seat."""
    lowered = principal.strip().lower()
    if lowered.startswith(TEAMS_PREFIXES) or lowered in {"teams", "msteams"}:
        raise SoftDualError(
            "Teams is notify-only; it cannot be seat_a or seat_b",
            reason_code="SOFT_DUAL",
        )
