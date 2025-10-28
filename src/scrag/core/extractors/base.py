"""Extractor interfaces and base implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup

from core.cache import CacheStore, CacheableHTTPClient


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

    def __init__(
        self, 
        *, 
        user_agent: Optional[str] = None, 
        timeout: int = 10,
        cache_store: Optional[CacheStore] = None,
        use_cache: bool = True,
    ) -> None:
        super().__init__(name="http")
        self._user_agent = user_agent or "ScragBot/0.1"
        self._timeout = timeout
        self._use_cache = use_cache
        self._http_client = CacheableHTTPClient(
            cache_store=cache_store,
            user_agent=self._user_agent,
            timeout=self._timeout,
        )

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        """Fetch the page via HTTP and extract readable text using BeautifulSoup."""

        if not context.url:
            return ExtractionResult(
                content="",
                metadata={"extractor": self.name, "reason": "missing_url"},
                succeeded=False,
            )

        # Get headers and cache settings from context
        config_headers = context.metadata.get("headers", {}) if context.metadata else {}
        use_cache = context.metadata.get("use_cache", self._use_cache) if context.metadata else self._use_cache

        # Use the cacheable HTTP client
        content, status_code, response_headers = self._http_client.get(
            context.url,
            headers=config_headers,
            use_cache=use_cache,
        )

        if content is None or status_code is None:
            return ExtractionResult(
                content="",
                metadata={
                    "extractor": self.name,
                    "reason": response_headers.get("error", "unknown error"),
                },
                succeeded=False,
            )

        soup = BeautifulSoup(content, "html.parser")
        text_segments = list(s.strip() for s in soup.stripped_strings)
        extracted_content = "\n".join(segment for segment in text_segments if segment)

        metadata = {
            "extractor": self.name,
            "status_code": status_code,
            "title": soup.title.string.strip() if soup.title and soup.title.string else None,
            "cached": response_headers.get("cached", False),
            **(context.metadata or {}),
        }

        return ExtractionResult(
            content=extracted_content,
            metadata=metadata,
            succeeded=bool(extracted_content.strip()),
        )
