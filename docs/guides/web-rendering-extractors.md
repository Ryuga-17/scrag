# Web Rendering Extractors

This document describes Scrag's optional web rendering extractors that provide JavaScript execution capabilities for extracting content from dynamic, JavaScript-heavy web pages.

## Overview

Web rendering extractors use full browser automation to:
- Execute JavaScript and wait for dynamic content to load
- Handle single-page applications (SPAs) and AJAX-heavy sites
- Extract content that is only available after client-side rendering
- Support complex interaction patterns and wait conditions

## Available Extractors

### Selenium Extractor

**Extractor Names:** `selenium`, `selenium_chrome`, `selenium_firefox`

The Selenium extractor uses the Selenium WebDriver framework with automatic driver management.

**Supported Browsers:**
- Chrome (default)
- Firefox

**Features:**
- Automatic WebDriver management via `webdriver-manager`
- Configurable timeouts and wait conditions
- Screenshot capture on errors (configurable)
- Custom JavaScript execution
- Support for headless and headed modes

### Playwright Extractor

**Extractor Names:** `playwright`, `playwright_chromium`, `playwright_firefox`, `playwright_webkit`

The Playwright extractor uses Microsoft's Playwright framework for modern web automation.

**Supported Browsers:**
- Chromium (default)
- Firefox
- WebKit (Safari-like)

**Features:**
- Built-in browser binaries (no separate driver installation)
- Fast page loading and network interception
- Advanced wait conditions
- Better handling of modern web applications
- Lower resource usage than Selenium

## Installation

Web rendering extractors require optional dependencies:

```bash
# Install all web rendering dependencies
pip install 'scrag[web-render]'

# Or install individual packages
pip install selenium webdriver-manager playwright
```

After installing Playwright, install browser binaries:

```bash
playwright install
```

## Configuration

### Basic Configuration

```yaml
# config/default.yml
pipeline:
  extractors:
    - selenium  # or playwright
  extractor_options:
    selenium:
      browser: chrome
      headless: true
      timeout: 30
      page_load_timeout: 30
      window_width: 1920
      window_height: 1080
```

### Advanced Configuration

```yaml
pipeline:
  extractors:
    - selenium_chrome
  extractor_options:
    selenium_chrome:
      headless: true
      timeout: 60
      page_load_timeout: 45
      implicit_wait: 10
      javascript_enabled: true
      wait_for_selector: ".content-loaded"
      wait_for_text: "Page Ready"
      screenshot_on_error: true
      custom_wait_script: "return document.readyState === 'complete' && window.myApp && window.myApp.loaded"
      user_agent: "Custom Scrag Bot 1.0"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `browser` | string | `"chrome"` | Browser to use (chrome/firefox for Selenium, chromium/firefox/webkit for Playwright) |
| `headless` | boolean | `true` | Run browser in headless mode |
| `timeout` | integer | `30` | General timeout in seconds |
| `page_load_timeout` | integer | `30` | Page load timeout in seconds |
| `implicit_wait` | integer | `10` | Implicit wait timeout in seconds |
| `window_width` | integer | `1920` | Browser window width |
| `window_height` | integer | `1080` | Browser window height |
| `javascript_enabled` | boolean | `true` | Enable JavaScript execution |
| `wait_for_selector` | string | `null` | CSS selector to wait for |
| `wait_for_text` | string | `null` | Text content to wait for |
| `screenshot_on_error` | boolean | `false` | Take screenshot on errors |
| `custom_wait_script` | string | `null` | Custom JavaScript to execute and wait for |
| `user_agent` | string | `null` | Custom user agent string |

## CLI Usage

### Using Web Rendering Extractors

```bash
# Use Selenium with Chrome
scrag extract https://spa-example.com --selenium --browser chrome

# Use Playwright with Firefox
scrag extract https://dynamic-site.com --playwright --browser firefox

# Configure timeout and headless mode
scrag extract https://slow-site.com --selenium --timeout 60 --no-headless

# List available extractors and dependency status
scrag extractors
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--selenium` | Use Selenium for JavaScript-heavy pages |
| `--playwright` | Use Playwright for JavaScript-heavy pages |
| `--browser BROWSER` | Browser to use (chrome, firefox, chromium, webkit) |
| `--headless/--no-headless` | Run browser in headless mode |
| `--timeout SECONDS` | Page load timeout in seconds |

## Programming Interface

### Direct Usage

```python
from scrag.core.extractors.selenium_extractor import create_selenium_extractor
from scrag.core.extractors.playwright_extractor import create_playwright_extractor
from scrag.core.extractors.base import ExtractionContext

# Create Selenium extractor
selenium_extractor = create_selenium_extractor(
    browser="chrome",
    headless=True,
    timeout=30
)

# Create Playwright extractor
playwright_extractor = create_playwright_extractor(
    browser="chromium",
    headless=True,
    timeout=30
)

# Extract content
context = ExtractionContext(url="https://example.com")
result = selenium_extractor.extract(context)

if result.succeeded:
    print(f"Extracted {len(result.content)} characters")
    print(f"Page title: {result.metadata.get('title')}")
