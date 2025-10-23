import unittest.mock
from core.extractors.base import ExtractionContext
from core.extractors.readability_extractor import ReadabilityExtractor

def test_readability_extractor_with_raw_html():
    """
    Tests that the extractor can parse raw HTML content passed via metadata.
    """
    # 1. Your test HTML fixture
    html_fixture = """
    <html>
      <head><title>A Test Title</title></head>
      <body>
        <p>This is the main article text.</p>
        <footer>This is a footer.</footer>
      </body>
    </html>
    """

    # 2. Create the extractor and the context
    extractor = ReadabilityExtractor()
    # THIS IS THE KEY CHANGE: Pass HTML inside the 'metadata' dict
    context = ExtractionContext(url=None, metadata={'html': html_fixture})

    # 3. Run the extraction
    result = extractor.extract(context)

    # 4. Assert the results
    assert result.succeeded is True
    assert "This is the main article text" in result.content
    assert "This is a footer" not in result.content
    assert result.metadata["title"] == "A Test Title"


def test_readability_extractor_with_url():
    """
    Tests that the extractor can fetch and parse content from a URL.
    """
    # 1. Define the mock HTML that our fake URL will "return"
    mock_html = """
    <html><head><title>Mocked URL Title</title></head>
    <body><p>Content from a mocked URL.</p></body></html>
    """
    
    # 2. Create a mock response for 'requests.get'
    mock_response = unittest.mock.Mock()
    mock_response.text = mock_html
    mock_response.raise_for_status.return_value = None

    # 3. Set up the extractor and context with a fake URL
    extractor = ReadabilityExtractor()
    test_url = "https://fake-test-url.com"
    context = ExtractionContext(url=test_url) # This was correct

    # 4. Patch 'requests.get' and run extraction
    with unittest.mock.patch('core.extractors.readability_extractor.requests.get', return_value=mock_response) as mock_get:
        result = extractor.extract(context)

    # 5. Assert the results
    assert result.succeeded is True
    assert "Content from a mocked URL" in result.content
    assert result.metadata["title"] == "Mocked URL Title"
    mock_get.assert_called_once()


def test_readability_extractor_fails_with_no_input():
    """
    Tests that the extractor fails gracefully when given no URL or HTML.
    """
    extractor = ReadabilityExtractor()
    # Create a context with no URL and no HTML metadata
    context = ExtractionContext(url=None, metadata=None) 
    
    result = extractor.extract(context)
    
    assert result.succeeded is False
    assert result.metadata["reason"] == "no_html_or_url"