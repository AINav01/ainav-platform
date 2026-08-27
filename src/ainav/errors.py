"""Mothership / provision errors. Fail-closed."""

from __future__ import annotations

from agent_gov.errors import AgentGovError


class ProvisionError(AgentGovError):
    reason_code = "PROVISION"


class SoftDualError(AgentGovError):
    reason_code = "SOFT_DUAL"


class LivePinError(AgentGovError):
    reason_code = "LIVE_PIN_NOT_CLAIMED"


class IPError(AgentGovError):
    """IP or competitor-boundary refusal. Not a signed legal opinion (G12 open)."""

    reason_code = "IP_PROTECTED"
