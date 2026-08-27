"""Dual-admit: two distinct principals + action_hash + single-use consume."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agent_gov.clock import utc_now
from agent_gov.consume import ConsumeLedger
from agent_gov.errors import AdmitDenied, ConsumeReplay
from agent_gov.grant import grant_id
from agent_gov.hashing import action_hash, normalize_action
from agent_gov.lockfile import Lockfile, default_lockfile, load_lockfile
from agent_gov.records import decision_record, new_request_id
from agent_gov.seats import DEFAULT_VERIFIER, SeatVerifier, require_seat


def _require_seat(value: Any, name: str) -> str:
    return require_seat(value, name)


def admit(
    action: Any,
    lockfile: Lockfile | Mapping[str, Any] | None = None,
    *,
    ledger: ConsumeLedger | None = None,
    seat_a: str,
    seat_b: str,
    verifier: SeatVerifier | None = None,
) -> dict[str, Any]:
    """Admit a privileged action under dual human seats.

    Success returns a sealed DecisionRecord mapping with ``request_id`` and
    ``action_hash``. Failure raises (fail-closed). The consume slot is the
    lockfile-prefixed action_hash; a second admit of the same hash raises
    ``ConsumeReplay``.
    """
    lock = load_lockfile(lockfile if lockfile is not None else default_lockfile())
    canonical = normalize_action(action)
    digest = action_hash(canonical)
    seats = verifier or DEFAULT_VERIFIER
    a = seats.verify(seat_a, "seat_a")
    b = seats.verify(seat_b, "seat_b")
    consume = ledger or ConsumeLedger()
    if a == b:
        _deny(
            consume,
            action=canonical,
            action_hash=digest,
            seat_a=a,
            seat_b=b,
            lock=lock,
            reason_code="SEATS_NOT_DISTINCT",
            message="seat_a and seat_b must be distinct principals",
        )
    missing = [
        field
        for field in lock.required_action_fields
        if canonical.get(field) in (None, "")
    ]
    if missing:
        _deny(
            consume,
            action=canonical,
            action_hash=digest,
            seat_a=a,
            seat_b=b,
            lock=lock,
            reason_code="ACTION_FIELD_REQUIRED",
            message=f"action missing required fields: {', '.join(missing)}",
        )
    request_id = new_request_id()
    policy_hash = lock.policy_hash or lock.digest()
    rec = decision_record(
        record_type="admit_ok",
        request_id=request_id,
        action_hash=digest,
        action=canonical,
        seat_a=a,
        seat_b=b,
        policy_id=lock.policy_id,
        extra={
            "consumed_at": utc_now(),
            "policy_hash": policy_hash,
            "slot_key": lock.slot_key(digest),
            "grant_id": grant_id(
                action_hash=digest,
                seat_a=a,
                seat_b=b,
                policy_hash=policy_hash,
            ),
        },
    )
    try:
        stored = consume.consume(lock.slot_key(digest), rec)
    except ConsumeReplay:
        replay = decision_record(
            record_type="consume_replay",
            request_id=request_id,
            action_hash=digest,
            action=canonical,
            seat_a=a,
            seat_b=b,
            policy_id=lock.policy_id,
            reason_code="CONSUME_REPLAY",
        )
        consume.store.put_denied(replay)
        raise
    return stored


def _deny(
    ledger: ConsumeLedger,
    *,
    action: Mapping[str, Any],
    action_hash: str,
    seat_a: str,
    seat_b: str,
    lock: Lockfile,
    reason_code: str,
    message: str,
) -> None:
    rec = decision_record(
        record_type="admit_denied",
        request_id=new_request_id(),
        action_hash=action_hash,
        action=action,
        seat_a=seat_a,
        seat_b=seat_b,
        policy_id=lock.policy_id,
        reason_code=reason_code,
    )
    ledger.store.put_denied(rec)
    raise AdmitDenied(message, reason_code=reason_code)


def run_and_apply(
    action: Any,
    lockfile: Lockfile | Mapping[str, Any] | None = None,
    *,
    seat_a: str,
    seat_b: str,
    apply: Any | None = None,
    ledger: ConsumeLedger | None = None,
    effects: Any | None = None,
    verifier: SeatVerifier | None = None,
) -> dict[str, Any]:
    """Admit, then run the effect gate (optional SoR apply callback)."""
    from agent_gov.effect import EffectLedger

    rec = admit(
        action,
        lockfile if lockfile is not None else default_lockfile(),
        ledger=ledger or ConsumeLedger(),
        seat_a=seat_a,
        seat_b=seat_b,
        verifier=verifier,
    )
    gate = effects if effects is not None else EffectLedger()
    return gate.effect(rec["request_id"], rec["action_hash"], apply=apply)
