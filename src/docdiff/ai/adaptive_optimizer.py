"""Adaptive batch optimization for AI translation with intelligent node merging."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from docdiff.ai.context_manager import ContextManager
from docdiff.ai.glossary import Glossary
from docdiff.ai.token_estimator import TokenEstimator
from docdiff.models.export_schema import (
    DocumentHierarchy,
    SharedBatchContext,
    TranslationBatch,
    TranslationNode,
)


@dataclass
class OptimizationMetrics:
    """Metrics for batch optimization."""

    total_nodes: int = 0
    total_batches: int = 0
    avg_batch_size: float = 0.0
    avg_utilization: float = 0.0
    min_batch_tokens: int = 0
    max_batch_tokens: int = 0
    api_calls_saved: int = 0
    token_reduction_percent: float = 0.0


class AdaptiveBatchOptimizer:
    """Adaptive batch optimizer with intelligent node merging.

    This optimizer significantly improves batch efficiency by:
    1. Merging small nodes to reach optimal batch size (500-2000 tokens)
    2. Preserving semantic relationships between nodes
    3. Maintaining section boundaries when beneficial
    4. Optimizing for minimal API calls
    """

    def __init__(
        self,
        target_batch_size: int = 1500,
        min_batch_size: int = 500,
        max_batch_size: int = 2000,
        source_lang: str = "en",
        preserve_hierarchy: bool = True,
        enable_context: bool = True,
        context_window: int = 3,
    ):
        """Initialize adaptive batch optimizer.

        Args:
            target_batch_size: Target tokens per batch (optimal)
            min_batch_size: Minimum tokens per batch
            max_batch_size: Maximum tokens per batch
            source_lang: Source language for token estimation
            preserve_hierarchy: Maintain document hierarchy
            enable_context: Add context windows to nodes
            context_window: Size of context window
        """
        self.target_batch_size = target_batch_size
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        self.source_lang = source_lang
        self.preserve_hierarchy = preserve_hierarchy
        self.enable_context = enable_context
        self.context_window = context_window

        self.token_estimator = TokenEstimator()
        self.context_manager = ContextManager(window_size=context_window)
        self._batch_counter = 0
        self._metrics = OptimizationMetrics()

    def optimize_hierarchy(
        self,
        hierarchy: DocumentHierarchy,
        glossary: Optional[Glossary] = None,
    ) -> Tuple[List[TranslationBatch], OptimizationMetrics]:
        """Optimize document hierarchy into efficient batches.

        Args:
            hierarchy: Document hierarchy to optimize
            glossary: Optional glossary for terminology

        Returns:
            Tuple of optimized batches and metrics
        """
        all_batches = []

        # Process each file
        for file_path, doc_file in hierarchy.files.items():
            # Get translatable nodes
            translatable_nodes = self._get_translatable_nodes(doc_file.nodes)

            if not translatable_nodes:
                continue

            # Add context if enabled
            if self.enable_context:
                self._enhance_with_context(translatable_nodes)

            # Create adaptive batches
            file_batches = self._create_adaptive_batches(
                file_path,
                translatable_nodes,
                doc_file.nodes,
                glossary,
            )

            all_batches.extend(file_batches)

        # Optimize batch order
        self._optimize_batch_order(all_batches)

        # Calculate metrics
        self._metrics = self._calculate_metrics(all_batches, hierarchy)

        return all_batches, self._metrics

    def _get_translatable_nodes(
        self,
        nodes: Dict[str, TranslationNode],
    ) -> List[TranslationNode]:
        """Get nodes that need translation."""
        return [
            node for node in nodes.values() if node.status in ["missing", "outdated"]
        ]

    def _enhance_with_context(
        self,
        nodes: List[TranslationNode],
    ) -> None:
        """Add context windows to nodes."""
        windows = self.context_manager.build_context_windows(nodes)

        for node in nodes:
            if node.id in windows:
                self.context_manager.enhance_node_context(node, windows[node.id])

    def _create_adaptive_batches(
        self,
        file_path: str,
        nodes: List[TranslationNode],
        all_nodes: Dict[str, TranslationNode],
        glossary: Optional[Glossary],
    ) -> List[TranslationBatch]:
        """Create adaptive batches with intelligent merging.

        This is the core optimization algorithm that:
        1. Groups related nodes (sections, paragraphs)
        2. Merges small groups to reach target size
        3. Splits large groups if necessary
        4. Maintains semantic coherence
        """
        batches = []

        # Group nodes by semantic units
        semantic_groups = self._create_semantic_groups(nodes, all_nodes)

        # Merge small groups intelligently
        optimized_groups = self._merge_small_groups(semantic_groups)

        # Create batches from optimized groups
        for group in optimized_groups:
            group_batches = self._create_group_batches(
                file_path,
                group,
                all_nodes,
                glossary,
            )
            batches.extend(group_batches)

        return batches

    def _create_semantic_groups(
        self,
        nodes: List[TranslationNode],
        all_nodes: Dict[str, TranslationNode],
    ) -> List[List[TranslationNode]]:
        """Group nodes by semantic relationships."""
        groups = []
        current_group: List[TranslationNode] = []
        current_section = None

        for node in nodes:
            # Check if this is a section
            is_section = self._is_section_node(node)

            if is_section:
                # Save current group if exists
                if current_group:
                    groups.append(current_group)

                # Start new group with section
                current_group = [node]
                current_section = node
            elif current_section and node.parent_id == current_section.id:
                # Add to current section group
                current_group.append(node)
            else:
                # Check if node belongs to current section
                parent_section = self._find_parent_section(node, all_nodes)

                if parent_section == current_section:
                    current_group.append(node)
                else:
                    # Save current group and start new one
                    if current_group:
                        groups.append(current_group)
                    current_group = [node]
                    current_section = parent_section

        # Add final group
        if current_group:
            groups.append(current_group)

        return groups

    def _merge_small_groups(
        self,
        groups: List[List[TranslationNode]],
    ) -> List[List[TranslationNode]]:
        """Merge small groups to reach optimal batch size."""
        if not groups:
            return []

        optimized = []
        pending_merge: List[List[TranslationNode]] = []
        pending_tokens = 0

        for group in groups:
            # Estimate group tokens
            group_tokens = self._estimate_group_tokens(group)

            # If group is large enough, add as-is
            if group_tokens >= self.min_batch_size:
                # First, flush any pending groups
                if pending_merge:
                    optimized.append(self._flatten_groups(pending_merge))
                    pending_merge = []
                    pending_tokens = 0

                # Add this group
                optimized.append(group)
            else:
                # Try to merge with pending groups
                if pending_tokens + group_tokens <= self.max_batch_size:
                    pending_merge.append(group)
                    pending_tokens += group_tokens

                    # Check if we've reached target size
                    if pending_tokens >= self.target_batch_size:
                        optimized.append(self._flatten_groups(pending_merge))
                        pending_merge = []
                        pending_tokens = 0
                else:
                    # Can't merge, flush pending and start new
                    if pending_merge:
                        optimized.append(self._flatten_groups(pending_merge))
                    pending_merge = [group]
                    pending_tokens = group_tokens

        # Flush final pending groups
        if pending_merge:
            optimized.append(self._flatten_groups(pending_merge))

        return optimized

    def _flatten_groups(
        self,
        groups: List[List[TranslationNode]],
    ) -> List[TranslationNode]:
        """Flatten multiple groups into single list."""
        flattened = []
        for group in groups:
            flattened.extend(group)
        return flattened

    def _estimate_group_tokens(
        self,
        nodes: List[TranslationNode],
    ) -> int:
        """Estimate total tokens for a group of nodes."""
        total = 0

        for node in nodes:
            # Determine content type
            content_type = self._get_content_type(node.type)

            # Estimate tokens
            tokens = self.token_estimator.estimate(
                node.source,
                content_type,
                self.source_lang,
            )

            # Add JSON overhead
            tokens += 50  # Per-node overhead

            total += tokens

        return total

    def _create_group_batches(
        self,
        file_path: str,
        nodes: List[TranslationNode],
        all_nodes: Dict[str, TranslationNode],
        glossary: Optional[Glossary],
    ) -> List[TranslationBatch]:
        """Create batches from a group of nodes."""
        batches = []

        # Estimate total tokens
        total_tokens = self._estimate_group_tokens(nodes)

        # If group fits in one batch, keep together
        if total_tokens <= self.max_batch_size:
            batch = self._create_batch(
                file_path,
                nodes,
                all_nodes,
                glossary,
            )
            batches.append(batch)
        else:
            # Split into multiple batches
            current_batch_nodes: List[TranslationNode] = []
            current_tokens = 0

            for node in nodes:
                node_tokens = self._estimate_node_tokens(node)

                # Check if adding would exceed limit
                if (
                    current_tokens + node_tokens > self.max_batch_size
                    and current_batch_nodes
                ):
                    # Create batch
                    batch = self._create_batch(
                        file_path,
                        current_batch_nodes,
                        all_nodes,
                        glossary,
                    )
                    batches.append(batch)

                    # Start new batch
                    current_batch_nodes = [node]
                    current_tokens = node_tokens
                else:
                    current_batch_nodes.append(node)
                    current_tokens += node_tokens

            # Create final batch
            if current_batch_nodes:
                batch = self._create_batch(
                    file_path,
                    current_batch_nodes,
                    all_nodes,
                    glossary,
                )
                batches.append(batch)

        return batches

    def _create_batch(
        self,
        file_path: str,
        nodes: List[TranslationNode],
        all_nodes: Dict[str, TranslationNode],
        glossary: Optional[Glossary],
    ) -> TranslationBatch:
        """Create a single optimized batch."""
        self._batch_counter += 1

        # Get section info
        section_title = self._get_batch_section_title(nodes, all_nodes)

        # Get glossary terms
        glossary_terms = []
        if glossary:
            batch_content = " ".join(node.source for node in nodes)
            found_terms = glossary.find_terms_in_text(batch_content)
            glossary_terms = [term.term for term in found_terms[:10]]  # Limit to 10

        # Create shared context
        shared_context = SharedBatchContext(
            glossary_terms=glossary_terms,
            section_title=section_title,
            file_path=file_path,
            batch_theme=self._detect_batch_theme(nodes),
        )

        # Calculate tokens
        estimated_tokens = self._estimate_group_tokens(nodes)

        # Determine section range
        section_range = self._get_section_range(nodes, all_nodes)

        return TranslationBatch(
            batch_id=self._batch_counter,
            estimated_tokens=estimated_tokens,
            file_group=file_path,
            section_range=section_range,
            node_ids=[node.id for node in nodes],
            shared_context=shared_context,
            priority=self._calculate_priority(nodes),
        )

    def _estimate_node_tokens(
        self,
        node: TranslationNode,
    ) -> int:
        """Estimate tokens for a single node."""
        content_type = self._get_content_type(node.type)
        tokens = self.token_estimator.estimate(
            node.source,
            content_type,
            self.source_lang,
        )
        return tokens + 50  # Add overhead

    def _get_content_type(
        self,
        node_type: str,
    ) -> str:
        """Determine content type from node type."""
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

    def _is_section_node(
        self,
        node: TranslationNode,
    ) -> bool:
        """Check if node is a section."""
        type_lower = node.type.lower()
        return any(
            keyword in type_lower
            for keyword in ["section", "heading", "title", "chapter"]
        )

    def _find_parent_section(
        self,
        node: TranslationNode,
        all_nodes: Dict[str, TranslationNode],
    ) -> Optional[TranslationNode]:
        """Find parent section of a node."""
        if self._is_section_node(node):
            return node

        current = node
        while current.parent_id:
            parent = all_nodes.get(current.parent_id)
            if not parent:
                break

            if self._is_section_node(parent):
                return parent

            current = parent

        return None

    def _get_batch_section_title(
        self,
        nodes: List[TranslationNode],
        all_nodes: Dict[str, TranslationNode],
    ) -> Optional[str]:
        """Get section title for batch."""
        for node in nodes:
            if self._is_section_node(node):
                return node.source[:100]

            parent_section = self._find_parent_section(node, all_nodes)
            if parent_section:
                return parent_section.source[:100]

        return None

    def _get_section_range(
        self,
        nodes: List[TranslationNode],
        all_nodes: Dict[str, TranslationNode],
    ) -> str:
        """Get human-readable section range."""
        if not nodes:
            return "Empty"

        first_section = None
        last_section = None

        for node in nodes:
            section = self._find_parent_section(node, all_nodes)
            if section:
                if first_section is None:
                    first_section = section.source[:50]
                last_section = section.source[:50]

        if first_section and last_section and first_section != last_section:
            return f"{first_section} to {last_section}"
        elif first_section:
            return first_section
        else:
            # Use line numbers
            first_line = nodes[0].context.line_number if nodes[0].context else 0
            last_line = nodes[-1].context.line_number if nodes[-1].context else 0
            return f"Lines {first_line}-{last_line}"

    def _detect_batch_theme(
        self,
        nodes: List[TranslationNode],
    ) -> Optional[str]:
        """Detect theme of batch content."""
        content = " ".join(node.source.lower() for node in nodes)

        themes = {
            "Installation": ["install", "setup", "requirement", "pip", "npm"],
            "Configuration": ["config", "setting", "option", "parameter"],
            "API Reference": ["api", "function", "method", "class", "return"],
            "Tutorial": ["example", "step", "first", "create", "build"],
            "Testing": ["test", "assert", "expect", "mock", "fixture"],
        }

        for theme, keywords in themes.items():
            matches = sum(1 for kw in keywords if kw in content)
            if matches >= 2:
                return theme

        return None

    def _calculate_priority(
        self,
        nodes: List[TranslationNode],
    ) -> int:
        """Calculate batch priority."""
        priority = 0

        for node in nodes:
            # Sections are high priority
            if self._is_section_node(node):
                priority += 10

            # Early content is higher priority
            if node.context and node.context.line_number < 100:
                priority += 5

            # Nodes with children are important
            if len(node.children_ids) > 3:
                priority += 3

        return priority

    def _optimize_batch_order(
        self,
        batches: List[TranslationBatch],
    ) -> None:
        """Optimize batch processing order."""
        # Sort by priority and dependencies
        batches.sort(key=lambda b: (-b.priority, b.batch_id))

        # Set dependencies
        file_groups: Dict[str, List[TranslationBatch]] = {}
        for batch in batches:
            if batch.file_group not in file_groups:
                file_groups[batch.file_group] = []
            file_groups[batch.file_group].append(batch)

        # Within each file, set sequential dependencies
        for file_batches in file_groups.values():
            for i in range(1, len(file_batches)):
                prev_batch = file_batches[i - 1]
                curr_batch = file_batches[i]
                if prev_batch.batch_id not in curr_batch.dependencies:
                    curr_batch.dependencies.append(prev_batch.batch_id)

    def _calculate_metrics(
        self,
        batches: List[TranslationBatch],
        hierarchy: DocumentHierarchy,
    ) -> OptimizationMetrics:
        """Calculate optimization metrics."""
        if not batches:
            return OptimizationMetrics()

        total_nodes = hierarchy.total_nodes
        total_batches = len(batches)

        # Calculate batch statistics
        batch_tokens = [b.estimated_tokens for b in batches]
        avg_batch_size = sum(batch_tokens) / len(batch_tokens)

        # Calculate utilization
        utilizations = [
            min(100, (tokens / self.target_batch_size) * 100) for tokens in batch_tokens
        ]
        avg_utilization = sum(utilizations) / len(utilizations)

        # API calls saved (compared to one-node-per-batch)
        api_calls_saved = total_nodes - total_batches

        # Token reduction (overhead reduction)
        original_overhead = total_nodes * 100  # Assume 100 tokens overhead per node
        optimized_overhead = total_batches * 100
        token_reduction = (
            (original_overhead - optimized_overhead) / original_overhead * 100
            if original_overhead > 0
            else 0
        )

        return OptimizationMetrics(
            total_nodes=total_nodes,
            total_batches=total_batches,
            avg_batch_size=avg_batch_size,
            avg_utilization=avg_utilization,
            min_batch_tokens=min(batch_tokens) if batch_tokens else 0,
            max_batch_tokens=max(batch_tokens) if batch_tokens else 0,
            api_calls_saved=api_calls_saved,
            token_reduction_percent=token_reduction,
        )

    def get_metrics_report(self) -> str:
        """Get human-readable metrics report."""
        m = self._metrics

        return f"""
Adaptive Batch Optimization Report
===================================
Total Nodes:         {m.total_nodes}
Total Batches:       {m.total_batches}
Batch Efficiency:    {m.avg_utilization:.1f}%

Token Statistics:
  Average:           {m.avg_batch_size:.0f} tokens/batch
  Min:               {m.min_batch_tokens} tokens
  Max:               {m.max_batch_tokens} tokens
  Target:            {self.target_batch_size} tokens

Optimization Results:
  API Calls Saved:   {m.api_calls_saved} ({m.api_calls_saved / m.total_nodes * 100:.1f}% reduction)
  Token Overhead:    {m.token_reduction_percent:.1f}% reduction
  
Status: {"✅ Optimized" if m.avg_utilization > 80 else "⚠️ Sub-optimal"}
"""
