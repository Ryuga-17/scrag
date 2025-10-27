"""Typer-powered CLI surface for Scrag."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
from typing import Optional

import typer

from core import __version__
from core.pipeline import PipelineRunner
from core.utils import ScragConfig, load_config

app = typer.Typer(help="Adaptive scraping toolkit for RAG pipelines.")


def _resolve_config(config_dir: Optional[Path], environment: Optional[str]) -> ScragConfig:
    """Internal helper to load configuration using CLI parameters."""

    if config_dir is not None:
        directory = config_dir
    else:
        parents = list(Path(__file__).resolve().parents)
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
def extract(
    url: str = typer.Argument(..., help="URL to scrape and process."),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Directory or file path where processed content should be stored.",
    ),
    output_format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Override storage format when writing to disk (e.g. json or txt).",
    ),
    config_dir: Optional[Path] = typer.Option(None, help="Configuration directory location."),
    environment: Optional[str] = typer.Option(None, help="Configuration environment name."),
    min_length: Optional[int] = typer.Option(
        None,
        "--min-length",
        help="Override the minimum content length requirement for this run.",
    ),
    use_async: bool = typer.Option(
        False,
        "--async",
        help="[EXPERIMENTAL] Enable async extraction for improved throughput with batch processing.",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Disable HTTP caching. Fetch fresh content regardless of cache.",
    ),
) -> None:
    """Execute the configured extraction pipeline for the provided URL."""

    normalized_url = _normalize_target_url(url)

    config = _resolve_config(config_dir=config_dir, environment=environment)
    
    # Override extractors if async mode is enabled
    if use_async:
        original_extractors = config.data.get("pipeline", {}).get("extractors", [])
        config.data.setdefault("pipeline", {}).setdefault("extractors", [])
        config.data["pipeline"]["extractors"] = ["async_http"] + original_extractors
    
    runner = PipelineRunner(config)

    normalized_output = _normalize_output_path(output)

    result = runner.run(
        url=normalized_url,
        output=normalized_output,
        storage_format=output_format,
        min_content_length_override=min_length,
    )
    
    if use_async:
        typer.echo("  mode: async (experimental)")

    typer.echo("Pipeline completed successfully.")
    typer.echo(f"  extractor: {result.extractor}")
    if result.processors:
        typer.echo(f"  processors: {', '.join(result.processors)}")
    typer.echo(f"  content-characters: {len(result.content)}")
    if result.storage and result.storage.path:
        typer.echo(f"  saved-to: {result.storage.path}")
    typer.echo(f"  environment: {config.environment}")
    if isinstance(result.metadata, dict) and result.metadata.get("partial"):
        typer.echo("  note: content below configured minimum threshold")
    warnings = result.metadata.get("warnings") if isinstance(result.metadata, dict) else None
    if warnings:
        for warning in warnings:
            typer.echo(f"  warning: {warning}")


@app.callback()
def main_callback(
    version: bool = typer.Option(False, "--version", help="Display the Scrag version and exit."),
) -> None:
    """Global CLI callback to expose version info."""

    if version:
        typer.echo(__version__)
        raise typer.Exit()


def _normalize_output_path(output: Optional[Path]) -> Optional[Path]:
    if output is None:
        return None
    if output.suffix:
        return output
    return output.resolve()


def _normalize_target_url(raw_url: str) -> str:
    cleaned = raw_url.strip()
    if not cleaned:
        raise typer.BadParameter("URL cannot be empty")

    parsed = urlparse(cleaned)
    if parsed.scheme and parsed.netloc:
        return cleaned

    candidate = f"https://{cleaned.lstrip('/')}"
    candidate_parsed = urlparse(candidate)
    if candidate_parsed.scheme and candidate_parsed.netloc:
        return candidate

    raise typer.BadParameter("URL must include a valid hostname")


def main() -> None:
    """Entrypoint used by executable scripts."""

    app()
