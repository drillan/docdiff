"""Repository classes for database operations."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from docdiff.database.connection import DatabaseConnection
from docdiff.models.node import DocumentNode, NodeType
from docdiff.models.reference import Reference, ReferenceType
from docdiff.models.translation import TranslationStatus, TranslationUnit


class NodeRepository:
    """Repository for DocumentNode operations."""

    def __init__(self, connection: DatabaseConnection) -> None:
        """Initialize NodeRepository.

        Args:
            connection: Database connection
        """
        self.connection = connection

    def save(self, node: DocumentNode) -> None:
        """Save a document node to the database.

        Args:
            node: DocumentNode to save
        """
        metadata_json = json.dumps(node.metadata) if node.metadata else None

        self.connection.execute(
            """
            INSERT OR REPLACE INTO document_nodes (
                id, type, content, level, title, label, name, caption,
                language, parent_id, file_path, line_number, content_hash, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                node.id,
                node.type.value,
                node.content,
                node.level,
                node.title,
                node.label,
                node.name,
                node.caption,
                node.language,
                node.parent_id,
                str(node.file_path),
                node.line_number,
                node.content_hash,
                metadata_json,
            ),
        )

        # Save children relationships
        if node.children_ids:
            self.connection.execute(
                "DELETE FROM node_children WHERE parent_id = ?", (node.id,)
            )
            params_list: List[Tuple[Any, ...]] = [
                (node.id, child_id, i) for i, child_id in enumerate(node.children_ids)
            ]
            self.connection.execute_many(
                "INSERT INTO node_children (parent_id, child_id, position) VALUES (?, ?, ?)",
                params_list,
            )

        self.connection.commit()

    def find_by_id(self, node_id: str) -> Optional[DocumentNode]:
        """Find a node by its ID.

        Args:
            node_id: Node ID to search for

        Returns:
            DocumentNode if found, None otherwise
        """
        result = self.connection.execute(
            "SELECT * FROM document_nodes WHERE id = ?", (node_id,)
        )
        if not result:
            return None

        row = result[0]
        return self._row_to_node(row)

    def find_by_file(self, file_path: Path) -> List[DocumentNode]:
        """Find all nodes from a specific file.

        Args:
            file_path: File path to search for

        Returns:
            List of DocumentNodes
        """
        result = self.connection.execute(
            "SELECT * FROM document_nodes WHERE file_path = ? ORDER BY line_number",
            (str(file_path),),
        )
        return [self._row_to_node(row) for row in result]

    def find_by_label(self, label: str) -> Optional[DocumentNode]:
        """Find a node by its label.

        Args:
            label: Label to search for

        Returns:
            DocumentNode if found, None otherwise
        """
        result = self.connection.execute(
            "SELECT * FROM document_nodes WHERE label = ?", (label,)
        )
        if not result:
            return None

        row = result[0]
        return self._row_to_node(row)

    def update(self, node: DocumentNode) -> None:
        """Update an existing node.

        Args:
            node: DocumentNode with updated values
        """
        self.save(node)  # save method handles INSERT OR REPLACE

    def delete(self, node_id: str) -> None:
        """Delete a node by its ID.

        Args:
            node_id: ID of the node to delete
        """
        self.connection.execute(
            "DELETE FROM node_children WHERE parent_id = ? OR child_id = ?",
            (node_id, node_id),
        )
        self.connection.execute("DELETE FROM document_nodes WHERE id = ?", (node_id,))
        self.connection.commit()

    def get_all_nodes(self) -> List[DocumentNode]:
        """Get all nodes from the database.

        Returns:
            List of all DocumentNodes
        """
        result = self.connection.execute(
            "SELECT * FROM document_nodes ORDER BY file_path, line_number"
        )
        return [self._row_to_node(row) for row in result]

    def _row_to_node(self, row: Dict[str, Any]) -> DocumentNode:
        """Convert a database row to a DocumentNode.

        Args:
            row: Database row

        Returns:
            DocumentNode instance
        """
        # Get children IDs
        children_result = self.connection.execute(
            "SELECT child_id FROM node_children WHERE parent_id = ? ORDER BY position",
            (row["id"],),
        )
        children_ids = [child["child_id"] for child in children_result]

        # Parse metadata
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}

        return DocumentNode(
            id=row["id"],
            type=NodeType(row["type"]),
            content=row["content"],
            level=row["level"],
            title=row["title"],
            label=row["label"],
            name=row["name"],
            caption=row["caption"],
            language=row["language"],
            parent_id=row["parent_id"],
            children_ids=children_ids,
            file_path=Path(row["file_path"]),
            line_number=row["line_number"],
            content_hash=row["content_hash"],
            metadata=metadata,
            doc_language="en",  # Default value, will be updated from db later
            source_file_hash=None,  # Will be populated from db if exists
            last_modified=None,  # Will be populated from db if exists
        )


