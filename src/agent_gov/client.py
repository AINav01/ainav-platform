"""2.1.0 named surface: AdmitClient and DualSession."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agent_gov.admit import _require_seat, admit, run_and_apply
from agent_gov.consume import ConsumeLedger
from agent_gov.effect import ApplyFn, EffectLedger
from agent_gov.errors import AdmitDenied
from agent_gov.lockfile import Lockfile, default_lockfile, load_lockfile
from agent_gov.store import AuthorityStore, default_store


class AdmitClient:
    """One client, one store, one lockfile — admit then effect on the same plane."""

    def __init__(
        self,
        lockfile: Lockfile | Mapping[str, Any] | None = None,
        store: AuthorityStore | None = None,
        *,
        ledger: ConsumeLedger | None = None,
        effects: EffectLedger | None = None,
    ) -> None:
        self.lockfile = load_lockfile(lockfile if lockfile is not None else default_lockfile())
        self.store = store or default_store()
        self.ledger = ledger or ConsumeLedger(store=self.store)
        self.effects = effects or EffectLedger(store=self.store)

    def admit(self, action: Any, *, seat_a: str, seat_b: str) -> dict[str, Any]:
        return admit(
            action,
            self.lockfile,
            ledger=self.ledger,
            seat_a=seat_a,
            seat_b=seat_b,
        )

    def effect(
        self,
        request_id: str,
        action_hash: str,
        *,
        apply: ApplyFn | None = None,
    ) -> dict[str, Any]:
        return self.effects.effect(request_id, action_hash, apply=apply)

    def run_and_apply(
        self,
        action: Any,
        *,
        seat_a: str,
        seat_b: str,
        apply: ApplyFn | None = None,
    ) -> dict[str, Any]:
        return run_and_apply(
            action,
            self.lockfile,
            seat_a=seat_a,
            seat_b=seat_b,
            apply=apply,
            ledger=self.ledger,
            effects=self.effects,
        )

    def session(self, seat_a: str, seat_b: str) -> DualSession:
        return DualSession(seat_a, seat_b, client=self)


class DualSession:
    """Two distinct seats bound for the life of the session."""

    def __init__(
        self,
        seat_a: str,
        seat_b: str,
        *,
        client: AdmitClient | None = None,
        lockfile: Lockfile | Mapping[str, Any] | None = None,
        store: AuthorityStore | None = None,
    ) -> None:
        self.seat_a = _require_seat(seat_a, "seat_a")
        self.seat_b = _require_seat(seat_b, "seat_b")
        if self.seat_a == self.seat_b:
            raise AdmitDenied(
                "seat_a and seat_b must be distinct principals",
                reason_code="SEATS_NOT_DISTINCT",
            )
        self.client = client or AdmitClient(lockfile=lockfile, store=store)

    def admit(self, action: Any) -> dict[str, Any]:
        return self.client.admit(action, seat_a=self.seat_a, seat_b=self.seat_b)

    def effect(
        self,
        request_id: str,
        action_hash: str,
        *,
        apply: ApplyFn | None = None,
    ) -> dict[str, Any]:
        return self.client.effect(request_id, action_hash, apply=apply)

    def run_and_apply(self, action: Any, *, apply: ApplyFn | None = None) -> dict[str, Any]:
        return self.client.run_and_apply(
            action,
            seat_a=self.seat_a,
            seat_b=self.seat_b,
            apply=apply,
        )
