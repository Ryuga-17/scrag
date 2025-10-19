from src.scrag.extractors.newspaper_extractor import NewspaperExtractor

def test_newspaper_extractor_basic_fields():
    extractor = NewspaperExtractor()
    url = ""  # you can put any url here to test. example: "https://en.wikipedia.org/wiki/Web_scraping"

    result = extractor.extract(url)

    assert isinstance(result, dict)

    assert "title" in result
    assert "text" in result
    assert "authors" in result
    assert "publish_date" in result
    assert "url" in result

def test_newspaper_extractor_invalid_url():
    extractor = NewspaperExtractor()
    url = "" # put any invalid url to test

    result = extractor.extract(url)

    assert result is None