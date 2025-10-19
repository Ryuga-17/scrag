"""Unit tests for layered configuration loading."""

from __future__ import annotations

from pathlib import Path

from core.utils import load_config


def test_load_config_merges_layers(tmp_path: Path) -> None:
    default = tmp_path / "default.yml"
    default.write_text(
        "logging:\n  level: INFO\nfeature:\n  enabled: false\n",
        encoding="utf8",
    )
    staging = tmp_path / "staging.yml"
    staging.write_text(
        "feature:\n  enabled: true\n",
        encoding="utf8",
    )

    config = load_config(config_dir=tmp_path, environment="staging", runtime_overrides={"logging": {"level": "DEBUG"}})

    assert config.environment == "staging"
    assert config.get("feature.enabled") is True
    assert config.get("logging.level") == "DEBUG"


def test_get_returns_default_for_missing_path(tmp_path: Path) -> None:
    (tmp_path / "default.yml").write_text("{}\n", encoding="utf8")
    config = load_config(config_dir=tmp_path, environment="default")
    assert config.get("nonexistent", "fallback") == "fallback"
