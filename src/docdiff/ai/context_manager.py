"""Context window management for enhanced translation quality."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from docdiff.models.export_schema import TranslationNode


@dataclass
class ContextWindow:
    """Context information for a node."""

    preceding_nodes: List[TranslationNode]
    following_nodes: List[TranslationNode]
    parent_section: Optional[TranslationNode] = None
    sibling_nodes: Optional[List[TranslationNode]] = None

    @property
    def preceding_text(self) -> str:
        """Get concatenated preceding text."""
        if not self.preceding_nodes:
            return ""
        texts = [node.source[:200] for node in self.preceding_nodes]
        return " [...] ".join(texts)

    @property
    def following_text(self) -> str:
        """Get concatenated following text."""
        if not self.following_nodes:
            return ""
        texts = [node.source[:200] for node in self.following_nodes]
        return " [...] ".join(texts)

    @property
    def section_title(self) -> str:
        """Get parent section title if available."""
        if self.parent_section:
            return self.parent_section.source[:100]
        return ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export."""
        return {
            "preceding_text": self.preceding_text,
            "following_text": self.following_text,
            "section_title": self.section_title,
            "has_siblings": bool(self.sibling_nodes),
            "sibling_count": len(self.sibling_nodes) if self.sibling_nodes else 0,
        }


class ContextManager:
    """Manage context windows for translation nodes."""

    def __init__(self, window_size: int = 3, max_text_length: int = 200):
        """Initialize context manager.

        Args:
            window_size: Number of nodes to include before/after
            max_text_length: Maximum text length per node in context
        """
        self.window_size = window_size
        self.max_text_length = max_text_length
        self._node_index: Dict[str, int] = {}
        self._nodes_list: List[TranslationNode] = []
        self._parent_map: Dict[str, TranslationNode] = {}

    def build_context_windows(
        self,
        nodes: List[TranslationNode],
    ) -> Dict[str, ContextWindow]:
        """Build context windows for all nodes.

        Args:
            nodes: List of translation nodes

        Returns:
            Dictionary mapping node ID to context window
        """
        # Build internal indices
        self._build_indices(nodes)

        # Create context windows
        context_windows: Dict[str, ContextWindow] = {}

        for i, node in enumerate(self._nodes_list):
            context_window = self._create_context_window(i, node)
            context_windows[node.id] = context_window

        return context_windows

    def _build_indices(self, nodes: List[TranslationNode]) -> None:
        """Build internal node indices.

        Args:
            nodes: List of translation nodes
        """
        self._nodes_list = nodes
        self._node_index.clear()
        self._parent_map.clear()

        # Build node index
        for i, node in enumerate(nodes):
            self._node_index[node.id] = i

        # Build parent map
        for node in nodes:
            if node.parent_id:
                parent = self._find_node_by_id(node.parent_id)
                if parent:
                    self._parent_map[node.id] = parent

    def _create_context_window(
        self,
        index: int,
        node: TranslationNode,
    ) -> ContextWindow:
        """Create context window for a single node.

        Args:
            index: Node index in list
            node: Translation node

        Returns:
            Context window for the node
        """
        # Get preceding nodes
        preceding_nodes = self._get_preceding_nodes(index)

        # Get following nodes
        following_nodes = self._get_following_nodes(index)

        # Get parent section
        parent_section = self._parent_map.get(node.id)

        # Get sibling nodes
        sibling_nodes = self._get_sibling_nodes(node)

        return ContextWindow(
            preceding_nodes=preceding_nodes,
            following_nodes=following_nodes,
            parent_section=parent_section,
            sibling_nodes=sibling_nodes,
        )

    def _get_preceding_nodes(self, index: int) -> List[TranslationNode]:
        """Get preceding nodes within window.

        Args:
            index: Current node index

        Returns:
            List of preceding nodes
        """
        preceding: List[TranslationNode] = []
        count = 0

        for i in range(index - 1, -1, -1):
            if count >= self.window_size:
                break

            node = self._nodes_list[i]

            # Skip section headers in context
            if not self._is_section_node(node):
                preceding.insert(0, node)
                count += 1

        return preceding

    def _get_following_nodes(self, index: int) -> List[TranslationNode]:
        """Get following nodes within window.

        Args:
            index: Current node index

        Returns:
            List of following nodes
        """
        following: List[TranslationNode] = []
        count = 0

        for i in range(index + 1, len(self._nodes_list)):
            if count >= self.window_size:
                break

            node = self._nodes_list[i]

            # Skip section headers in context
            if not self._is_section_node(node):
                following.append(node)
                count += 1

        return following

    def _get_sibling_nodes(self, node: TranslationNode) -> List[TranslationNode]:
        """Get sibling nodes (same parent).

        Args:
            node: Current node

        Returns:
            List of sibling nodes
        """
        if not node.parent_id:
            return []

        siblings: List[TranslationNode] = []

        for other_node in self._nodes_list:
            if other_node.parent_id == node.parent_id and other_node.id != node.id:
                siblings.append(other_node)

        return siblings

    def _find_node_by_id(self, node_id: str) -> Optional[TranslationNode]:
        """Find node by ID.

        Args:
            node_id: Node ID to find

        Returns:
            Node if found, None otherwise
        """
        index = self._node_index.get(node_id)
        if index is not None:
            return self._nodes_list[index]
        return None

    def _is_section_node(self, node: TranslationNode) -> bool:
        """Check if node is a section.

        Args:
            node: Translation node

        Returns:
            True if node is a section
        """
        type_lower = node.type.lower()
        return any(
            keyword in type_lower
            for keyword in ["section", "heading", "title", "chapter"]
        )

    def enhance_node_context(
        self,
        node: TranslationNode,
        context_window: ContextWindow,
    ) -> None:
        """Enhance a node with context information.

        Args:
            node: Node to enhance
            context_window: Context window for the node
        """
        if node.context:
            # Update existing context
            node.context.preceding_text = context_window.preceding_text
            node.context.following_text = context_window.following_text
            if context_window.parent_section:
                node.context.parent_section = context_window.section_title

    def get_context_summary(
        self,
        node_id: str,
        context_windows: Dict[str, ContextWindow],
    ) -> str:
        """Get a summary of context for a node.

        Args:
            node_id: ID of the node
            context_windows: All context windows

        Returns:
            Context summary string
        """
        window = context_windows.get(node_id)
        if not window:
            return "No context available"

        parts = []

        if window.section_title:
            parts.append(f"Section: {window.section_title}")

        if window.preceding_text:
            parts.append(f"Before: {window.preceding_text[:100]}...")

        if window.following_text:
            parts.append(f"After: {window.following_text[:100]}...")

        if window.sibling_nodes:
            parts.append(f"Siblings: {len(window.sibling_nodes)} nodes")

        return " | ".join(parts) if parts else "Minimal context"
