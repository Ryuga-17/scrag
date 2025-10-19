"""CLI smoke tests for the Scrag scaffold."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from core.cli import app


def test_info_command_runs_without_configuration(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["info", "--config-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "\"environment\"" in result.stdout


def test_sample_command_uses_configuration(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "default.yml").write_text("logging:\n  level: DEBUG\n", encoding="utf8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "sample",
            "https://example.com",
            "--config-dir",
            str(config_dir),
        ],
    )
    assert result.exit_code == 0
    assert "Pipeline completed" in result.stdout
