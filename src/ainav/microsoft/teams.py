"""Teams Premium notify sink. Never a seat."""

from __future__ import annotations

from typing import Any

from ainav.errors import SoftDualError
from ainav.microsoft.stack import assert_not_a_seat


class TeamsNotifier:
    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []

    def notify(self, event: dict[str, Any]) -> dict[str, Any]:
        if event.get("as_seat"):
            raise SoftDualError("Teams cannot cast a vote", reason_code="SOFT_DUAL")
        payload = {"channel": "teams", "as_seat": False, "event": dict(event)}
        self.sent.append(payload)
        return payload

    def refuse_seat(self, principal: str) -> None:
        assert_not_a_seat(principal)
