"""Extractor interfaces and base implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ExtractionContext:
    """Input payload for extraction strategies."""

    url: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExtractionResult:
    """Normalized output from an extractor."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    succeeded: bool = True


class BaseExtractor(ABC):
    """Abstract base for all extraction strategies."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def extract(self, context: ExtractionContext) -> ExtractionResult:
        """Extract content from a URL-centered context."""

    def supports(self, context: ExtractionContext) -> bool:
        """Return True when the extractor can handle the given context."""

        return bool(context.url)


class SimpleExtractor(BaseExtractor):
    """Fallback extractor placeholder for scaffolding."""

    def __init__(self) -> None:
        super().__init__(name="simple")

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        """Return a minimal extraction result that echoes the context."""

        summary = f"Scraped placeholder for {context.url or 'unknown resource'}"
        combined_meta = {"extractor": self.name, **context.metadata}
        return ExtractionResult(
            content=summary,
            metadata=combined_meta,
            succeeded=bool(context.url),
        )
