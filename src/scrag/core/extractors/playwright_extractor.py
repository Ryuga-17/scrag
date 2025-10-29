"""Playwright-based extractor for JavaScript-heavy web pages."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from .web_render_base import (
    WebRenderConfig,
    WebRenderDependencyError,
    WebRenderExtractor,
    check_web_render_dependency,
)

logger = logging.getLogger(__name__)

# Check for Playwright dependencies at module import time
try:
    check_web_render_dependency("playwright", ["playwright"])
    
    from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
    
    PLAYWRIGHT_AVAILABLE = True
    
except ImportError as e:
    PLAYWRIGHT_AVAILABLE = False
    _playwright_error = e


class PlaywrightExtractor(WebRenderExtractor):
    """Playwright-based extractor for JavaScript-heavy pages.
    
    Supports Chromium, Firefox, and WebKit browsers with fast page rendering.
    Generally faster and more reliable than Selenium for modern web applications.
    
    Example usage:
        extractor = PlaywrightExtractor(
            browser="chromium",
            timeout=30,
            headless=True,
            wait_for_selector=".content"
        )
    """
    
    def __init__(
        self,
        browser: str = "chromium",
        config: Optional[WebRenderConfig] = None,
        **kwargs: Any
    ) -> None:
        if not PLAYWRIGHT_AVAILABLE:
            raise _playwright_error
            
        super().__init__(name="playwright", config=config, **kwargs)
        self.browser = browser.lower()
        
        if self.browser not in ("chromium", "firefox", "webkit"):
            raise ValueError(f"Unsupported browser: {browser}. Use 'chromium', 'firefox', or 'webkit'")
        
        self._playwright = None
        self._browser_instance = None
    
    def _initialize_driver(self) -> Page:
        """Initialize and configure the Playwright browser and page."""
        try:
            # Initialize Playwright
            self._playwright = sync_playwright().start()
            
            # Launch browser
            if self.browser == "chromium":
                self._browser_instance = self._playwright.chromium.launch(
                    headless=self.config.headless,
                    args=self._get_browser_args()
                )
            elif self.browser == "firefox":
                self._browser_instance = self._playwright.firefox.launch(
                    headless=self.config.headless,
                    args=self._get_browser_args()
                )
            elif self.browser == "webkit":
                self._browser_instance = self._playwright.webkit.launch(
                    headless=self.config.headless
                )
            
            # Create browser context
            context_options = {
                "viewport": {
                    "width": self.config.window_width,
                    "height": self.config.window_height
                },
                "java_script_enabled": self.config.javascript_enabled,
            }
            
            if self.config.user_agent:
                context_options["user_agent"] = self.config.user_agent
            
            context = self._browser_instance.new_context(**context_options)
            
            # Create new page
            page = context.new_page()
            
            # Set timeouts
            page.set_default_timeout(self.config.timeout * 1000)  # Playwright uses milliseconds
            page.set_default_navigation_timeout(self.config.page_load_timeout * 1000)
            
            return page
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.browser} browser: {e}")
            self._cleanup_playwright()
            raise
    
    def _get_browser_args(self) -> List[str]:
        """Get browser launch arguments."""
        args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
        ]
        
        return args
    
    def _navigate_to_url(self, page: Page, url: str) -> None:
        """Navigate to the specified URL."""
        page.goto(url, wait_until="domcontentloaded")
    
    def _wait_for_page_load(self, page: Page) -> None:
        """Wait for the page to fully load based on configuration."""
        try:
            # Wait for network to be idle (no requests for 500ms)
            page.wait_for_load_state("networkidle", timeout=self.config.timeout * 1000)
            
            # Wait for specific selector if provided
            if self.config.wait_for_selector:
                page.wait_for_selector(
                    self.config.wait_for_selector, 
                    timeout=self.config.timeout * 1000
                )
                logger.debug(f"Found selector: {self.config.wait_for_selector}")
            
            # Wait for specific text if provided
            if self.config.wait_for_text:
                page.wait_for_function(
                    f"document.body.innerText.includes('{self.config.wait_for_text}')",
                    timeout=self.config.timeout * 1000
                )
                logger.debug(f"Found text: {self.config.wait_for_text}")
            
            # Execute custom wait script if provided
            if self.config.custom_wait_script:
                page.wait_for_function(
                    self.config.custom_wait_script,
                    timeout=self.config.timeout * 1000
                )
                logger.debug("Custom wait script completed")
            
        except PlaywrightTimeoutError as e:
            logger.warning(f"Page load timeout after {self.config.timeout}s: {e}")
            # Continue anyway - partial content might still be extractable
    
    def _extract_content(self, page: Page) -> str:
        """Extract text content from the loaded page."""
        try:
            # Get visible text content
            content = page.evaluate("""
                () => {
                    // Remove script and style elements
                    const scripts = document.querySelectorAll('script, style');
                    scripts.forEach(el => el.remove());
                    
                    // Get text content
                    return document.body.innerText || document.body.textContent || '';
                }
            """)
            
            # Clean up the content
            if content:
                lines = (line.strip() for line in content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                content = "\n".join(chunk for chunk in chunks if chunk)
            
            return content or ""
            
        except Exception as e:
            logger.error(f"Failed to extract content: {e}")
            return ""
    
    def _get_page_title(self, page: Page) -> Optional[str]:
        """Get the page title."""
        try:
            title = page.title()
            return title.strip() if title else None
        except Exception as e:
            logger.warning(f"Failed to get page title: {e}")
            return None
    
    def _cleanup_driver(self, page: Page) -> None:
        """Clean up and close the browser."""
        try:
            if page:
                page.close()
            self._cleanup_playwright()
        except Exception as e:
            logger.warning(f"Error during page cleanup: {e}")
    
    def _cleanup_playwright(self) -> None:
        """Clean up Playwright resources."""
        try:
            if self._browser_instance:
                self._browser_instance.close()
                self._browser_instance = None
            
            if self._playwright:
                self._playwright.stop()
                self._playwright = None
                
        except Exception as e:
            logger.warning(f"Error during Playwright cleanup: {e}")


class AsyncPlaywrightExtractor(WebRenderExtractor):
    """Async version of Playwright extractor for better performance in async contexts.
    
    Note: This requires running in an async context and may not work well
    with the synchronous extractor interface. Use PlaywrightExtractor for
    most use cases.
    """
    
    def __init__(
        self,
        browser: str = "chromium",
        config: Optional[WebRenderConfig] = None,
        **kwargs: Any
    ) -> None:
        if not PLAYWRIGHT_AVAILABLE:
            raise _playwright_error
            
        super().__init__(name="playwright_async", config=config, **kwargs)
        self.browser = browser.lower()
        
        if self.browser not in ("chromium", "firefox", "webkit"):
            raise ValueError(f"Unsupported browser: {browser}. Use 'chromium', 'firefox', or 'webkit'")
    
    def _initialize_driver(self) -> Any:
        """This method should not be called directly for async extractor."""
        raise NotImplementedError("Use extract_async() method for async extraction")
    
    def _navigate_to_url(self, driver: Any, url: str) -> None:
        """Not used in async version."""
        pass
    
    def _wait_for_page_load(self, driver: Any) -> None:
        """Not used in async version."""
        pass
    
    def _extract_content(self, driver: Any) -> str:
        """Not used in async version."""
        return ""
    
    def _get_page_title(self, driver: Any) -> Optional[str]:
        """Not used in async version."""
        return None
    
    def _cleanup_driver(self, driver: Any) -> None:
        """Not used in async version."""
        pass
    
    async def extract_async(self, context: Any) -> Any:
        """Async version of extract method."""
        # This would need to be implemented for full async support
        # For now, we'll focus on the synchronous version
        raise NotImplementedError("Async extraction not yet implemented")


# Create convenience factory function
def create_playwright_extractor(
    browser: str = "chromium",
    headless: bool = True,
    timeout: int = 30,
    **kwargs: Any
) -> PlaywrightExtractor:
    """Create a configured Playwright extractor.
    
    Args:
        browser: Browser to use ("chromium", "firefox", or "webkit")
        headless: Whether to run in headless mode
        timeout: Page load timeout in seconds
        **kwargs: Additional configuration options
    
    Returns:
        Configured PlaywrightExtractor instance
        
    Raises:
        WebRenderDependencyError: If Playwright dependencies are not installed
    """
    config = WebRenderConfig(
        headless=headless,
        timeout=timeout,
        **kwargs
    )
    return PlaywrightExtractor(browser=browser, config=config)