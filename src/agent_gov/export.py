"""Versioned export envelope for DecisionRecord chains."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from agent_gov.errors import IntegrityError
from agent_gov.hashing import hashes_equal
from agent_gov.records import verify_chain

EXPORT_SCHEMA = "agent_gov.export.v1"


def export_envelope(
    records: Sequence[Mapping[str, Any]],
    *,
    tip: str,
) -> dict[str, Any]:
    return {
        "schema_version": EXPORT_SCHEMA,
        "product": "job_c",
        "count": len(records),
        "tip": tip,
        "records": [dict(r) for r in records],
    }


def verify_export(document: Mapping[str, Any]) -> str:
    if document.get("schema_version") != EXPORT_SCHEMA:
        raise IntegrityError("unsupported export schema", reason_code="EXPORT_SCHEMA")
    if document.get("product") != "job_c":
        raise IntegrityError("export product must be job_c", reason_code="EXPORT_PRODUCT")
    records = document.get("records")
    if not isinstance(records, list):
        raise IntegrityError("export records must be a list")
    if document.get("count") != len(records):
        raise IntegrityError("export count does not match records")
    tip = verify_chain(records)
    if not hashes_equal(document.get("tip"), tip):
        raise IntegrityError("export tip does not match chain", reason_code="EXPORT_TIP")
    return tip
