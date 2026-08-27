"""Executable Job C invariants. Gold runs these; they are not documentation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agent_gov.errors import IntegrityError
from agent_gov.grant import grant_id
from agent_gov.hashing import hashes_equal
from agent_gov.lockfile import HARD_INVARIANTS, Lockfile
from agent_gov.records import verify_record


def check_lockfile(lock: Lockfile) -> None:
    lock.verify()
    if lock.effect_gate != "strict":
        raise IntegrityError("effect_gate must be strict")
    if lock.product != "job_c":
        raise IntegrityError("product must be job_c")
    for key, required in HARD_INVARIANTS.items():
        if lock.invariants.get(key) is not required:
            raise IntegrityError(f"invariant {key} weakened")
    if "action_class" not in lock.required_action_fields:
        raise IntegrityError("action_class is required")


def check_admit_ok(record: Mapping[str, Any], *, policy_hash: str) -> None:
    verify_record(record)
    if record.get("record_type") != "admit_ok":
        raise IntegrityError("record is not admit_ok")
    if record.get("consumed") is not True:
        raise IntegrityError("admit_ok must be consumed")
    if record.get("seat_a") == record.get("seat_b"):
        raise IntegrityError("seats are not distinct")
    expected = grant_id(
        action_hash=str(record.get("action_hash")),
        seat_a=str(record.get("seat_a")),
        seat_b=str(record.get("seat_b")),
        policy_hash=policy_hash,
    )
    if not hashes_equal(record.get("grant_id"), expected):
        raise IntegrityError("grant_id does not bind seats to action_hash")


def check_effect_applied(record: Mapping[str, Any]) -> None:
    verify_record(record)
    if record.get("record_type") != "effect_applied":
        raise IntegrityError("record is not effect_applied")
