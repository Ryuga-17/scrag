"""Storage backends and adapters."""

from .base import BaseStorageAdapter, InMemoryStorage, StorageContext, StorageResult

__all__ = [
    "BaseStorageAdapter",
    "StorageContext",
    "StorageResult",
    "InMemoryStorage",
]
