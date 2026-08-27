"""DecisionRecord v1 — proof that dual-admit happened (or was denied)."""

from __future__ import annotations

import secrets
import string
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from agent_gov.clock import utc_now
from agent_gov.errors import IntegrityError
from agent_gov.hashing import content_hash, hashes_equal

SCHEMA_VERSION = "decision_record.v1"
GENESIS_HASH = "0" * 64
RECORD_TYPES = frozenset(
    {
        "admit_ok",
        "admit_denied",
        "consume_replay",
        "effect_blocked",
        "effect_reserved",
        "effect_applied",
        "effect_apply_failed",
    }
)
EFFECT_STATES = frozenset({"effect_reserved", "effect_applied", "effect_apply_failed"})
REQUIRED_FIELDS = (
    "schema_version",
    "record_id",
    "record_type",
    "request_id",
    "action_hash",
    "integrity",
)


class DecisionRecord(dict):
    """Dict-shaped record so ``rec["request_id"]`` stays the caller contract.

    After ``seal()`` the mapping is immutable. Mutating a sealed receipt is
    an integrity failure, not a programming convenience.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        object.__setattr__(self, "_sealed", False)

    def seal(self) -> DecisionRecord:
        object.__setattr__(self, "_sealed", True)
        return self

    @property
    def sealed(self) -> bool:
        return bool(getattr(self, "_sealed", False))

    def verify(self) -> DecisionRecord:
        verify_record(self)
        return self

    def _guard(self) -> None:
        if getattr(self, "_sealed", False):
            raise IntegrityError(
                "sealed DecisionRecord is immutable",
                reason_code="SEALED",
            )

    def __setitem__(self, key: Any, value: Any) -> None:
        self._guard()
        super().__setitem__(key, value)

    def __delitem__(self, key: Any) -> None:
        self._guard()
        super().__delitem__(key)

    def clear(self) -> None:
        self._guard()
        super().clear()

    def pop(self, *args: Any, **kwargs: Any) -> Any:
        self._guard()
        return super().pop(*args, **kwargs)

    def popitem(self) -> Any:
        self._guard()
        return super().popitem()

    def update(self, *args: Any, **kwargs: Any) -> None:
        self._guard()
        super().update(*args, **kwargs)

    def setdefault(self, *args: Any, **kwargs: Any) -> Any:
        self._guard()
        return super().setdefault(*args, **kwargs)


def as_sealed(record: Mapping[str, Any]) -> DecisionRecord:
    return DecisionRecord(record).seal()


def utc_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def new_request_id() -> str:
    return f"req_{uuid4().hex}"


def new_record_id() -> str:
    alphabet = string.ascii_lowercase + string.digits
    suffix = "".join(secrets.choice(alphabet) for _ in range(6))
    return f"dr_{utc_compact()}_{suffix}"


def hashable_body(record: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k != "integrity"}


def verify_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Fail-closed integrity check. Returns a mutable copy on success."""
    if not isinstance(record, Mapping):
        raise IntegrityError("record must be a mapping", reason_code="RECORD_SCHEMA")
    for field in REQUIRED_FIELDS:
        if field not in record:
            raise IntegrityError(f"record missing {field}", reason_code="RECORD_SCHEMA")
    integrity = record.get("integrity")
    if not isinstance(integrity, Mapping):
        raise IntegrityError("record missing integrity block", reason_code="RECORD_SCHEMA")
    expected = content_hash(hashable_body(record))
    found = integrity.get("content_hash")
    if not hashes_equal(found, expected):
        raise IntegrityError(
            "record content_hash mismatch",
            reason_code="INTEGRITY_HASH",
        )
    return dict(record)


def verify_chain(records: Sequence[Mapping[str, Any]]) -> str:
    """Walk prev_receipt_hash → content_hash. Returns the tip hash."""
    tip = GENESIS_HASH
    expected_seq = 1
    for rec in records:
        verify_record(rec)
        prev = rec.get("prev_receipt_hash")
        if prev is None and isinstance(rec.get("integrity"), Mapping):
            prev = rec["integrity"].get("prev_receipt_hash")
        if not hashes_equal(prev, tip):
            raise IntegrityError(
                "receipt chain broken",
                reason_code="INTEGRITY_CHAIN",
            )
        seq = rec.get("seq")
        if seq is not None and seq != expected_seq:
            raise IntegrityError(
                f"receipt sequence broken at {seq}",
                reason_code="INTEGRITY_SEQ",
            )
        expected_seq += 1
        tip = rec["integrity"]["content_hash"]
    return tip


def decision_record(
    *,
    record_type: str,
    request_id: str,
    action_hash: str,
    action: Mapping[str, Any],
    seat_a: str | None = None,
    seat_b: str | None = None,
    policy_id: str | None = None,
    reason_code: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> DecisionRecord:
    if record_type not in RECORD_TYPES:
        raise ValueError(f"unknown record_type {record_type!r}")
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_id": new_record_id(),
        "record_type": record_type,
        "created_at": utc_now(),
        "request_id": request_id,
        "action_hash": action_hash,
        "proposal": {
            "action_class": action.get("action_class"),
            "action_hash": action_hash,
            "payload": action.get("payload"),
            "policy_id": action.get("policy_id", policy_id),
            "proposal_id": action.get("proposal_id"),
            "sor_target": action.get("sor_target"),
        },
        "seat_a": seat_a,
        "seat_b": seat_b,
        "policy_id": policy_id or action.get("policy_id"),
        "reason_code": reason_code,
        "distinct_principals": bool(seat_a and seat_b and seat_a != seat_b),
    }
    if extra:
        body.update(dict(extra))
    body["integrity"] = {"alg": "sha256", "content_hash": content_hash(hashable_body(body))}
    return DecisionRecord(body)
