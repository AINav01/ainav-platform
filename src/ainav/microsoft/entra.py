"""Entra seat verifier. Consumes object ids. Does not replace the IdP.

Without tenant credentials this verifier only accepts oid-shaped principals.
It never calls Microsoft Graph in this tree — that would be a live pin.
"""

from __future__ import annotations

import os
import re
from typing import Any

from agent_gov.errors import AdmitDenied
from agent_gov.seats import require_seat
from ainav.errors import LivePinError
from ainav.microsoft.stack import assert_not_a_seat

OID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
LAB_OID_RE = re.compile(r"^oid-[A-Za-z0-9._:-]+$")


class EntraSeatVerifier:
    """Job C seat hook. Job B (IdP replacement) is out of scope."""

    def __init__(self, *, allow_lab_oids: bool = True) -> None:
        self.allow_lab_oids = allow_lab_oids

    def verify(self, seat: Any, name: str) -> str:
        principal = require_seat(seat, name)
        assert_not_a_seat(principal)
        if self.allow_lab_oids and LAB_OID_RE.match(principal):
            return principal
        if OID_RE.match(principal):
            return principal
        raise AdmitDenied(
            f"{name} must be an Entra object id (or lab oid-*)",
            reason_code="SEAT_TYPE",
        )

    def graph_configured(self) -> bool:
        return bool(
            os.environ.get("ENTRA_TENANT_ID")
            and os.environ.get("ENTRA_CLIENT_ID")
            and os.environ.get("ENTRA_CLIENT_SECRET")
        )

    def live_group_check(self, *_args: Any, **_kwargs: Any) -> None:
        raise LivePinError(
            "Entra Graph group check is not claimed. G1 LIVE_PIN_OK is open.",
            reason_code="LIVE_PIN_NOT_CLAIMED",
        )
