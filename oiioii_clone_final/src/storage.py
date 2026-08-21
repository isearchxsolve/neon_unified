"""
In-memory storage for the AI Animation Agent Platform.

Provides thread-safe storage abstraction for users, projects, workflows, jobs, and assets.
"""

from typing import Dict, List, Optional, TypeVar, Generic
from threading import RLock

T = TypeVar("T")

class InMemoryStorage(Generic[T]):
    """Thread-safe in-memory storage using re-entrant locks."""

    def __init__(self):
        self._store: Dict[str, T] = {}
        self._lock = RLock()

    def add(self, key: str, item: T) -> None:
        """Add an item to storage."""
        with self._lock:
            self._store[key] = item

    def get(self, key: str) -> Optional[T]:
        """Retrieve an item from storage."""
        with self._lock:
            return self._store.get(key)

    def all(self) -> List[T]:
        """Return all items."""
        with self._lock:
            return list(self._store.values())

    def delete(self, key: str) -> bool:
        """Remove an item from storage."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def count(self) -> int:
        """Return number of items in storage."""
        with self._lock:
            return len(self._store)

    def clear(self) -> None:
        """Clear all items."""
        with self._lock:
            self._store.clear()

    def filter(self, predicate) -> List[T]:
        """Filter items by predicate."""
        with self._lock:
            return [item for item in self._store.values() if predicate(item)]

# Global storage instances
users_store: InMemoryStorage = InMemoryStorage()
projects_store: InMemoryStorage = InMemoryStorage()
workflows_store: InMemoryStorage = InMemoryStorage()
jobs_store: InMemoryStorage = InMemoryStorage()
assets_store: InMemoryStorage = InMemoryStorage()
sessions_store: InMemoryStorage = InMemoryStorage()

def reset_all_stores() -> None:
    """Utility to clear all global stores between tests or request boundaries."""
    users_store.clear()
    projects_store.clear()
    workflows_store.clear()
    jobs_store.clear()
    assets_store.clear()
    sessions_store.clear()
