"""Canonical action hashing. Any field change must change the hash.

Canonical JSON here is the JCS subset we need for Job C: UTF-8, sorted keys,
no insignificant whitespace, no NaN/Inf. That is the interop contract for
``action_hash`` and receipt ``content_hash``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Mapping
from typing import Any

from agent_gov.errors import AdmitDenied

HASH_FIELDS = (
    "action_class",
    "payload",
    "proposal_id",
    "sor_target",
    "policy_id",
)


def _strict_default(obj: Any) -> Any:
    raise TypeError(f"action is not JSON-canonical: {type(obj).__name__}")


def canonical_json(value: Any) -> str:
    """UTF-8 JSON, sorted keys, no whitespace variance."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=_strict_default,
        allow_nan=False,
    )


def sha256_hex(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def hashes_equal(left: Any, right: Any) -> bool:
    """Constant-time compare for hex digests. Fail-closed on type/length mismatch."""
    if not isinstance(left, str) or not isinstance(right, str):
        return False
    if len(left) != len(right):
        return False
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def normalize_action(action: Any) -> dict[str, Any]:
    """Coerce an action into a JSON-canonical mapping. Fail-closed otherwise."""
    if action is None:
        raise AdmitDenied("action is required", reason_code="ACTION_MISSING")
    if isinstance(action, Mapping):
        raw = dict(action)
    elif hasattr(action, "to_canonical") and callable(action.to_canonical):
        raw = action.to_canonical()
        if not isinstance(raw, Mapping):
            raise AdmitDenied(
                "action.to_canonical() must return a mapping",
                reason_code="ACTION_TYPE",
            )
        raw = dict(raw)
    else:
        raise AdmitDenied(
            "action must be a mapping or expose to_canonical()",
            reason_code="ACTION_TYPE",
        )
    if not raw:
        raise AdmitDenied("action must not be empty", reason_code="ACTION_EMPTY")
    try:
        return json.loads(canonical_json(raw))
    except (TypeError, ValueError) as exc:
        raise AdmitDenied(
            f"action is not canonical-JSON serializable: {exc}",
            reason_code="ACTION_NOT_CANONICAL",
        ) from exc


def action_hash(action: Any) -> str:
    """SHA-256 hex digest of the canonical action document."""
    return sha256_hex(canonical_json(normalize_action(action)))


def content_hash(document: Mapping[str, Any]) -> str:
    """SHA-256 hex digest of an arbitrary canonical document."""
    return sha256_hex(canonical_json(dict(document)))
