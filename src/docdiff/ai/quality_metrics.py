"""Quality metrics for AI translation optimization."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from docdiff.ai.glossary import Glossary
from docdiff.models.export_schema import TranslationBatch, TranslationNode


@dataclass
class BatchQualityScore:
    """Quality score for a single batch."""

    batch_id: int
    token_utilization: float  # 0-100%
    semantic_coherence: float  # 0-100%
    context_completeness: float  # 0-100%
    glossary_coverage: float  # 0-100%
    overall_score: float  # 0-100%


@dataclass
class TranslationQualityReport:
    """Comprehensive quality report for translation export."""

    total_batches: int = 0
    total_nodes: int = 0
    avg_batch_efficiency: float = 0.0
    api_calls_reduction: float = 0.0
    token_overhead_reduction: float = 0.0

    # Quality scores
    terminology_consistency: float = 0.0
    reference_preservation: float = 0.0
    context_coverage: float = 0.0

    # Batch distribution
    optimal_batches: int = 0  # 80-100% utilization
    good_batches: int = 0  # 60-80% utilization
    poor_batches: int = 0  # < 60% utilization

    # Warnings
    warnings: List[str] = field(default_factory=list)

    # Batch scores
    batch_scores: List[BatchQualityScore] = field(default_factory=list)


class TranslationQualityMetrics:
    """Measure and report translation quality metrics."""

    def __init__(
        self,
        target_batch_size: int = 1500,
        min_batch_size: int = 500,
        max_batch_size: int = 2000,
    ):
        """Initialize quality metrics.

        Args:
            target_batch_size: Target tokens per batch
            min_batch_size: Minimum acceptable batch size
            max_batch_size: Maximum batch size
        """
        self.target_batch_size = target_batch_size
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size

    def evaluate_batches(
        self,
        batches: List[TranslationBatch],
        nodes: Dict[str, TranslationNode],
        glossary: Optional[Glossary] = None,
    ) -> TranslationQualityReport:
        """Evaluate quality of translation batches.

        Args:
            batches: List of translation batches
            nodes: All translation nodes
            glossary: Optional glossary for terminology check

        Returns:
            Comprehensive quality report
        """
        report = TranslationQualityReport()

        if not batches:
            return report

        # Basic statistics
        report.total_batches = len(batches)
        report.total_nodes = len(nodes)

        # Evaluate each batch
        batch_scores = []
        for batch in batches:
            score = self._evaluate_batch(batch, nodes, glossary)
            batch_scores.append(score)
            report.batch_scores.append(score)

        # Calculate aggregate metrics
        self._calculate_efficiency_metrics(report, batch_scores)
        self._calculate_quality_metrics(report, batches, nodes, glossary)
        self._categorize_batches(report, batch_scores)
        self._generate_warnings(report, batch_scores)

        return report

    def _evaluate_batch(
        self,
        batch: TranslationBatch,
        nodes: Dict[str, TranslationNode],
        glossary: Optional[Glossary],
    ) -> BatchQualityScore:
        """Evaluate a single batch."""
        # Token utilization
        utilization = min(100, (batch.estimated_tokens / self.target_batch_size) * 100)

        # Semantic coherence (are nodes related?)
        coherence = self._calculate_semantic_coherence(batch, nodes)

        # Context completeness
        context_completeness = self._calculate_context_completeness(batch, nodes)

        # Glossary coverage
        glossary_coverage = self._calculate_glossary_coverage(batch, nodes, glossary)

        # Overall score (weighted average)
        overall = (
            utilization * 0.4  # Most important
            + coherence * 0.3
            + context_completeness * 0.2
            + glossary_coverage * 0.1
        )

        return BatchQualityScore(
            batch_id=batch.batch_id,
            token_utilization=utilization,
            semantic_coherence=coherence,
            context_completeness=context_completeness,
            glossary_coverage=glossary_coverage,
            overall_score=overall,
        )

    def _calculate_semantic_coherence(
        self,
        batch: TranslationBatch,
        nodes: Dict[str, TranslationNode],
    ) -> float:
        """Calculate how semantically related the batch nodes are."""
        if len(batch.node_ids) <= 1:
            return 100.0  # Single node is always coherent

        # Check if nodes are from same section
        sections = set()
        for node_id in batch.node_ids:
            node = nodes.get(node_id)
            if node and node.parent_id:
                sections.add(node.parent_id)

        # Score based on section diversity
        if len(sections) == 1:
            return 100.0  # All from same section
        elif len(sections) <= 2:
            return 80.0  # Two sections
        elif len(sections) <= 3:
            return 60.0  # Three sections
        else:
            return 40.0  # Too diverse

    def _calculate_context_completeness(
        self,
        batch: TranslationBatch,
        nodes: Dict[str, TranslationNode],
    ) -> float:
        """Calculate how complete the context is."""
        nodes_with_context = 0

        for node_id in batch.node_ids:
            node = nodes.get(node_id)
            if node and node.context:
                # Check if context has meaningful content
                if (
                    node.context.preceding_text
                    or node.context.following_text
                    or node.context.parent_section
                ):
                    nodes_with_context += 1

        if not batch.node_ids:
            return 0.0

        return (nodes_with_context / len(batch.node_ids)) * 100

    def _calculate_glossary_coverage(
        self,
        batch: TranslationBatch,
        nodes: Dict[str, TranslationNode],
        glossary: Optional[Glossary],
    ) -> float:
        """Calculate how well glossary terms are covered."""
        if not glossary or not glossary.terms:
            return 100.0  # No glossary to check

        # Collect batch text
        batch_text = ""
        for node_id in batch.node_ids:
            node = nodes.get(node_id)
            if node:
                batch_text += " " + node.source

        # Find glossary terms in text
        found_terms = glossary.find_terms_in_text(batch_text)

        # Check if shared context includes these terms
        shared_terms = (
            set(batch.shared_context.glossary_terms) if batch.shared_context else set()
        )
        found_term_names = {term.term for term in found_terms}

        if not found_term_names:
            return 100.0  # No terms to cover

        coverage = len(shared_terms & found_term_names) / len(found_term_names)
        return coverage * 100

    def _calculate_efficiency_metrics(
        self,
        report: TranslationQualityReport,
        batch_scores: List[BatchQualityScore],
    ) -> None:
        """Calculate efficiency metrics."""
        if not batch_scores:
            return

        # Average batch efficiency
        utilizations = [score.token_utilization for score in batch_scores]
        report.avg_batch_efficiency = sum(utilizations) / len(utilizations)

        # API calls reduction (compared to one-node-per-call)
        report.api_calls_reduction = (
            (report.total_nodes - report.total_batches) / report.total_nodes * 100
            if report.total_nodes > 0
            else 0
        )

        # Token overhead reduction
        # Assume 100 tokens overhead per API call
        original_overhead = report.total_nodes * 100
        optimized_overhead = report.total_batches * 100
        report.token_overhead_reduction = (
            (original_overhead - optimized_overhead) / original_overhead * 100
            if original_overhead > 0
            else 0
        )

    def _calculate_quality_metrics(
        self,
        report: TranslationQualityReport,
        batches: List[TranslationBatch],
        nodes: Dict[str, TranslationNode],
        glossary: Optional[Glossary],
    ) -> None:
        """Calculate quality metrics."""
        # Terminology consistency (based on glossary coverage)
        if glossary and glossary.terms:
            total_coverage = 0.0
            for batch in batches:
                score = self._calculate_glossary_coverage(batch, nodes, glossary)
                total_coverage += score
            report.terminology_consistency = (
                total_coverage / len(batches) if batches else 0.0
            )
        else:
            report.terminology_consistency = 100.0  # No glossary to check

        # Reference preservation (check if references are in same batch)
        report.reference_preservation = self._calculate_reference_preservation(
            batches, nodes
        )

        # Context coverage
        context_scores = [score.context_completeness for score in report.batch_scores]
        report.context_coverage = (
            sum(context_scores) / len(context_scores) if context_scores else 0.0
        )

    def _calculate_reference_preservation(
        self,
        batches: List[TranslationBatch],
        nodes: Dict[str, TranslationNode],
    ) -> float:
        """Calculate how well references are preserved in batches."""
        # Simple heuristic: check if referenced nodes are in same batch
        references_preserved = 0
        total_references = 0

        for batch in batches:
            batch_node_ids = set(batch.node_ids)

            for node_id in batch.node_ids:
                node = nodes.get(node_id)
                if not node:
                    continue

                # Check if node has references (simplified check)
                if "{ref}" in node.source or "{term}" in node.source:
                    total_references += 1
                    # Assume reference is preserved if batch has multiple nodes
                    if len(batch_node_ids) > 1:
                        references_preserved += 1

        if total_references == 0:
            return 100.0  # No references to preserve

        return (references_preserved / total_references) * 100

    def _categorize_batches(
        self,
        report: TranslationQualityReport,
        batch_scores: List[BatchQualityScore],
    ) -> None:
        """Categorize batches by utilization."""
        for score in batch_scores:
            if score.token_utilization >= 80:
                report.optimal_batches += 1
            elif score.token_utilization >= 60:
                report.good_batches += 1
            else:
                report.poor_batches += 1

    def _generate_warnings(
        self,
        report: TranslationQualityReport,
        batch_scores: List[BatchQualityScore],
    ) -> None:
        """Generate warnings for potential issues."""
        # Check for very small batches
        small_batches = [s for s in batch_scores if s.token_utilization < 30]
        if small_batches:
            report.warnings.append(
                f"Found {len(small_batches)} very small batches (<30% utilization)"
            )

        # Check for poor semantic coherence
        incoherent_batches = [s for s in batch_scores if s.semantic_coherence < 50]
        if incoherent_batches:
            report.warnings.append(
                f"Found {len(incoherent_batches)} batches with poor semantic coherence"
            )

        # Check overall efficiency
        if report.avg_batch_efficiency < 60:
            report.warnings.append(
                f"Low average batch efficiency: {report.avg_batch_efficiency:.1f}%"
            )

        # Check if adaptive batching would help
        if report.poor_batches > report.optimal_batches:
            report.warnings.append(
                "Consider enabling adaptive batching for better efficiency"
            )

    def format_report(self, report: TranslationQualityReport) -> str:
        """Format quality report as human-readable text."""
        lines = [
            "Translation Quality Report",
            "=" * 50,
            "",
            "📊 Batch Statistics",
            f"  Total Batches:       {report.total_batches}",
            f"  Total Nodes:         {report.total_nodes}",
            f"  Avg Efficiency:      {report.avg_batch_efficiency:.1f}%",
            "",
            "📈 Optimization Metrics",
            f"  API Calls Reduced:   {report.api_calls_reduction:.1f}%",
            f"  Token Overhead:      -{report.token_overhead_reduction:.1f}%",
            "",
            "✅ Quality Scores",
            f"  Terminology:         {report.terminology_consistency:.1f}%",
            f"  References:          {report.reference_preservation:.1f}%",
            f"  Context Coverage:    {report.context_coverage:.1f}%",
            "",
            "📦 Batch Distribution",
            f"  Optimal (80-100%):   {report.optimal_batches} batches",
            f"  Good (60-80%):       {report.good_batches} batches",
            f"  Poor (<60%):         {report.poor_batches} batches",
        ]

        if report.warnings:
            lines.extend(
                [
                    "",
                    "⚠️ Warnings",
                ]
            )
            for warning in report.warnings:
                lines.append(f"  - {warning}")

        # Overall status
        lines.extend(
            [
                "",
                "📋 Overall Status",
            ]
        )

        if report.avg_batch_efficiency >= 80:
            lines.append("  ✅ Excellent optimization")
        elif report.avg_batch_efficiency >= 60:
            lines.append("  ⚠️ Good optimization, room for improvement")
        else:
            lines.append("  ❌ Poor optimization, consider using adaptive batching")

        return "\n".join(lines)
