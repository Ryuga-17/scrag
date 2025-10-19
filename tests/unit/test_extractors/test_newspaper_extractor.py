from core.extractors import ExtractionContext, NewspaperExtractor


def test_newspaper_extractor_handles_missing_dependency() -> None:
    extractor = NewspaperExtractor()
    context = ExtractionContext(url="https://example.com")

    result = extractor.extract(context)

    assert result.succeeded is False
    assert "newspaper3k" in result.metadata.get("reason", "")


def test_newspaper_extractor_requires_url() -> None:
    extractor = NewspaperExtractor()
    context = ExtractionContext(url="")

    result = extractor.extract(context)

    assert result.succeeded is False
    assert result.metadata.get("reason") == "missing_url"