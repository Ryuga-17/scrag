from src.scrag.extractors.readability_extractor import ReadabilityExtractor

def test_readability_extractor_with_html():
    extractor = ReadabilityExtractor()
    html_data = """
    <html>
      <head>
        <title>A Test Article for Extraction</title>
      </head>
      <body>
        <nav>
          <ul><li><a href="#">Home</a></li><li><a href="#">About</a></li></ul>
        </nav>
        <main>
          <h1>This is the Main Headline</h1>
          <p>This is the first paragraph of the article's main content. The extractor should definitely find this text.</p>
          <p>This is the second paragraph, which provides additional details and should also be included in the final output.</p>
        </main>
        <footer>
          <p>Copyright 2025. This footer text should be ignored.</p>
        </footer>
      </body>
    </html>
    """

    result = extractor.extract(html_content=html_data)

    assert isinstance(result, dict)
    assert "title" in result
    assert "text" in result
    assert "Heading" in result["text"]

def test_readability_extractor_invalid_input():
    extractor = ReadabilityExtractor()
    result = extractor.extract()

    assert "error" in result

# Add this test function to the existing test file
def test_readability_extractor_with_raw_html():
    """Tests that the extractor can parse raw HTML content."""
    
    # 1. Define the project's context objects
    from core.extractors import ExtractionContext
    
    # 2. Your test HTML fixture
    html_fixture = """
    <html>
      <head><title>A Test Title</title></head>
      <body>
        <p>This is the main article text.</p>
        <footer>This is a footer.</footer>
      </body>
    </html>
    """

    # 3. Create the extractor and the context
    extractor = ReadabilityExtractor()
    # Pass the HTML fixture into the context object
    context = ExtractionContext(html=html_fixture)

    # 4. Run the extraction
    result = extractor.extract(context)

    # 5. Assert the results
    assert result.succeeded is True
    assert "This is the main article text" in result.content
    assert "This is a footer" not in result.content  # Readability should remove this
    assert result.metadata["title"] == "A Test Title"
