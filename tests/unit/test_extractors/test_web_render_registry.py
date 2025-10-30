"""Integration tests for web render extractor registry."""

import pytest
from unittest.mock import patch

from scrag.core.extractors import (
    get_available_extractors,
    is_web_render_extractor,
    get_missing_web_render_dependencies,
    build_extractors,
    EXTRACTOR_REGISTRY,
    WEB_RENDER_EXTRACTORS,
    ALL_EXTRACTORS,
)


class TestExtractorRegistry:
    """Test extractor registry functionality."""
    
    def test_core_extractors_always_available(self):
        """Test that core extractors are always in the registry."""
        available = get_available_extractors()
        
        # Core extractors should always be available
        assert "http" in available
        assert "simple" in available
        assert "newspaper" in available
        assert "readability" in available
        assert "async_http" in available
        assert "async" in available
    
    def test_is_web_render_extractor(self):
        """Test identification of web render extractors."""
        # Core extractors should not be web-render
        assert is_web_render_extractor("http") is False
        assert is_web_render_extractor("newspaper") is False
        assert is_web_render_extractor("readability") is False
        
        # Web-render extractors should be identified correctly
        # (These may or may not be available depending on dependencies)
        if "selenium" in WEB_RENDER_EXTRACTORS:
            assert is_web_render_extractor("selenium") is True
            assert is_web_render_extractor("selenium_chrome") is True
            assert is_web_render_extractor("selenium_firefox") is True
        
        if "playwright" in WEB_RENDER_EXTRACTORS:
            assert is_web_render_extractor("playwright") is True
            assert is_web_render_extractor("playwright_chromium") is True
            assert is_web_render_extractor("playwright_firefox") is True
            assert is_web_render_extractor("playwright_webkit") is True
    
    def test_get_missing_dependencies(self):
        """Test getting missing web render dependencies."""
        missing = get_missing_web_render_dependencies()
        
        # Should be a list (may be empty if all dependencies are installed)
        assert isinstance(missing, list)
        
        # Each missing dependency should be a string
        for dep in missing:
            assert isinstance(dep, str)
            assert dep in ["selenium", "playwright"]
    
    def test_build_extractors_with_core_only(self):
        """Test building extractors with only core extractors."""
        extractors = build_extractors(["http", "newspaper", "readability"])
        
        assert len(extractors) == 3
        assert all(hasattr(ext, "extract") for ext in extractors)
        assert all(hasattr(ext, "name") for ext in extractors)
    
    def test_build_extractors_with_unknown_extractor(self):
        """Test building extractors with unknown extractor name."""
        extractors = build_extractors(["http", "unknown_extractor", "newspaper"])
        
        # Should skip unknown extractor but include known ones
        assert len(extractors) == 2
        assert extractors[0].name == "http"
        assert extractors[1].name == "newspaper"
    
    def test_build_extractors_with_options(self):
        """Test building extractors with configuration options."""
        options = {
            "http": {"timeout": 60, "user_agent": "Custom Agent"},
            "newspaper": {"language": "en"}
        }
        
        extractors = build_extractors(["http", "newspaper"], options=options)
        
        assert len(extractors) == 2
        # Note: We can't easily test the internal configuration without
        # making the extractors expose their config, but the build should succeed


@patch('scrag.core.extractors.WEB_RENDER_EXTRACTORS', {})
class TestExtractorRegistryWithoutWebRender:
    """Test extractor registry when web-render extractors are not available."""
    
    def test_missing_selenium_dependency(self):
        """Test behavior when Selenium is not available."""
        missing = get_missing_web_render_dependencies()
        assert "selenium" in missing
    
    def test_missing_playwright_dependency(self):
        """Test behavior when Playwright is not available."""
        missing = get_missing_web_render_dependencies()
        assert "playwright" in missing
    
    def test_build_extractors_with_missing_selenium(self):
        """Test building extractors when Selenium is requested but not available."""
        extractors = build_extractors(["http", "selenium", "newspaper"])
        
        # Should skip selenium but include available extractors
        assert len(extractors) == 2
        assert extractors[0].name == "http"
        assert extractors[1].name == "newspaper"
    
    def test_build_extractors_with_missing_playwright(self):
        """Test building extractors when Playwright is requested but not available."""
        extractors = build_extractors(["http", "playwright", "newspaper"])
        
        # Should skip playwright but include available extractors
        assert len(extractors) == 2
        assert extractors[0].name == "http"
        assert extractors[1].name == "newspaper"


class TestExtractorRegistryIntegration:
    """Test extractor registry integration features."""
    
    def test_all_extractors_include_core_and_web_render(self):
        """Test that ALL_EXTRACTORS includes both core and web-render extractors."""
        all_extractors = get_available_extractors()
        
        # Should include all core extractors
        for name in EXTRACTOR_REGISTRY:
            assert name in all_extractors
        
        # Should include available web-render extractors
        for name in WEB_RENDER_EXTRACTORS:
            assert name in all_extractors
    
    def test_extractor_registry_immutable(self):
        """Test that getting available extractors returns a copy."""
        extractors1 = get_available_extractors()
        extractors2 = get_available_extractors()
        
        # Should be equal but not the same object
        assert extractors1 == extractors2
        assert extractors1 is not extractors2
        
        # Modifying one shouldn't affect the other
        extractors1["test"] = "value"
        assert "test" not in extractors2