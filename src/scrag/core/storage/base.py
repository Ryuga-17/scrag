"""Storage adapter interfaces and basic implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import json
import re


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
    path: Optional[Path] = None


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


class FileStorage(BaseStorageAdapter):
    """Persist content to disk for future retrieval."""

    SUPPORTED_FORMATS = {"json", "txt", "ndjson", "md"}

    def __init__(self, directory: Path, *, format: str = "json", filename: Optional[str] = None) -> None:
        super().__init__(name="file")
        self._directory = directory
        self._format = format.lower()
        self._filename_override = filename
        self._directory.mkdir(parents=True, exist_ok=True)
        
        if self._format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format '{format}'. Supported formats: {', '.join(sorted(self.SUPPORTED_FORMATS))}")

    def store(self, context: StorageContext) -> StorageResult:
        filename = (
            _sanitize_filename(self._filename_override)
            if self._filename_override
            else _build_filename(context.metadata)
        )
        path = self._directory / f"{filename}.{self._format}"

        if self._format == "json":
            payload = {
                "content": context.content,
                "metadata": context.metadata,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf8")
        elif self._format == "ndjson":
            # Create line-delimited JSON where each line is a separate JSON object
            # For ndjson, we write each field as a separate JSON object on its own line
            timestamp = datetime.now(timezone.utc).isoformat()
            lines = [
                json.dumps({"content": context.content}, ensure_ascii=False),
                json.dumps({"metadata": context.metadata}, ensure_ascii=False),
                json.dumps({"timestamp": timestamp}, ensure_ascii=False),
            ]
            path.write_text("\n".join(lines), encoding="utf8")
        elif self._format == "md":
            # Create markdown format with content and metadata
            md_content = []
            if context.metadata.get("title"):
                md_content.append(f"# {context.metadata['title']}\n")
            if context.metadata.get("url"):
                md_content.append(f"**Source URL:** {context.metadata['url']}\n")
            if context.metadata.get("author"):
                md_content.append(f"**Author:** {context.metadata['author']}\n")
            if context.metadata.get("date"):
                md_content.append(f"**Date:** {context.metadata['date']}\n")
            
            md_content.append("---\n\n")
            md_content.append(context.content)
            
            path.write_text("".join(md_content), encoding="utf8")
        else:  # txt format
            path.write_text(context.content, encoding="utf8")

        meta = {"storage": self.name, "path": str(path), **context.metadata}
        return StorageResult(success=True, metadata=meta, path=path)


STORAGE_REGISTRY = {
    "memory": InMemoryStorage,
    "file": FileStorage,
}


def build_storage(name: str, *, options: Dict[str, Any] | None = None) -> BaseStorageAdapter:
    cls = STORAGE_REGISTRY.get(name)
    if not cls:
        raise ValueError(f"Unknown storage backend '{name}'")
    options = options or {}
    if cls is FileStorage:
        if "directory" not in options:
            raise ValueError("FileStorage requires a 'directory' option")
        options["directory"] = Path(options["directory"])
    return cls(**options)


def _build_filename(metadata: Dict[str, Any]) -> str:
    base = metadata.get("title") or metadata.get("url") or "scrag-output"
    base = str(base)
    base = base.strip().lower() or "scrag-output"
    base = re.sub(r"[^a-z0-9]+", "-", base)
    base = base.strip("-") or "scrag-output"
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{base}-{suffix}"


def _sanitize_filename(filename: str) -> str:
    base = Path(filename).stem
    base = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-") or "scrag-output"
    return base
