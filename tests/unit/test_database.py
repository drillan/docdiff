"""Unit tests for database layer."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from docdiff.database.connection import DatabaseConnection
from docdiff.database.repository import (
    NodeRepository,
    ReferenceRepository,
    TranslationRepository,
)
from docdiff.database.schema import create_tables
from docdiff.models.node import DocumentNode, NodeType
from docdiff.models.reference import Reference, ReferenceType
from docdiff.models.translation import TranslationStatus, TranslationUnit


@pytest.fixture
def db_connection() -> Generator[DatabaseConnection, None, None]:
    """Create a temporary database connection for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp_file:
        conn = DatabaseConnection(Path(tmp_file.name))
        conn.connect()
        create_tables(conn)
        yield conn
        conn.close()


class TestDatabaseConnection:
    """Test database connection management."""

    def test_connection_creation(self) -> None:
        """Test database connection creation."""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp_file:
            conn = DatabaseConnection(Path(tmp_file.name))
            conn.connect()
            assert conn.connection is not None
            conn.close()

    def test_execute_query(self, db_connection: DatabaseConnection) -> None:
        """Test executing queries."""
        result = db_connection.execute("SELECT 1 as test")
        assert result[0]["test"] == 1

    def test_transaction_management(self, db_connection: DatabaseConnection) -> None:
        """Test transaction commit and rollback."""
        with db_connection.transaction():
            db_connection.execute(
                "CREATE TABLE test_table (id INTEGER PRIMARY KEY, value TEXT)"
            )
            db_connection.execute(
                "INSERT INTO test_table (value) VALUES (?)", ("test_value",)
            )

        result = db_connection.execute("SELECT * FROM test_table")
        assert len(result) == 1
        assert result[0]["value"] == "test_value"


class TestNodeRepository:
    """Test NodeRepository operations."""

    def test_save_node(self, db_connection: DatabaseConnection) -> None:
        """Test saving a document node."""
        repo = NodeRepository(db_connection)
        node = DocumentNode(
            id="test_node",
            type=NodeType.SECTION,
            content="# Test Section",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="test_hash",
        )
        repo.save(node)

        saved_node = repo.find_by_id("test_node")
        assert saved_node is not None
        assert saved_node.id == node.id
        assert saved_node.type == node.type

    def test_find_by_file(self, db_connection: DatabaseConnection) -> None:
        """Test finding nodes by file path."""
        repo = NodeRepository(db_connection)
        file_path = Path("test.md")

        for i in range(3):
            node = DocumentNode(
                id=f"node_{i}",
                type=NodeType.PARAGRAPH,
                content=f"Paragraph {i}",
                file_path=file_path,
                line_number=i + 1,
                content_hash=f"hash_{i}",
            )
            repo.save(node)

        nodes = repo.find_by_file(file_path)
        assert len(nodes) == 3
        assert all(node.file_path == file_path for node in nodes)

    def test_update_node(self, db_connection: DatabaseConnection) -> None:
        """Test updating an existing node."""
        repo = NodeRepository(db_connection)
        node = DocumentNode(
            id="update_test",
            type=NodeType.CODE_BLOCK,
            content="print('old')",
            file_path=Path("test.py"),
            line_number=1,
            content_hash="old_hash",
        )
        repo.save(node)

        node.content = "print('new')"
        node.content_hash = "new_hash"
        repo.update(node)

        updated_node = repo.find_by_id("update_test")
        assert updated_node is not None
        assert updated_node.content == "print('new')"
        assert updated_node.content_hash == "new_hash"

    def test_delete_node(self, db_connection: DatabaseConnection) -> None:
        """Test deleting a node."""
        repo = NodeRepository(db_connection)
        node = DocumentNode(
            id="delete_test",
            type=NodeType.PARAGRAPH,
            content="To be deleted",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="delete_hash",
        )
        repo.save(node)

        repo.delete("delete_test")
        assert repo.find_by_id("delete_test") is None

    def test_find_by_label(self, db_connection: DatabaseConnection) -> None:
        """Test finding nodes by label."""
        repo = NodeRepository(db_connection)
        node = DocumentNode(
            id="labeled_node",
            type=NodeType.SECTION,
            content="# Labeled Section",
            label="test-label",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="label_hash",
        )
        repo.save(node)

        found = repo.find_by_label("test-label")
        assert found is not None
        assert found.id == "labeled_node"
        assert found.label == "test-label"


