"""Teams Enterprise + Premium notify sinks. Never a seat."""

from __future__ import annotations

from typing import Any

from ainav.errors import SoftDualError
from ainav.microsoft.connections import intended_request
from ainav.microsoft.stack import assert_not_a_seat

NOTIFY_CONNECTIONS = frozenset({"teams.enterprise", "teams.premium"})


class TeamsNotifier:
    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []

    def notify(self, event: dict[str, Any], *, connection_id: str = "teams.enterprise") -> dict[str, Any]:
        if event.get("as_seat"):
            raise SoftDualError("Teams cannot cast a vote", reason_code="SOFT_DUAL")
        if connection_id not in NOTIFY_CONNECTIONS:
            raise SoftDualError("unknown Teams connection", reason_code="SOFT_DUAL")
        intended = intended_request(
            connection_id,
            method="POST",
            path="/{team-id}/channels/{channel-id}/messages",
            payload={"body": {"contentType": "text", "content": dict(event)}, "as_seat": False},
        )
        payload = {
            "channel": "teams",
            "connection": connection_id,
            "as_seat": False,
            "live": False,
            "sent": False,
            "protection": event.get("protection") if connection_id == "teams.premium" else None,
            "event": dict(event),
            "intended": intended,
        }
        self.sent.append(payload)
        return payload

    def refuse_seat(self, principal: str) -> None:
        assert_not_a_seat(principal)
