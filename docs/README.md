### Readability Extractor

The `ReadabilityExtractor` uses the `readability-lxml` library to extract the main content and title from a webpage or raw HTML.

**Usage Example:**
```python
from src.scrag.extractors.readability_extractor import ReadabilityExtractor

extractor = ReadabilityExtractor()

# Extract from a URL
result = extractor.extract(url="https://example.com/article")

# Or directly from raw HTML
html_data = "<html><body><h1>Hello</h1><p>Sample content</p></body></html>"
result = extractor.extract(html_content=html_data)

print(result["title"])
print(result["text"])
