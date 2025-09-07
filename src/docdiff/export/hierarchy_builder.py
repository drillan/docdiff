"""Build hierarchical structure from flat node list."""

import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from docdiff.compare.models import NodeMapping
from docdiff.models.export_schema import (
    DocumentFile,
    DocumentHierarchy,
    NodeContext,
    TranslationNode,
)
from docdiff.models.node import DocumentNode, NodeType


class HierarchyBuilder:
    """Build hierarchical document structure for AI-optimized export."""

    def __init__(self, context_window: int = 3):
        """Initialize hierarchy builder.

        Args:
            context_window: Number of nodes to include in context before/after
        """
        self.context_window = context_window
        self._node_map: Dict[str, TranslationNode] = {}
        self._file_groups: Dict[str, List[DocumentNode]] = {}

    def build_hierarchy(self, mappings: List[NodeMapping]) -> DocumentHierarchy:
        """Build complete document hierarchy from node mappings.

        Args:
            mappings: List of node mappings from comparison

        Returns:
            Complete document hierarchy with parent-child relationships
        """
        # Group nodes by file
        self._group_by_file(mappings)

        # Build hierarchy for each file
        hierarchy = DocumentHierarchy()

        for file_path, nodes in self._file_groups.items():
            doc_file = self._build_file_hierarchy(file_path, nodes, mappings)
            hierarchy.files[file_path] = doc_file
            hierarchy.total_files += 1
            hierarchy.total_nodes += doc_file.total_nodes

        return hierarchy

    def _group_by_file(self, mappings: List[NodeMapping]) -> None:
        """Group nodes by their source file."""
        self._file_groups.clear()

        for mapping in mappings:
            node = mapping.source_node
            file_path = str(getattr(node, "file_path", "unknown"))

            if file_path not in self._file_groups:
                self._file_groups[file_path] = []

            self._file_groups[file_path].append(node)

    def _build_file_hierarchy(
        self, file_path: str, nodes: List[DocumentNode], mappings: List[NodeMapping]
    ) -> DocumentFile:
        """Build hierarchy for a single file.

        Args:
            file_path: Path to the file
            nodes: All nodes in the file
            mappings: Original mappings for status information

        Returns:
            DocumentFile with hierarchical structure
        """
        # Create document file
        doc_file = DocumentFile(
            file_path=file_path,
            file_hash=self._calculate_file_hash(nodes),
            relative_path=self._get_relative_path(file_path),
        )

        # Create translation nodes
        translation_nodes: Dict[str, TranslationNode] = {}
        # Use list indices to map nodes to their generated IDs
        node_ids: List[str] = []  # Parallel list to nodes

        # First pass: Create all nodes
        for node in nodes:
            # Find corresponding mapping
            mapping = self._find_mapping(node, mappings)

            # Generate unique ID
            node_id = self._generate_node_id(node)
            node_ids.append(node_id)

            # Create translation node
            trans_node = self._create_translation_node(
                node, node_id, mapping, file_path
            )

            translation_nodes[node_id] = trans_node
            self._node_map[node_id] = trans_node

        # Second pass: Build parent-child relationships
        self._build_relationships(nodes, node_ids, translation_nodes)

        # Third pass: Add context windows
        self._add_context_windows(nodes, node_ids, translation_nodes)

        # Find root nodes (no parent)
        root_node_ids = [
            node_id
            for node_id, node in translation_nodes.items()
            if node.parent_id is None
        ]

        # Update document file
        doc_file.nodes = translation_nodes
        doc_file.root_node_ids = root_node_ids
        doc_file.total_nodes = len(translation_nodes)
        doc_file.missing_nodes = sum(
            1 for node in translation_nodes.values() if node.status == "missing"
        )
        doc_file.outdated_nodes = sum(
            1 for node in translation_nodes.values() if node.status == "outdated"
        )

        return doc_file

    def _create_translation_node(
        self,
        node: DocumentNode,
        node_id: str,
        mapping: Optional[NodeMapping],
        file_path: str,
    ) -> TranslationNode:
        """Create a translation node from document node.

        Args:
            node: Source document node
            node_id: Unique ID for the node
            mapping: Node mapping with translation status
            file_path: Path to the source file

        Returns:
            Translation node with all metadata
        """
        # Determine status and target content
        status = "missing"
        target = ""

        if mapping:
            status = mapping.mapping_type
            if mapping.target_node:
                target = mapping.target_node.content

        # Create context
        context = NodeContext(
            file_path=file_path, line_number=getattr(node, "line_number", 0)
        )

        # Extract metadata
        metadata = {}
        if hasattr(node, "label") and node.label:
            metadata["label"] = node.label
        if hasattr(node, "name") and node.name:
            metadata["name"] = node.name
        if hasattr(node, "caption") and node.caption:
            metadata["caption"] = node.caption

        return TranslationNode(
            id=node_id,
            type=self._get_node_type_string(node),
            level=node.level if node.level is not None else 0,
            source=node.content,
            target=target,
            status=status,
            context=context,
            metadata=metadata,
        )

    def _build_relationships(
        self,
        nodes: List[DocumentNode],
        node_ids: List[str],
        translation_nodes: Dict[str, TranslationNode],
    ) -> None:
        """Build parent-child relationships between nodes.

        Args:
            nodes: All document nodes
            node_ids: List of node IDs (parallel to nodes list)
            translation_nodes: All translation nodes
        """
        # Track section hierarchy with indices
        section_stack: List[tuple[int, int]] = []  # (node_index, level)

        for i, node in enumerate(nodes):
            node_id = node_ids[i]
            trans_node = translation_nodes[node_id]

            # Handle sections
            if self._is_section(node):
                # Pop sections at same or higher level
                node_level = node.level if node.level is not None else 0
                while section_stack and section_stack[-1][1] >= node_level:
                    section_stack.pop()

                # Set parent if there's a parent section
                if section_stack:
                    parent_idx, _ = section_stack[-1]
                    parent_id = node_ids[parent_idx]
                    trans_node.parent_id = parent_id
                    translation_nodes[parent_id].children_ids.append(node_id)

                # Add to stack
                section_stack.append((i, node_level))

            # Non-section nodes belong to current section
            elif section_stack:
                parent_idx, _ = section_stack[-1]
                parent_id = node_ids[parent_idx]
                trans_node.parent_id = parent_id
                translation_nodes[parent_id].children_ids.append(node_id)

    def _add_context_windows(
        self,
        nodes: List[DocumentNode],
        node_ids: List[str],
        translation_nodes: Dict[str, TranslationNode],
    ) -> None:
        """Add context windows to each node.

        Args:
            nodes: All document nodes
            node_ids: List of node IDs (parallel to nodes list)
            translation_nodes: All translation nodes
        """
        for i, node in enumerate(nodes):
            node_id = node_ids[i]
            trans_node = translation_nodes[node_id]

            # Get preceding context
            if trans_node.context:
                preceding_text = self._get_preceding_context(nodes, i)
                if preceding_text:
                    trans_node.context.preceding_text = preceding_text

                # Get following context
                following_text = self._get_following_context(nodes, i)
                if following_text:
                    trans_node.context.following_text = following_text

                # Get parent section title
                if trans_node.parent_id:
                    parent_node = translation_nodes.get(trans_node.parent_id)
                    if parent_node and self._is_section_type(parent_node.type):
                        trans_node.context.parent_section = parent_node.source

    def _get_preceding_context(
        self, nodes: List[DocumentNode], current_index: int
    ) -> str:
        """Get preceding text context.

        Args:
            nodes: All document nodes
            current_index: Index of current node

        Returns:
            Concatenated preceding text
        """
        context_parts: List[str] = []
        count = 0

        for i in range(current_index - 1, -1, -1):
            if count >= self.context_window:
                break

            node = nodes[i]
            # Skip sections and code blocks for context
            if not self._is_section(node) and node.type != NodeType.CODE_BLOCK:
                context_parts.insert(0, node.content[:200])  # Limit length
                count += 1

        return " [...] ".join(context_parts) if context_parts else ""

    def _get_following_context(
        self, nodes: List[DocumentNode], current_index: int
    ) -> str:
        """Get following text context.

        Args:
            nodes: All document nodes
            current_index: Index of current node

        Returns:
            Concatenated following text
        """
        context_parts: List[str] = []
        count = 0

        for i in range(current_index + 1, len(nodes)):
            if count >= self.context_window:
                break

            node = nodes[i]
            # Skip sections and code blocks for context
            if not self._is_section(node) and node.type != NodeType.CODE_BLOCK:
                context_parts.append(node.content[:200])  # Limit length
                count += 1

        return " [...] ".join(context_parts) if context_parts else ""

    def _find_mapping(
        self, node: DocumentNode, mappings: List[NodeMapping]
    ) -> Optional[NodeMapping]:
        """Find the mapping for a given node.

        Args:
            node: Document node to find mapping for
            mappings: All node mappings

        Returns:
            Corresponding mapping or None
        """
        for mapping in mappings:
            if mapping.source_node == node:
                return mapping
        return None

    def _generate_node_id(self, node: DocumentNode) -> str:
        """Generate unique ID for a node.

        Args:
            node: Document node

        Returns:
            Unique ID string
        """
        # Use existing ID if available
        if hasattr(node, "id") and node.id:
            return node.id

        # Generate new UUID
        return f"node-{uuid4().hex[:8]}"

    def _calculate_file_hash(self, nodes: List[DocumentNode]) -> str:
        """Calculate hash for file content.

        Args:
            nodes: All nodes in the file

        Returns:
            SHA256 hash of content
        """
        content = "".join(node.content for node in nodes)
        return f"sha256:{hashlib.sha256(content.encode()).hexdigest()[:16]}"

    def _get_relative_path(self, file_path: str) -> str:
        """Get relative path from absolute path.

        Args:
            file_path: Absolute file path

        Returns:
            Relative path string
        """
        try:
            path = Path(file_path)
            # Try to make relative to common doc directories
            for parent in ["docs", "documentation", "doc"]:
                if parent in path.parts:
                    idx = path.parts.index(parent)
                    return str(Path(*path.parts[idx:]))

            # Fallback to just the filename
            return path.name
        except Exception:
            return file_path

    def _is_section(self, node: DocumentNode) -> bool:
        """Check if node is a section.

        Args:
            node: Document node

        Returns:
            True if node is a section
        """
        return node.type == NodeType.SECTION

    def _is_section_type(self, node_type: str) -> bool:
        """Check if node type string represents a section.

        Args:
            node_type: Node type string

        Returns:
            True if type is section
        """
        return node_type.lower() in ["section", "heading", "title"]

    def _get_node_type_string(self, node: DocumentNode) -> str:
        """Get string representation of node type.

        Args:
            node: Document node

        Returns:
            Node type as string
        """
        if hasattr(node.type, "value"):
            return node.type.value
        return str(node.type).lower().replace("nodetype.", "")
