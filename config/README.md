# Configuration Structure

This directory contains configuration files for different aspects of Scrag.

## Structure

### `/extractors/`
Configuration files for different extraction strategies:
- `newspaper3k.yaml` - Configuration for newspaper3k extractor
- `readability.yaml` - Configuration for readability-lxml extractor
- `beautifulsoup.yaml` - Configuration for BeautifulSoup heuristics
- `selenium.yaml` - Configuration for headless browser rendering
- `custom_extractors.yaml` - Configuration for custom extraction strategies

### `/rag/`
Configuration files for RAG-related functionality:
- `chunking.yaml` - Text chunking strategies and parameters
- `embeddings.yaml` - Embedding model configurations
- `indexing.yaml` - Vector database and indexing configurations
- `retrieval.yaml` - Retrieval and ranking configurations

### Root Level
- `default.yaml` - Default application configuration
- `logging.yaml` - Logging configuration
- `performance.yaml` - Performance and optimization settings

## Configuration Format

All configuration files use YAML format for readability and ease of modification.
Environment variables can be used for sensitive values using the format `${ENV_VAR_NAME}`.