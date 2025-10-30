"""Base classes for web renderer extractors (Selenium, Playwright)."""

from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .base import BaseExtractor, ExtractionContext, ExtractionResult

logger = logging.getLogger(__name__)


@dataclass
class WebRenderConfig:
    """Configuration for web rendering extractors."""
    
    timeout: int = 30
    page_load_timeout: int = 30
    implicit_wait: int = 10
    headless: bool = True
    window_width: int = 1920
    window_height: int = 1080
    user_agent: Optional[str] = None
    javascript_enabled: bool = True
    wait_for_selector: Optional[str] = None
    wait_for_text: Optional[str] = None
    screenshot_on_error: bool = False
    custom_wait_script: Optional[str] = None


class WebRenderExtractor(BaseExtractor):
    """Base class for JavaScript-enabled web extractors.
    
    This class provides common functionality for extractors that need
    to execute JavaScript and wait for dynamic content to load.
    """
    
    def __init__(
        self, 
        name: str, 
        config: Optional[WebRenderConfig] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(name=name)
        self.config = config or WebRenderConfig()
        
        # Override config with any kwargs
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    @abstractmethod
    def _initialize_driver(self) -> Any:
        """Initialize and return the web driver instance."""
        
    @abstractmethod
    def _navigate_to_url(self, driver: Any, url: str) -> None:
        """Navigate to the specified URL."""
        
    @abstractmethod
    def _wait_for_page_load(self, driver: Any) -> None:
        """Wait for the page to fully load."""
        
    @abstractmethod
    def _extract_content(self, driver: Any) -> str:
        """Extract text content from the loaded page."""
        
    @abstractmethod
    def _get_page_title(self, driver: Any) -> Optional[str]:
        """Get the page title."""
        
    @abstractmethod
    def _cleanup_driver(self, driver: Any) -> None:
        """Clean up and close the driver."""
        
    def extract(self, context: ExtractionContext) -> ExtractionResult:
        """Extract content from a JavaScript-heavy web page."""
        
        if not context.url:
            return ExtractionResult(
                content="",
                metadata={"extractor": self.name, "reason": "missing_url"},
                succeeded=False,
            )
        
        driver = None
        try:
            # Initialize web driver
            driver = self._initialize_driver()
            
            # Apply context-specific config overrides
            if context.metadata:
                for key, value in context.metadata.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            
            # Navigate to URL
            logger.info(f"Navigating to {context.url} with {self.name}")
            self._navigate_to_url(driver, context.url)
            
            # Wait for page to load
            self._wait_for_page_load(driver)
            
            # Extract content
            content = self._extract_content(driver)
            
            # Get additional metadata
            title = self._get_page_title(driver)
            
            metadata = {
                "extractor": self.name,
                "timeout": self.config.timeout,
                "page_load_timeout": self.config.page_load_timeout,
                "headless": self.config.headless,
                "title": title,
                **(context.metadata or {}),
            }
            
            return ExtractionResult(
                content=content,
                metadata=metadata,
                succeeded=bool(content.strip()),
            )
            
        except Exception as error:
            logger.error(f"Web rendering extraction failed for {context.url}: {error}")
            
            error_metadata = {
                "extractor": self.name,
                "reason": str(error),
                "error_type": type(error).__name__,
                **(context.metadata or {}),
            }
            
            return ExtractionResult(
                content="",
                metadata=error_metadata,
                succeeded=False,
            )
            
        finally:
            if driver:
                try:
                    self._cleanup_driver(driver)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup driver: {cleanup_error}")
    
    def supports(self, context: ExtractionContext) -> bool:
        """Check if this extractor can handle the given context."""
        return bool(context.url and context.url.startswith(("http://", "https://")))


class WebRenderDependencyError(ImportError):
    """Raised when web rendering dependencies are not available."""
    
    def __init__(self, extractor_name: str, dependencies: List[str]) -> None:
        self.extractor_name = extractor_name
        self.dependencies: List[str] = dependencies
        deps_str = ", ".join(dependencies)
        super().__init__(
            f"{extractor_name} extractor requires optional dependencies: {deps_str}. "
            f"Install with: pip install 'scrag[web-render]'"
        )


def check_web_render_dependency(dependency_name: str, import_names: List[str]) -> None:
    """Check if a web rendering dependency is available."""
    for import_name in import_names:
            try:
            __import__(import_name)
        except ImportError:
            raise WebRenderDependencyError(dependency_name, import_names)