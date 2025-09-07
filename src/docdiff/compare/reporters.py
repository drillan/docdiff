"""Report generators for comparison results."""

from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

from docdiff.compare.models import ComparisonResult, NodeMapping


class MarkdownReporter:
    """Generate Markdown reports from comparison results."""

    # Default limits for different display modes
    DEFAULT_LIMITS = {
        "labels": 20,
        "names": 10,
        "sidebyside": 20,
        "files": 5,
        "items_per_file": 5,
    }

    VERBOSE_LIMITS = {
        "labels": 100,
        "names": 50,
        "sidebyside": 100,
        "files": 20,
        "items_per_file": 20,
    }

    def __init__(self, style: str = "detailed", limit_mode: str = "default"):
        """Initialize reporter with style and limit mode.

        Args:
            style: Report style (detailed/compact/github)
            limit_mode: Limit mode (default/verbose/none)
                - default: Use default limits
                - verbose: Use expanded limits
                - none: No limits (show all)
        """
        self.style = style
        self.limit_mode = limit_mode

        # Set limits based on mode
        self.limits: Dict[str, Optional[int]]
        if limit_mode == "none":
            self.limits = {k: None for k in self.DEFAULT_LIMITS}
        elif limit_mode == "verbose":
            # Cast to Dict[str, Optional[int]] as VERBOSE_LIMITS has all int values
            self.limits = {k: v for k, v in self.VERBOSE_LIMITS.items()}
        else:
            # Cast to Dict[str, Optional[int]] as DEFAULT_LIMITS has all int values
            self.limits = {k: v for k, v in self.DEFAULT_LIMITS.items()}

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
        items_limit = (
            self.limits["items_per_file"] if self.limits["items_per_file"] else 5
        )
        missing_mappings = [m for m in result.mappings if m.mapping_type == "missing"]

        if items_limit is None:
            items_to_show = missing_mappings
        else:
            items_to_show = missing_mappings[:items_limit]

        if items_to_show:
            lines.append("### Top Missing:")
            for m in items_to_show:
                identifier = self._get_node_identifier(m.source_node)
                lines.append(f"- [ ] {identifier} (Line {m.source_node.line_number})")

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

        # Apply limit for GitHub task list
        task_limit = self.limits["names"]  # Reuse names limit for consistency
        items_to_show = (
            list(missing_by_label.items())
            if task_limit is None
            else list(missing_by_label.items())[:task_limit]
        )

        for label, mappings in items_to_show:
            lines.append(f"- [ ] **{label}** ({len(mappings)} items)")

        if task_limit and len(missing_by_label) > task_limit:
            remaining = len(missing_by_label) - task_limit
            lines.append(f"- [ ] ... and {remaining} more tasks")

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

            # Apply limit for labels
            label_limit = self.limits["labels"]
            items_to_show = (
                sorted_stats if label_limit is None else sorted_stats[:label_limit]
            )

            for label, (translated, total, coverage) in items_to_show:
                emoji = self._get_coverage_emoji(coverage)
                progress = self._get_progress_bar(coverage, width=16)
                lines.append(f"- {emoji} **{label}** ({coverage:.0f}%) {progress}")

            if label_limit and len(sorted_stats) > label_limit:
                remaining = len(sorted_stats) - label_limit
                help_text = (
                    " (use --full to show all)" if self.limit_mode != "none" else ""
                )
                lines.append(f"- ... and {remaining} more{help_text}")
            lines.append("")

        # Group by names
        name_stats = self._calculate_metadata_stats(result.mappings, "name")

        if name_stats:
            lines.append("### Name Attributes")
            lines.append("")

            sorted_stats = sorted(
                name_stats.items(), key=lambda x: x[1][2], reverse=True
            )

            # Apply limit for names
            name_limit = self.limits["names"]
            items_to_show = (
                sorted_stats if name_limit is None else sorted_stats[:name_limit]
            )

            for name, (translated, total, coverage) in items_to_show:
                emoji = self._get_coverage_emoji(coverage)
                lines.append(
                    f"- {emoji} `@{name}` - {translated}/{total} ({coverage:.0f}%)"
                )

            if name_limit and len(sorted_stats) > name_limit:
                remaining = len(sorted_stats) - name_limit
                help_text = (
                    " (use --full to show all)" if self.limit_mode != "none" else ""
                )
                lines.append(f"- ... and {remaining} more{help_text}")
            lines.append("")

        return lines

    def _generate_sidebyside_section(self, result: ComparisonResult) -> List[str]:
        """Generate side-by-side comparison section."""
        lines = ["## Side-by-Side Comparison", ""]
        lines.append("| Status | Source (EN) | Target (JA) | Match | Type |")
        lines.append("|:------:|:------------|:------------|:-----:|:-----|")

        # Apply limit for side-by-side comparison
        sidebyside_limit = self.limits["sidebyside"]
        items_to_show = (
            result.mappings
            if sidebyside_limit is None
            else result.mappings[:sidebyside_limit]
        )

        for mapping in items_to_show:
            status = self._get_status_emoji(mapping)

            # Use structural identifiers instead of content
            source = self._get_node_identifier(mapping.source_node)

            # Target identifier
            if mapping.target_node:
                target = self._get_node_identifier(mapping.target_node)
            else:
                target = "*(missing)*"

            # Match percentage
            match = f"{mapping.similarity * 100:.0f}%" if mapping.target_node else "0%"

            # Node type as metadata
            node_type = mapping.source_node.type.value

            lines.append(f"| {status} | {source} | {target} | {match} | {node_type} |")

        if sidebyside_limit and len(result.mappings) > sidebyside_limit:
            remaining = len(result.mappings) - sidebyside_limit
            help_text = " (use --full to show all)" if self.limit_mode != "none" else ""
            lines.append(f"| ... | *{remaining} more items{help_text}* | | | |")

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

        # Apply limits for files and items per file
        file_limit = self.limits["files"]
        items_limit = self.limits["items_per_file"]

        files_to_show = (
            list(by_file.items())
            if file_limit is None
            else list(by_file.items())[:file_limit]
        )

        for file_name, mappings in files_to_show:
            lines.append(f"### 📄 {file_name} ({len(mappings)} items)")
            lines.append("")

            items_to_show = mappings if items_limit is None else mappings[:items_limit]

            for m in items_to_show:
                node = m.source_node
                identifier = self._get_node_identifier(node)
                lines.append(f"- **Line {node.line_number}** - {identifier}")
                # Show first line of content as context (not in code block to avoid breaks)
                if node.content:
                    first_line = node.content.split("\n")[0][:80]
                    if first_line:
                        lines.append(
                            f"  > {first_line}{'...' if len(first_line) >= 80 or '\n' in node.content else ''}"
                        )

            if items_limit and len(mappings) > items_limit:
                remaining = len(mappings) - items_limit
                help_text = (
                    " (use --full to show all)" if self.limit_mode != "none" else ""
                )
                lines.append(f"- ... and {remaining} more in this file{help_text}")
            lines.append("")

        if file_limit and len(by_file) > file_limit:
            remaining = len(by_file) - file_limit
            help_text = " (use --full to show all)" if self.limit_mode != "none" else ""
            lines.append(f"*... and {remaining} more files{help_text}*")
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

    def _get_node_identifier(self, node) -> str:
        """Get structural identifier for a node instead of content.

        Priority: label > name > caption > title > type+line
        """
        # Import NodeType here to avoid circular import
        from docdiff.models import NodeType

        # Priority 1: Structural identifiers
        if node.label:
            return f"[{node.label}]"
        if node.name:
            return f"@{node.name}"
        if node.caption:
            return f'"{node.caption}"'

        # Priority 2: Title for sections
        if node.type == NodeType.SECTION and node.title:
            # Clean title from markdown headers
            title = node.title.strip()
            if title.startswith("#"):
                title = title.lstrip("#").strip()
            return title

        # Priority 3: Type-specific descriptions
        if node.type == NodeType.CODE_BLOCK:
            # Count lines in content
            lines = len(node.content.splitlines()) if node.content else 0
            lang = node.language or "code"
            return f"{lang} ({lines} lines)"

        if node.type == NodeType.LIST:
            # Count list items
            items = len(node.children_ids) if node.children_ids else 0
            if items > 0:
                return f"list ({items} items)"
            else:
                # Try to count from content
                list_lines = node.content.splitlines() if node.content else []
                items = sum(
                    1
                    for line in list_lines
                    if line.strip().startswith(("-", "*", "+", "1."))
                )
                return f"list ({items} items)" if items > 0 else "list"

        if node.type == NodeType.TABLE:
            # Try to extract table info
            table_lines = node.content.splitlines() if node.content else []
            rows = sum(1 for line in table_lines if "|" in line)
            return f"table ({rows} rows)" if rows > 0 else "table"

        if node.type == NodeType.FIGURE:
            return "figure"

        if node.type == NodeType.MATH_BLOCK:
            return "math block"

        if node.type == NodeType.ADMONITION:
            return "admonition"

        # Default: type and line number
        return f"{node.type.value} (L{node.line_number})"

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
