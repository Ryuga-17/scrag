"""Processor interfaces and base implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ProcessingContext:
    """Input payload for processor components."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProcessingResult:
    """Output from processor components."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseProcessor(ABC):
    """Base class for content processors."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def process(self, context: ProcessingContext) -> ProcessingResult:
        """Transform processed content and metadata."""


class SimpleProcessor(BaseProcessor):
    """Basic processor that trims whitespace."""

    def __init__(self) -> None:
        super().__init__(name="simple")

    def process(self, context: ProcessingContext) -> ProcessingResult:
        """Return content stripped of surrounding whitespace."""

        cleaned = context.content.strip()
        updated_meta = {"processor": self.name, **context.metadata}
        return ProcessingResult(content=cleaned, metadata=updated_meta)