else:
    print(f"Extraction failed: {result.metadata.get('reason')}")
```

### Advanced Configuration

```python
from scrag.core.extractors.web_render_base import WebRenderConfig
from scrag.core.extractors.selenium_extractor import SeleniumExtractor

# Create custom configuration
config = WebRenderConfig(
    timeout=60,
    headless=False,
    wait_for_selector=".app-loaded",
    wait_for_text="Ready",
    custom_wait_script="return window.appReady === true",
    screenshot_on_error=True
)

# Create extractor with custom config
extractor = SeleniumExtractor(browser="chrome", config=config)
```

### Error Handling

```python
from scrag.core.extractors.web_render_base import WebRenderDependencyError

try:
    extractor = create_selenium_extractor()
except WebRenderDependencyError as e:
    print(f"Missing dependencies: {e.dependencies}")
    print("Install with: pip install 'scrag[web-render]'")
```

## Performance Considerations

### Resource Usage

Web rendering extractors have significantly higher resource requirements than traditional HTTP-based extractors:

| Aspect | HTTP Extractor | Selenium | Playwright |
|--------|----------------|----------|------------|
| Memory Usage | ~5-10 MB | ~100-200 MB | ~80-150 MB |
| CPU Usage | Low | Medium-High | Medium |
| Startup Time | ~50ms | ~2-5s | ~1-3s |
| Page Load Time | ~200ms | ~2-10s | ~1-5s |

### Optimization Tips

1. **Use headless mode** for production environments
2. **Set appropriate timeouts** to avoid hanging on slow pages
3. **Reuse extractor instances** when processing multiple URLs
4. **Configure specific wait conditions** instead of relying on timeouts
5. **Consider using Playwright** for better performance than Selenium

### CI/CD Considerations

Web rendering extractors are **not recommended for CI environments** due to:

- Heavy resource requirements
- Additional browser dependencies
- Potential for flaky tests
- Longer execution times

For CI/CD pipelines, consider:

```yaml
# GitHub Actions example
- name: Install dependencies (excluding web-render)
  run: pip install scrag  # Without [web-render]

- name: Run tests (core extractors only)
  run: pytest tests/ -k "not web_render"
```

## Common Use Cases

### Single Page Applications (SPAs)

```python
# React/Vue/Angular apps that load content dynamically
config = WebRenderConfig(
    wait_for_selector="[data-testid='app-loaded']",
    timeout=30
)
```

### Infinite Scroll Pages

```python
# Pages that load content on scroll
config = WebRenderConfig(
    custom_wait_script="""
        // Scroll to bottom and wait for content
        window.scrollTo(0, document.body.scrollHeight);
        return document.querySelectorAll('.content-item').length > 50;
    """,
    timeout=60
)
```

### Authentication Required

```python
# Pages requiring login or authentication
config = WebRenderConfig(
    wait_for_text="Welcome back",
    timeout=45
)
```

### AJAX-Heavy Content

```python
# Pages with complex AJAX loading
config = WebRenderConfig(
    custom_wait_script="return window.dataLoaded === true",
    timeout=30
)
```

## Troubleshooting

### Common Issues

**1. Driver/Browser Not Found**
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```
*Solution:* Web rendering extractors use automatic driver management. Ensure you have the `webdriver-manager` package installed.

**2. Timeout Errors**
```
TimeoutException: Page load timeout after 30s
```
*Solution:* Increase timeout values or add specific wait conditions.

**3. JavaScript Execution Errors**
```
WebDriverException: javascript error: ReferenceError: myVariable is not defined
```
*Solution:* Ensure your custom wait scripts are valid JavaScript and that referenced variables exist.

**4. Memory Issues**
```
Out of memory error during browser startup
```
*Solution:* Use headless mode and limit concurrent extractions.

### Debugging

Enable debug logging to troubleshoot extraction issues:

```python
import logging
logging.getLogger('scrag.core.extractors').setLevel(logging.DEBUG)
```

Take screenshots for visual debugging:

```python
config = WebRenderConfig(screenshot_on_error=True)
```

### Fallback Strategy

Implement graceful fallback to HTTP extractors:

```yaml
pipeline:
  extractors:
    - selenium_chrome  # Try web rendering first
    - newspaper        # Fallback to traditional extraction
    - http             # Final fallback
```

## Best Practices

1. **Use the lightest extractor first**: Start with HTTP, fall back to web rendering
2. **Configure appropriate timeouts**: Balance thoroughness with performance
3. **Use specific wait conditions**: More reliable than fixed delays
4. **Monitor resource usage**: Web rendering can consume significant resources
5. **Test in production-like environments**: Browser behavior can vary
6. **Consider caching**: Web rendering results are expensive to generate
7. **Use headless mode in production**: Unless debugging visual issues
8. **Handle errors gracefully**: Web rendering can fail in many ways

## Security Considerations

- Web rendering extractors execute JavaScript from target websites
- Use trusted sources and validate URLs before extraction
- Consider running in sandboxed environments for untrusted content
- Be aware of potential browser security vulnerabilities
- Monitor resource usage to prevent denial-of-service