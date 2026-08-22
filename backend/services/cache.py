"""Tiny in-memory TTL cache with staleness tracking."""

from datetime import datetime, timedelta
from typing import Any


class StaleAwareCache:
    """Per-key cache whose entries expire after `ttl` (default 2 hours)."""

    def __init__(self, ttl: timedelta = timedelta(hours=2)) -> None:
        self.ttl = ttl
        self._store: dict[str, tuple[datetime, Any]] = {}

    def set(self, key: str, value: Any, *, now: datetime | None = None) -> None:
        self._store[key] = (now or datetime.now(), value)

    def get(self, key: str, *, now: datetime | None = None) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        fetched_at, value = entry
        if self.is_stale(fetched_at, now=now):
            return None
        return value

    def fetched_at(self, key: str) -> datetime | None:
        entry = self._store.get(key)
        return entry[0] if entry else None

    def is_stale(self, fetched_at: datetime, *, now: datetime | None = None) -> bool:
        return (now or datetime.now()) - fetched_at > self.ttl

    def clear(self) -> None:
        self._store.clear()
