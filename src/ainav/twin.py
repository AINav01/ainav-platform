"""Digital twin / sandbox SoR. Writes never leave the process.

A twin apply is not a live pin. Label every journal SANDBOX.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import EffectBlocked
from ainav.catalog import l1_action_classes


class BusinessCentralTwin:
    """In-process twin of Dynamics 365 Business Central general journal."""

    live = False
    label = "SANDBOX"

    def __init__(self) -> None:
        self.journals: list[dict[str, Any]] = []

    def post_journal(self, grant: dict[str, Any]) -> dict[str, Any]:
        proposal = grant.get("proposal") or {}
        action_class = proposal.get("action_class")
        if action_class not in l1_action_classes():
            raise EffectBlocked(
                f"twin refuses action_class {action_class!r}",
                reason_code="TWIN_ACTION",
            )
        if grant.get("record_type") != "admit_ok":
            raise EffectBlocked("twin refuses grant that is not admit_ok")
        entry = {
            "label": self.label,
            "live": self.live,
            "action_class": action_class,
            "action_hash": grant.get("action_hash"),
            "grant_id": grant.get("grant_id"),
            "request_id": grant.get("request_id"),
            "payload": proposal.get("payload"),
            "sor_target": proposal.get("sor_target") or "bc.sandbox",
        }
        self.journals.append(entry)
        return {"posted": True, "label": self.label, "live": False, "seq": len(self.journals)}
