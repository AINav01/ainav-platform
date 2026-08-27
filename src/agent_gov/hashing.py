"""Canonical action hashing. Any field change must change the hash."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from agent_gov.errors import AdmitDenied

# Fields that bind the privileged write. Extra keys are also hashed so callers
# cannot smuggle unbound payload beside a stable five-tuple.
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


def normalize_action(action: Any) -> dict[str, Any]:
    """Coerce an action into a JSON-canonical mapping. Fail-closed otherwise."""
    if action is None:
        raise AdmitDenied("action is required", reason_code="ACTION_MISSING")
    if isinstance(action, Mapping):
        raw = dict(action)
    elif hasattr(action, "to_canonical") and callable(action.to_canonical):
        raw = action.to_canonical()
        if not isinstance(raw, Mapping):
            raise AdmitDenied("action.to_canonical() must return a mapping")
        raw = dict(raw)
    else:
        raise AdmitDenied(
            "action must be a mapping or expose to_canonical()",
            reason_code="ACTION_TYPE",
        )
    if not raw:
        raise AdmitDenied("action must not be empty", reason_code="ACTION_EMPTY")
    try:
        # Round-trip through canonical JSON so the hash is stable and types
        # that json cannot represent fail here, not after consume.
        return json.loads(canonical_json(raw))
    except (TypeError, ValueError) as exc:
        raise AdmitDenied(
            f"action is not canonical-JSON serializable: {exc}",
            reason_code="ACTION_NOT_CANONICAL",
        ) from exc


def action_hash(action: Any) -> str:
    """SHA-256 hex digest of the canonical action document."""
    body = canonical_json(normalize_action(action))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def content_hash(document: Mapping[str, Any]) -> str:
    """SHA-256 hex digest of an arbitrary canonical document."""
    body = canonical_json(dict(document))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()
