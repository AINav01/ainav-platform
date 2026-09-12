"""Read-only examiner prove. Merkle inclusion. Not 17a-4. Not WORM."""

from __future__ import annotations

from typing import Any

from agent_gov.store import AuthorityStore, default_store


def prove(record_id: str, store: AuthorityStore | None = None) -> dict[str, Any]:
    """Wrap store.prove. Read-only. Not a filing and not a live pin."""
    if not record_id or not isinstance(record_id, str):
        from agent_gov.errors import IntegrityError

        raise IntegrityError("record_id is required", reason_code="EXAMINER_NO_RECORD")
    proof = (store or default_store()).prove(record_id)
    return {
        "kind": "ainav.examiner.v1",
        "read_only": True,
        "seventeen_a4": False,
        "worm": False,
        "live": False,
        "claimed": False,
        **proof,
    }


def action_schema() -> dict[str, Any]:
    import json
    from pathlib import Path

    path = Path(__file__).with_name("data") / "action.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))
