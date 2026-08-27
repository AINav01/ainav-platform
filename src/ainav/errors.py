"""Mothership / provision errors. Fail-closed."""

from __future__ import annotations

from agent_gov.errors import AgentGovError


class ProvisionError(AgentGovError):
    reason_code = "PROVISION"


class SoftDualError(AgentGovError):
    reason_code = "SOFT_DUAL"


class LivePinError(AgentGovError):
    reason_code = "LIVE_PIN_NOT_CLAIMED"
