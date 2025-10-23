# from src.scrag.extractors.readability_extractor import ReadabilityExtractor

# def test_readability_extractor_with_html():
#     extractor = ReadabilityExtractor()
#     html_data = """
#     <html>
#       <head>
#         <title>A Test Article for Extraction</title>
#       </head>
#       <body>
#         <nav>
#           <ul><li><a href="#">Home</a></li><li><a href="#">About</a></li></ul>
#         </nav>
#         <main>
#           <h1>This is the Main Headline</h1>
#           <p>This is the first paragraph of the article's main content. The extractor should definitely find this text.</p>
#           <p>This is the second paragraph, which provides additional details and should also be included in the final output.</p>
#         </main>
#         <footer>
#           <p>Copyright 2025. This footer text should be ignored.</p>
#         </footer>
#       </body>
#     </html>
#     """

#     result = extractor.extract(html_content=html_data)

#     assert isinstance(result, dict)
#     assert "title" in result
#     assert "text" in result
#     assert "Heading" in result["text"]

# def test_readability_extractor_invalid_input():
#     extractor = ReadabilityExtractor()
#     result = extractor.extract()

#     assert "error" in result

# # Add this test function to the existing test file
# def test_readability_extractor_with_raw_html():
#     """Tests that the extractor can parse raw HTML content."""
    
#     # 1. Define the project's context objects
#     from core.extractors import ExtractionContext
    
#     # 2. Your test HTML fixture
#     html_fixture = """
#     <html>
#       <head><title>A Test Title</title></head>
#       <body>
#         <p>This is the main article text.</p>
#         <footer>This is a footer.</footer>
#       </body>
#     </html>
#     """

#     # 3. Create the extractor and the context
#     extractor = ReadabilityExtractor()
#     # Pass the HTML fixture into the context object
#     context = ExtractionContext(html=html_fixture)

#     # 4. Run the extraction
#     result = extractor.extract(context)

#     # 5. Assert the results
#     assert result.succeeded is True
#     assert "This is the main article text" in result.content
#     assert "This is a footer" not in result.content  # Readability should remove this
#     assert result.metadata["title"] == "A Test Title"

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