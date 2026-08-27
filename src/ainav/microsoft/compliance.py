"""Microsoft 365 E7 / Purview / Sentinel sinks. In-process until a live pin exists."""

from __future__ import annotations

from typing import Any

from ainav.errors import LivePinError
from ainav.microsoft.connections import intended_request


class ComplianceSink:
    """Sandbox export of sealed audit envelopes onto the E7 tenant. Not live."""

    live = False
    connection_id = "m365.e7"

    def __init__(self) -> None:
        self.exported: list[dict[str, Any]] = []

    def export_audit(self, envelope: dict[str, Any]) -> dict[str, Any]:
        record = {
            "connection": self.connection_id,
            "sink": "sandbox.m365.e7",
            "live": False,
            "sent": False,
            "envelope": dict(envelope),
            "intended": intended_request(
                self.connection_id,
                method="POST",
                path="/security/alerts_v2",
                payload={"kind": "ainav.audit", "live": False},
            ),
        }
        self.exported.append(record)
        return {
            "exported": True,
            "connection": self.connection_id,
            "live": False,
            "seq": len(self.exported),
        }

    def live_sentinel(self) -> None:
        raise LivePinError(
            "Microsoft Sentinel live ingest is not claimed. G1 LIVE_PIN_OK is open.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )

    def live_purview(self) -> None:
        raise LivePinError(
            "Microsoft Purview live export is not claimed. G1 LIVE_PIN_OK is open.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )
