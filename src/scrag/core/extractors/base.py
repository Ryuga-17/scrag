"""Extractor interfaces and base implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup


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
    """HTTP-based extractor that fetches and cleans web page content."""

    def __init__(self, *, user_agent: Optional[str] = None, timeout: int = 10) -> None:
        super().__init__(name="http")
        self._user_agent = user_agent or "ScragBot/0.1"
        self._timeout = timeout

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        """Fetch the page via HTTP and extract readable text using BeautifulSoup."""

        if not context.url:
            return ExtractionResult(
                content="",
                metadata={"extractor": self.name, "reason": "missing_url"},
                succeeded=False,
            )

        headers = {"User-Agent": self._user_agent}
        config_headers = context.metadata.get("headers", {}) if context.metadata else {}
        headers.update(config_headers)
        timeout = context.metadata.get("timeout", self._timeout) if context.metadata else self._timeout

        try:
            response = requests.get(context.url, headers=headers, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as error:
            return ExtractionResult(
                content="",
                metadata={
                    "extractor": self.name,
                    "reason": str(error),
                },
                succeeded=False,
            )

        soup = BeautifulSoup(response.text, "html.parser")
        text_segments = list(s.strip() for s in soup.stripped_strings)
        content = "\n".join(segment for segment in text_segments if segment)

        metadata = {
            "extractor": self.name,
            "status_code": response.status_code,
            "title": soup.title.string.strip() if soup.title and soup.title.string else None,
            **(context.metadata or {}),
        }

        return ExtractionResult(
            content=content,
            metadata=metadata,
            succeeded=bool(content.strip()),
        )
