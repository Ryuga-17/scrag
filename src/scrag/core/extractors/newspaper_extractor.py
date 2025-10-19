"""Newspaper3k-backed extractor implementation."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseExtractor, ExtractionContext, ExtractionResult

try:
    from newspaper import Article
except ImportError:  # pragma: no cover - exercised in unit tests
    Article = None  # type: ignore[assignment]


class NewspaperExtractor(BaseExtractor):
    """Strategy that uses newspaper3k to extract article content."""

    def __init__(self, *, language: Optional[str] = None) -> None:
        super().__init__(name="newspaper")
        self._language = language

    def supports(self, context: ExtractionContext) -> bool:
        return bool(context.url)

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        if not context.url:
            return ExtractionResult(content="", succeeded=False, metadata={"reason": "missing_url"})

        if Article is None:
            message = "newspaper3k is not installed; install 'newspaper3k' to enable this extractor."
            return ExtractionResult(content="", succeeded=False, metadata={"reason": message})

        try:
            article = Article(context.url, language=self._language)
            article.download()
            article.parse()
        except Exception as error:  # pragma: no cover - requires external dependency
            return ExtractionResult(content="", succeeded=False, metadata={"reason": str(error)})

        metadata: Dict[str, Any] = {
            "extractor": self.name,
            "title": article.title,
            "authors": article.authors,
            "publish_date": article.publish_date.isoformat() if article.publish_date else None,
            **context.metadata,
        }
        return ExtractionResult(content=article.text, succeeded=True, metadata=metadata)
