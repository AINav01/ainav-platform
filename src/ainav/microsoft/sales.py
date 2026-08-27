"""Dynamics 365 Sales Enterprise adapter. Twin is default. Live write is gated."""

from __future__ import annotations

from typing import Any

from ainav.errors import LivePinError
from ainav.twin import SalesEnterpriseTwin


class SalesEnterpriseAdapter:
    def __init__(self, *, twin: SalesEnterpriseTwin | None = None, live: bool = False) -> None:
        if live:
            raise LivePinError(
                "Live Sales Enterprise write is G14. Use the digital twin.",
                reason_code="LIVE_PIN_NOT_CLAIMED",
            )
        self.twin = twin or SalesEnterpriseTwin()
        self.live = False

    def apply(self, grant: dict[str, Any]) -> dict[str, Any]:
        return self.twin.apply(grant)
