"""Typed privileged action. Dicts still work; this is the future-proof form."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Action:
    action_class: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    proposal_id: str = ""
    sor_target: str = ""
    policy_id: str = "dual-admit-v1"

    def to_canonical(self) -> dict[str, Any]:
        return {
            "action_class": self.action_class,
            "payload": dict(self.payload),
            "policy_id": self.policy_id,
            "proposal_id": self.proposal_id,
            "sor_target": self.sor_target,
        }
