"""Async HTTP extractor using aiohttp for concurrent scraping."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

try:
    import aiohttp
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover - exercised in unit tests
    aiohttp = None  # type: ignore[assignment]

from .base import BaseExtractor, ExtractionContext, ExtractionResult


class AsyncHttpExtractor(BaseExtractor):
    """Async extractor using aiohttp for concurrent batch scraping."""

    def __init__(
        self,
        *,
        user_agent: Optional[str] = None,
        timeout: int = 10,
        max_concurrent: int = 10,
    ) -> None:
        super().__init__(name="async_http")
        self._user_agent = user_agent or "ScragBot/0.1"
        self._timeout = timeout
        self._max_concurrent = max_concurrent

    def supports(self, context: ExtractionContext) -> bool:
        """Check if aiohttp is available."""
        return aiohttp is not None and bool(context.url)

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        """Extract content synchronously (for single URL compatibility)."""
        if not context.url:
            return ExtractionResult(
                content="",
                metadata={"extractor": self.name, "reason": "missing_url"},
                succeeded=False,
            )

        if aiohttp is None:
            return ExtractionResult(
                content="",
                metadata={"extractor": self.name, "reason": "aiohttp not installed"},
                succeeded=False,
            )

        try:
            return asyncio.run(self._extract_single(context.url))
        except Exception as error:
            return ExtractionResult(
                content="",
                metadata={"extractor": self.name, "reason": str(error)},
                succeeded=False,
            )

    async def _extract_single(self, url: str) -> ExtractionResult:
        """Extract content from a single URL using aiohttp."""
        timeout = aiohttp.ClientTimeout(total=self._timeout)
        headers = {"User-Agent": self._user_agent}

        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    html = await response.text()

                    soup = BeautifulSoup(html, "html.parser")
                    text_segments = list(s.strip() for s in soup.stripped_strings)
                    content = "\n".join(segment for segment in text_segments if segment)

                    metadata: Dict[str, Any] = {
                        "extractor": self.name,
                        "status_code": response.status,
                        "title": soup.title.string.strip() if soup.title and soup.title.string else None,
                    }

                    return ExtractionResult(
                        content=content,
                        metadata=metadata,
                        succeeded=bool(content.strip()),
                    )
            except asyncio.TimeoutError:
                return ExtractionResult(
                    content="",
                    metadata={"extractor": self.name, "reason": "Request timeout"},
                    succeeded=False,
                )
            except aiohttp.ClientError as error:
                return ExtractionResult(
                    content="",
                    metadata={"extractor": self.name, "reason": str(error)},
                    succeeded=False,
                )

    async def extract_batch(self, urls: List[str]) -> List[ExtractionResult]:
        """Extract content from multiple URLs concurrently."""
        if aiohttp is None:
            return [
                ExtractionResult(
                    content="",
                    metadata={"extractor": self.name, "reason": "aiohttp not installed"},
                    succeeded=False,
                )
            ] * len(urls)

        semaphore = asyncio.Semaphore(self._max_concurrent)

        async def fetch_with_semaphore(url: str) -> ExtractionResult:
            async with semaphore:
                return await self._extract_single(url)

        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    ExtractionResult(
                        content="",
                        metadata={"extractor": self.name, "reason": str(result)},
                        succeeded=False,
                    )
                )
            else:
                processed_results.append(result)

        return processed_results
