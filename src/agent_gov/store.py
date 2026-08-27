"""Shared authority store. ConsumeLedger and EffectLedger default to one plane."""

from __future__ import annotations

import threading
from collections.abc import Mapping
from typing import Any, Protocol

from agent_gov.errors import ConsumeReplay, EffectBlocked

AdmitRecord = dict[str, Any]
EffectRecord = dict[str, Any]


class AuthorityStore(Protocol):
    def try_consume(self, slot_key: str, record: Mapping[str, Any]) -> AdmitRecord: ...

    def get_admit(self, request_id: str) -> AdmitRecord | None: ...

    def get_by_slot(self, slot_key: str) -> AdmitRecord | None: ...

    def try_effect(self, request_id: str, action_hash: str) -> EffectRecord: ...

    def get_effect(self, request_id: str) -> EffectRecord | None: ...

    def put_denied(self, record: Mapping[str, Any]) -> AdmitRecord: ...

    def decisions(self) -> list[dict[str, Any]]: ...


class MemoryAuthorityStore:
    """Process-local store. Consume is atomic (validate-all-then-write-all)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._slots: dict[str, AdmitRecord] = {}
        self._admits: dict[str, AdmitRecord] = {}
        self._effects: dict[str, EffectRecord] = {}
        self._denied: list[AdmitRecord] = []

    def try_consume(self, slot_key: str, record: Mapping[str, Any]) -> AdmitRecord:
        payload = dict(record)
        with self._lock:
            if slot_key in self._slots:
                raise ConsumeReplay(
                    f"slot already consumed: {slot_key}",
                    reason_code="CONSUME_REPLAY",
                )
            stored = dict(payload)
            stored["slot_key"] = slot_key
            stored["consumed"] = True
            self._slots[slot_key] = stored
            request_id = str(stored["request_id"])
            self._admits[request_id] = stored
            return dict(stored)

    def get_admit(self, request_id: str) -> AdmitRecord | None:
        with self._lock:
            rec = self._admits.get(request_id)
            return dict(rec) if rec is not None else None

    def get_by_slot(self, slot_key: str) -> AdmitRecord | None:
        with self._lock:
            rec = self._slots.get(slot_key)
            return dict(rec) if rec is not None else None

    def try_effect(self, request_id: str, action_hash: str) -> EffectRecord:
        with self._lock:
            admit = self._admits.get(request_id)
            if admit is None:
                raise EffectBlocked(
                    f"no admit record for request_id={request_id}",
                    reason_code="EFFECT_NO_ADMIT",
                )
            if admit.get("record_type") != "admit_ok":
                raise EffectBlocked(
                    "admit was not ok; SoR write is forbidden",
                    reason_code="EFFECT_ADMIT_NOT_OK",
                )
            if admit.get("action_hash") != action_hash:
                raise EffectBlocked(
                    "action_hash does not match admitted grant",
                    reason_code="EFFECT_HASH_MISMATCH",
                )
            if request_id in self._effects:
                raise EffectBlocked(
                    f"effect already applied for request_id={request_id}",
                    reason_code="EFFECT_REPLAY",
                )
            effect: EffectRecord = {
                "record_type": "effect_applied",
                "request_id": request_id,
                "action_hash": action_hash,
                "slot_key": admit.get("slot_key"),
                "seat_a": admit.get("seat_a"),
                "seat_b": admit.get("seat_b"),
            }
            self._effects[request_id] = effect
            return dict(effect)

    def get_effect(self, request_id: str) -> EffectRecord | None:
        with self._lock:
            rec = self._effects.get(request_id)
            return dict(rec) if rec is not None else None

    def put_denied(self, record: Mapping[str, Any]) -> AdmitRecord:
        stored = dict(record)
        stored["consumed"] = False
        with self._lock:
            self._denied.append(stored)
            # Denied grants are auditable but never occupy a consume slot
            # and are never retrievable as an effectable admit.
            return dict(stored)

    def decisions(self) -> list[dict[str, Any]]:
        with self._lock:
            ok = [dict(v) for v in self._admits.values()]
            denied = [dict(v) for v in self._denied]
            effects = [dict(v) for v in self._effects.values()]
        return ok + denied + effects


_DEFAULT: MemoryAuthorityStore | None = None
_DEFAULT_GUARD = threading.Lock()


def default_store() -> MemoryAuthorityStore:
    global _DEFAULT
    with _DEFAULT_GUARD:
        if _DEFAULT is None:
            _DEFAULT = MemoryAuthorityStore()
        return _DEFAULT


def reset_default_store() -> MemoryAuthorityStore:
    """Replace the process-wide default store. For tests only."""
    global _DEFAULT
    with _DEFAULT_GUARD:
        _DEFAULT = MemoryAuthorityStore()
        return _DEFAULT
