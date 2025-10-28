"""Unit tests for web rendering extractors."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from scrag.core.extractors.web_render_base import (
    WebRenderConfig,
    WebRenderExtractor,
    WebRenderDependencyError,
    check_web_render_dependency,
)
from scrag.core.extractors.base import ExtractionContext, ExtractionResult


class TestWebRenderConfig:
    """Test WebRenderConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = WebRenderConfig()
        
        assert config.timeout == 30
        assert config.page_load_timeout == 30
        assert config.implicit_wait == 10
        assert config.headless is True
        assert config.window_width == 1920
        assert config.window_height == 1080
        assert config.user_agent is None
        assert config.javascript_enabled is True
        assert config.wait_for_selector is None
        assert config.wait_for_text is None
        assert config.screenshot_on_error is False
        assert config.custom_wait_script is None
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = WebRenderConfig(
            timeout=60,
            headless=False,
            window_width=1366,
            window_height=768,
            user_agent="Custom Agent",
            javascript_enabled=False,
            wait_for_selector=".content",
            wait_for_text="Loaded",
            screenshot_on_error=True,
            custom_wait_script="return true;"
        )
        
        assert config.timeout == 60
        assert config.headless is False
        assert config.window_width == 1366
        assert config.window_height == 768
        assert config.user_agent == "Custom Agent"
        assert config.javascript_enabled is False
        assert config.wait_for_selector == ".content"
        assert config.wait_for_text == "Loaded"
        assert config.screenshot_on_error is True
        assert config.custom_wait_script == "return true;"


class TestWebRenderDependencyError:
    """Test WebRenderDependencyError exception."""
    
    def test_error_message(self):
        """Test error message formatting."""
        error = WebRenderDependencyError("selenium", ["selenium", "webdriver_manager"])
        
        expected_msg = (
            "selenium extractor requires optional dependencies: selenium, webdriver_manager. "
            "Install with: pip install 'scrag[web-render]'"
        )
        assert str(error) == expected_msg
        assert error.extractor_name == "selenium"
        assert error.dependencies == ["selenium", "webdriver_manager"]


class TestCheckWebRenderDependency:
    """Test dependency checking function."""
    
    def test_check_existing_dependency(self):
        """Test checking for an existing dependency."""
        # Should not raise an exception for built-in modules
        check_web_render_dependency("builtins", ["builtins"])
    
    def test_check_missing_dependency(self):
        """Test checking for a missing dependency."""
        with pytest.raises(WebRenderDependencyError) as exc_info:
            check_web_render_dependency("nonexistent", ["nonexistent_module"])
        
        assert exc_info.value.extractor_name == "nonexistent"
        assert exc_info.value.dependencies == ["nonexistent_module"]


class MockWebRenderExtractor(WebRenderExtractor):
    """Mock implementation of WebRenderExtractor for testing."""
    
    def __init__(self, config=None, **kwargs):
        super().__init__(name="mock_web_render", config=config, **kwargs)
        self.driver = Mock()
        self.navigation_called = False
        self.wait_called = False
        self.content_extracted = False
        self.title_retrieved = False
        self.cleanup_called = False
    
    def _initialize_driver(self):
        return self.driver
    
    def _navigate_to_url(self, driver, url):
        self.navigation_called = True
        assert driver == self.driver
    
    def _wait_for_page_load(self, driver):
        self.wait_called = True
        assert driver == self.driver
    
    def _extract_content(self, driver):
        self.content_extracted = True
        assert driver == self.driver
        return "Mock extracted content from JavaScript-heavy page."
    
    def _get_page_title(self, driver):
        self.title_retrieved = True
        assert driver == self.driver
        return "Mock Page Title"
    
    def _cleanup_driver(self, driver):
        self.cleanup_called = True
        assert driver == self.driver


