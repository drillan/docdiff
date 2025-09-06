"""Unit tests for Pydantic models."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from docdiff.models.node import DocumentNode, NodeType
from docdiff.models.reference import Reference, ReferenceType
from docdiff.models.translation import TranslationStatus, TranslationUnit


class TestDocumentNode:
    """Test DocumentNode model."""

    def test_document_node_creation(self) -> None:
        """Test basic DocumentNode creation."""
        node = DocumentNode(
            id="test_id",
            type=NodeType.SECTION,
            content="# Test Section",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="abc123",
        )
        assert node.id == "test_id"
        assert node.type == NodeType.SECTION
        assert node.content == "# Test Section"
        assert node.file_path == Path("test.md")
        assert node.line_number == 1
        assert node.content_hash == "abc123"

    def test_node_hierarchy(self) -> None:
        """Test parent-child relationship management."""
        parent = DocumentNode(
            id="parent_id",
            type=NodeType.SECTION,
            content="# Parent",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="parent_hash",
        )
        child = DocumentNode(
            id="child_id",
            type=NodeType.PARAGRAPH,
            content="Child paragraph",
            parent_id=parent.id,
            file_path=Path("test.md"),
            line_number=3,
            content_hash="child_hash",
        )
        assert child.parent_id == parent.id
        parent.children_ids.append(child.id)
        assert child.id in parent.children_ids

    def test_section_attributes(self) -> None:
        """Test section-specific attributes."""
        section = DocumentNode(
            id="section_id",
            type=NodeType.SECTION,
            content="## Subsection",
            level=2,
            title="Subsection",
            label="subsection-label",
            file_path=Path("test.md"),
            line_number=5,
            content_hash="section_hash",
        )
        assert section.level == 2
        assert section.title == "Subsection"
        assert section.label == "subsection-label"

    def test_code_block_attributes(self) -> None:
        """Test code block specific attributes."""
        code_block = DocumentNode(
            id="code_id",
            type=NodeType.CODE_BLOCK,
            content="print('hello')",
            language="python",
            name="example-code",
            caption="Example Python Code",
            file_path=Path("test.md"),
            line_number=10,
            content_hash="code_hash",
        )
        assert code_block.language == "python"
        assert code_block.name == "example-code"
        assert code_block.caption == "Example Python Code"

    def test_metadata_field(self) -> None:
        """Test metadata field for storing additional attributes."""
        node = DocumentNode(
            id="meta_id",
            type=NodeType.FIGURE,
            content="",
            metadata={"width": "80%", "alt": "Diagram", "align": "center"},
            file_path=Path("test.md"),
            line_number=15,
            content_hash="meta_hash",
        )
        assert node.metadata["width"] == "80%"
        assert node.metadata["alt"] == "Diagram"
        assert node.metadata["align"] == "center"

    def test_all_node_types(self) -> None:
        """Test that all node types can be created."""
        for node_type in NodeType:
            node = DocumentNode(
                id=f"{node_type.value}_id",
                type=node_type,
                content=f"Content for {node_type.value}",
                file_path=Path("test.md"),
                line_number=1,
                content_hash=f"{node_type.value}_hash",
            )
            assert node.type == node_type

    def test_invalid_node_creation(self) -> None:
        """Test that invalid node creation raises ValidationError."""
        with pytest.raises(ValidationError):
            DocumentNode(
                id="invalid_id",
                type="invalid_type",  # type: ignore
                content="Content",
                file_path=Path("test.md"),
                line_number=1,
                content_hash="hash",
            )

    def test_content_hash_generation(self) -> None:
        """Test content hash generation from content."""
        import hashlib

        content = "Test content for hashing"
        expected_hash = hashlib.sha256(content.encode()).hexdigest()

        node = DocumentNode.create_with_hash(
            id="hash_test",
            type=NodeType.PARAGRAPH,
            content=content,
            file_path=Path("test.md"),
            line_number=1,
        )
        assert node.content_hash == expected_hash


class TestTranslationUnit:
    """Test TranslationUnit model."""

    def test_translation_unit_creation(self) -> None:
        """Test basic TranslationUnit creation."""
        unit = TranslationUnit(
            id="trans_id",
            source_node_id="node_id",
            source_content="Hello",
            source_lang="en",
            target_lang="ja",
            status=TranslationStatus.PENDING,
        )
        assert unit.id == "trans_id"
        assert unit.source_node_id == "node_id"
        assert unit.source_content == "Hello"
        assert unit.source_lang == "en"
        assert unit.target_lang == "ja"
        assert unit.status == TranslationStatus.PENDING
        assert unit.target_content is None

    def test_translated_unit(self) -> None:
        """Test translation unit with translated content."""
        unit = TranslationUnit(
            id="trans_id",
            source_node_id="node_id",
            source_content="Hello",
            target_content="こんにちは",
            source_lang="en",
            target_lang="ja",
            status=TranslationStatus.TRANSLATED,
        )
        assert unit.target_content == "こんにちは"
        assert unit.status == TranslationStatus.TRANSLATED

    def test_translation_status_transitions(self) -> None:
        """Test all translation status values."""
        for status in TranslationStatus:
            unit = TranslationUnit(
                id=f"trans_{status.value}",
                source_node_id="node_id",
                source_content="Content",
                source_lang="en",
                target_lang="ja",
                status=status,
            )
            assert unit.status == status

    def test_outdated_translation(self) -> None:
        """Test outdated translation with hash tracking."""
        unit = TranslationUnit(
            id="outdated_id",
            source_node_id="node_id",
            source_content="Updated content",
            target_content="古い翻訳",
            source_lang="en",
            target_lang="ja",
            status=TranslationStatus.OUTDATED,
            source_hash="new_hash",
            translated_hash="old_hash",
        )
        assert unit.status == TranslationStatus.OUTDATED
        assert unit.source_hash != unit.translated_hash


class TestReference:
    """Test Reference model."""

    def test_reference_creation(self) -> None:
        """Test basic Reference creation."""
        ref = Reference(
            id="ref_id",
            from_node_id="source_node",
            to_label="target-label",
            reference_type=ReferenceType.REF,
            line_number=10,
        )
        assert ref.id == "ref_id"
        assert ref.from_node_id == "source_node"
        assert ref.to_label == "target-label"
        assert ref.reference_type == ReferenceType.REF
        assert ref.line_number == 10

    def test_resolved_reference(self) -> None:
        """Test reference with resolved target."""
        ref = Reference(
            id="ref_id",
            from_node_id="source_node",
            to_label="target-label",
            to_node_id="target_node",
            reference_type=ReferenceType.DOC,
            line_number=20,
        )
        assert ref.to_node_id == "target_node"
        assert ref.is_resolved is True

    def test_unresolved_reference(self) -> None:
        """Test unresolved reference."""
        ref = Reference(
            id="ref_id",
            from_node_id="source_node",
            to_label="missing-label",
            reference_type=ReferenceType.REF,
            line_number=30,
        )
        assert ref.to_node_id is None
        assert ref.is_resolved is False

    def test_all_reference_types(self) -> None:
        """Test all reference types."""
        for ref_type in ReferenceType:
            ref = Reference(
                id=f"ref_{ref_type.value}",
                from_node_id="source",
                to_label="target",
                reference_type=ref_type,
                line_number=1,
            )
            assert ref.reference_type == ref_type
