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
