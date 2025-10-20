"""CLI smoke tests for the Scrag CLI."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import patch

from core.cli import app


def test_info_command_runs_without_configuration(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["info", "--config-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "\"environment\"" in result.stdout


def test_extract_command_invokes_pipeline(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yml").write_text("logging:\n  level: DEBUG\n", encoding="utf8")

    runner = CliRunner()
    with patch("core.cli.app.PipelineRunner") as mock_runner:
        instance = mock_runner.return_value
        instance.run.return_value = SimpleNamespace(
            content="example",
            metadata={},
            extractor="http",
            processors=["normalize_whitespace"],
            storage=None,
        )

        result = runner.invoke(
            app,
            [
                "extract",
                "https://example.com",
                "--config-dir",
                str(config_dir),
            ],
        )
    assert result.exit_code == 0
    assert "Pipeline completed successfully." in result.stdout
    mock_runner.assert_called_once()
    _call_args, call_kwargs = mock_runner.return_value.run.call_args
    assert call_kwargs["min_content_length_override"] is None
    assert result.exit_code == 0
    assert "Pipeline completed" in result.stdout


def test_extract_command_adds_default_scheme(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yml").write_text("logging:\n  level: DEBUG\n", encoding="utf8")

    runner = CliRunner()
    with patch("core.cli.app.PipelineRunner") as mock_runner:
        instance = mock_runner.return_value
        instance.run.return_value = SimpleNamespace(
            content="example",
            metadata={},
            extractor="http",
            processors=["normalize_whitespace"],
            storage=None,
        )

        result = runner.invoke(
            app,
            [
                "extract",
                "example.com/article",
                "--config-dir",
                str(config_dir),
            ],
        )

    assert result.exit_code == 0
    _args, kwargs = instance.run.call_args
    assert kwargs["url"] == "https://example.com/article"
    assert kwargs["min_content_length_override"] is None


def test_extract_command_respects_min_length_override(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yml").write_text("logging:\n  level: DEBUG\n", encoding="utf8")

    runner = CliRunner()
    with patch("core.cli.app.PipelineRunner") as mock_runner:
        instance = mock_runner.return_value
        instance.run.return_value = SimpleNamespace(
            content="example",
            metadata={"warnings": ["test"], "partial": True},
            extractor="http",
            processors=["normalize_whitespace"],
            storage=None,
        )

        result = runner.invoke(
            app,
            [
                "extract",
                "https://example.com",
                "--config-dir",
                str(config_dir),
                "--min-length",
                "50",
            ],
        )

    assert result.exit_code == 0
    _args, kwargs = instance.run.call_args
    assert kwargs["min_content_length_override"] == 50
    assert "warning:" in result.stdout.lower()
