"""Tests for TranslationPair model."""

from datetime import datetime

import pytest

from docdiff.models.translation import TranslationPair, TranslationStatus


class TestTranslationPair:
    """Test TranslationPair model."""

    def test_translation_pair_creation_minimal(self):
        """Test creating TranslationPair with minimal fields."""
        pair = TranslationPair(source_node_id="node-en-1", target_language="ja")

        assert pair.source_node_id == "node-en-1"
        assert pair.target_node_id is None
        assert pair.source_language == "en"  # default
        assert pair.target_language == "ja"
        assert pair.status == TranslationStatus.PENDING  # default
        assert pair.similarity_score is None
        assert isinstance(pair.created_at, datetime)
        assert pair.updated_at is None

    def test_translation_pair_creation_full(self):
        """Test creating TranslationPair with all fields."""
        now = datetime.now()
        pair = TranslationPair(
            source_node_id="node-en-1",
            target_node_id="node-ja-1",
            source_language="en",
            target_language="ja",
            status=TranslationStatus.TRANSLATED,
            similarity_score=0.95,
            created_at=now,
            updated_at=now,
        )

        assert pair.source_node_id == "node-en-1"
        assert pair.target_node_id == "node-ja-1"
        assert pair.source_language == "en"
        assert pair.target_language == "ja"
        assert pair.status == TranslationStatus.TRANSLATED
        assert pair.similarity_score == 0.95
        assert pair.created_at == now
        assert pair.updated_at == now

    def test_translation_pair_similarity_score_validation(self):
        """Test similarity score validation."""
        # Valid score
        pair = TranslationPair(
            source_node_id="node-1", target_language="ja", similarity_score=0.5
        )
        assert pair.similarity_score == 0.5

        # Score at boundaries
        pair = TranslationPair(
            source_node_id="node-1", target_language="ja", similarity_score=0.0
        )
        assert pair.similarity_score == 0.0

        pair = TranslationPair(
            source_node_id="node-1", target_language="ja", similarity_score=1.0
        )
        assert pair.similarity_score == 1.0

        # Invalid score (too high)
        with pytest.raises(ValueError):
            TranslationPair(
                source_node_id="node-1", target_language="ja", similarity_score=1.5
            )

        # Invalid score (negative)
        with pytest.raises(ValueError):
            TranslationPair(
                source_node_id="node-1", target_language="ja", similarity_score=-0.1
            )

    def test_translation_pair_status_enum(self):
        """Test different translation status values."""
        # Test all enum values
        for status in TranslationStatus:
            pair = TranslationPair(
                source_node_id="node-1", target_language="ja", status=status
            )
            assert pair.status == status

    def test_translation_pair_json_schema(self):
        """Test JSON schema example."""
        schema = TranslationPair.model_config.get("json_schema_extra", {})
        assert "example" in schema

        example = schema["example"]
        assert "source_node_id" in example
        assert "target_node_id" in example
        assert "source_language" in example
        assert "target_language" in example
        assert "status" in example
        assert "similarity_score" in example

    def test_translation_pair_model_export(self):
        """Test model export to dict."""
        pair = TranslationPair(
            source_node_id="node-en-1",
            target_node_id="node-ja-1",
            source_language="en",
            target_language="ja",
            status=TranslationStatus.REVIEWED,
            similarity_score=0.85,
        )

        data = pair.model_dump()

        assert data["source_node_id"] == "node-en-1"
        assert data["target_node_id"] == "node-ja-1"
        assert data["source_language"] == "en"
        assert data["target_language"] == "ja"
        assert data["status"] == TranslationStatus.REVIEWED
        assert data["similarity_score"] == 0.85
        assert "created_at" in data
        assert "updated_at" in data

    def test_translation_pair_model_json(self):
        """Test model JSON serialization."""
        pair = TranslationPair(source_node_id="node-en-1", target_language="ja")

        json_str = pair.model_dump_json()
        assert isinstance(json_str, str)
        assert "node-en-1" in json_str
        assert "ja" in json_str
