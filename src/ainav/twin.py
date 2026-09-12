"""Digital twin / sandbox SoR. Writes never leave the process.

A twin apply is not a live pin. Label every write SANDBOX.
Direct public writes on a mothership-sealed twin are forbidden.
"""

from __future__ import annotations

from typing import Any

from agent_gov.errors import EffectBlocked
from ainav.catalog import l1_action_classes, udual_action_classes
from ainav.errors import ProvisionError

SANDBOX_TARGETS = frozenset({"bc.sandbox", "d365.sales.sandbox"})


def _require_admit_ok(grant: dict[str, Any]) -> dict[str, Any]:
    if grant.get("record_type") != "admit_ok":
        raise EffectBlocked("twin refuses grant that is not admit_ok")
    return grant.get("proposal") or {}


def _require_sandbox_target(proposal: dict[str, Any], *, default_target: str) -> str:
    target = str(proposal.get("sor_target") or default_target)
    lowered = target.lower()
    if "live" in lowered or lowered.endswith(".production"):
        raise EffectBlocked(
            f"twin refuses live sor_target {target!r}",
            reason_code="TWIN_TARGET",
        )
    if "sandbox" not in lowered and target not in SANDBOX_TARGETS:
        raise EffectBlocked(
            f"twin refuses non-sandbox sor_target {target!r}",
            reason_code="TWIN_TARGET",
        )
    return target


def _sandbox_entry(grant: dict[str, Any], proposal: dict[str, Any], *, default_target: str) -> dict[str, Any]:
    target = _require_sandbox_target(proposal, default_target=default_target)
    return {
        "label": "SANDBOX",
        "live": False,
        "action_class": proposal.get("action_class"),
        "action_hash": grant.get("action_hash"),
        "grant_id": grant.get("grant_id"),
        "request_id": grant.get("request_id"),
        "payload": proposal.get("payload"),
        "sor_target": target,
    }


def _refuse_direct(sealed: bool, trusted: bool) -> None:
    if sealed and not trusted:
        raise ProvisionError(
            "direct twin write is forbidden; use run_and_apply",
            reason_code="TWIN_SEALED",
        )


class BusinessCentralTwin:
    """In-process twin of Dynamics 365 Business Central general journal."""

    live = False
    label = "SANDBOX"

    def __init__(self, *, sealed: bool = False) -> None:
        self.sealed = sealed
        self.journals: list[dict[str, Any]] = []

    def post_journal(self, grant: dict[str, Any], *, trusted: bool = False) -> dict[str, Any]:
        _refuse_direct(self.sealed, trusted)
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

    def __init__(self, *, sealed: bool = False) -> None:
        self.sealed = sealed
        self.writes: list[dict[str, Any]] = []

    def apply(self, grant: dict[str, Any], *, trusted: bool = False) -> dict[str, Any]:
        _refuse_direct(self.sealed, trusted)
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
        sealed: bool = False,
    ) -> None:
        self.bc = bc or BusinessCentralTwin()
        self.sales = sales or SalesEnterpriseTwin()
        self.sealed = sealed

    def apply(self, grant: dict[str, Any], *, trusted: bool = False) -> dict[str, Any]:
        _refuse_direct(self.sealed, trusted)
        _require_admit_ok(grant)
        proposal = grant.get("proposal") or {}
        action_class = proposal.get("action_class")
        if action_class in l1_action_classes():
            return self.bc.post_journal(grant, trusted=True)
        if action_class in udual_action_classes():
            return self.sales.apply(grant, trusted=True)
        raise EffectBlocked(
            f"no sandbox SoR for action_class {action_class!r}",
            reason_code="TWIN_ACTION",
        )
