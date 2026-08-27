"""Pinned Job C policy. Lockfiles cannot weaken hard invariants."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from agent_gov.errors import LockfileError
from agent_gov.hashing import canonical_json, content_hash

POLICY_ID = "dual-admit-v1"
LOCKFILE_SCHEMA = "agent_gov.lockfile.v1"

# These cannot be turned off by a lockfile, env flag, or caller argument.
HARD_INVARIANTS: dict[str, bool] = {
    "distinct_principals": True,
    "single_use_consume": True,
    "fail_closed": True,
}


def _as_bool(value: Any, key: str) -> bool:
    if isinstance(value, bool):
        return value
    raise LockfileError(f"lockfile invariant {key!r} must be a boolean")


@dataclass(frozen=True)
class Lockfile:
    """Pinned admit policy. Treat as a content-addressed document."""

    schema_version: str = LOCKFILE_SCHEMA
    product: str = "job_c"
    policy_id: str = POLICY_ID
    effect_gate: str = "strict"
    slot_prefix: str = "dual:"
    invariants: dict[str, bool] = field(default_factory=lambda: dict(HARD_INVARIANTS))
    policy_hash: str = ""

    def to_canonical(self) -> dict[str, Any]:
        return {
            "effect_gate": self.effect_gate,
            "invariants": {
                "distinct_principals": True,
                "fail_closed": True,
                "single_use_consume": True,
            },
            "policy_id": self.policy_id,
            "product": self.product,
            "schema_version": self.schema_version,
            "slot_prefix": self.slot_prefix,
        }

    def digest(self) -> str:
        return content_hash(self.to_canonical())

    def verify(self) -> None:
        if self.schema_version != LOCKFILE_SCHEMA:
            raise LockfileError(
                f"unsupported lockfile schema {self.schema_version!r}",
                reason_code="LOCKFILE_SCHEMA",
            )
        if self.product != "job_c":
            raise LockfileError(
                "lockfile product must be job_c",
                reason_code="LOCKFILE_PRODUCT",
            )
        if self.effect_gate != "strict":
            raise LockfileError(
                "effect_gate must be strict (fail-closed)",
                reason_code="LOCKFILE_EFFECT_GATE",
            )
        inv = self.invariants
        for key, required in HARD_INVARIANTS.items():
            if key not in inv:
                raise LockfileError(
                    f"lockfile missing hard invariant {key}",
                    reason_code="LOCKFILE_INVARIANT",
                )
            if _as_bool(inv[key], key) is not required:
                raise LockfileError(
                    f"lockfile cannot weaken hard invariant {key}",
                    reason_code="LOCKFILE_WEAKENED",
                )
        expected = self.digest()
        if self.policy_hash and self.policy_hash != expected:
            raise LockfileError(
                "lockfile policy_hash does not match canonical digest",
                reason_code="LOCKFILE_HASH_MISMATCH",
            )

    def slot_key(self, action_hash: str) -> str:
        if not action_hash or not isinstance(action_hash, str):
            raise LockfileError("action_hash required for slot key")
        return f"{self.slot_prefix}{action_hash}"


def default_lockfile() -> Lockfile:
    """Return the pinned Job C lockfile (deterministic policy_hash)."""
    draft = Lockfile()
    return Lockfile(
        schema_version=draft.schema_version,
        product=draft.product,
        policy_id=draft.policy_id,
        effect_gate=draft.effect_gate,
        slot_prefix=draft.slot_prefix,
        invariants=dict(HARD_INVARIANTS),
        policy_hash=draft.digest(),
    )


def load_lockfile(document: Mapping[str, Any] | Lockfile) -> Lockfile:
    """Load and verify a lockfile mapping. Fail-closed on any defect."""
    if isinstance(document, Lockfile):
        document.verify()
        return document
    if not isinstance(document, Mapping):
        raise LockfileError("lockfile must be a mapping or Lockfile")
    try:
        inv_raw = document.get("invariants", HARD_INVARIANTS)
        if not isinstance(inv_raw, Mapping):
            raise LockfileError("lockfile.invariants must be a mapping")
        lock = Lockfile(
            schema_version=str(document.get("schema_version", LOCKFILE_SCHEMA)),
            product=str(document.get("product", "job_c")),
            policy_id=str(document.get("policy_id", POLICY_ID)),
            effect_gate=str(document.get("effect_gate", "strict")),
            slot_prefix=str(document.get("slot_prefix", "dual:")),
            invariants={str(k): _as_bool(v, str(k)) for k, v in dict(inv_raw).items()},
            policy_hash=str(document.get("policy_hash", "")),
        )
    except LockfileError:
        raise
    except (TypeError, ValueError) as exc:
        raise LockfileError(f"lockfile parse failed: {exc}") from exc
    lock.verify()
    return lock


def lockfile_json(lock: Lockfile | None = None) -> str:
    lock = lock or default_lockfile()
    lock.verify()
    body = lock.to_canonical()
    body["policy_hash"] = lock.policy_hash or lock.digest()
    return canonical_json(body)


def dumps_lockfile(lock: Lockfile | None = None) -> str:
    return json.dumps(json.loads(lockfile_json(lock)), indent=2, sort_keys=True) + "\n"
