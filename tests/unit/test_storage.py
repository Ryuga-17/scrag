"""Tests for storage adapters and formats."""

import json
from pathlib import Path
from datetime import datetime

import pytest

from core.storage.base import FileStorage, StorageContext, build_storage


class TestFileStorage:
    """Test FileStorage with different formats."""

    def test_supported_formats(self):
        """Test that FileStorage supports the expected formats."""
        assert FileStorage.SUPPORTED_FORMATS == {"json", "txt", "ndjson", "md"}

    def test_invalid_format_raises_error(self, tmp_path: Path):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported format"):
            FileStorage(tmp_path, format="invalid")

    def test_format_validation_case_insensitive(self, tmp_path: Path):
        """Test that format validation is case insensitive."""
        # Should not raise error
        storage = FileStorage(tmp_path, format="JSON")
        assert storage._format == "json"

    def test_json_format_storage(self, tmp_path: Path):
        """Test JSON format storage and retrieval."""
        storage = FileStorage(tmp_path, format="json")
        
        context = StorageContext(
            content="Test content",
            metadata={"title": "Test Article", "url": "https://example.com"}
        )
        
        result = storage.store(context)
        
        assert result.success
        assert result.path is not None
        assert result.path.suffix == ".json"
        
        # Read back the file
        content = result.path.read_text(encoding="utf8")
        data = json.loads(content)
        
        assert data["content"] == "Test content"
        assert data["metadata"]["title"] == "Test Article"
        assert data["metadata"]["url"] == "https://example.com"
        assert "timestamp" in data

    def test_txt_format_storage(self, tmp_path: Path):
        """Test TXT format storage and retrieval."""
        storage = FileStorage(tmp_path, format="txt")
        
        context = StorageContext(
            content="Plain text content",
            metadata={"title": "Test Article"}
        )
        
        result = storage.store(context)
        
        assert result.success
        assert result.path is not None
        assert result.path.suffix == ".txt"
        
        # Read back the file
        content = result.path.read_text(encoding="utf8")
        assert content == "Plain text content"

    def test_ndjson_format_storage(self, tmp_path: Path):
        """Test NDJSON format storage and retrieval."""
        storage = FileStorage(tmp_path, format="ndjson")
        
        context = StorageContext(
            content="NDJSON test content",
            metadata={"title": "Test Article", "author": "Test Author"}
        )
        
        result = storage.store(context)
        
        assert result.success
        assert result.path is not None
        assert result.path.suffix == ".ndjson"
        
        # Read back the file
        content = result.path.read_text(encoding="utf8")
        lines = content.strip().split("\n")
        
        assert len(lines) == 3
        
        # Parse each line as JSON
        content_line = json.loads(lines[0])
        metadata_line = json.loads(lines[1])
        timestamp_line = json.loads(lines[2])
        
        assert content_line["content"] == "NDJSON test content"
        assert metadata_line["metadata"]["title"] == "Test Article"
        assert metadata_line["metadata"]["author"] == "Test Author"
        assert "timestamp" in timestamp_line

    def test_md_format_storage(self, tmp_path: Path):
        """Test Markdown format storage and retrieval."""
        storage = FileStorage(tmp_path, format="md")
        
        context = StorageContext(
            content="This is the main content of the article.",
            metadata={
                "title": "Test Article",
                "url": "https://example.com/article",
                "author": "John Doe",
                "date": "2024-01-01"
            }
        )
        
        result = storage.store(context)
        
        assert result.success
        assert result.path is not None
        assert result.path.suffix == ".md"
        
        # Read back the file
        content = result.path.read_text(encoding="utf8")
        
        assert "# Test Article" in content
        assert "**Source URL:** https://example.com/article" in content
        assert "**Author:** John Doe" in content
        assert "**Date:** 2024-01-01" in content
        assert "---" in content
        assert "This is the main content of the article." in content

    def test_md_format_storage_minimal_metadata(self, tmp_path: Path):
        """Test Markdown format storage with minimal metadata."""
        storage = FileStorage(tmp_path, format="md")
        
        context = StorageContext(
            content="Content without much metadata",
            metadata={"url": "https://example.com"}
        )
        
        result = storage.store(context)
        
        assert result.success
        
        # Read back the file
        content = result.path.read_text(encoding="utf8")
        
        assert "**Source URL:** https://example.com" in content
        assert "Content without much metadata" in content
        assert "---" in content
        # Should not contain title, author, or date sections
        assert "# " not in content
        assert "**Author:**" not in content
        assert "**Date:**" not in content

    def test_round_trip_json(self, tmp_path: Path):
        """Test round-trip storage and retrieval for JSON format."""
        storage = FileStorage(tmp_path, format="json")
        
        original_context = StorageContext(
            content="Round trip test content",
            metadata={"title": "Round Trip Test", "tags": ["test", "storage"]}
        )
        
        result = storage.store(original_context)
        assert result.success
        
        # Read back and verify
        content = result.path.read_text(encoding="utf8")
        data = json.loads(content)
        
        assert data["content"] == original_context.content
        assert data["metadata"]["title"] == original_context.metadata["title"]
        assert data["metadata"]["tags"] == original_context.metadata["tags"]

    def test_round_trip_txt(self, tmp_path: Path):
        """Test round-trip storage and retrieval for TXT format."""
        storage = FileStorage(tmp_path, format="txt")
        
        original_content = "Round trip test content for TXT format"
        original_context = StorageContext(content=original_content)
        
        result = storage.store(original_context)
        assert result.success
        
        # Read back and verify
        content = result.path.read_text(encoding="utf8")
        assert content == original_content

    def test_round_trip_ndjson(self, tmp_path: Path):
        """Test round-trip storage and retrieval for NDJSON format."""
        storage = FileStorage(tmp_path, format="ndjson")
        
        original_context = StorageContext(
            content="Round trip test content for NDJSON",
            metadata={"title": "NDJSON Test", "category": "test"}
        )
        
        result = storage.store(original_context)
        assert result.success
        
        # Read back and verify
        content = result.path.read_text(encoding="utf8")
        lines = content.strip().split("\n")
        
        content_line = json.loads(lines[0])
        metadata_line = json.loads(lines[1])
        
        assert content_line["content"] == original_context.content
        assert metadata_line["metadata"]["title"] == original_context.metadata["title"]
        assert metadata_line["metadata"]["category"] == original_context.metadata["category"]

    def test_round_trip_md(self, tmp_path: Path):
        """Test round-trip storage and retrieval for Markdown format."""
        storage = FileStorage(tmp_path, format="md")
        
        original_content = "This is the main content for markdown round-trip test."
        original_context = StorageContext(
            content=original_content,
            metadata={
                "title": "Markdown Round Trip Test",
                "author": "Test Author",
                "url": "https://example.com/md-test"
            }
        )
        
        result = storage.store(original_context)
        assert result.success
        
        # Read back and verify
        content = result.path.read_text(encoding="utf8")
        
        assert "# Markdown Round Trip Test" in content
        assert "**Source URL:** https://example.com/md-test" in content
        assert "**Author:** Test Author" in content
        assert "---" in content
        assert original_content in content

    def test_filename_generation(self, tmp_path: Path):
        """Test that filenames are generated correctly for different formats."""
        storage = FileStorage(tmp_path, format="json")
        
        context = StorageContext(
            content="Test content",
            metadata={"title": "Test Article Title"}
        )
        
        result = storage.store(context)
        
        assert result.success
        assert result.path is not None
        assert result.path.stem.startswith("test-article-title")
        assert result.path.suffix == ".json"

    def test_custom_filename(self, tmp_path: Path):
        """Test custom filename override."""
        storage = FileStorage(tmp_path, format="md", filename="custom-article")
        
        context = StorageContext(content="Test content")
        
        result = storage.store(context)
        
        assert result.success
        assert result.path is not None
        assert result.path.stem == "custom-article"
        assert result.path.suffix == ".md"

    def test_directory_creation(self, tmp_path: Path):
        """Test that storage creates directories if they don't exist."""
        nested_dir = tmp_path / "nested" / "directory"
        storage = FileStorage(nested_dir, format="txt")
        
        context = StorageContext(content="Test content")
        result = storage.store(context)
        
        assert result.success
        assert nested_dir.exists()
        assert result.path.parent == nested_dir

    def test_build_storage_with_format(self, tmp_path: Path):
        """Test build_storage function with format parameter."""
        storage = build_storage("file", options={"directory": tmp_path, "format": "ndjson"})
        
        assert isinstance(storage, FileStorage)
        assert storage._format == "ndjson"
        
        context = StorageContext(content="Test content")
        result = storage.store(context)
        
        assert result.success
        assert result.path.suffix == ".ndjson"

    def test_unicode_content_handling(self, tmp_path: Path):
        """Test that unicode content is handled correctly in all formats."""
        unicode_content = "Test content with unicode: 你好世界 🌍 émojis"
        
        for format_name in ["json", "txt", "ndjson", "md"]:
            storage = FileStorage(tmp_path, format=format_name)
            context = StorageContext(content=unicode_content)
            
            result = storage.store(context)
            assert result.success
            
            # Read back and verify unicode is preserved
            content = result.path.read_text(encoding="utf8")
            if format_name == "json":
                data = json.loads(content)
                assert data["content"] == unicode_content
            elif format_name == "ndjson":
                lines = content.strip().split("\n")
                content_line = json.loads(lines[0])
                assert content_line["content"] == unicode_content
            elif format_name == "md":
                assert unicode_content in content
            else:  # txt
                assert content == unicode_content
