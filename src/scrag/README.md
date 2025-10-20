# Scrag Python Package

This package houses the adaptive scraping toolkit that powers Scrag. The codebase is organized
according to the architectural guidance in the root documentation and is intended to provide a
clean starting point for future contributors.

## Package Layout

- `core.extractors` – strategy-based content extractors (HTTP, readability, newspaper3k).
- `core.processors` – pipeline-friendly processors used to normalize text.
- `core.storage` – adapters that persist processed payloads (memory or file-based).
- `core.rag` – Retrieval-Augmented Generation primitives (`NoOpRAGComponent`).
- `core.utils` – shared utilities such as the layered configuration loader.
- `core.cli` – Typer-powered command-line experience exposed via the `scrag` executable.

## Getting Started

```bash
# sync dependencies and create a virtual environment
uv sync

# install the scrag package in editable mode to expose the CLI script
uv pip install -e .

# inspect the active configuration snapshot
uv run python -m core.cli info

# run the extraction pipeline against a URL
uv run scrag extract https://example.com
```

The CLI uses the configuration files in the repository `config/` directory by default. Override the
config directory or environment when testing alternative setups:

```bash
uv run scrag info --config-dir path/to/config --environment staging
```
