"""Extraction strategy interfaces and implementations."""

from inspect import Parameter, signature
from typing import Dict, Iterable, List

from .base import BaseExtractor, ExtractionContext, ExtractionResult, SimpleExtractor
from .newspaper_extractor import NewspaperExtractor
from .readability_extractor import ReadabilityExtractor
from .async_extractor import AsyncHttpExtractor

EXTRACTOR_REGISTRY = {
    "http": SimpleExtractor,
    "simple": SimpleExtractor,
    "newspaper": NewspaperExtractor,
    "readability": ReadabilityExtractor,
    "async_http": AsyncHttpExtractor,
    "async": AsyncHttpExtractor,
}


def build_extractors(names: Iterable[str], *, options: Dict[str, Dict] | None = None) -> List[BaseExtractor]:
    """Instantiate extractors defined in configuration order."""

    options = options or {}
    extractors: List[BaseExtractor] = []
    for name in names:
        cls = EXTRACTOR_REGISTRY.get(name)
        if not cls:
            continue
        kwargs = options.get(name, {})
        if kwargs:
            init_params = signature(cls).parameters
            accepts_kwargs = any(param.kind == Parameter.VAR_KEYWORD for param in init_params.values())
            if not accepts_kwargs:
                kwargs = {key: value for key, value in kwargs.items() if key in init_params}
        extractors.append(cls(**kwargs))
    return extractors


__all__ = [
    "BaseExtractor",
    "ExtractionContext",
    "ExtractionResult",
    "SimpleExtractor",
    "NewspaperExtractor",
    "ReadabilityExtractor",
    "AsyncHttpExtractor",
    "EXTRACTOR_REGISTRY",
    "build_extractors",
]
