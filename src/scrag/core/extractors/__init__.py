"""Extraction strategy interfaces and implementations."""

from .base import BaseExtractor, ExtractionContext, ExtractionResult, SimpleExtractor
from .newspaper_extractor import NewspaperExtractor

__all__ = [
    "BaseExtractor",
    "ExtractionContext",
    "ExtractionResult",
    "SimpleExtractor",
    "NewspaperExtractor",
]
