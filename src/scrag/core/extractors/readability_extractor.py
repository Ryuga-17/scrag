"""Readability-based fallback extractor."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .base import BaseExtractor, ExtractionContext, ExtractionResult

try:
    from readability import Document
except ImportError:  # pragma: no cover - optional dependency at runtime
    Document = None  # type: ignore[assignment]


class ReadabilityExtractor(BaseExtractor):
    """Use readability-lxml to generate simplified article text."""

    def __init__(self, *, user_agent: Optional[str] = None, timeout: int = 10) -> None:
        super().__init__(name="readability")
        self._user_agent = user_agent or "ScragBot/0.1"
        self._timeout = timeout

    def supports(self, context: ExtractionContext) -> bool:
        return bool(context.url)

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        if not context.url:
            return ExtractionResult(content="", succeeded=False, metadata={"reason": "missing_url"})

        if Document is None:
            message = "readability-lxml is not installed; install 'readability-lxml' to enable this extractor."
            return ExtractionResult(content="", succeeded=False, metadata={"reason": message})

        headers = {"User-Agent": self._user_agent}
        headers.update(context.metadata.get("headers", {}))
        timeout = context.metadata.get("timeout", self._timeout)

        try:
            response = requests.get(context.url, headers=headers, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as error:  # pragma: no cover - network errors not deterministic
            return ExtractionResult(content="", succeeded=False, metadata={"reason": str(error)})

        document = Document(response.text)
        title = document.short_title()
        summary_html = document.summary()

        text = _strip_html(summary_html)
        metadata: Dict[str, Any] = {
            "extractor": self.name,
            "title": title,
            **context.metadata,
        }

        return ExtractionResult(content=text, succeeded=bool(text.strip()), metadata=metadata)


def _strip_html(html: str) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    return "\n".join(segment for segment in soup.stripped_strings)
