"""Unforgeable grant ticket: seats + action_hash + policy_hash."""

from __future__ import annotations

from agent_gov.hashing import content_hash


def grant_id(
    *,
    action_hash: str,
    seat_a: str,
    seat_b: str,
    policy_hash: str,
) -> str:
    """Content-addressed grant. Seat swap or policy swap changes the id."""
    return content_hash(
        {
            "action_hash": action_hash,
            "policy_hash": policy_hash,
            "seat_a": seat_a,
            "seat_b": seat_b,
            "v": 1,
        }
    )
