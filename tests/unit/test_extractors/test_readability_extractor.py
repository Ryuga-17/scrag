from src.scrag.extractors.readability_extractor import ReadabilityExtractor

def test_readability_extractor_with_html():
    extractor = ReadabilityExtractor()
    html_data = """
    <html>
        <head><title>Sample Page</title></head>
        <body>
            <article><h1>Heading</h1><p>This is some content.</p></article>
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
