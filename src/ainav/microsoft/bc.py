"""Business Central Premium adapter. Twin is default. Live post is gated."""

from __future__ import annotations

from typing import Any

from ainav.errors import LivePinError
from ainav.microsoft.connections import intended_request
from ainav.twin import BusinessCentralTwin


class BusinessCentralAdapter:
    def __init__(self, *, twin: BusinessCentralTwin | None = None, live: bool = False) -> None:
        if live:
            raise LivePinError(
                "Live Business Central post is G14. Use the digital twin.",
                reason_code="LIVE_PIN_NOT_CLAIMED",
            )
        self.twin = twin or BusinessCentralTwin()
        self.live = False
        self.connection_id = "bc.premium"

    def apply(self, grant: dict[str, Any]) -> dict[str, Any]:
        posted = self.twin.post_journal(grant)
        posted["connection"] = self.connection_id
        posted["intended"] = intended_request(
            self.connection_id,
            method="POST",
            path="/{tenant}/{env}/api/v2.0/companies({company})/journals({journal})/journalLines",
            payload=grant.get("proposal") or {},
        )
        return posted
