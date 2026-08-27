"""M365 E7 / Purview / Sentinel sinks. In-process until a live pin exists."""

from __future__ import annotations

from typing import Any

from ainav.errors import LivePinError


class ComplianceSink:
    """Sandbox export of sealed audit envelopes. Not a live Purview/Sentinel write."""

    live = False

    def __init__(self) -> None:
        self.exported: list[dict[str, Any]] = []

    def export_audit(self, envelope: dict[str, Any]) -> dict[str, Any]:
        record = {
            "sink": "sandbox.purview",
            "live": False,
            "envelope": dict(envelope),
        }
        self.exported.append(record)
        return {"exported": True, "live": False, "seq": len(self.exported)}

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
