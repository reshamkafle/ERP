"""In-memory login brute-force lockout (per email)."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from app.core.config import get_settings


@dataclass
class _AttemptState:
    failures: int = 0
    locked_until: float = 0.0


_lock = threading.Lock()
_attempts: dict[str, _AttemptState] = {}


def _key(email: str) -> str:
    return email.strip().lower()


def is_locked(email: str) -> tuple[bool, int]:
    """Return (locked, seconds_remaining)."""
    settings = get_settings()
    now = time.monotonic()
    with _lock:
        state = _attempts.get(_key(email))
        if state is None or state.locked_until <= now:
            return False, 0
        remaining = max(1, int(state.locked_until - now))
        return True, remaining


def record_failure(email: str) -> None:
    settings = get_settings()
    lockout_seconds = settings.login_lockout_minutes * 60
    with _lock:
        key = _key(email)
        state = _attempts.setdefault(key, _AttemptState())
        state.failures += 1
        if state.failures >= settings.login_max_failures:
            state.locked_until = time.monotonic() + lockout_seconds
            state.failures = 0


def clear_failures(email: str) -> None:
    with _lock:
        _attempts.pop(_key(email), None)