class TranslationRepository:
    """Repository for TranslationUnit operations."""

    def __init__(self, connection: DatabaseConnection) -> None:
        """Initialize TranslationRepository.

        Args:
            connection: Database connection
        """
        self.connection = connection

    def save(self, unit: TranslationUnit) -> None:
        """Save a translation unit to the database.

        Args:
            unit: TranslationUnit to save
        """
        self.connection.execute(
            """
            INSERT OR REPLACE INTO translation_units (
                id, source_node_id, source_content, target_content,
                source_lang, target_lang, status, source_hash,
                translated_hash, translated_at, reviewed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                unit.id,
                unit.source_node_id,
                unit.source_content,
                unit.target_content,
                unit.source_lang,
                unit.target_lang,
                unit.status.value,
                unit.source_hash,
                unit.translated_hash,
                unit.translated_at.isoformat() if unit.translated_at else None,
                unit.reviewed_at.isoformat() if unit.reviewed_at else None,
            ),
        )
        self.connection.commit()

    def find_by_id(self, unit_id: str) -> Optional[TranslationUnit]:
        """Find a translation unit by its ID.

        Args:
            unit_id: Translation unit ID

        Returns:
            TranslationUnit if found, None otherwise
        """
        result = self.connection.execute(
            "SELECT * FROM translation_units WHERE id = ?", (unit_id,)
        )
        if not result:
            return None

        row = result[0]
        return self._row_to_unit(row)

    def find_by_source_node(self, source_node_id: str) -> List[TranslationUnit]:
        """Find all translation units for a source node.

        Args:
            source_node_id: Source node ID

        Returns:
            List of TranslationUnits
        """
        result = self.connection.execute(
            "SELECT * FROM translation_units WHERE source_node_id = ?",
            (source_node_id,),
        )
        return [self._row_to_unit(row) for row in result]

    def find_by_status(self, status: TranslationStatus) -> List[TranslationUnit]:
        """Find all translation units with a specific status.

        Args:
            status: Translation status

        Returns:
            List of TranslationUnits
        """
        result = self.connection.execute(
            "SELECT * FROM translation_units WHERE status = ?", (status.value,)
        )
        return [self._row_to_unit(row) for row in result]

    def update(self, unit: TranslationUnit) -> None:
        """Update an existing translation unit.

        Args:
            unit: TranslationUnit with updated values
        """
        self.save(unit)  # save method handles INSERT OR REPLACE

    def _row_to_unit(self, row: Dict[str, Any]) -> TranslationUnit:
        """Convert a database row to a TranslationUnit.

        Args:
            row: Database row

        Returns:
            TranslationUnit instance
        """
        from datetime import datetime

        return TranslationUnit(
            id=row["id"],
            source_node_id=row["source_node_id"],
            source_content=row["source_content"],
            target_content=row["target_content"],
            source_lang=row["source_lang"],
            target_lang=row["target_lang"],
            status=TranslationStatus(row["status"]),
            source_hash=row["source_hash"],
            translated_hash=row["translated_hash"],
            translated_at=(
                datetime.fromisoformat(row["translated_at"])
                if row["translated_at"]
                else None
            ),
            reviewed_at=(
                datetime.fromisoformat(row["reviewed_at"])
                if row["reviewed_at"]
                else None
            ),
        )


class ReferenceRepository:
    """Repository for Reference operations."""

    def __init__(self, connection: DatabaseConnection) -> None:
        """Initialize ReferenceRepository.

        Args:
            connection: Database connection
        """
        self.connection = connection

    def save(self, reference: Reference) -> None:
        """Save a reference to the database.

        Args:
            reference: Reference to save
        """
        self.connection.execute(
            """
            INSERT OR REPLACE INTO document_references (
                id, from_node_id, to_label, to_node_id,
                reference_type, line_number, file_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reference.id,
                reference.from_node_id,
                reference.to_label,
                reference.to_node_id,
                reference.reference_type.value,
                reference.line_number,
                reference.file_path,
            ),
        )
        self.connection.commit()

    def find_by_id(self, ref_id: str) -> Optional[Reference]:
        """Find a reference by its ID.

        Args:
            ref_id: Reference ID

        Returns:
            Reference if found, None otherwise
        """
        result = self.connection.execute(
            "SELECT * FROM document_references WHERE id = ?", (ref_id,)
        )
        if not result:
            return None

        row = result[0]
        return self._row_to_reference(row)

    def find_by_from_node(self, from_node_id: str) -> List[Reference]:
        """Find all references from a specific node.

        Args:
            from_node_id: Source node ID

        Returns:
            List of References
        """
        result = self.connection.execute(
            "SELECT * FROM document_references WHERE from_node_id = ?", (from_node_id,)
        )
        return [self._row_to_reference(row) for row in result]

    def find_unresolved(self) -> List[Reference]:
        """Find all unresolved references.

        Returns:
            List of unresolved References
        """
        result = self.connection.execute(
            "SELECT * FROM document_references WHERE to_node_id IS NULL"
        )
        return [self._row_to_reference(row) for row in result]

    def resolve(self, ref_id: str, to_node_id: str) -> None:
        """Resolve a reference to a target node.

        Args:
            ref_id: Reference ID
            to_node_id: Target node ID
        """
        self.connection.execute(
            "UPDATE document_references SET to_node_id = ? WHERE id = ?",
            (to_node_id, ref_id),
        )
        self.connection.commit()

    def _row_to_reference(self, row: Dict[str, Any]) -> Reference:
        """Convert a database row to a Reference.

        Args:
            row: Database row

        Returns:
            Reference instance
        """
        return Reference(
            id=row["id"],
            from_node_id=row["from_node_id"],
            to_label=row["to_label"],
            to_node_id=row["to_node_id"],
            reference_type=ReferenceType(row["reference_type"]),
            line_number=row["line_number"],
            file_path=row["file_path"],
        )
