# Getting Started with Scrag

This guide will help you set up and start using Scrag for your web scraping and RAG pipeline needs.

## Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, or virtualenv)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ACM-VIT/scrag.git
cd scrag
```

### 2. Set Up Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n scrag python=3.8
conda activate scrag
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Scrag in Development Mode

```bash
pip install -e .
```

## Basic Usage

### Command Line Interface

```bash
# Scrape a single URL
scrag scrape https://example.com/article

# Scrape multiple URLs
scrag scrape urls.txt --output scraped_content/

# Build a RAG index from scraped content
scrag rag-build --source scraped_content/ --index my_rag_index
```

### Python API

```python
from scrag import Scraper, RAGBuilder

# Initialize scraper with default configuration
scraper = Scraper()

# Scrape content from a URL
result = scraper.extract("https://example.com/article")
print(f"Title: {result.title}")
print(f"Content: {result.content[:200]}...")

# Build RAG index
rag_builder = RAGBuilder()
index = rag_builder.build_from_content([result])
```

## Configuration

Scrag uses YAML configuration files located in the `config/` directory:

- `config/default.yaml` - Default settings
- `config/extractors/` - Extractor-specific configurations
- `config/rag/` - RAG pipeline configurations

You can override default settings by creating a custom configuration file:

```yaml
# my_config.yaml
extractors:
  newspaper3k:
    timeout: 30
  selenium:
    headless: true
    
rag:
  chunk_size: 1000
  overlap: 200
```

Use your custom config:

```bash
scrag --config my_config.yaml scrape https://example.com
```

## Next Steps

1. **Read the Architecture**: Check out [ARCHITECTURE.md](../ARCHITECTURE.md) for detailed system design
2. **Check the API Reference**: Browse `docs/api/` for detailed API documentation
3. **Follow Tutorials**: Work through tutorials in `docs/tutorials/`

## Getting Help

- Check the [FAQ](FAQ.md) for common questions
- Read the [Troubleshooting Guide](troubleshooting.md)
- Open an issue on GitHub for bugs or feature requests
- Join our community discussions

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](../CONTRIBUTING.md) and check out the [Development Setup Guide](development.md) if you want to contribute code.