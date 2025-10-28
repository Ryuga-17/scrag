"""Selenium-based extractor for JavaScript-heavy web pages."""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from .web_render_base import (
    WebRenderConfig,
    WebRenderDependencyError,
    WebRenderExtractor,
    check_web_render_dependency,
)

logger = logging.getLogger(__name__)

# Check for Selenium dependencies at module import time
try:
    check_web_render_dependency("selenium", ["selenium", "webdriver_manager"])
    
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    
    SELENIUM_AVAILABLE = True
    
except ImportError as e:
    SELENIUM_AVAILABLE = False
    _selenium_error = e


class SeleniumExtractor(WebRenderExtractor):
    """Selenium-based extractor for JavaScript-heavy pages.
    
    Supports Chrome and Firefox browsers with automatic driver management.
    Provides configurable timeouts and wait conditions for dynamic content.
    
    Example usage:
        extractor = SeleniumExtractor(
            browser="chrome",
            timeout=30,
            headless=True,
            wait_for_selector=".content"
        )
    """
    
    def __init__(
        self,
        browser: str = "chrome",
        config: Optional[WebRenderConfig] = None,
        **kwargs: Any
    ) -> None:
        if not SELENIUM_AVAILABLE:
            raise _selenium_error
            
        super().__init__(name="selenium", config=config, **kwargs)
        self.browser = browser.lower()
        
        if self.browser not in ("chrome", "firefox"):
            raise ValueError(f"Unsupported browser: {browser}. Use 'chrome' or 'firefox'")
    
    def _initialize_driver(self) -> webdriver.Remote:
        """Initialize and configure the Selenium WebDriver."""
        try:
            if self.browser == "chrome":
                return self._create_chrome_driver()
            elif self.browser == "firefox":
                return self._create_firefox_driver()
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.browser} driver: {e}")
            raise WebDriverException(f"Could not initialize {self.browser} driver: {e}")
    
    def _create_chrome_driver(self) -> webdriver.Chrome:
        """Create Chrome WebDriver with appropriate options."""
        options = ChromeOptions()
        
        if self.config.headless:
            options.add_argument("--headless")
        
        # Essential Chrome arguments for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        
        # Set window size
        options.add_argument(f"--window-size={self.config.window_width},{self.config.window_height}")
        
        # Set user agent if provided
        if self.config.user_agent:
            options.add_argument(f"--user-agent={self.config.user_agent}")
        
        # Disable JavaScript if configured
        if not self.config.javascript_enabled:
            options.add_experimental_option("prefs", {"profile.managed_default_content_settings.javascript": 2})
        
        # Create service with auto-managed driver
        service = ChromeService(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Set timeouts
        driver.set_page_load_timeout(self.config.page_load_timeout)
        driver.implicitly_wait(self.config.implicit_wait)
        
        return driver
    
    def _create_firefox_driver(self) -> webdriver.Firefox:
        """Create Firefox WebDriver with appropriate options."""
        options = FirefoxOptions()
        
        if self.config.headless:
            options.add_argument("--headless")
        
        # Set window size
        options.add_argument(f"--width={self.config.window_width}")
        options.add_argument(f"--height={self.config.window_height}")
        
        # Set user agent if provided
        if self.config.user_agent:
            options.set_preference("general.useragent.override", self.config.user_agent)
        
        # Disable JavaScript if configured
        if not self.config.javascript_enabled:
            options.set_preference("javascript.enabled", False)
        
        # Create service with auto-managed driver
        service = FirefoxService(GeckoDriverManager().install())
        
        driver = webdriver.Firefox(service=service, options=options)
        
        # Set timeouts
        driver.set_page_load_timeout(self.config.page_load_timeout)
        driver.implicitly_wait(self.config.implicit_wait)
        
        return driver
    
    def _navigate_to_url(self, driver: webdriver.Remote, url: str) -> None:
        """Navigate to the specified URL."""
        driver.get(url)
    
    def _wait_for_page_load(self, driver: webdriver.Remote) -> None:
        """Wait for the page to fully load based on configuration."""
        wait = WebDriverWait(driver, self.config.timeout)
        
        try:
            # Wait for document ready state
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            
            # Wait for specific selector if provided
            if self.config.wait_for_selector:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.config.wait_for_selector)))
                logger.debug(f"Found selector: {self.config.wait_for_selector}")
            
            # Wait for specific text if provided
            if self.config.wait_for_text:
                wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), self.config.wait_for_text))
                logger.debug(f"Found text: {self.config.wait_for_text}")
            
            # Execute custom wait script if provided
            if self.config.custom_wait_script:
                wait.until(lambda d: d.execute_script(self.config.custom_wait_script))
                logger.debug("Custom wait script completed")
            
            # Small additional wait for any remaining async operations
            time.sleep(1)
            
        except TimeoutException as e:
            logger.warning(f"Page load timeout after {self.config.timeout}s: {e}")
            # Continue anyway - partial content might still be extractable
    
    def _extract_content(self, driver: webdriver.Remote) -> str:
        """Extract text content from the loaded page."""
        try:
            # First try to get visible text
            body = driver.find_element(By.TAG_NAME, "body")
            content = body.text
            
            # If no visible text, fall back to page source parsing
            if not content.strip():
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(driver.page_source, "html.parser")
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                content = soup.get_text()
            
            # Clean up the content
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = "\n".join(chunk for chunk in chunks if chunk)
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to extract content: {e}")
            return ""
    
    def _get_page_title(self, driver: webdriver.Remote) -> Optional[str]:
        """Get the page title."""
        try:
            title = driver.title
            return title.strip() if title else None
        except Exception as e:
            logger.warning(f"Failed to get page title: {e}")
            return None
    
    def _cleanup_driver(self, driver: webdriver.Remote) -> None:
        """Clean up and close the driver."""
        try:
            driver.quit()
        except Exception as e:
            logger.warning(f"Error during driver cleanup: {e}")


# Create convenience factory function
def create_selenium_extractor(
    browser: str = "chrome",
    headless: bool = True,
    timeout: int = 30,
    **kwargs: Any
) -> SeleniumExtractor:
    """Create a configured Selenium extractor.
    
    Args:
        browser: Browser to use ("chrome" or "firefox")
        headless: Whether to run in headless mode
        timeout: Page load timeout in seconds
        **kwargs: Additional configuration options
    
    Returns:
        Configured SeleniumExtractor instance
        
    Raises:
        WebRenderDependencyError: If Selenium dependencies are not installed
    """
    config = WebRenderConfig(
        headless=headless,
        timeout=timeout,
        **kwargs
    )
    return SeleniumExtractor(browser=browser, config=config)