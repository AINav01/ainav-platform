"""Drafting AIs wrap AdmitClient. The drafter id is not a seat.

Not live. Not a dual seat. The Cloud Agent is not a drafter-as-seat.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agent_gov.client import AdmitClient, ApplyFn
from agent_gov.errors import AdmitDenied
from agent_gov.lockfile import Lockfile
from agent_gov.store import AuthorityStore


class DraftAdmitClient:
    """One drafting AI, one AdmitClient. Drafter id cannot bind."""

    live = False

    def __init__(
        self,
        drafter_id: str,
        client: AdmitClient | None = None,
        *,
        lockfile: Lockfile | Mapping[str, Any] | None = None,
        store: AuthorityStore | None = None,
    ) -> None:
        if not drafter_id or not isinstance(drafter_id, str):
            raise AdmitDenied("drafter_id is required", reason_code="DRAFTER_REQUIRED")
        self.drafter_id = drafter_id
        self.client = client or AdmitClient(lockfile=lockfile, store=store)

    def _refuse_drafter_as_seat(self, seat_a: str, seat_b: str) -> None:
        if self.drafter_id in {seat_a, seat_b}:
            raise AdmitDenied(
                "drafter is not a seat",
                reason_code="DRAFTER_IS_NOT_SEAT",
            )

    def admit(self, action: Any, *, seat_a: str, seat_b: str) -> dict[str, Any]:
        self._refuse_drafter_as_seat(seat_a, seat_b)
        return self.client.admit(action, seat_a=seat_a, seat_b=seat_b)

    def run_and_apply(
        self,
        action: Any,
        *,
        seat_a: str,
        seat_b: str,
        apply: ApplyFn | None = None,
    ) -> dict[str, Any]:
        self._refuse_drafter_as_seat(seat_a, seat_b)
        return self.client.run_and_apply(
            action,
            seat_a=seat_a,
            seat_b=seat_b,
            apply=apply,
        )

    def prove(self, record_id: str) -> dict[str, Any]:
        return self.client.prove(record_id)


def wrap(
    drafter_id: str,
    client: AdmitClient | None = None,
    **kwargs: Any,
) -> DraftAdmitClient:
    return DraftAdmitClient(drafter_id, client, **kwargs)
