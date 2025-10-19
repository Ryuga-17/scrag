from core.extractors import ExtractionContext, SimpleExtractor


def test_simple_extractor_generates_metadata() -> None:
    extractor = SimpleExtractor()
    context = ExtractionContext(url="https://example.com", metadata={"source": "test"})

    result = extractor.extract(context)

    assert result.succeeded is True
    assert "example.com" in result.content
    assert result.metadata["extractor"] == "simple"
    assert result.metadata["source"] == "test"


def test_simple_extractor_handles_missing_url() -> None:
    extractor = SimpleExtractor()
    context = ExtractionContext(url="")

    result = extractor.extract(context)

    assert result.succeeded is False
    assert "unknown resource" in result.content
    assert result.metadata["extractor"] == "simple"