class TestTranslationRepository:
    """Test TranslationRepository operations."""

    def test_save_translation_unit(self, db_connection: DatabaseConnection) -> None:
        """Test saving a translation unit."""
        # First create a node that the translation unit references
        node_repo = NodeRepository(db_connection)
        node = DocumentNode(
            id="node_1",
            type=NodeType.PARAGRAPH,
            content="Hello",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="hello_hash",
        )
        node_repo.save(node)

        repo = TranslationRepository(db_connection)
        unit = TranslationUnit(
            id="trans_1",
            source_node_id="node_1",
            source_content="Hello",
            source_lang="en",
            target_lang="ja",
            status=TranslationStatus.PENDING,
        )
        repo.save(unit)

        saved_unit = repo.find_by_id("trans_1")
        assert saved_unit is not None
        assert saved_unit.id == unit.id
        assert saved_unit.source_content == "Hello"

    def test_find_by_source_node(self, db_connection: DatabaseConnection) -> None:
        """Test finding translation units by source node."""
        # First create a node
        node_repo = NodeRepository(db_connection)
        node = DocumentNode(
            id="source_1",
            type=NodeType.PARAGRAPH,
            content="Hello",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="source_hash",
        )
        node_repo.save(node)

        repo = TranslationRepository(db_connection)
        source_node_id = "source_1"

        for lang in ["ja", "fr", "de"]:
            unit = TranslationUnit(
                id=f"trans_{lang}",
                source_node_id=source_node_id,
                source_content="Hello",
                source_lang="en",
                target_lang=lang,
                status=TranslationStatus.PENDING,
            )
            repo.save(unit)

        units = repo.find_by_source_node(source_node_id)
        assert len(units) == 3
        assert all(unit.source_node_id == source_node_id for unit in units)

    def test_update_translation_status(self, db_connection: DatabaseConnection) -> None:
        """Test updating translation status."""
        # First create a node
        node_repo = NodeRepository(db_connection)
        node = DocumentNode(
            id="node_1",
            type=NodeType.PARAGRAPH,
            content="Test",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="test_hash",
        )
        node_repo.save(node)

        repo = TranslationRepository(db_connection)
        unit = TranslationUnit(
            id="status_test",
            source_node_id="node_1",
            source_content="Test",
            source_lang="en",
            target_lang="ja",
            status=TranslationStatus.PENDING,
        )
        repo.save(unit)

        unit.status = TranslationStatus.TRANSLATED
        unit.target_content = "テスト"
        repo.update(unit)

        updated = repo.find_by_id("status_test")
        assert updated is not None
        assert updated.status == TranslationStatus.TRANSLATED
        assert updated.target_content == "テスト"

    def test_find_pending_translations(self, db_connection: DatabaseConnection) -> None:
        """Test finding pending translations."""
        # First create nodes
        node_repo = NodeRepository(db_connection)
        for i in range(4):
            node = DocumentNode(
                id=f"node_{i}",
                type=NodeType.PARAGRAPH,
                content=f"Content {i}",
                file_path=Path("test.md"),
                line_number=i + 1,
                content_hash=f"hash_{i}",
            )
            node_repo.save(node)

        repo = TranslationRepository(db_connection)

        statuses = [
            TranslationStatus.PENDING,
            TranslationStatus.TRANSLATED,
            TranslationStatus.PENDING,
            TranslationStatus.REVIEWED,
        ]

        for i, status in enumerate(statuses):
            unit = TranslationUnit(
                id=f"unit_{i}",
                source_node_id=f"node_{i}",
                source_content=f"Content {i}",
                source_lang="en",
                target_lang="ja",
                status=status,
            )
            repo.save(unit)

        pending = repo.find_by_status(TranslationStatus.PENDING)
        assert len(pending) == 2
        assert all(unit.status == TranslationStatus.PENDING for unit in pending)


