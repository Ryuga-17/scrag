"""Storage adapter interfaces and basic implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class StorageContext:
    """Normalized payload that is ready for persistence."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StorageResult:
    """Outcome returned by storage adapters."""

    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseStorageAdapter(ABC):
    """Abstract base for storage backends."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def store(self, context: StorageContext) -> StorageResult:
        """Persist the payload to the configured backend."""


class InMemoryStorage(BaseStorageAdapter):
    """In-memory storage useful for quick experiments and tests."""

    def __init__(self) -> None:
        super().__init__(name="memory")
        self._items: List[StorageContext] = []

    def store(self, context: StorageContext) -> StorageResult:
        """Append payloads to the in-memory list."""

        self._items.append(context)
        meta = {"storage": self.name, "items": len(self._items), **context.metadata}
        return StorageResult(success=True, metadata=meta)

    @property
    def items(self) -> List[StorageContext]:
        """Expose stored items for inspection in tests."""

        return list(self._items)
