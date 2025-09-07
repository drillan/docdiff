"""Export schema models for AI-optimized JSON format."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExportStatistics(BaseModel):
    """Statistics about the export content."""

    total_nodes: int = 0
    missing: int = 0
    outdated: int = 0
    translated: int = 0
    total_files: int = 0
    coverage_percentage: float = 0.0


class ExportMetadata(BaseModel):
    """Metadata for the export."""

    docdiff_version: str = "0.0.1"
    export_timestamp: datetime = Field(default_factory=datetime.now)
    source_lang: str
    target_lang: str
    statistics: ExportStatistics = Field(default_factory=ExportStatistics)
    schema_version: str = "1.0"


class GlossaryTermExport(BaseModel):
    """Glossary term for export."""

    term: str
    definition: str
    source_file: str
    line_number: int
    aliases: List[str] = Field(default_factory=list)
    target_translation: Optional[str] = None
    usage_count: int = 0


class CrossReferenceExport(BaseModel):
    """Cross-reference information for export."""

    type: str  # ref, doc, term, numref, etc.
    from_node: str  # Node ID where reference appears
    to_label: str  # Target label or document
    resolved: bool = False
    source_file: str
    line_number: int


class SphinxContextExport(BaseModel):
    """Sphinx-specific context for translation."""

    glossary_terms: List[GlossaryTermExport] = Field(default_factory=list)
    cross_references: List[CrossReferenceExport] = Field(default_factory=list)
    project_name: Optional[str] = None
    project_version: Optional[str] = None
    has_myst: bool = False
    has_i18n: bool = False


class NodeContext(BaseModel):
    """Context information for a translation node."""

    preceding_text: Optional[str] = None
    following_text: Optional[str] = None
    parent_section: Optional[str] = None
    document_title: Optional[str] = None
    file_path: str
    line_number: int = 0


class TranslationNode(BaseModel):
    """Individual translation unit with hierarchy."""

    id: str
    type: str  # section, paragraph, code_block, etc.
    level: int = 0
    source: str
    target: str = ""
    status: str = "missing"  # missing, outdated, translated
    context: Optional[NodeContext] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentFile(BaseModel):
    """Document file with hierarchical nodes."""

    file_path: str
    file_hash: str
    relative_path: str
    root_node_ids: List[str] = Field(default_factory=list)
    nodes: Dict[str, TranslationNode] = Field(default_factory=dict)
    total_nodes: int = 0
    missing_nodes: int = 0
    outdated_nodes: int = 0


class SharedBatchContext(BaseModel):
    """Shared context for a translation batch."""

    glossary_terms: List[str] = Field(default_factory=list)
    section_title: Optional[str] = None
    document_title: Optional[str] = None
    file_path: str
    batch_theme: Optional[str] = None  # e.g., "API Reference", "User Guide"


class TranslationBatch(BaseModel):
    """Optimized batch for AI translation."""

    batch_id: int
    estimated_tokens: int
    file_group: str  # Primary file path
    section_range: str  # e.g., "Introduction to Quick Start"
    node_ids: List[str]
    shared_context: SharedBatchContext
    priority: int = 0  # Higher priority batches should be translated first
    dependencies: List[int] = Field(default_factory=list)  # Other batch IDs


class DocumentHierarchy(BaseModel):
    """Complete document hierarchy."""

    files: Dict[str, DocumentFile] = Field(default_factory=dict)
    total_files: int = 0
    total_nodes: int = 0


class ExportSchema(BaseModel):
    """Complete export schema for AI-optimized translation."""

    schema_version: str = "1.0"
    metadata: ExportMetadata
    sphinx_context: Optional[SphinxContextExport] = None
    document_hierarchy: DocumentHierarchy
    translation_batches: List[TranslationBatch] = Field(default_factory=list)

    def get_node_by_id(self, node_id: str) -> Optional[TranslationNode]:
        """Get a node by its ID from any file."""
        for file in self.document_hierarchy.files.values():
            if node_id in file.nodes:
                return file.nodes[node_id]
        return None

    def get_batch_nodes(self, batch_id: int) -> List[TranslationNode]:
        """Get all nodes in a specific batch."""
        for batch in self.translation_batches:
            if batch.batch_id == batch_id:
                nodes: List[TranslationNode] = []
                for node_id in batch.node_ids:
                    node = self.get_node_by_id(node_id)
                    if node is not None:
                        nodes.append(node)
                return nodes
        return []

    def calculate_total_tokens(self) -> int:
        """Calculate total estimated tokens across all batches."""
        return sum(batch.estimated_tokens for batch in self.translation_batches)

    def get_priority_batches(self) -> List[TranslationBatch]:
        """Get batches sorted by priority."""
        return sorted(self.translation_batches, key=lambda b: b.priority, reverse=True)
