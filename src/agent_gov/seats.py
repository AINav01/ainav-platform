"""Seat verification. Default: non-empty distinct principal strings.

A future Entra/OIDC verifier implements the same protocol. That is Job B
and is not shipped here — the hook exists so Job C does not bake in strings
as the only possible identity.
"""

from __future__ import annotations

from typing import Any, Protocol

from agent_gov.errors import AdmitDenied


class SeatVerifier(Protocol):
    def verify(self, seat: Any, name: str) -> str: ...


def require_seat(value: Any, name: str) -> str:
    if value is None:
        raise AdmitDenied(f"{name} is required", reason_code="SEAT_MISSING")
    if not isinstance(value, str):
        raise AdmitDenied(f"{name} must be a string principal id", reason_code="SEAT_TYPE")
    seat = value.strip()
    if not seat:
        raise AdmitDenied(f"{name} must be a non-empty principal id", reason_code="SEAT_EMPTY")
    return seat


class PrincipalIdVerifier:
    """Accepts any non-empty string principal. Does not talk to an IdP."""

    def verify(self, seat: Any, name: str) -> str:
        return require_seat(seat, name)


DEFAULT_VERIFIER = PrincipalIdVerifier()
