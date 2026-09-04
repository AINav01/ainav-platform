from __future__ import annotations

import json

from agent_gov.errors import IntegrityError
from ainav.catalog import load_catalog, validate_catalog

STRUCTURE = {
    "edge",
    "quality",
    "host_freshness",
    "owner_ssl",
    "investor",
    "engineering",
    "executive_summary",
    "graph",
    "formal",
    "gold_ci",
    "gaps",
    "success",
    "walk",
    "activate",
    "holding",
    "client_dashboard",
    "motions",
    "hostname_rehearsal",
    "competitive",
    "entra_groups",
    "first_glance",
    "must_have",
    "public_face",
    "proof_day_floor",
    "pending_bind",
    "freeze_console",
    "examiner_walk",
    "view_assignment",
    "included_and_upsells",
    "grant_ttl",
    "ai_inventory",
    "admit_client",
    "examiner",
    "access",
    "dashboard",
    "floor",
    "plane_interface",
    "microsoft_stack",
    "expert_review",
    "organization",
    "bake_off",
    "qualify",
    "ciso",
    "seat_b",
    "continuity",
    "walk_away_ledger",
    "human_control",
    "print",
    "pricing_models",
}


def _walk(obj, prefix=()):
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = prefix + (key,)
            yield path, value
            yield from _walk(value, path)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            yield from _walk(item, prefix + (index,))


def _set_path(root, path, value):
    cursor = root
    for step in path[:-1]:
        cursor = cursor[step]
    cursor[path[-1]] = value


def _candidates(path, value):
    key = path[-1] if path else ""
    if isinstance(value, dict) and key in STRUCTURE:
        yield None
        yield "x"
    if isinstance(value, list) and 0 < len(value) <= 20:
        yield []
        if value and all(isinstance(item, str) for item in value):
            yield ["nope"]
    if isinstance(value, str) and 0 < len(value) <= 120:
        yield ""
        yield "nope"
    if value is True:
        yield False
    if value is None and key in {"entra_oid", "second_officer", "incorporation_date"}:
        yield "invented"
    if isinstance(value, int) and value == 0 and key in {"L1", "P-ADM", "U-DUAL", "count"}:
        yield 1


def test_catalog_mutation_walk_stays_fail_closed():
    original = load_catalog()
    raw = json.dumps(original)
    hits = 0
    for path, value in _walk(original):
        for candidate in _candidates(path, value):
            mutated = json.loads(raw)
            _set_path(mutated, path, candidate)
            try:
                validate_catalog(mutated)
            except IntegrityError:
                hits += 1
            except Exception as exc:
                raise AssertionError(
                    f"not fail-closed at {path}={candidate!r}: {type(exc).__name__}: {exc}"
                ) from exc
    assert hits >= 800
