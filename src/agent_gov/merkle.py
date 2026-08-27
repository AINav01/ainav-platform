"""Merkle tree over DecisionRecord content hashes.

The linear receipt chain is the source of order. The Merkle root is a compact
witness that a record is in that ledger — Certificate Transparency style,
without claiming a public log.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from agent_gov.errors import IntegrityError
from agent_gov.hashing import canonical_json, hashes_equal, sha256_hex
from agent_gov.records import GENESIS_HASH


def leaf_hash(record: Mapping[str, Any]) -> str:
    integrity = record.get("integrity")
    if not isinstance(integrity, Mapping) or not integrity.get("content_hash"):
        raise IntegrityError("record missing content_hash", reason_code="MERKLE_LEAF")
    return str(integrity["content_hash"])


def parent_hash(left: str, right: str) -> str:
    return sha256_hex(canonical_json({"L": left, "R": right}))


def merkle_root(leaves: Sequence[str]) -> str:
    if not leaves:
        return GENESIS_HASH
    layer = list(leaves)
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        layer = [parent_hash(layer[i], layer[i + 1]) for i in range(0, len(layer), 2)]
    return layer[0]


def inclusion_proof(leaves: Sequence[str], index: int) -> list[dict[str, str]]:
    if index < 0 or index >= len(leaves):
        raise IntegrityError("proof index out of range", reason_code="MERKLE_INDEX")
    proof: list[dict[str, str]] = []
    layer = list(leaves)
    idx = index
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        sibling = idx ^ 1
        side = "R" if idx % 2 == 0 else "L"
        proof.append({"side": side, "hash": layer[sibling]})
        layer = [parent_hash(layer[i], layer[i + 1]) for i in range(0, len(layer), 2)]
        idx //= 2
    return proof


def verify_inclusion(leaf: str, proof: Sequence[Mapping[str, str]], root: str) -> str:
    acc = leaf
    for step in proof:
        side = step.get("side")
        sibling = step.get("hash")
        if not isinstance(sibling, str):
            raise IntegrityError("proof step missing hash", reason_code="MERKLE_PROOF")
        if side == "R":
            acc = parent_hash(acc, sibling)
        elif side == "L":
            acc = parent_hash(sibling, acc)
        else:
            raise IntegrityError("proof step has invalid side", reason_code="MERKLE_PROOF")
    if not hashes_equal(acc, root):
        raise IntegrityError("inclusion proof does not match root", reason_code="MERKLE_MISMATCH")
    return acc


def prove_record(
    records: Sequence[Mapping[str, Any]],
    record_id: str,
) -> dict[str, Any]:
    leaves = [leaf_hash(rec) for rec in records]
    for i, rec in enumerate(records):
        if rec.get("record_id") == record_id:
            root = merkle_root(leaves)
            proof = inclusion_proof(leaves, i)
            verify_inclusion(leaves[i], proof, root)
            return {
                "record_id": record_id,
                "index": i,
                "leaf": leaves[i],
                "merkle_root": root,
                "proof": proof,
            }
    raise IntegrityError(f"record_id not in ledger: {record_id}", reason_code="MERKLE_MISSING")
