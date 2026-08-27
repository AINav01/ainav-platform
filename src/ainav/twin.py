"""Digital twin / sandbox SoR. Writes never leave the process.

A twin apply is not a live pin. Label every write SANDBOX.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import EffectBlocked
from ainav.catalog import l1_action_classes, udual_action_classes


def _require_admit_ok(grant: dict[str, Any]) -> dict[str, Any]:
    if grant.get("record_type") != "admit_ok":
        raise EffectBlocked("twin refuses grant that is not admit_ok")
    return grant.get("proposal") or {}


def _sandbox_entry(grant: dict[str, Any], proposal: dict[str, Any], *, default_target: str) -> dict[str, Any]:
    return {
        "label": "SANDBOX",
        "live": False,
        "action_class": proposal.get("action_class"),
        "action_hash": grant.get("action_hash"),
        "grant_id": grant.get("grant_id"),
        "request_id": grant.get("request_id"),
        "payload": proposal.get("payload"),
        "sor_target": proposal.get("sor_target") or default_target,
    }


class BusinessCentralTwin:
    """In-process twin of Dynamics 365 Business Central general journal."""

    live = False
    label = "SANDBOX"

    def __init__(self) -> None:
        self.journals: list[dict[str, Any]] = []

    def post_journal(self, grant: dict[str, Any]) -> dict[str, Any]:
        proposal = _require_admit_ok(grant)
        action_class = proposal.get("action_class")
        if action_class not in l1_action_classes():
            raise EffectBlocked(
                f"twin refuses action_class {action_class!r}",
                reason_code="TWIN_ACTION",
            )
        entry = _sandbox_entry(grant, proposal, default_target="bc.sandbox")
        self.journals.append(entry)
        return {"posted": True, "label": self.label, "live": False, "seq": len(self.journals)}


class SalesEnterpriseTwin:
    """In-process twin of Dynamics 365 Sales Enterprise privileged writes."""

    live = False
    label = "SANDBOX"

    def __init__(self) -> None:
        self.writes: list[dict[str, Any]] = []

    def apply(self, grant: dict[str, Any]) -> dict[str, Any]:
        proposal = _require_admit_ok(grant)
        action_class = proposal.get("action_class")
        if action_class not in udual_action_classes():
            raise EffectBlocked(
                f"sales twin refuses action_class {action_class!r}",
                reason_code="TWIN_ACTION",
            )
        entry = _sandbox_entry(grant, proposal, default_target="d365.sales.sandbox")
        self.writes.append(entry)
        return {"posted": True, "label": self.label, "live": False, "seq": len(self.writes)}


class SandboxRouter:
    """Route an admitted grant to the matching sandbox SoR. Never live."""

    live = False

    def __init__(
        self,
        *,
        bc: BusinessCentralTwin | None = None,
        sales: SalesEnterpriseTwin | None = None,
    ) -> None:
        self.bc = bc or BusinessCentralTwin()
        self.sales = sales or SalesEnterpriseTwin()

    def apply(self, grant: dict[str, Any]) -> dict[str, Any]:
        proposal = grant.get("proposal") or {}
        action_class = proposal.get("action_class")
        if action_class in l1_action_classes():
            return self.bc.post_journal(grant)
        if action_class in udual_action_classes():
            return self.sales.apply(grant)
        raise EffectBlocked(
            f"no sandbox SoR for action_class {action_class!r}",
            reason_code="TWIN_ACTION",
        )
