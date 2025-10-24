# Getting Started with Scrag

Scrag is a Typer-powered CLI for running a multi-strategy scraping pipeline. The default configuration fans out across `newspaper3k`, `readability-lxml`, and a BeautifulSoup HTTP fallback, then normalizes the text and writes results to `data/`.

## Prerequisites

- Python 3.13 (matches the `requires-python` in `pyproject.toml`)
- [uv](https://docs.astral.sh/uv/) 0.4+ for dependency and virtualenv management
- Git

> Tip: `uv` bundles its own virtual environment. You do not need to create a venv manually.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ACM-VIT/scrag.git
cd scrag
```

### 2. Sync dependencies

```bash
uv sync
uv pip install -e src/scrag
```

`uv sync` resolves the lockfile `uv.lock` (if present) and installs toolchain requirements. The editable install exposes the `scrag` CLI entry point.

> **Dependency Management:** This project uses `uv` as the canonical dependency manager. All dependencies are defined in `src/scrag/pyproject.toml` and managed via `uv.lock`. Do not use `pip install -r requirements.txt` as the root `requirements.txt` has been removed to avoid conflicts.

### 3. Verify the CLI

```bash
uv run scrag info
```

This command prints the merged configuration (`config/default.yml` by default). Seeing valid JSON means the CLI and config loader are healthy.

## Basic Usage

### Extract a URL

```bash
uv run scrag extract https://example.com/article
```

The CLI prints the extractor that succeeded, the processors that ran, the character count, and the path of any stored artifact. By default, storage is `data/<slug>-<timestamp>.json`.

### Override runtime options

```bash
# Write plain text to a custom directory
uv run scrag extract https://example.com/article --output data/export --format txt

# Relax the minimum content length for thin pages
uv run scrag extract https://example.com/article --min-length 50

# Point at a different config directory or environment
uv run scrag extract https://example.com/article --config-dir config --environment staging
```

When every extractor falls below the configured minimum length (`pipeline.minimum_content_length`), Scrag now returns the best short result and includes `warning` messages in the CLI output.

### Inspect saved output

Artifacts live in `data/` and are ignored by Git. JSON records include:

- `content`: normalized text
- `metadata`: extractor details, URL, timestamps, optional warnings

## Configuration

The configuration loader merges `<config-dir>/default.yml` with `<config-dir>/<environment>.yml`.

Key sections in `config/default.yml`:

- `scraping` – shared HTTP options (user agent, timeout)
- `pipeline.extractors` – ordered list of extractor registry keys
- `pipeline.minimum_content_length` – global floor before a fallback result is flagged as partial
- `pipeline.storage` – storage adapter and options (defaults to file-based JSON)

You can supply per-extractor overrides via `pipeline.extractor_options` and per-processor overrides via `pipeline.processor_options`.

## Testing the Installation

```bash
uv run pytest
```

The unit suite covers the CLI contract, pipeline behavior (including minimum-length handling), and extractor edge cases such as missing optional dependencies.

## Next Steps

1. Read [ARCHITECTURE.md](../../ARCHITECTURE.md) for the domain-driven overview of extractors, processors, and storage adapters.
2. Follow the [Development Setup Guide](development.md) when you are ready to contribute.
3. Explore the tests in `tests/unit/` to see concrete usage and mocking patterns.

## Getting Help

- Search existing issues and open a new one with reproducible steps if needed.
- Use the CLI `--help` output (`uv run scrag --help`) to discover command options.
- For configuration questions, inspect `core/utils/config.py` and `config/default.yml` to understand how overrides merge.