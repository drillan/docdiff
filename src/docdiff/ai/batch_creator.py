"""Intelligent batching for AI translation with semantic awareness."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from docdiff.ai.token_estimator import TokenEstimator
from docdiff.models.export_schema import TranslationNode


@dataclass
class TranslationBatch:
    """A batch of nodes for translation."""

    id: str
    nodes: List[TranslationNode] = field(default_factory=list)
    estimated_tokens: int = 0
    file_path: str = ""
    section_title: Optional[str] = None
    batch_type: str = "mixed"  # section, paragraph, code, mixed
    language: str = "en"
    metadata: Dict = field(default_factory=dict)

    @property
    def node_count(self) -> int:
        """Get number of nodes in batch."""
        return len(self.nodes)

    @property
    def is_full(self) -> bool:
        """Check if batch is at capacity."""
        return self.estimated_tokens >= self.metadata.get("max_tokens", 2000)

    @property
    def utilization(self) -> float:
        """Get batch utilization percentage."""
        max_tokens = self.metadata.get("max_tokens", 2000)
        if max_tokens == 0:
            return 0.0
        return (self.estimated_tokens / max_tokens) * 100


class BatchCreator:
    """Smart batching with context preservation."""

    def __init__(
        self,
        max_tokens: int = 2000,
        min_tokens: int = 500,
        strategy: str = "semantic",
    ):
        """Initialize batch creator.

        Args:
            max_tokens: Maximum tokens per batch
            min_tokens: Minimum tokens per batch (for context)
            strategy: Batching strategy (semantic, size, hybrid)
        """
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self.strategy = strategy
        self.estimator = TokenEstimator()
        self._batch_counter = 0

    def create_batches(
        self,
        nodes: List[TranslationNode],
        language: str = "en",
    ) -> List[TranslationBatch]:
        """Create optimized batches from nodes.

        Args:
            nodes: List of translation nodes
            language: Source language for token estimation

        Returns:
            List of translation batches
        """
        if not nodes:
            return []

        if self.strategy == "semantic":
            return self._semantic_batching(nodes, language)
        elif self.strategy == "size":
            return self._size_batching(nodes, language)
        else:  # hybrid
            return self._hybrid_batching(nodes, language)

    def _semantic_batching(
        self,
        nodes: List[TranslationNode],
        language: str,
    ) -> List[TranslationBatch]:
        """Create batches based on semantic relationships.

        Groups related content together:
        - Keeps sections with their content
        - Groups related paragraphs
        - Maintains document flow
        """
        batches: List[TranslationBatch] = []
        current_batch: Optional[TranslationBatch] = None
        current_section: Optional[TranslationNode] = None

        for node in nodes:
            # Check if this is a section node
            is_section = self._is_section_node(node)

            # Start new batch for new sections
            if is_section:
                # Save current batch if it exists and has content
                if current_batch and current_batch.nodes:
                    batches.append(current_batch)

                # Create new batch for this section
                current_batch = self._create_batch(language)
                current_batch.section_title = node.source[:100]  # First 100 chars
                current_batch.batch_type = "section"
                current_section = node

            # Create first batch if needed
            if current_batch is None:
                current_batch = self._create_batch(language)

            # Estimate tokens for this node
            node_tokens = self._estimate_node_tokens(node, language)

            # Check if adding would exceed limit
            if current_batch.estimated_tokens + node_tokens > self.max_tokens:
                # Don't split sections if possible
                if is_section or (current_section and current_batch.node_count == 1):
                    # Force include to keep section with at least some content
                    current_batch.nodes.append(node)
                    current_batch.estimated_tokens += node_tokens
                    batches.append(current_batch)
                    current_batch = self._create_batch(language)
                    if current_section:
                        current_batch.section_title = current_section.source[:100]
                else:
                    # Start new batch
                    if current_batch.estimated_tokens >= self.min_tokens:
                        batches.append(current_batch)
                        current_batch = self._create_batch(language)
                        if current_section:
                            current_batch.section_title = current_section.source[:100]
                        current_batch.nodes.append(node)
                        current_batch.estimated_tokens = node_tokens
                    else:
                        # Force include to meet minimum
                        current_batch.nodes.append(node)
                        current_batch.estimated_tokens += node_tokens
            else:
                # Add to current batch
                current_batch.nodes.append(node)
                current_batch.estimated_tokens += node_tokens

        # Add final batch
        if current_batch and current_batch.nodes:
            batches.append(current_batch)

        return batches

    def _size_batching(
        self,
        nodes: List[TranslationNode],
        language: str,
    ) -> List[TranslationBatch]:
        """Create batches based purely on size constraints.

        Simple batching that maximizes token utilization.
        """
        batches: List[TranslationBatch] = []
        current_batch = self._create_batch(language)

        for node in nodes:
            node_tokens = self._estimate_node_tokens(node, language)

            # Check if adding would exceed limit
            if current_batch.estimated_tokens + node_tokens > self.max_tokens:
                if current_batch.nodes:
                    batches.append(current_batch)
                current_batch = self._create_batch(language)

            current_batch.nodes.append(node)
            current_batch.estimated_tokens += node_tokens

        # Add final batch
        if current_batch.nodes:
            batches.append(current_batch)

        return batches

    def _hybrid_batching(
        self,
        nodes: List[TranslationNode],
        language: str,
    ) -> List[TranslationBatch]:
        """Hybrid approach balancing semantics and size.

        Tries to keep related content together while optimizing size.
        """
        # Start with semantic batching
        semantic_batches = self._semantic_batching(nodes, language)

        # Optimize by merging small batches
        optimized: List[TranslationBatch] = []
        pending: Optional[TranslationBatch] = None

        for batch in semantic_batches:
            if pending:
                # Try to merge with pending
                combined_tokens = pending.estimated_tokens + batch.estimated_tokens
                if combined_tokens <= self.max_tokens:
                    # Merge batches
                    pending.nodes.extend(batch.nodes)
                    pending.estimated_tokens = combined_tokens
                    # Update batch type
                    if pending.batch_type != batch.batch_type:
                        pending.batch_type = "mixed"
                else:
                    # Can't merge, save pending and continue
                    optimized.append(pending)
                    pending = batch
            else:
                # Check if batch is too small
                if batch.estimated_tokens < self.min_tokens:
                    pending = batch
                else:
                    optimized.append(batch)

        # Add final pending batch
        if pending:
            optimized.append(pending)

        return optimized

    def _create_batch(self, language: str) -> TranslationBatch:
        """Create a new batch instance.

        Args:
            language: Language for the batch

        Returns:
            New TranslationBatch instance
        """
        self._batch_counter += 1
        return TranslationBatch(
            id=f"batch-{self._batch_counter:04d}",
            language=language,
            metadata={"max_tokens": self.max_tokens},
        )

    def _estimate_node_tokens(
        self,
        node: TranslationNode,
        language: str,
    ) -> int:
        """Estimate tokens for a single node.

        Args:
            node: Translation node
            language: Language code

        Returns:
            Estimated token count
        """
        # Determine content type from node type
        content_type = self._get_content_type(node.type)

        # Estimate source tokens
        source_tokens = self.estimator.estimate(node.source, content_type, language)

        # Add overhead for JSON structure
        overhead = 50  # ID, type, status, metadata, etc.

        return source_tokens + overhead

    def _get_content_type(self, node_type: str) -> str:
        """Get content type from node type.

        Args:
            node_type: Node type string

        Returns:
            Content type for token estimation
        """
        type_lower = node_type.lower()

        if "code" in type_lower:
            return "code"
        elif "equation" in type_lower or "math" in type_lower:
            return "equation"
        elif "table" in type_lower:
            return "table"
        elif "list" in type_lower:
            return "list"
        else:
            return "text"

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

    def calculate_metrics(
        self,
        batches: List[TranslationBatch],
    ) -> Dict:
        """Calculate batching metrics.

        Args:
            batches: List of translation batches

        Returns:
            Dictionary of metrics
        """
        if not batches:
            return {
                "total_batches": 0,
                "total_nodes": 0,
                "avg_utilization": 0.0,
                "avg_nodes_per_batch": 0.0,
                "min_batch_size": 0,
                "max_batch_size": 0,
            }

        total_nodes = sum(batch.node_count for batch in batches)
        utilizations = [batch.utilization for batch in batches]
        batch_sizes = [batch.node_count for batch in batches]

        return {
            "total_batches": len(batches),
            "total_nodes": total_nodes,
            "avg_utilization": sum(utilizations) / len(utilizations),
            "avg_nodes_per_batch": total_nodes / len(batches),
            "min_batch_size": min(batch_sizes),
            "max_batch_size": max(batch_sizes),
            "batch_types": self._count_batch_types(batches),
        }

    def _count_batch_types(self, batches: List[TranslationBatch]) -> Dict[str, int]:
        """Count batches by type.

        Args:
            batches: List of translation batches

        Returns:
            Count of each batch type
        """
        type_counts: Dict[str, int] = {}
        for batch in batches:
            batch_type = batch.batch_type
            type_counts[batch_type] = type_counts.get(batch_type, 0) + 1
        return type_counts
