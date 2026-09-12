"""Fail-closed error types for the Job C admit plane."""

from __future__ import annotations


class AgentGovError(Exception):
    """Base error. All governance failures are fail-closed."""

    reason_code: str = "GOV_ERROR"

    def __init__(self, message: str, *, reason_code: str | None = None) -> None:
        super().__init__(message)
        if reason_code is not None:
            self.reason_code = reason_code


class AdmitDenied(AgentGovError):
    """Action was not dual-admitted. SoR must not proceed."""

    reason_code = "ADMIT_DENIED"


class ConsumeReplay(AgentGovError):
    """Single-use slot was already consumed. Second consume is an error."""

    reason_code = "CONSUME_REPLAY"


class EffectBlocked(AgentGovError):
    """Effect gate refused the write. Fail-closed: do not touch SoR."""

    reason_code = "EFFECT_BLOCKED"


class LockfileError(AgentGovError):
    """Lockfile missing, corrupt, or attempting to weaken hard invariants."""

    reason_code = "LOCKFILE_INVALID"


class IntegrityError(AgentGovError):
    """DecisionRecord hash, chain, or ledger file failed verification."""

    reason_code = "INTEGRITY"
