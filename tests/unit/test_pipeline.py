from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Dict
from unittest.mock import MagicMock

import pytest

from core.pipeline import PipelineRunner
from core.utils import ScragConfig


class DummyExtractor:
    name = "dummy"

    def supports(self, context):
        return True

    def extract(self, context):
        return SimpleNamespace(content="example content", metadata={"extractor": self.name}, succeeded=True)


class DummyProcessor:
    name = "cleaner"

    def process(self, context):
        return SimpleNamespace(content=context.content.upper(), metadata=context.metadata)


class DummyStorage:
    name = "memory"

    def __init__(self):
        self.saved = []

    def store(self, context):
        self.saved.append(context)
        return SimpleNamespace(success=True, metadata=context.metadata, path=None)


@pytest.fixture(autouse=True)
def patch_components(monkeypatch):
    monkeypatch.setattr("core.pipeline.build_extractors", lambda names, options=None: [DummyExtractor()])
    monkeypatch.setattr("core.pipeline.build_processors", lambda names, options=None: [DummyProcessor()])
    monkeypatch.setattr("core.pipeline.build_storage", lambda name, options=None: DummyStorage())


def test_pipeline_runner_invokes_all_stages(tmp_path: Path) -> None:
    config = ScragConfig(
        environment="test",
        data={
            "scraping": {"user_agent": "TestAgent", "request_timeout": 5},
            "pipeline": {
                "extractors": ["dummy"],
                "processors": ["dummy"],
                "storage": {"type": "memory"},
            },
        },
    )

    runner = PipelineRunner(config)
    result = runner.run(url="https://example.com")

    assert result.content == "EXAMPLE CONTENT"
    assert result.extractor == "dummy"
    assert result.processors == ["cleaner"]
    assert result.storage is not None