"""Configuration loading utilities for Scrag."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping, Optional

import yaml


@dataclass(slots=True)
class ScragConfig:
    """Runtime configuration assembled from layered sources."""

    environment: str
    data: Dict[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        """Access configuration values using dotted paths."""

        parts = key.split(".")
        value: Any = self.data
        for part in parts:
            if not isinstance(value, Mapping) or part not in value:
                return default
            value = value[part]
        return value

    def to_pretty_json(self) -> str:
        """Render configuration payload as formatted JSON."""

        return json.dumps({"environment": self.environment, "data": self.data}, indent=2, sort_keys=True)


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf8") as handle:
        loaded = yaml.safe_load(handle) or {}
        if not isinstance(loaded, MutableMapping):
            raise ValueError(f"Configuration file {path} must contain a mapping at the top level.")
        return dict(loaded)


def _merge_dicts(base: Dict[str, Any], override: Mapping[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], MutableMapping) and isinstance(value, Mapping):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(
    *,
    config_dir: Path,
    environment: str,
    runtime_overrides: Optional[Mapping[str, Any]] = None,
) -> ScragConfig:
    """Load Scrag configuration using the layered precedence described in the docs."""

    default_config = _read_yaml(config_dir / "default.yml")
    env_config = _read_yaml(config_dir / f"{environment}.yml")
    merged = _merge_dicts(default_config, env_config)
    if runtime_overrides:
        merged = _merge_dicts(merged, runtime_overrides)
    return ScragConfig(environment=environment, data=merged)
