"""Offline stand-in for dual_consume.lua.

Contract (must match the Redis script):
- validate-all-then-write-all
- same-slot keys
- return '{ok}' | '{err}'
"""

from __future__ import annotations

import threading
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

OK = "{ok}"
ERR = "{err}"


class LuaSimulator:
    """In-memory EVAL of validate-all-then-write-all consume.

    If any KEY already exists, write nothing and return {err}.
    If every KEY is free, write every KEY with the same ARGV payload and
    return {ok}. Concurrent callers are serialized by an internal lock.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._keys: dict[str, dict[str, str]] = {}

    def eval(self, keys: Sequence[str], argv: Sequence[str] | None = None) -> str:
        if not keys:
            return ERR
        payload = _argv_payload(argv)
        with self._lock:
            for key in keys:
                if key in self._keys:
                    return ERR
            for key in keys:
                self._keys[key] = dict(payload)
            return OK

    def exists(self, key: str) -> bool:
        with self._lock:
            return key in self._keys

    def get(self, key: str) -> dict[str, str] | None:
        with self._lock:
            value = self._keys.get(key)
            return dict(value) if value is not None else None

    def keycount(self) -> int:
        with self._lock:
            return len(self._keys)

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._keys.pop(key, None) is not None


def _argv_payload(argv: Sequence[str] | None) -> dict[str, str]:
    argv = list(argv or [])
    # ARGV: request_id, action_hash, seat_a, seat_b, now  (extras kept)
    names = ("request_id", "action_hash", "seat_a", "seat_b", "consumed_at")
    payload: dict[str, str] = {}
    for i, name in enumerate(names):
        if i < len(argv):
            payload[name] = str(argv[i])
    if len(argv) > len(names):
        payload["extra"] = "\0".join(str(x) for x in argv[len(names) :])
    return payload


def dual_consume(sim: LuaSimulator, keys: Iterable[str], fields: Mapping[str, Any]) -> str:
    """Helper used by ConsumeLedger when a simulator is attached."""
    argv = [
        str(fields.get("request_id", "")),
        str(fields.get("action_hash", "")),
        str(fields.get("seat_a", "")),
        str(fields.get("seat_b", "")),
        str(fields.get("consumed_at", "")),
    ]
    return sim.eval(list(keys), argv)
