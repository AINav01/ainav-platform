"""Shared authority store. ConsumeLedger and EffectLedger default to one plane."""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol

from agent_gov.clock import utc_now
from agent_gov.errors import ConsumeReplay, EffectBlocked, IntegrityError
from agent_gov.grant import grant_id
from agent_gov.hashing import canonical_json, content_hash, hashes_equal
from agent_gov.merkle import leaf_hash, merkle_root, prove_record
from agent_gov.records import (
    EFFECT_STATES,
    GENESIS_HASH,
    SCHEMA_VERSION,
    as_sealed,
    hashable_body,
    new_record_id,
    verify_chain,
    verify_record,
)

AdmitRecord = dict[str, Any]
EffectRecord = dict[str, Any]


class AuthorityStore(Protocol):
    def try_consume(self, slot_key: str, record: Mapping[str, Any]) -> AdmitRecord: ...

    def get_admit(self, request_id: str) -> AdmitRecord | None: ...

    def get_by_slot(self, slot_key: str) -> AdmitRecord | None: ...

    def reserve_effect(self, request_id: str, action_hash: str) -> EffectRecord: ...

    def finalize_effect(
        self,
        request_id: str,
        action_hash: str,
        *,
        record_type: str,
        apply_result: Any = None,
    ) -> EffectRecord: ...

    def try_effect(self, request_id: str, action_hash: str) -> EffectRecord: ...

    def get_effect(self, request_id: str) -> EffectRecord | None: ...

    def put_denied(self, record: Mapping[str, Any]) -> AdmitRecord: ...

    def decisions(self) -> list[dict[str, Any]]: ...

    def tip(self) -> str: ...


