# Tests

This directory contains comprehensive tests for all Scrag components.

## Structure

### `/unit/`
Unit tests for individual components:
- `test_extractors/` - Tests for extraction strategies
- `test_processors/` - Tests for content processing modules
- `test_storage/` - Tests for storage adapters
- `test_cli/` - Tests for CLI functionality
- `test_rag/` - Tests for RAG pipeline components
- `test_utils/` - Tests for utility functions

### `/integration/`
Integration tests for component interactions:
- `test_extraction_pipeline.py` - End-to-end extraction pipeline tests
- `test_rag_pipeline.py` - RAG pipeline integration tests
- `test_storage_integration.py` - Storage system integration tests
- `test_web_interface.py` - Web interface integration tests

### `/performance/`
Performance and load tests:
- `test_extraction_performance.py` - Extraction speed benchmarks
- `test_memory_usage.py` - Memory usage profiling
- `test_concurrent_processing.py` - Concurrent processing tests
- `test_large_dataset.py` - Large dataset processing tests

### `/fixtures/`
Test data and fixtures:
- `sample_html/` - Sample HTML files for testing
- `expected_outputs/` - Expected extraction outputs
- `test_urls.txt` - Test URLs for integration tests
- `mock_responses/` - Mock HTTP responses

## Test Configuration

- Uses pytest as the primary testing framework
- Includes coverage reporting with pytest-cov
- Mock external dependencies with pytest-mock
- Performance tests use pytest-benchmark

## Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run with coverage
pytest --cov=src/scrag --cov-report=html

# Run performance benchmarks
pytest tests/performance/ --benchmark-only
```