class TestReferenceRepository:
    """Test ReferenceRepository operations."""

    def test_save_reference(self, db_connection: DatabaseConnection) -> None:
        """Test saving a reference."""
        # First create a node
        node_repo = NodeRepository(db_connection)
        node = DocumentNode(
            id="source_node",
            type=NodeType.PARAGRAPH,
            content="Content with reference",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="ref_hash",
        )
        node_repo.save(node)

        repo = ReferenceRepository(db_connection)
        ref = Reference(
            id="ref_1",
            from_node_id="source_node",
            to_label="target-label",
            reference_type=ReferenceType.REF,
            line_number=10,
        )
        repo.save(ref)

        saved_ref = repo.find_by_id("ref_1")
        assert saved_ref is not None
        assert saved_ref.id == ref.id
        assert saved_ref.to_label == "target-label"

    def test_find_by_from_node(self, db_connection: DatabaseConnection) -> None:
        """Test finding references from a specific node."""
        # First create a node
        node_repo = NodeRepository(db_connection)
        node = DocumentNode(
            id="source_node",
            type=NodeType.PARAGRAPH,
            content="Content",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="from_hash",
        )
        node_repo.save(node)

        repo = ReferenceRepository(db_connection)
        from_node_id = "source_node"

        for i in range(3):
            ref = Reference(
                id=f"ref_{i}",
                from_node_id=from_node_id,
                to_label=f"label_{i}",
                reference_type=ReferenceType.REF,
                line_number=i + 1,
            )
            repo.save(ref)

        refs = repo.find_by_from_node(from_node_id)
        assert len(refs) == 3
        assert all(ref.from_node_id == from_node_id for ref in refs)

    def test_resolve_reference(self, db_connection: DatabaseConnection) -> None:
        """Test resolving a reference to a target node."""
        # First create nodes
        node_repo = NodeRepository(db_connection)
        source_node = DocumentNode(
            id="source",
            type=NodeType.PARAGRAPH,
            content="Source",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="source_hash",
        )
        target_node = DocumentNode(
            id="target_node_id",
            type=NodeType.SECTION,
            content="Target",
            label="target-label",
            file_path=Path("test.md"),
            line_number=10,
            content_hash="target_hash",
        )
        node_repo.save(source_node)
        node_repo.save(target_node)

        repo = ReferenceRepository(db_connection)
        ref = Reference(
            id="unresolved_ref",
            from_node_id="source",
            to_label="target-label",
            reference_type=ReferenceType.REF,
            line_number=5,
        )
        repo.save(ref)

        repo.resolve("unresolved_ref", "target_node_id")

        resolved = repo.find_by_id("unresolved_ref")
        assert resolved is not None
        assert resolved.to_node_id == "target_node_id"
        assert resolved.is_resolved is True

    def test_find_unresolved_references(
        self, db_connection: DatabaseConnection
    ) -> None:
        """Test finding unresolved references."""
        # First create nodes
        node_repo = NodeRepository(db_connection)
        source_node = DocumentNode(
            id="source",
            type=NodeType.PARAGRAPH,
            content="Source",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="source_hash",
        )
        node_repo.save(source_node)

        for i in range(2):
            target_node = DocumentNode(
                id=f"target_{i}",
                type=NodeType.SECTION,
                content=f"Target {i}",
                label=f"label_{i}",
                file_path=Path("test.md"),
                line_number=(i + 1) * 10,
                content_hash=f"target_hash_{i}",
            )
            node_repo.save(target_node)

        repo = ReferenceRepository(db_connection)

        # Save some resolved references
        for i in range(2):
            ref = Reference(
                id=f"resolved_{i}",
                from_node_id="source",
                to_label=f"label_{i}",
                to_node_id=f"target_{i}",
                reference_type=ReferenceType.REF,
                line_number=i,
            )
            repo.save(ref)

        # Save some unresolved references
        for i in range(3):
            ref = Reference(
                id=f"unresolved_{i}",
                from_node_id="source",
                to_label=f"missing_{i}",
                reference_type=ReferenceType.REF,
                line_number=i + 10,
            )
            repo.save(ref)

        unresolved = repo.find_unresolved()
        assert len(unresolved) == 3
        assert all(not ref.is_resolved for ref in unresolved)