class TestWebRenderExtractor:
    """Test WebRenderExtractor base class."""
    
    def test_initialization_with_default_config(self):
        """Test extractor initialization with default config."""
        extractor = MockWebRenderExtractor()
        
        assert extractor.name == "mock_web_render"
        assert isinstance(extractor.config, WebRenderConfig)
        assert extractor.config.timeout == 30
        assert extractor.config.headless is True
    
    def test_initialization_with_custom_config(self):
        """Test extractor initialization with custom config."""
        config = WebRenderConfig(timeout=60, headless=False)
        extractor = MockWebRenderExtractor(config=config)
        
        assert extractor.config.timeout == 60
        assert extractor.config.headless is False
    
    def test_initialization_with_kwargs(self):
        """Test extractor initialization with kwargs override."""
        extractor = MockWebRenderExtractor(timeout=45, headless=False)
        
        assert extractor.config.timeout == 45
        assert extractor.config.headless is False
    
    def test_supports_http_url(self):
        """Test that extractor supports HTTP URLs."""
        extractor = MockWebRenderExtractor()
        
        context = ExtractionContext(url="http://example.com")
        assert extractor.supports(context) is True
        
        context = ExtractionContext(url="https://example.com")
        assert extractor.supports(context) is True
    
    def test_supports_rejects_invalid_urls(self):
        """Test that extractor rejects invalid URLs."""
        extractor = MockWebRenderExtractor()
        
        context = ExtractionContext(url="ftp://example.com")
        assert extractor.supports(context) is False
        
        context = ExtractionContext(url="")
        assert extractor.supports(context) is False
        
        context = ExtractionContext(url="not-a-url")
        assert extractor.supports(context) is False
    
    def test_successful_extraction(self):
        """Test successful web rendering extraction."""
        extractor = MockWebRenderExtractor()
        context = ExtractionContext(url="https://example.com")
        
        result = extractor.extract(context)
        
        assert result.succeeded is True
        assert result.content == "Mock extracted content from JavaScript-heavy page."
        assert result.metadata["extractor"] == "mock_web_render"
        assert result.metadata["title"] == "Mock Page Title"
        assert result.metadata["timeout"] == 30
        assert result.metadata["headless"] is True
        
        # Verify all methods were called
        assert extractor.navigation_called is True
        assert extractor.wait_called is True
        assert extractor.content_extracted is True
        assert extractor.title_retrieved is True
        assert extractor.cleanup_called is True
    
    def test_extraction_with_missing_url(self):
        """Test extraction with missing URL."""
        extractor = MockWebRenderExtractor()
        context = ExtractionContext(url="")
        
        result = extractor.extract(context)
        
        assert result.succeeded is False
        assert result.content == ""
        assert result.metadata["extractor"] == "mock_web_render"
        assert result.metadata["reason"] == "missing_url"
    
    def test_extraction_with_driver_failure(self):
        """Test extraction when driver initialization fails."""
        extractor = MockWebRenderExtractor()
        context = ExtractionContext(url="https://example.com")
        
        # Make driver initialization fail
        def failing_init():
            raise Exception("Driver failed to start")
        
        extractor._initialize_driver = failing_init
        
        result = extractor.extract(context)
        
        assert result.succeeded is False
        assert result.content == ""
        assert result.metadata["extractor"] == "mock_web_render"
        assert "Driver failed to start" in result.metadata["reason"]
        assert result.metadata["error_type"] == "Exception"
    
    def test_extraction_with_context_metadata_override(self):
        """Test extraction with context metadata overriding config."""
        extractor = MockWebRenderExtractor()
        context = ExtractionContext(
            url="https://example.com",
            metadata={"timeout": 120, "headless": False}
        )
        
        result = extractor.extract(context)
        
        assert result.succeeded is True
        assert extractor.config.timeout == 120
        assert extractor.config.headless is False
        assert result.metadata["timeout"] == 120
        assert result.metadata["headless"] is False
    
    def test_cleanup_on_exception(self):
        """Test that cleanup is called even when extraction fails."""
        extractor = MockWebRenderExtractor()
        context = ExtractionContext(url="https://example.com")
        
        # Make navigation fail
        def failing_navigation(driver, url):
            raise Exception("Navigation failed")
        
        extractor._navigate_to_url = failing_navigation
        
        result = extractor.extract(context)
        
        assert result.succeeded is False
        assert extractor.cleanup_called is True
    
    def test_cleanup_exception_handling(self):
        """Test that cleanup exceptions are handled gracefully."""
        extractor = MockWebRenderExtractor()
        context = ExtractionContext(url="https://example.com")
        
        # Make cleanup fail
        def failing_cleanup(driver):
            raise Exception("Cleanup failed")
        
        extractor._cleanup_driver = failing_cleanup
        
        # Should not raise an exception
        result = extractor.extract(context)
        
        assert result.succeeded is True  # Main extraction should still succeed