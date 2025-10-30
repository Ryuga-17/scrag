"""Unit tests for Selenium extractor."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from scrag.core.extractors.base import ExtractionContext


# Mock Selenium dependencies at module level
selenium_mock = MagicMock()
webdriver_mock = MagicMock()
chrome_options_mock = MagicMock()
firefox_options_mock = MagicMock()
chrome_service_mock = MagicMock()
firefox_service_mock = MagicMock()
by_mock = MagicMock()
expected_conditions_mock = MagicMock()
webdriver_wait_mock = MagicMock()
timeout_exception_mock = Exception
webdriver_exception_mock = Exception
chrome_driver_manager_mock = MagicMock()
gecko_driver_manager_mock = MagicMock()

# Mock the dependency check to succeed
with patch('scrag.core.extractors.selenium_extractor.check_web_render_dependency'):
    with patch.dict('sys.modules', {
        'selenium': selenium_mock,
        'selenium.webdriver': webdriver_mock,
        'selenium.webdriver.chrome.options': chrome_options_mock,
        'selenium.webdriver.chrome.service': chrome_service_mock,
        'selenium.webdriver.firefox.options': firefox_options_mock,
        'selenium.webdriver.firefox.service': firefox_service_mock,
        'selenium.webdriver.common.by': by_mock,
        'selenium.webdriver.support': expected_conditions_mock,
        'selenium.webdriver.support.ui': webdriver_wait_mock,
        'selenium.common.exceptions': MagicMock(),
        'webdriver_manager.chrome': chrome_driver_manager_mock,
        'webdriver_manager.firefox': gecko_driver_manager_mock,
    }):
        # Set the availability flag
        import scrag.core.extractors.selenium_extractor as selenium_extractor_module
        selenium_extractor_module.SELENIUM_AVAILABLE = True
        
        from scrag.core.extractors.selenium_extractor import (
            SeleniumExtractor,
            create_selenium_extractor,
        )
        from scrag.core.extractors.web_render_base import WebRenderConfig


class TestSeleniumExtractor:
    """Test SeleniumExtractor with mocked dependencies."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Reset mocks
        selenium_mock.reset_mock()
        webdriver_mock.reset_mock()
        
        # Configure mock driver
        self.mock_driver = Mock()
        self.mock_driver.title = "Test Page Title"
        self.mock_driver.page_source = "<html><body>Test content</body></html>"
        
        # Configure mock body element
        self.mock_body = Mock()
        self.mock_body.text = "Test extracted content from Selenium"
        self.mock_driver.find_element.return_value = self.mock_body
        
        # Configure mock service and driver manager
        chrome_driver_manager_mock.ChromeDriverManager.return_value.install.return_value = "/path/to/chromedriver"
        gecko_driver_manager_mock.GeckoDriverManager.return_value.install.return_value = "/path/to/geckodriver"
    
    def test_initialization_with_chrome(self):
        """Test Selenium extractor initialization with Chrome."""
        extractor = SeleniumExtractor(browser="chrome")
        
        assert extractor.name == "selenium"
        assert extractor.browser == "chrome"
        assert isinstance(extractor.config, WebRenderConfig)
    
    def test_initialization_with_firefox(self):
        """Test Selenium extractor initialization with Firefox."""
        extractor = SeleniumExtractor(browser="firefox")
        
        assert extractor.name == "selenium"
        assert extractor.browser == "firefox"
    
    def test_initialization_with_invalid_browser(self):
        """Test Selenium extractor initialization with invalid browser."""
        with pytest.raises(ValueError, match="Unsupported browser: invalid"):
            SeleniumExtractor(browser="invalid")
    
    @patch('scrag.core.extractors.selenium_extractor.webdriver.Chrome')
    @patch('scrag.core.extractors.selenium_extractor.ChromeService')
    @patch('scrag.core.extractors.selenium_extractor.ChromeOptions')
    @patch('scrag.core.extractors.selenium_extractor.ChromeDriverManager')
    def test_create_chrome_driver(self, mock_driver_manager, mock_options, mock_service, mock_webdriver):
        """Test Chrome driver creation."""
        # Setup mocks
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        mock_options_instance = Mock()
        mock_options.return_value = mock_options_instance
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_webdriver.return_value = self.mock_driver
        
        extractor = SeleniumExtractor(browser="chrome")
        driver = extractor._create_chrome_driver()
        
        # Verify options were configured
        mock_options_instance.add_argument.assert_any_call("--headless")
        mock_options_instance.add_argument.assert_any_call("--no-sandbox")
        mock_options_instance.add_argument.assert_any_call("--disable-dev-shm-usage")
        
        # Verify service was created with auto-managed driver
        mock_service.assert_called_once()
        
        # Verify Chrome driver was created
        mock_webdriver.assert_called_once_with(service=mock_service_instance, options=mock_options_instance)
        
        # Verify timeouts were set
        self.mock_driver.set_page_load_timeout.assert_called_once()
        self.mock_driver.implicitly_wait.assert_called_once()
        
        assert driver == self.mock_driver
    
    @patch('scrag.core.extractors.selenium_extractor.webdriver.Firefox')
    @patch('scrag.core.extractors.selenium_extractor.FirefoxService')
    @patch('scrag.core.extractors.selenium_extractor.FirefoxOptions')
    @patch('scrag.core.extractors.selenium_extractor.GeckoDriverManager')
    def test_create_firefox_driver(self, mock_driver_manager, mock_options, mock_service, mock_webdriver):
        """Test Firefox driver creation."""
        # Setup mocks
        mock_driver_manager.return_value.install.return_value = "/path/to/geckodriver"
        mock_options_instance = Mock()
        mock_options.return_value = mock_options_instance
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_webdriver.return_value = self.mock_driver
        
        extractor = SeleniumExtractor(browser="firefox")
        driver = extractor._create_firefox_driver()
        
        # Verify options were configured
        mock_options_instance.add_argument.assert_any_call("--headless")
        
        # Verify service was created with auto-managed driver
        mock_service.assert_called_once()
        
        # Verify Firefox driver was created
        mock_webdriver.assert_called_once_with(service=mock_service_instance, options=mock_options_instance)
        
        assert driver == self.mock_driver
    
    def test_navigate_to_url(self):
        """Test URL navigation."""
        extractor = SeleniumExtractor(browser="chrome")
        extractor._navigate_to_url(self.mock_driver, "https://example.com")
        
        self.mock_driver.get.assert_called_once_with("https://example.com")
    
    @patch('scrag.core.extractors.selenium_extractor.WebDriverWait')
    def test_wait_for_page_load(self, mock_wait):
        """Test page load waiting."""
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        
        extractor = SeleniumExtractor(browser="chrome")
        extractor._wait_for_page_load(self.mock_driver)
        
        # Verify WebDriverWait was created
        mock_wait.assert_called_once()
        
        # Verify wait conditions were called
        mock_wait_instance.until.assert_called()
    
    @patch('scrag.core.extractors.selenium_extractor.WebDriverWait')
    def test_wait_for_page_load_with_selector(self, mock_wait):
        """Test page load waiting with specific selector."""
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        
        config = WebRenderConfig(wait_for_selector=".content")
        extractor = SeleniumExtractor(browser="chrome", config=config)
        extractor._wait_for_page_load(self.mock_driver)
        
        # Should call multiple wait conditions
        assert mock_wait_instance.until.call_count >= 2
    
    def test_extract_content(self):
        """Test content extraction."""
        extractor = SeleniumExtractor(browser="chrome")
        content = extractor._extract_content(self.mock_driver)
        
        self.mock_driver.find_element.assert_called_once()
        assert content == "Test extracted content from Selenium"
    
    @patch('scrag.core.extractors.selenium_extractor.BeautifulSoup')
    def test_extract_content_fallback(self, mock_soup):
        """Test content extraction fallback to page source."""
        # Make the body element return empty text
        self.mock_body.text = ""
        
        # Mock BeautifulSoup
        mock_soup_instance = Mock()
        mock_soup_instance.get_text.return_value = "Fallback content from page source"
        mock_soup.return_value = mock_soup_instance
        
        extractor = SeleniumExtractor(browser="chrome")
        content = extractor._extract_content(self.mock_driver)
        
        # Should use BeautifulSoup fallback
        mock_soup.assert_called_once()
        assert "Fallback content" in content
    
    def test_get_page_title(self):
        """Test page title extraction."""
        extractor = SeleniumExtractor(browser="chrome")
        title = extractor._get_page_title(self.mock_driver)
        
        assert title == "Test Page Title"
    
    def test_cleanup_driver(self):
        """Test driver cleanup."""
        extractor = SeleniumExtractor(browser="chrome")
        extractor._cleanup_driver(self.mock_driver)
        
        self.mock_driver.quit.assert_called_once()
    
    @patch('scrag.core.extractors.selenium_extractor.SeleniumExtractor._initialize_driver')
    def test_successful_extraction(self, mock_init_driver):
        """Test successful end-to-end extraction."""
        mock_init_driver.return_value = self.mock_driver
        
        extractor = SeleniumExtractor(browser="chrome")
        context = ExtractionContext(url="https://example.com")
        
        result = extractor.extract(context)
        
        assert result.succeeded is True
        assert result.content == "Test extracted content from Selenium"
        assert result.metadata["extractor"] == "selenium"
        assert result.metadata["title"] == "Test Page Title"
        assert result.metadata["headless"] is True
        
        # Verify cleanup was called
        self.mock_driver.quit.assert_called_once()
    
    @patch('scrag.core.extractors.selenium_extractor.SeleniumExtractor._initialize_driver')
    def test_extraction_with_driver_error(self, mock_init_driver):
        """Test extraction when driver fails."""
        mock_init_driver.side_effect = Exception("Driver initialization failed")
        
        extractor = SeleniumExtractor(browser="chrome")
        context = ExtractionContext(url="https://example.com")
        
        result = extractor.extract(context)
        
        assert result.succeeded is False
        assert result.content == ""
        assert "Driver initialization failed" in result.metadata["reason"]


class TestCreateSeleniumExtractor:
    """Test convenience factory function."""
    
    def test_create_with_defaults(self):
        """Test creating extractor with default settings."""
        extractor = create_selenium_extractor()
        
        assert isinstance(extractor, SeleniumExtractor)
        assert extractor.browser == "chrome"
        assert extractor.config.headless is True
        assert extractor.config.timeout == 30
    
    def test_create_with_custom_settings(self):
        """Test creating extractor with custom settings."""
        extractor = create_selenium_extractor(
            browser="firefox",
            headless=False,
            timeout=60,
            window_width=1366
        )
        
        assert extractor.browser == "firefox"
        assert extractor.config.headless is False
        assert extractor.config.timeout == 60
        assert extractor.config.window_width == 1366


# Test what happens when Selenium is not available
class TestSeleniumUnavailable:
    """Test behavior when Selenium dependencies are not available."""
    
    @patch('scrag.core.extractors.selenium_extractor.SELENIUM_AVAILABLE', False)
    def test_extractor_creation_fails_when_unavailable(self):
        """Test that creating extractor fails when Selenium is unavailable."""
        # This would need to be tested in a separate test environment
        # where the selenium_extractor module is imported without the dependencies
        pass