"""Typer-powered CLI surface for Scrag."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from core import __version__
from core.extractors import ExtractionContext, SimpleExtractor
from core.processors import ProcessingContext, SimpleProcessor
from core.storage import InMemoryStorage, StorageContext
from core.utils import ScragConfig, load_config

app = typer.Typer(help="Adaptive scraping toolkit for RAG pipelines.")


def _resolve_config(config_dir: Optional[Path], environment: Optional[str]) -> ScragConfig:
    """Internal helper to load configuration using CLI parameters."""

    if config_dir is not None:
        directory = config_dir
    else:
        parents = (parent for parent in Path(__file__).resolve().parents)
        root_candidate = next((candidate for candidate in (parent / "config" for parent in parents) if candidate.exists()), None)
        candidates = [
            Path.cwd() / "config",
            Path.cwd().parent / "config",
        ]
        if root_candidate is not None:
            candidates.append(root_candidate)
        directory = next((candidate for candidate in candidates if candidate.exists()), candidates[0])
    env = environment or "default"
    return load_config(config_dir=directory, environment=env)


@app.command()
def info(
    config_dir: Optional[Path] = typer.Option(
        None,
        help="Directory containing layered configuration YAML files.",
    ),
    environment: Optional[str] = typer.Option(
        None,
        help="Named environment override (e.g. local, staging).",
    ),
) -> None:
    """Show the active configuration snapshot."""

    config = _resolve_config(config_dir=config_dir, environment=environment)
    typer.echo(config.to_pretty_json())


@app.command()
def sample(
    url: str = typer.Argument(..., help="URL to process with the scaffold pipeline."),
    config_dir: Optional[Path] = typer.Option(None, help="Configuration directory location."),
    environment: Optional[str] = typer.Option(None, help="Configuration environment name."),
) -> None:
    """Run the scaffold pipeline with simple extractor/processor/storage."""

    config = _resolve_config(config_dir=config_dir, environment=environment)
    extractor = SimpleExtractor()
    processor = SimpleProcessor()
    storage = InMemoryStorage()

    extraction = extractor.extract(ExtractionContext(url=url))
    processed = processor.process(ProcessingContext(content=extraction.content, metadata=extraction.metadata))
    result = storage.store(StorageContext(content=processed.content, metadata=processed.metadata))

    typer.echo("Pipeline completed:")
    typer.echo(f"  extractor={extraction.metadata.get('extractor')}")
    typer.echo(f"  processor={processed.metadata.get('processor')}")
    typer.echo(f"  storage_items={result.metadata.get('items')}")
    typer.echo(f"  config_environment={config.environment}")


@app.callback()
def main_callback() -> None:
    """Global CLI callback to expose version info."""

    pass


def main() -> None:
    """Entrypoint used by executable scripts."""

    app()
