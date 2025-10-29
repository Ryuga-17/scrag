"""Extraction strategy interfaces and implementations."""
from functools import partial
import logging
from inspect import Parameter, signature
from typing import Dict, Iterable, List, Optional, Type

from .base import BaseExtractor, ExtractionContext, ExtractionResult, SimpleExtractor
from .newspaper_extractor import NewspaperExtractor
from .readability_extractor import ReadabilityExtractor
from .async_extractor import AsyncHttpExtractor

logger = logging.getLogger(__name__)

# Registry for always-available extractors
EXTRACTOR_REGISTRY = {
    "http": SimpleExtractor,
    "simple": SimpleExtractor,
    "newspaper": NewspaperExtractor,
    "readability": ReadabilityExtractor,
    "async_http": AsyncHttpExtractor,
    "async": AsyncHttpExtractor,
}

# Registry for optional web-render extractors
WEB_RENDER_EXTRACTORS = {}

# Try to register Selenium extractor
try:
    from .selenium_extractor import SeleniumExtractor
    WEB_RENDER_EXTRACTORS["selenium"] = SeleniumExtractor
    WEB_RENDER_EXTRACTORS["selenium_chrome"] = partial(SeleniumExtractor, browser="chrome")
    WEB_RENDER_EXTRACTORS["selenium_firefox"] = partial(SeleniumExtractor, browser="firefox")
except ImportError as e:
    logger.debug(f"Selenium extractor not available: {e}")

# Try to register Playwright extractor
try:
    from .playwright_extractor import PlaywrightExtractor
    WEB_RENDER_EXTRACTORS["playwright"] = PlaywrightExtractor
    WEB_RENDER_EXTRACTORS["playwright_chromium"] = partial(PlaywrightExtractor, browser="chromium")
    WEB_RENDER_EXTRACTORS["playwright_firefox"] = partial(PlaywrightExtractor, browser="firefox")
    WEB_RENDER_EXTRACTORS["playwright_webkit"] = partial(PlaywrightExtractor, browser="webkit")
except ImportError as e:
    logger.debug(f"Playwright extractor not available: {e}")

# Combine registries
ALL_EXTRACTORS = {**EXTRACTOR_REGISTRY, **WEB_RENDER_EXTRACTORS}


def get_available_extractors() -> Dict[str, Type[BaseExtractor]]:
    """Get all currently available extractors."""
    return ALL_EXTRACTORS.copy()


def is_web_render_extractor(name: str) -> bool:
    """Check if an extractor requires web-render dependencies."""
    return name in WEB_RENDER_EXTRACTORS


def get_missing_web_render_dependencies() -> List[str]:
    """Get list of missing web-render extractor dependencies."""
    missing = []
    
    # Check Selenium
    if "selenium" not in WEB_RENDER_EXTRACTORS:
        missing.append("selenium")
    
    # Check Playwright
    if "playwright" not in WEB_RENDER_EXTRACTORS:
        missing.append("playwright")
    
    return missing


def build_extractors(names: Iterable[str], *, options: Dict[str, Dict] | None = None) -> List[BaseExtractor]:
    """Instantiate extractors defined in configuration order.
    
    Args:
        names: List of extractor names to build
        options: Optional configuration dict for each extractor
        
    Returns:
        List of successfully instantiated extractors
        
    Note:
        Web-render extractors that are missing dependencies will be skipped
        with a warning. Use get_missing_web_render_dependencies() to check
        what's missing.
    """
    options = options or {}
    extractors: List[BaseExtractor] = []
    
    for name in names:
        cls = ALL_EXTRACTORS.get(name)
        if not cls:
            logger.warning(f"Unknown extractor: {name}")
            continue
        
        # Check if this is a web-render extractor that might fail
        if is_web_render_extractor(name):
            if name not in WEB_RENDER_EXTRACTORS:
                logger.warning(
                    f"Web-render extractor '{name}' is not available. "
                    f"Install with: pip install 'scrag[web-render]'"
                )
                continue
        
        try:
            kwargs = options.get(name, {})
            if kwargs:
                init_params = signature(cls).parameters
                accepts_kwargs = any(param.kind == Parameter.VAR_KEYWORD for param in init_params.values())
                if not accepts_kwargs:
                    kwargs = {key: value for key, value in kwargs.items() if key in init_params}
            
            # Handle callable factory functions
            if callable(cls) and not isinstance(cls, type):
                extractor = cls(**kwargs)
            else:
                extractor = cls(**kwargs)
                
            extractors.append(extractor)
            logger.debug(f"Successfully built extractor: {name}")
            
        except Exception as e:
            logger.error(f"Failed to build extractor '{name}': {e}")
            
            # Provide helpful error messages for web-render extractors
            if is_web_render_extractor(name):
                logger.error(
                    f"Web-render extractor '{name}' failed to initialize. "
                    f"Ensure dependencies are installed: pip install 'scrag[web-render]'"
                )
    
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
    "WEB_RENDER_EXTRACTORS",
    "ALL_EXTRACTORS",
    "build_extractors",
    "get_available_extractors",
    "is_web_render_extractor",
    "get_missing_web_render_dependencies",
]
