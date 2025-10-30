"""Extractor interfaces and base implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import requests

from ..utils.utils import parse_html_content
from ..utils.headers import normalize_headers, get_header_value


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

"""Extractor interfaces and base implementations."""

# ...existing imports...

class SimpleExtractor(BaseExtractor):
    """HTTP-based extractor that fetches and cleans web page content."""

    def __init__(self, *, user_agent: Optional[str] = None, timeout: int = 10) -> None:
        super().__init__(name="http")
        self._user_agent = user_agent or "ScragBot/0.1"
        self._timeout = timeout

    def _get_metadata_value(self, context: ExtractionContext, key: str, default: Any) -> Any:
        """Helper method to retrieve a value from context metadata."""
        return context.metadata.get(key, default) if context.metadata else default

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        """Fetch the page via HTTP and extract readable text using BeautifulSoup."""

        if not context.url:
            return ExtractionResult(
                content="",
                metadata={"extractor": self.name, "reason": "missing_url"},
                succeeded=False,
            )

        headers = {"User-Agent": self._user_agent}
        config_headers = self._get_metadata_value(context, "headers", {})
        headers.update(config_headers)
        
        # Normalize headers for case-insensitive handling
        headers = normalize_headers(headers)
        timeout = self._get_metadata_value(context, "timeout", self._timeout)

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

        content, metadata = parse_html_content(response.text, self.name, response.status_code)
        metadata.update(context.metadata or {})

        return ExtractionResult(
            content=content,
            metadata=metadata,
            succeeded=bool(content.strip()),
        )