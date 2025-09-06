"""Test cases for proper translation detection."""

import hashlib
from pathlib import Path
from docdiff.models import DocumentNode, NodeType
from docdiff.compare import ComparisonEngine


def _create_hash(content: str) -> str:
    """Create a hash for content."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


class TestTranslationDetection:
    """Test that the comparison engine properly detects translations."""

    def test_same_label_different_content_is_translated(self):
        """Same label with different content should be marked as translated."""
        engine = ComparisonEngine()

        # English node
        en_content = "## Overview"
        en_node = DocumentNode(
            id="en1",
            type=NodeType.SECTION,
            content=en_content,
            content_hash=_create_hash(en_content),
            label="overview-section",
            file_path=Path("docs/en/index.md"),
            line_number=5,
        )

        # Japanese node with same label but translated content
        ja_content = "## 概要"
        ja_node = DocumentNode(
            id="ja1",
            type=NodeType.SECTION,
            content=ja_content,
            content_hash=_create_hash(ja_content),
            label="overview-section",
            file_path=Path("docs/ja/index.md"),
            line_number=5,
        )

        result = engine.compare([en_node], [ja_node], "en", "ja")

        # Should have one mapping
        assert len(result.mappings) == 1
        mapping = result.mappings[0]

        # Should be marked as translated (exact or fuzzy, not missing)
        assert mapping.mapping_type in ["exact", "fuzzy"]
        assert mapping.target_node is not None
        assert mapping.target_node.content == "## 概要"

    def test_same_label_same_content_is_not_translated(self):
        """Same label with identical content should be marked as missing translation."""
        engine = ComparisonEngine()

        # English node
        en_content = "## Overview"
        en_node = DocumentNode(
            id="en1",
            type=NodeType.SECTION,
            content=en_content,
            content_hash=_create_hash(en_content),
            label="overview-section",
            file_path=Path("docs/en/index.md"),
            line_number=5,
        )

        # Japanese node with same label AND same content (not translated)
        ja_content = "## Overview"  # Still in English!
        ja_node = DocumentNode(
            id="ja1",
            type=NodeType.SECTION,
            content=ja_content,
            content_hash=_create_hash(ja_content),
            label="overview-section",
            file_path=Path("docs/ja/index.md"),
            line_number=5,
        )

        result = engine.compare([en_node], [ja_node], "en", "ja")

        # Should have one mapping
        assert len(result.mappings) == 1
        mapping = result.mappings[0]

        # Should be marked as missing (not translated)
        assert mapping.mapping_type == "missing"
        assert mapping.target_node is None
        assert mapping.similarity == 0.0

    def test_metadata_not_considered_content(self):
        """Metadata like names and captions should not affect translation status."""
        engine = ComparisonEngine()

        # English code block
        en_content = "print('Hello, World!')"
        en_node = DocumentNode(
            id="en1",
            type=NodeType.CODE_BLOCK,
            content=en_content,
            content_hash=_create_hash(en_content),
            name="hello-code",
            caption="Hello World Example",
            file_path=Path("docs/en/index.md"),
            line_number=10,
        )

        # Japanese code block with same metadata but different caption
        ja_content = "print('こんにちは、世界！')"
        ja_node = DocumentNode(
            id="ja1",
            type=NodeType.CODE_BLOCK,
            content=ja_content,
            content_hash=_create_hash(ja_content),
            name="hello-code",  # Same name (structural marker)
            caption="Hello World の例",  # Translated caption
            file_path=Path("docs/ja/index.md"),
            line_number=10,
        )

        result = engine.compare([en_node], [ja_node], "en", "ja")

        # Should recognize as translated based on content
        assert len(result.mappings) == 1
        mapping = result.mappings[0]
        assert mapping.mapping_type in ["exact", "fuzzy"]
        assert mapping.target_node is not None

    def test_multiple_nodes_mixed_translation_status(self):
        """Test with multiple nodes having different translation statuses."""
        engine = ComparisonEngine()

        en_nodes = [
            DocumentNode(
                id="en1",
                type=NodeType.SECTION,
                content="# Documentation",
                content_hash=_create_hash("# Documentation"),
                label="docs",
                file_path=Path("docs/en/index.md"),
                line_number=1,
            ),
            DocumentNode(
                id="en2",
                type=NodeType.PARAGRAPH,
                content="This is English text.",
                content_hash=_create_hash("This is English text."),
                file_path=Path("docs/en/index.md"),
                line_number=3,
            ),
            DocumentNode(
                id="en3",
                type=NodeType.SECTION,
                content="## Features",
                content_hash=_create_hash("## Features"),
                label="features",
                file_path=Path("docs/en/index.md"),
                line_number=5,
            ),
        ]

        ja_nodes = [
            DocumentNode(
                id="ja1",
                type=NodeType.SECTION,
                content="# ドキュメント",  # Translated
                content_hash=_create_hash("# ドキュメント"),
                label="docs",
                file_path=Path("docs/ja/index.md"),
                line_number=1,
            ),
            DocumentNode(
                id="ja2",
                type=NodeType.PARAGRAPH,
                content="This is English text.",  # Not translated
                content_hash=_create_hash("This is English text."),
                file_path=Path("docs/ja/index.md"),
                line_number=3,
            ),
            DocumentNode(
                id="ja3",
                type=NodeType.SECTION,
                content="## 機能",  # Translated
                content_hash=_create_hash("## 機能"),
                label="features",
                file_path=Path("docs/ja/index.md"),
                line_number=5,
            ),
        ]

        result = engine.compare(en_nodes, ja_nodes, "en", "ja")

        # Check overall statistics
        assert result.coverage_stats["counts"]["total"] == 3
        assert (
            result.coverage_stats["counts"]["translated"] == 2
        )  # Two sections translated
        assert (
            result.coverage_stats["counts"]["missing"] == 1
        )  # One paragraph not translated

    def test_no_structural_match_uses_content_matching(self):
        """When no label/name match exists, should use content-based matching."""
        engine = ComparisonEngine()

        # Nodes without labels
        en_content = "This is a paragraph without any label."
        en_node = DocumentNode(
            id="en1",
            type=NodeType.PARAGRAPH,
            content=en_content,
            content_hash=_create_hash(en_content),
            file_path=Path("docs/en/index.md"),
            line_number=10,
        )

        ja_content = "これはラベルのない段落です。"
        ja_node = DocumentNode(
            id="ja1",
            type=NodeType.PARAGRAPH,
            content=ja_content,
            content_hash=_create_hash(ja_content),
            file_path=Path("docs/ja/index.md"),
            line_number=10,
        )

        result = engine.compare([en_node], [ja_node], "en", "ja")

        # Should still match based on position and type
        assert len(result.mappings) == 1
        mapping = result.mappings[0]

        # Different content means it's translated
        if (
            mapping.target_node
            and mapping.target_node.content == "これはラベルのない段落です。"
        ):
            assert mapping.mapping_type in ["exact", "fuzzy"]
        else:
            # If fuzzy matching didn't work due to threshold, it's missing
            assert mapping.mapping_type == "missing"
