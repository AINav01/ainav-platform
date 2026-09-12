"""Injectable clock. Receipts stay deterministic when a frozen clock is set."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    def now(self) -> str: ...


class SystemClock:
    def now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class FrozenClock:
    def __init__(self, timestamp: str) -> None:
        self.timestamp = timestamp

    def now(self) -> str:
        return self.timestamp


_CLOCK: Clock = SystemClock()


def utc_now() -> str:
    return _CLOCK.now()


def set_clock(clock: Clock) -> None:
    global _CLOCK
    _CLOCK = clock


def reset_clock() -> None:
    global _CLOCK
    _CLOCK = SystemClock()
