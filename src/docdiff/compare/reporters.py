"""Report generators for comparison results."""

from typing import List, Dict
from datetime import datetime
from collections import defaultdict

from docdiff.compare.models import ComparisonResult, NodeMapping


class MarkdownReporter:
    """Generate Markdown reports from comparison results."""

    def __init__(self, style: str = "detailed"):
        """Initialize reporter with style.

        Args:
            style: Report style (detailed/compact/github)
        """
        self.style = style

    def generate(self, result: ComparisonResult, include_badges: bool = False) -> str:
        """Generate markdown report.

        Args:
            result: Comparison result
            include_badges: Whether to include coverage badges

        Returns:
            Markdown formatted report
        """
        if self.style == "github":
            return self._generate_github(result, include_badges)
        elif self.style == "compact":
            return self._generate_compact(result)
        else:
            return self._generate_detailed(result, include_badges)

    def _generate_detailed(
        self, result: ComparisonResult, include_badges: bool = False
    ) -> str:
        """Generate detailed markdown report."""
        lines = []

        # Header
        lines.append("# Translation Comparison Report")
        lines.append("")

        # Metadata
        coverage_pct = result.coverage_stats["overall"] * 100
        coverage_emoji = self._get_coverage_emoji(coverage_pct)

        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Languages:** {result.source_lang} → {result.target_lang}")
        lines.append(f"**Coverage:** {coverage_pct:.1f}% {coverage_emoji}")
        lines.append("")

        # Coverage badge
        if include_badges:
            badge_color = self._get_badge_color(coverage_pct)
            lines.append(
                f"![Coverage](https://img.shields.io/badge/coverage-{coverage_pct:.1f}%25-{badge_color})"
            )
            lines.append("")

        # Table of Contents
        lines.append("## Table of Contents")
        lines.append("")
        lines.append("- [Summary Statistics](#summary-statistics)")
        lines.append("- [Coverage by Metadata](#coverage-by-metadata)")
        lines.append("- [Side-by-Side Comparison](#side-by-side-comparison)")
        lines.append("- [Missing Translations](#missing-translations)")
        lines.append("")

        # Summary Statistics
        lines.append("## Summary Statistics")
        lines.append("")
        lines.append("| Metric | Value | Visual |")
        lines.append("|:-------|------:|:-------|")

        counts = result.coverage_stats["counts"]
        assert isinstance(counts, dict)
        total = counts["total"]
        translated = counts["translated"]
        missing = counts["missing"]
        fuzzy = counts.get("fuzzy", 0)

        lines.append(f"| **Total Nodes** | {total} | 📊 |")
        lines.append(f"| **Translated** | {translated} | ✅ {translated}/{total} |")
        lines.append(f"| **Missing** | {missing} | ❌ {missing}/{total} |")
        lines.append(f"| **Fuzzy Matches** | {fuzzy} | ⚠️ {fuzzy}/{total} |")
        lines.append(
            f"| **Overall Coverage** | {coverage_pct:.1f}% | {self._get_progress_bar(coverage_pct)} |"
        )
        lines.append("")

        # Coverage by Metadata
        lines.extend(self._generate_metadata_section(result))

        # Side-by-Side Comparison
        lines.extend(self._generate_sidebyside_section(result))

        # Missing Translations
        lines.extend(self._generate_missing_section(result))

        # Structure Differences
        lines.extend(self._generate_structure_section(result))

        return "\n".join(lines)

    def _generate_compact(self, result: ComparisonResult) -> str:
        """Generate compact markdown report."""
        lines: List[str] = []

        overall_coverage = result.coverage_stats["overall"]
        assert isinstance(overall_coverage, (int, float))
        coverage_pct = overall_coverage * 100
        counts = result.coverage_stats["counts"]
        assert isinstance(counts, dict)
        total = counts["total"]
        missing = counts["missing"]

        lines.append(
            f"## Translation Status: {coverage_pct:.1f}% {self._get_coverage_emoji(coverage_pct)}"
        )
        lines.append("")
        lines.append(f"**{missing}/{total}** translations needed")
        lines.append("")

        # Top missing items
        missing_mappings = [m for m in result.mappings if m.mapping_type == "missing"][
            :5
        ]
        if missing_mappings:
            lines.append("### Top Missing:")
            for m in missing_mappings:
                lines.append(
                    f"- [ ] `{m.source_node.label or m.source_node.name or 'node'}`: {m.source_node.content[:50]}..."
                )

        return "\n".join(lines)

    def _generate_github(
        self, result: ComparisonResult, include_badges: bool = True
    ) -> str:
        """Generate GitHub-flavored markdown with extensions."""
        lines = []

        coverage_pct = result.coverage_stats["overall"] * 100

        # Header with badges
        lines.append("# 📊 Translation Report")
        lines.append("")

        if include_badges:
            lines.append(
                f"![Coverage](https://img.shields.io/badge/coverage-{coverage_pct:.1f}%25-{self._get_badge_color(coverage_pct)})"
            )
            lines.append(
                f"![Language](https://img.shields.io/badge/lang-{result.source_lang}→{result.target_lang}-blue)"
            )
            lines.append("")

        # Summary with alerts
        if coverage_pct < 50:
            lines.append("> [!WARNING]")
            lines.append(f"> Translation coverage is low: **{coverage_pct:.1f}%**")
        elif coverage_pct < 80:
            lines.append("> [!NOTE]")
            lines.append(f"> Translation coverage: **{coverage_pct:.1f}%**")
        else:
            lines.append("> [!TIP]")
            lines.append(f"> Good translation coverage: **{coverage_pct:.1f}%**")
        lines.append("")

        # Collapsible sections
        lines.append("<details>")
        lines.append("<summary>📈 Detailed Statistics</summary>")
        lines.append("")
        lines.extend(self._generate_stats_table(result))
        lines.append("</details>")
        lines.append("")

        # Mermaid diagram
        lines.append("<details>")
        lines.append("<summary>🔄 Translation Flow</summary>")
        lines.append("")
        lines.extend(self._generate_mermaid_diagram(result))
        lines.append("</details>")
        lines.append("")

        # Task list for missing translations
        lines.append("## 📝 Translation Tasks")
        lines.append("")
        missing_by_label = self._group_missing_by_metadata(result)
        for label, mappings in list(missing_by_label.items())[:10]:
            lines.append(f"- [ ] **{label}** ({len(mappings)} items)")

        return "\n".join(lines)

    def _generate_metadata_section(self, result: ComparisonResult) -> List[str]:
        """Generate metadata coverage section."""
        lines = ["## Coverage by Metadata", ""]

        # Group by labels
        label_stats = self._calculate_metadata_stats(result.mappings, "label")

        if label_stats:
            lines.append("### Labels")
            lines.append("")

            # Sort by coverage
            sorted_stats = sorted(
                label_stats.items(), key=lambda x: x[1][2], reverse=True
            )

            for label, (translated, total, coverage) in sorted_stats[:20]:
                emoji = self._get_coverage_emoji(coverage)
                progress = self._get_progress_bar(coverage, width=16)
                lines.append(f"- {emoji} **{label}** ({coverage:.0f}%) {progress}")

            if len(sorted_stats) > 20:
                lines.append(f"- ... and {len(sorted_stats) - 20} more")
            lines.append("")

        # Group by names
        name_stats = self._calculate_metadata_stats(result.mappings, "name")

        if name_stats:
            lines.append("### Name Attributes")
            lines.append("")

            sorted_stats = sorted(
                name_stats.items(), key=lambda x: x[1][2], reverse=True
            )

            for name, (translated, total, coverage) in sorted_stats[:10]:
                emoji = self._get_coverage_emoji(coverage)
                lines.append(
                    f"- {emoji} `@{name}` - {translated}/{total} ({coverage:.0f}%)"
                )

            if len(sorted_stats) > 10:
                lines.append(f"- ... and {len(sorted_stats) - 10} more")
            lines.append("")

        return lines

    def _generate_sidebyside_section(self, result: ComparisonResult) -> List[str]:
        """Generate side-by-side comparison section."""
        lines = ["## Side-by-Side Comparison", ""]
        lines.append("| Status | Source (EN) | Target (JA) | Match | Metadata |")
        lines.append("|:------:|:------------|:------------|:-----:|:---------|")

        # Show first 20 items
        for mapping in result.mappings[:20]:
            status = self._get_status_emoji(mapping)

            # Source content
            source = mapping.source_node.content[:40]
            if len(mapping.source_node.content) > 40:
                source += "..."

            # Target content
            if mapping.target_node:
                target = mapping.target_node.content[:40]
                if len(mapping.target_node.content) > 40:
                    target += "..."
            else:
                target = "*(missing)*"

            # Match percentage
            match = f"{mapping.similarity * 100:.0f}%" if mapping.target_node else "0%"

            # Metadata
            metadata = []
            if mapping.source_node.label:
                metadata.append(f"`label: {mapping.source_node.label}`")
            if mapping.source_node.name:
                metadata.append(f"`name: {mapping.source_node.name}`")
            metadata_str = " ".join(metadata) if metadata else "-"

            lines.append(
                f"| {status} | {source} | {target} | {match} | {metadata_str} |"
            )

        if len(result.mappings) > 20:
            lines.append(f"| ... | *{len(result.mappings) - 20} more items* | | | |")

        lines.append("")
        return lines

    def _generate_missing_section(self, result: ComparisonResult) -> List[str]:
        """Generate missing translations section."""
        lines = ["## Missing Translations", ""]

        missing = [m for m in result.mappings if m.mapping_type == "missing"]

        if not missing:
            lines.append("*No missing translations found!* 🎉")
            lines.append("")
            return lines

        lines.append(f"Total missing: **{len(missing)}** items")
        lines.append("")

        # Group by file
        by_file = defaultdict(list)
        for m in missing:
            if hasattr(m.source_node, "file_path"):
                by_file[m.source_node.file_path.name].append(m)

        for file_name, mappings in list(by_file.items())[:5]:
            lines.append(f"### 📄 {file_name} ({len(mappings)} items)")
            lines.append("")

            for m in mappings[:5]:
                node = m.source_node
                lines.append(f"- **Line {node.line_number}** ({node.type.value})")
                lines.append("  ```")
                lines.append(
                    f"  {node.content[:100]}{'...' if len(node.content) > 100 else ''}"
                )
                lines.append("  ```")

            if len(mappings) > 5:
                lines.append(f"- ... and {len(mappings) - 5} more in this file")
            lines.append("")

        if len(by_file) > 5:
            lines.append(f"*... and {len(by_file) - 5} more files*")
            lines.append("")

        return lines

    def _generate_structure_section(self, result: ComparisonResult) -> List[str]:
        """Generate structure differences section."""
        lines = ["## Structure Differences", ""]
        lines.append("| Node Type | Source | Target | Difference |")
        lines.append("|:----------|-------:|-------:|-----------:|")

        for node_type, stats in result.structure_diff.items():
            source = stats.get("source", 0)
            target = stats.get("target", 0)
            diff = stats.get("diff", target - source)

            diff_str = f"+{diff}" if diff > 0 else str(diff)
            if diff < 0:
                diff_str = f"**{diff_str}**"  # Bold for missing

            lines.append(f"| {node_type} | {source} | {target} | {diff_str} |")

        lines.append("")
        return lines

    def _generate_stats_table(self, result: ComparisonResult) -> List[str]:
        """Generate statistics table for GitHub style."""
        lines = []
        stats = result.coverage_stats

        lines.append("| Metric | Count | Percentage |")
        lines.append("|:-------|------:|-----------:|")
        counts = stats["counts"]
        assert isinstance(counts, dict)
        exact_match = stats.get("exact_match", 0)
        assert isinstance(exact_match, (int, float))
        fuzzy_match = stats.get("fuzzy_match", 0)
        assert isinstance(fuzzy_match, (int, float))
        missing_pct = stats.get("missing", 0)
        assert isinstance(missing_pct, (int, float))

        lines.append(f"| Total | {counts['total']} | 100% |")
        lines.append(
            f"| Translated | {counts['translated']} | {exact_match * 100:.1f}% |"
        )
        lines.append(f"| Fuzzy | {counts.get('fuzzy', 0)} | {fuzzy_match * 100:.1f}% |")
        lines.append(f"| Missing | {counts['missing']} | {missing_pct * 100:.1f}% |")
        lines.append("")

        return lines

    def _generate_mermaid_diagram(self, result: ComparisonResult) -> List[str]:
        """Generate Mermaid flow diagram."""
        lines = ["```mermaid", "pie title Translation Coverage"]

        counts = result.coverage_stats["counts"]
        assert isinstance(counts, dict)
        translated = counts["translated"]
        missing = counts["missing"]
        fuzzy = counts.get("fuzzy", 0)

        lines.append(f'    "Translated" : {translated}')
        lines.append(f'    "Missing" : {missing}')
        if fuzzy > 0:
            lines.append(f'    "Fuzzy" : {fuzzy}')

        lines.append("```")
        lines.append("")

        return lines

    def _calculate_metadata_stats(
        self, mappings: List[NodeMapping], attr: str
    ) -> Dict[str, tuple]:
        """Calculate statistics for metadata attribute."""
        stats: Dict[str, List[int]] = defaultdict(lambda: [0, 0])

        for mapping in mappings:
            value = getattr(mapping.source_node, attr, None)
            if value:
                stats[value][1] += 1  # total
                if mapping.target_node:
                    stats[value][0] += 1  # translated

        result = {}
        for key, (translated, total) in stats.items():
            percentage = (translated / total * 100) if total > 0 else 0
            result[key] = (translated, total, percentage)

        return result

    def _group_missing_by_metadata(
        self, result: ComparisonResult
    ) -> Dict[str, List[NodeMapping]]:
        """Group missing translations by metadata."""
        groups = defaultdict(list)

        for mapping in result.mappings:
            if mapping.mapping_type == "missing":
                key = mapping.source_node.label or mapping.source_node.name or "unnamed"
                groups[key].append(mapping)

        return dict(groups)

    def _get_coverage_emoji(self, coverage: float) -> str:
        """Get emoji for coverage percentage."""
        if coverage >= 90:
            return "🟢"
        elif coverage >= 70:
            return "🟡"
        elif coverage >= 50:
            return "🟠"
        else:
            return "🔴"

    def _get_status_emoji(self, mapping: NodeMapping) -> str:
        """Get status emoji for mapping."""
        if mapping.mapping_type == "exact":
            return "✅"
        elif mapping.mapping_type == "fuzzy":
            return "⚠️"
        else:
            return "❌"

    def _get_progress_bar(self, percentage: float, width: int = 16) -> str:
        """Generate text progress bar."""
        filled = int(percentage / 100 * width)
        empty = width - filled
        return "█" * filled + "░" * empty

    def _get_badge_color(self, coverage: float) -> str:
        """Get badge color based on coverage."""
        if coverage >= 90:
            return "brightgreen"
        elif coverage >= 70:
            return "yellow"
        elif coverage >= 50:
            return "orange"
        else:
            return "red"
