"""Redis dual-consume adapter. Offline gold uses LuaSimulator, not this."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol

from agent_gov.lua_simulator import ERR, OK, LuaSimulator

LUA_PATH = Path(__file__).with_name("dual_consume.lua")


class RedisLike(Protocol):
    def eval(self, script: str, numkeys: int, *parts: Any) -> Any: ...


class RedisDualConsume:
    """EVAL of dual_consume.lua: validate-all-then-write-all → {ok}|{err}.

    Does not import redis. Pass any client that implements ``eval``.
    Live multi-host HA is not claimed by constructing this class.
    """

    def __init__(self, client: RedisLike, *, script: str | None = None) -> None:
        self.client = client
        self.script = script if script is not None else LUA_PATH.read_text(encoding="utf-8")

    def eval(self, keys: Sequence[str], argv: Sequence[str] | None = None) -> str:
        argv = list(argv or [])
        keys = list(keys)
        raw = self.client.eval(self.script, len(keys), *keys, *argv)
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return str(raw)

    def delete(self, key: str) -> None:
        deleter = getattr(self.client, "delete", None)
        if callable(deleter):
            deleter(key)


class SimulatorRedis:
    """Redis-shaped client that honors the Lua contract in-process."""

    def __init__(self, simulator: LuaSimulator | None = None) -> None:
        self.simulator = simulator or LuaSimulator()

    def eval(self, script: str, numkeys: int, *parts: Any) -> str:
        if "{ok}" not in script or "{err}" not in script:
            return ERR
        keys = [str(p) for p in parts[:numkeys]]
        argv = [str(p) for p in parts[numkeys:]]
        result = self.simulator.eval(keys, argv)
        return result if result in {OK, ERR} else ERR

    def delete(self, key: str) -> None:
        self.simulator.delete(key)