class MemoryAuthorityStore:
    """Process-local store. Consume is atomic (validate-all-then-write-all)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._slots: dict[str, AdmitRecord] = {}
        self._admits: dict[str, AdmitRecord] = {}
        self._effects: dict[str, EffectRecord] = {}
        self._denied: list[AdmitRecord] = []
        self._chain: list[dict[str, Any]] = []
        self._tip = GENESIS_HASH

    def tip(self) -> str:
        with self._lock:
            return self._tip

    def _seal(self, record: Mapping[str, Any]) -> dict[str, Any]:
        body = hashable_body(record)
        body.setdefault("schema_version", SCHEMA_VERSION)
        body.setdefault("record_id", new_record_id())
        body["prev_receipt_hash"] = self._tip
        body["seq"] = len(self._chain) + 1
        digest = content_hash(body)
        sealed = dict(body)
        sealed["integrity"] = {
            "alg": "sha256",
            "content_hash": digest,
            "prev_receipt_hash": self._tip,
        }
        self._chain.append(sealed)
        self._tip = digest
        self._after_seal(sealed)
        return sealed

    def _after_seal(self, sealed: Mapping[str, Any]) -> None:
        return None

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
            sealed = self._seal(stored)
            self._slots[slot_key] = sealed
            self._admits[str(sealed["request_id"])] = sealed
            return as_sealed(sealed)

    def get_admit(self, request_id: str) -> AdmitRecord | None:
        with self._lock:
            rec = self._admits.get(request_id)
            return as_sealed(rec) if rec is not None else None

    def get_by_slot(self, slot_key: str) -> AdmitRecord | None:
        with self._lock:
            rec = self._slots.get(slot_key)
            return as_sealed(rec) if rec is not None else None

    def _require_admit(self, request_id: str, action_hash: str) -> AdmitRecord:
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
        if not hashes_equal(admit.get("action_hash"), action_hash):
            raise EffectBlocked(
                "action_hash does not match admitted grant",
                reason_code="EFFECT_HASH_MISMATCH",
            )
        expected_grant = grant_id(
            action_hash=str(admit.get("action_hash")),
            seat_a=str(admit.get("seat_a")),
            seat_b=str(admit.get("seat_b")),
            policy_hash=str(admit.get("policy_hash") or ""),
        )
        stored_grant = admit.get("grant_id")
        if not stored_grant or not isinstance(stored_grant, str):
            raise EffectBlocked(
                "admit_ok missing grant_id",
                reason_code="GRANT_MISSING",
            )
        if not hashes_equal(stored_grant, expected_grant):
            raise EffectBlocked(
                "grant_id does not bind seats to action_hash",
                reason_code="GRANT_MISMATCH",
            )
        return admit

    def reserve_effect(self, request_id: str, action_hash: str) -> EffectRecord:
        with self._lock:
            admit = self._require_admit(request_id, action_hash)
            if request_id in self._effects:
                raise EffectBlocked(
                    f"effect already reserved or applied for request_id={request_id}",
                    reason_code="EFFECT_REPLAY",
                )
            effect: EffectRecord = {
                "record_type": "effect_reserved",
                "request_id": request_id,
                "action_hash": action_hash,
                "slot_key": admit.get("slot_key"),
                "seat_a": admit.get("seat_a"),
                "seat_b": admit.get("seat_b"),
                "policy_id": admit.get("policy_id"),
                "policy_hash": admit.get("policy_hash"),
                "grant_id": admit.get("grant_id"),
                "record_id": admit.get("record_id"),
            }
            sealed = self._seal(effect)
            self._effects[request_id] = sealed
            return as_sealed(sealed)

    def finalize_effect(
        self,
        request_id: str,
        action_hash: str,
        *,
        record_type: str,
        apply_result: Any = None,
    ) -> EffectRecord:
        if record_type not in {"effect_applied", "effect_apply_failed"}:
            raise EffectBlocked(
                f"invalid effect final state {record_type!r}",
                reason_code="EFFECT_STATE",
            )
        with self._lock:
            current = self._effects.get(request_id)
            if current is None or current.get("record_type") != "effect_reserved":
                raise EffectBlocked(
                    f"effect is not reserved for request_id={request_id}",
                    reason_code="EFFECT_NOT_RESERVED",
                )
            if not hashes_equal(current.get("action_hash"), action_hash):
                raise EffectBlocked(
                    "action_hash does not match reserved effect",
                    reason_code="EFFECT_HASH_MISMATCH",
                )
            final = hashable_body(current)
            final["record_type"] = record_type
            if apply_result is not None:
                final["apply_result"] = apply_result
            if record_type == "effect_applied":
                final["effected_at"] = utc_now()
            sealed = self._seal(final)
            self._effects[request_id] = sealed
            return as_sealed(sealed)

    def try_effect(self, request_id: str, action_hash: str) -> EffectRecord:
        """Backward-compatible alias for reserve_effect."""
        return self.reserve_effect(request_id, action_hash)

    def get_effect(self, request_id: str) -> EffectRecord | None:
        with self._lock:
            rec = self._effects.get(request_id)
            return as_sealed(rec) if rec is not None else None

    def put_denied(self, record: Mapping[str, Any]) -> AdmitRecord:
        stored = dict(record)
        stored["consumed"] = False
        with self._lock:
            sealed = self._seal(stored)
            self._denied.append(sealed)
            return as_sealed(sealed)

    def decisions(self) -> list[dict[str, Any]]:
        with self._lock:
            return [as_sealed(v) for v in self._chain]

    def get_record(self, record_id: str) -> dict[str, Any] | None:
        with self._lock:
            for rec in self._chain:
                if rec.get("record_id") == record_id:
                    return as_sealed(rec)
        return None

    def verify(self) -> str:
        with self._lock:
            return verify_chain(self._chain)

    def merkle_root(self) -> str:
        with self._lock:
            return merkle_root([leaf_hash(rec) for rec in self._chain])

    def audit(self) -> dict[str, Any]:
        records = self.decisions()
        tip = verify_chain(records)
        root = merkle_root([leaf_hash(rec) for rec in records])
        counts: dict[str, int] = {}
        for rec in records:
            key = str(rec.get("record_type") or "unknown")
            counts[key] = counts.get(key, 0) + 1
        return {
            "ok": True,
            "count": len(records),
            "tip": tip,
            "merkle_root": root,
            "counts": counts,
        }

    def prove(self, record_id: str) -> dict[str, Any]:
        return prove_record(self.decisions(), record_id)


class FileAuthorityStore(MemoryAuthorityStore):
    """Append-only JSONL ledger. Reload rebuilds maps from the hash chain."""

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and self.path.stat().st_size:
            self._load()
        else:
            self.path.touch()

    def _replay(self, rec: Mapping[str, Any]) -> None:
        from agent_gov.invariants import check_admit_ok

        sealed = dict(rec)
        rtype = sealed.get("record_type")
        rid = sealed.get("request_id")
        self._chain.append(sealed)
        self._tip = sealed["integrity"]["content_hash"]
        if rtype == "admit_ok" and rid:
            check_admit_ok(sealed, policy_hash=str(sealed.get("policy_hash") or ""))
            self._admits[str(rid)] = sealed
            slot = sealed.get("slot_key")
            if slot:
                self._slots[str(slot)] = sealed
        elif rtype in EFFECT_STATES and rid:
            self._effects[str(rid)] = sealed
        else:
            self._denied.append(sealed)

    def _tip_path(self) -> Path:
        return self.path.with_name(self.path.name + ".tip")

    def _write_tip(self) -> None:
        payload = canonical_json(
            {
                "alg": "sha256",
                "count": len(self._chain),
                "merkle_root": merkle_root([leaf_hash(rec) for rec in self._chain]),
                "tip": self._tip,
            }
        ) + "\n"
        dest = self._tip_path()
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, dest)

    def _after_seal(self, sealed: Mapping[str, Any]) -> None:
        line = canonical_json(dict(sealed)) + "\n"
        with self.path.open("a", encoding="utf-8") as handle:
            try:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            except (ImportError, OSError):
                pass
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        self._write_tip()

    def _load(self) -> None:
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise IntegrityError(f"ledger unreadable: {exc}", reason_code="LEDGER_UNREADABLE") from exc
        for raw in lines:
            if not raw.strip():
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise IntegrityError("ledger JSONL is corrupt", reason_code="LEDGER_CORRUPT") from exc
            verify_record(rec)
            self._replay(rec)
        verify_chain(self._chain)
        tip_path = self._tip_path()
        if tip_path.exists():
            try:
                meta = json.loads(tip_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise IntegrityError("tip sidecar is corrupt", reason_code="LEDGER_CORRUPT") from exc
            if meta.get("count") != len(self._chain) or not hashes_equal(
                meta.get("tip"), self._tip
            ):
                raise IntegrityError(
                    "tip sidecar does not match ledger",
                    reason_code="TIP_MISMATCH",
                )


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
