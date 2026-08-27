"""Azure is the hosting target for the master mothership. Not a live pin."""

from __future__ import annotations

from typing import Any

from ainav.errors import LivePinError
from ainav.microsoft.stack import MICROSOFT_STACK


class AzureHost:
    """Declared Azure hosting. Live deploy is not claimed in this tree."""

    def __init__(self, *, live: bool = False) -> None:
        if live:
            raise LivePinError(
                "Live Azure deploy is not claimed. G1 LIVE_PIN_OK is open.",
                reason_code="LIVE_PIN_NOT_CLAIMED",
            )
        self.live = False
        self.region = "declared"

    def describe(self) -> dict[str, Any]:
        return {
            "hosting": MICROSOFT_STACK["hosting"],
            "live": False,
            "region": self.region,
            "role": "master mothership target",
        }

    def deploy_master(self) -> None:
        raise LivePinError(
            "Azure deploy of the master mothership is not claimed.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )
