"""Business Central adapter. Twin is default. Live post is gated."""

from __future__ import annotations

from typing import Any

from ainav.errors import LivePinError
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

    def apply(self, grant: dict[str, Any]) -> dict[str, Any]:
        return self.twin.post_journal(grant)
