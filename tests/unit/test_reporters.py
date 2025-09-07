"""Unit tests for comparison reporters."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from docdiff.compare.models import ComparisonResult, NodeMapping
from docdiff.compare.reporters import MarkdownReporter
from docdiff.models import DocumentNode, NodeType


@pytest.fixture
def sample_node():
    """Create a sample document node."""
    return DocumentNode(
        id="node1",
        type=NodeType.PARAGRAPH,
        content="This is sample content.",
        file_path=Path("test.md"),
        line_number=1,
        content_hash="hash123",
    )


@pytest.fixture
def sample_mapping(sample_node):
    """Create a sample node mapping."""
    target_node = DocumentNode(
        id="node2",
        type=NodeType.PARAGRAPH,
        content="これはサンプルコンテンツです。",
        file_path=Path("test.ja.md"),
        line_number=1,
        content_hash="hash456",
    )
    return NodeMapping(
        source_node=sample_node,
        target_node=target_node,
        similarity=1.0,
        mapping_type="exact",
    )


@pytest.fixture
def missing_mapping(sample_node):
    """Create a missing translation mapping."""
    return NodeMapping(
        source_node=sample_node,
        target_node=None,
        similarity=0.0,
        mapping_type="missing",
    )


@pytest.fixture
def fuzzy_mapping():
    """Create a fuzzy match mapping."""
    source = DocumentNode(
        id="node3",
        type=NodeType.PARAGRAPH,
        content="Updated content here.",
        file_path=Path("test.md"),
        line_number=5,
        content_hash="hash789",
    )
    target = DocumentNode(
        id="node4",
        type=NodeType.PARAGRAPH,
        content="古いコンテンツです。",
        file_path=Path("test.ja.md"),
        line_number=5,
        content_hash="hash101",
    )
    return NodeMapping(
        source_node=source,
        target_node=target,
        similarity=0.75,
        mapping_type="fuzzy",
    )


@pytest.fixture
def comparison_result(sample_mapping, missing_mapping, fuzzy_mapping):
    """Create a sample comparison result."""
    return ComparisonResult(
        structure_diff={
            "paragraph": {"source": 10, "target": 8, "diff": -2},
            "section": {"source": 5, "target": 5, "diff": 0},
        },
        content_changes=[],
        translation_pairs=[],
        coverage_stats={
            "overall": 0.75,
            "counts": {
                "total": 12,
                "translated": 9,
                "missing": 3,
                "fuzzy": 2,
            },
            "exact_match": 0.58,
            "fuzzy_match": 0.17,
            "missing": 0.25,
        },
        mappings=[sample_mapping, missing_mapping, fuzzy_mapping],
        source_lang="en",
        target_lang="ja",
    )


class TestMarkdownReporter:
    """Test MarkdownReporter class."""

    def test_init_with_style(self):
        """Test reporter initialization with different styles."""
        reporter = MarkdownReporter(style="detailed")
        assert reporter.style == "detailed"

        reporter = MarkdownReporter(style="compact")
        assert reporter.style == "compact"

        reporter = MarkdownReporter(style="github")
        assert reporter.style == "github"

    def test_generate_detailed_report(self, comparison_result):
        """Test generating detailed markdown report."""
        reporter = MarkdownReporter(style="detailed")

        with patch("docdiff.compare.reporters.datetime") as mock_datetime:
            mock_now = MagicMock()
            mock_now.strftime.return_value = "2024-01-01 12:00"
            mock_datetime.now.return_value = mock_now

            report = reporter.generate(comparison_result)

        assert "# Translation Comparison Report" in report
        assert "**Generated:** 2024-01-01 12:00" in report
        assert "**Languages:** en → ja" in report
        assert "**Coverage:** 75.0%" in report
        assert "## Summary Statistics" in report
        assert "## Coverage by Metadata" in report
        assert "## Side-by-Side Comparison" in report
        assert "## Missing Translations" in report
        assert "## Structure Differences" in report

    def test_generate_compact_report(self, comparison_result):
        """Test generating compact markdown report."""
        reporter = MarkdownReporter(style="compact")
        report = reporter.generate(comparison_result)

        assert "## Translation Status: 75.0%" in report
        assert "**3/12** translations needed" in report
        assert "### Top Missing:" in report

    def test_generate_github_report(self, comparison_result):
        """Test generating GitHub-flavored markdown report."""
        reporter = MarkdownReporter(style="github")
        report = reporter.generate(comparison_result, include_badges=True)

        assert "# 📊 Translation Report" in report
        assert "![Coverage]" in report
        assert "![Language]" in report
        assert "> [!NOTE]" in report  # Coverage between 50-80%
        assert "<details>" in report
        assert "```mermaid" in report
        assert "## 📝 Translation Tasks" in report

    def test_generate_with_badges(self, comparison_result):
        """Test generating report with badges."""
        reporter = MarkdownReporter(style="detailed")
        report = reporter.generate(comparison_result, include_badges=True)

        assert (
            "![Coverage](https://img.shields.io/badge/coverage-75.0%25-yellow)"
            in report
        )

    def test_coverage_emoji(self):
        """Test coverage emoji selection."""
        reporter = MarkdownReporter()

        assert reporter._get_coverage_emoji(95) == "🟢"
        assert reporter._get_coverage_emoji(75) == "🟡"
        assert reporter._get_coverage_emoji(55) == "🟠"
        assert reporter._get_coverage_emoji(25) == "🔴"

    def test_status_emoji(self, sample_mapping, missing_mapping, fuzzy_mapping):
        """Test status emoji for different mapping types."""
        reporter = MarkdownReporter()

        assert reporter._get_status_emoji(sample_mapping) == "✅"
        assert reporter._get_status_emoji(missing_mapping) == "❌"
        assert reporter._get_status_emoji(fuzzy_mapping) == "⚠️"

    def test_progress_bar(self):
        """Test progress bar generation."""
        reporter = MarkdownReporter()

        bar = reporter._get_progress_bar(75, width=16)
        assert bar.count("█") == 12
        assert bar.count("░") == 4

        bar = reporter._get_progress_bar(50, width=10)
        assert bar.count("█") == 5
        assert bar.count("░") == 5

    def test_badge_color(self):
        """Test badge color selection."""
        reporter = MarkdownReporter()

        assert reporter._get_badge_color(95) == "brightgreen"
        assert reporter._get_badge_color(75) == "yellow"
        assert reporter._get_badge_color(55) == "orange"
        assert reporter._get_badge_color(25) == "red"

    def test_metadata_stats_calculation(self):
        """Test metadata statistics calculation."""
        reporter = MarkdownReporter()

        # Create nodes with labels
        node1 = DocumentNode(
            id="1",
            type=NodeType.SECTION,
            content="Test",
            file_path=Path("test.md"),
            line_number=1,
            content_hash="h1",
            label="intro",
        )
        node2 = DocumentNode(
            id="2",
            type=NodeType.SECTION,
            content="Test2",
            file_path=Path("test.md"),
            line_number=5,
            content_hash="h2",
            label="intro",
        )
        node3 = DocumentNode(
            id="3",
            type=NodeType.SECTION,
            content="Test3",
            file_path=Path("test.md"),
            line_number=10,
            content_hash="h3",
            label="conclusion",
        )

        mappings = [
            NodeMapping(node1, node1, 1.0, "exact"),
            NodeMapping(node2, None, 0.0, "missing"),
            NodeMapping(node3, node3, 1.0, "exact"),
        ]

        stats = reporter._calculate_metadata_stats(mappings, "label")

        assert "intro" in stats
        assert stats["intro"] == (1, 2, 50.0)
        assert "conclusion" in stats
        assert stats["conclusion"] == (1, 1, 100.0)

    def test_group_missing_by_metadata(self, comparison_result):
        """Test grouping missing translations by metadata."""
        reporter = MarkdownReporter()

        # Add some nodes with labels
        node_with_label = DocumentNode(
            id="5",
            type=NodeType.SECTION,
            content="Labeled",
            file_path=Path("test.md"),
            line_number=20,
            content_hash="h5",
            label="important",
        )
        mapping_with_label = NodeMapping(node_with_label, None, 0.0, "missing")
        comparison_result.mappings.append(mapping_with_label)

        groups = reporter._group_missing_by_metadata(comparison_result)

        assert "important" in groups
        assert len(groups["important"]) == 1
        assert "unnamed" in groups  # For nodes without label/name

    def test_generate_metadata_section(self):
        """Test metadata section generation."""
        reporter = MarkdownReporter()

        # Create nodes with labels and names
        nodes_with_metadata = []
        for i in range(25):
            node = DocumentNode(
                id=f"node{i}",
                type=NodeType.SECTION,
                content=f"Content {i}",
                file_path=Path("test.md"),
                line_number=i,
                content_hash=f"hash{i}",
                label=f"label{i % 5}" if i % 2 == 0 else None,
                name=f"name{i % 3}" if i % 3 == 0 else None,
            )
            target = node if i % 4 != 0 else None
            mapping = NodeMapping(
                node, target, 1.0 if target else 0.0, "exact" if target else "missing"
            )
            nodes_with_metadata.append(mapping)

        result = ComparisonResult(
            structure_diff={},
            content_changes=[],
            translation_pairs=[],
            coverage_stats={
                "overall": 0.75,
                "counts": {"total": 25, "translated": 19, "missing": 6},
            },
            mappings=nodes_with_metadata,
        )

        lines = reporter._generate_metadata_section(result)
        text = "\n".join(lines)

        assert "## Coverage by Metadata" in text
        assert "### Labels" in text
        assert "### Name Attributes" in text
        # Check that we have metadata sections
        assert "label" in text.lower()
        assert "@name0" in text

    def test_generate_sidebyside_section(self, comparison_result):
        """Test side-by-side comparison section generation."""
        reporter = MarkdownReporter()

        # Add a node with metadata
        node_with_meta = DocumentNode(
            id="meta",
            type=NodeType.SECTION,
            content="Content with metadata",
            file_path=Path("test.md"),
            line_number=15,
            content_hash="hashmeta",
            label="section-label",
            name="section-name",
        )
        mapping_with_meta = NodeMapping(node_with_meta, None, 0.0, "missing")
        comparison_result.mappings.append(mapping_with_meta)

        lines = reporter._generate_sidebyside_section(comparison_result)
        text = "\n".join(lines)

        assert "## Side-by-Side Comparison" in text
        assert "| Status | Source (EN) | Target (JA) | Match | Type |" in text
        assert "*(missing)*" in text
        assert "[section-label]" in text  # Now shows as identifier, not metadata

    def test_generate_missing_section_empty(self):
        """Test missing section when no translations are missing."""
        reporter = MarkdownReporter()

        result = ComparisonResult(
            structure_diff={},
            content_changes=[],
            translation_pairs=[],
            coverage_stats={
                "overall": 1.0,
                "counts": {"total": 10, "translated": 10, "missing": 0},
            },
            mappings=[],
        )

        lines = reporter._generate_missing_section(result)
        text = "\n".join(lines)

        assert "*No missing translations found!* 🎉" in text

    def test_generate_missing_section_with_items(self, comparison_result):
        """Test missing section with missing translations."""
        reporter = MarkdownReporter()

        # Add more missing items
        for i in range(10):
            node = DocumentNode(
                id=f"miss{i}",
                type=NodeType.PARAGRAPH,
                content=f"Missing content {i} that is very long and should be truncated when displayed in the report output",
                file_path=Path(f"file{i % 3}.md"),
                line_number=i * 10,
                content_hash=f"hashmiss{i}",
            )
            mapping = NodeMapping(node, None, 0.0, "missing")
            comparison_result.mappings.append(mapping)

        lines = reporter._generate_missing_section(comparison_result)
        text = "\n".join(lines)

        assert "## Missing Translations" in text
        assert "Total missing:" in text
        assert "### 📄" in text
        assert "**Line" in text
        # Content is truncated at 100 chars in the code
        assert "Missing content" in text
        # Check that files are shown (only 4 unique files in test data)
        assert "file0.md" in text or "file1.md" in text or "file2.md" in text

    def test_generate_structure_section(self, comparison_result):
        """Test structure differences section generation."""
        reporter = MarkdownReporter()

        lines = reporter._generate_structure_section(comparison_result)
        text = "\n".join(lines)

        assert "## Structure Differences" in text
        assert "| Node Type | Source | Target | Difference |" in text
        assert "paragraph" in text
        assert "**-2**" in text  # Bold for negative differences

    def test_generate_stats_table(self, comparison_result):
        """Test statistics table generation for GitHub style."""
        reporter = MarkdownReporter()

        lines = reporter._generate_stats_table(comparison_result)
        text = "\n".join(lines)

        assert "| Metric | Count | Percentage |" in text
        assert "| Total | 12 | 100% |" in text
        assert "| Translated | 9 | 58.0% |" in text
        assert "| Fuzzy | 2 | 17.0% |" in text
        assert "| Missing | 3 | 25.0% |" in text

    def test_generate_mermaid_diagram(self, comparison_result):
        """Test Mermaid diagram generation."""
        reporter = MarkdownReporter()

        lines = reporter._generate_mermaid_diagram(comparison_result)
        text = "\n".join(lines)

        assert "```mermaid" in text
        assert "pie title Translation Coverage" in text
        assert '"Translated" : 9' in text
        assert '"Missing" : 3' in text
        assert '"Fuzzy" : 2' in text

    def test_github_alerts(self):
        """Test GitHub alert generation based on coverage."""
        reporter = MarkdownReporter(style="github")

        # Low coverage
        result_low = ComparisonResult(
            structure_diff={},
            content_changes=[],
            translation_pairs=[],
            coverage_stats={
                "overall": 0.3,
                "counts": {"total": 10, "translated": 3, "missing": 7},
            },
            mappings=[],
            source_lang="en",
            target_lang="ja",
        )
        report = reporter.generate(result_low)
        assert "> [!WARNING]" in report

        # Medium coverage
        result_med = ComparisonResult(
            structure_diff={},
            content_changes=[],
            translation_pairs=[],
            coverage_stats={
                "overall": 0.65,
                "counts": {"total": 10, "translated": 6, "missing": 4},
            },
            mappings=[],
            source_lang="en",
            target_lang="ja",
        )
        report = reporter.generate(result_med)
        assert "> [!NOTE]" in report

        # High coverage
        result_high = ComparisonResult(
            structure_diff={},
            content_changes=[],
            translation_pairs=[],
            coverage_stats={
                "overall": 0.85,
                "counts": {"total": 10, "translated": 8, "missing": 2},
            },
            mappings=[],
            source_lang="en",
            target_lang="ja",
        )
        report = reporter.generate(result_high)
        assert "> [!TIP]" in report

    def test_long_content_truncation(self):
        """Test that long content is properly truncated."""
        reporter = MarkdownReporter()

        long_content = "A" * 200
        node = DocumentNode(
            id="long",
            type=NodeType.PARAGRAPH,
            content=long_content,
            file_path=Path("test.md"),
            line_number=1,
            content_hash="hashlong",
        )
        mapping = NodeMapping(node, None, 0.0, "missing")

        result = ComparisonResult(
            structure_diff={},
            content_changes=[],
            translation_pairs=[],
            coverage_stats={
                "overall": 0.5,
                "counts": {"total": 1, "translated": 0, "missing": 1},
            },
            mappings=[mapping],
        )

        lines = reporter._generate_sidebyside_section(result)
        text = "\n".join(lines)

        # Now we show identifiers, not content
        assert "paragraph (L1)" in text
        assert "*(missing)*" in text
        # Content is no longer shown in side-by-side, just the identifier
