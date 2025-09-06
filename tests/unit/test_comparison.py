"""Tests for comparison engine."""

from pathlib import Path

import pytest

from docdiff.compare import ComparisonEngine, ComparisonResult, NodeMapping
from docdiff.models import DocumentNode, NodeType


@pytest.fixture
def sample_source_nodes():
    """Create sample source nodes for testing."""
    return [
        DocumentNode(
            id="src_1",
            type=NodeType.SECTION,
            content="# Introduction",
            level=1,
            title="Introduction",
            label="intro",
            file_path=Path("docs/en/index.md"),
            line_number=1,
            content_hash="hash1",
        ),
        DocumentNode(
            id="src_2",
            type=NodeType.PARAGRAPH,
            content="This is a paragraph about the project.",
            file_path=Path("docs/en/index.md"),
            line_number=3,
            content_hash="hash2",
        ),
        DocumentNode(
            id="src_3",
            type=NodeType.CODE_BLOCK,
            content="print('Hello, World!')",
            language="python",
            name="example-code",
            file_path=Path("docs/en/index.md"),
            line_number=5,
            content_hash="hash3",
        ),
    ]


@pytest.fixture
def sample_target_nodes():
    """Create sample target nodes for testing."""
    return [
        DocumentNode(
            id="tgt_1",
            type=NodeType.SECTION,
            content="# はじめに",
            level=1,
            title="はじめに",
            label="intro",  # Same label as source
            file_path=Path("docs/ja/index.md"),
            line_number=1,
            content_hash="hash4",
        ),
        DocumentNode(
            id="tgt_2",
            type=NodeType.PARAGRAPH,
            content="これはプロジェクトについての段落です。",
            file_path=Path("docs/ja/index.md"),
            line_number=3,
            content_hash="hash5",
        ),
        # Code block is missing in target (not translated)
    ]


class TestNodeMapping:
    """Test NodeMapping functionality."""

    def test_is_translated(self, sample_source_nodes, sample_target_nodes):
        """Test translation status detection."""
        # Translated mapping
        mapping = NodeMapping(
            source_node=sample_source_nodes[0],
            target_node=sample_target_nodes[0],
            similarity=1.0,
            mapping_type="exact",
        )
        assert mapping.is_translated() is True

        # Not translated mapping
        mapping = NodeMapping(
            source_node=sample_source_nodes[2],
            target_node=None,
            similarity=0.0,
            mapping_type="missing",
        )
        assert mapping.is_translated() is False

    def test_needs_translation(self, sample_source_nodes, sample_target_nodes):
        """Test translation need detection."""
        # Missing translation
        mapping = NodeMapping(
            source_node=sample_source_nodes[2],
            target_node=None,
            similarity=0.0,
            mapping_type="missing",
        )
        assert mapping.needs_translation() is True

        # Fuzzy match with low similarity
        mapping = NodeMapping(
            source_node=sample_source_nodes[1],
            target_node=sample_target_nodes[1],
            similarity=0.8,
            mapping_type="fuzzy",
        )
        assert mapping.needs_translation() is True

        # Exact match
        mapping = NodeMapping(
            source_node=sample_source_nodes[0],
            target_node=sample_target_nodes[0],
            similarity=1.0,
            mapping_type="exact",
        )
        assert mapping.needs_translation() is False


class TestComparisonResult:
    """Test ComparisonResult functionality."""

    def test_to_dict(self, sample_source_nodes, sample_target_nodes):
        """Test dictionary conversion."""
        mappings = [
            NodeMapping(
                source_node=sample_source_nodes[0],
                target_node=sample_target_nodes[0],
                similarity=1.0,
                mapping_type="exact",
            ),
            NodeMapping(
                source_node=sample_source_nodes[2],
                target_node=None,
                similarity=0.0,
                mapping_type="missing",
            ),
        ]

        result = ComparisonResult(
            structure_diff={"section": {"source": 1, "target": 1, "diff": 0}},
            content_changes=[],
            translation_pairs=[],
            coverage_stats={"overall": 0.67},
            mappings=mappings,
            source_lang="en",
            target_lang="ja",
        )

        data = result.to_dict()
        assert data["metadata"]["source_lang"] == "en"
        assert data["metadata"]["target_lang"] == "ja"
        assert data["summary"]["exact_matches"] == 1
        assert data["summary"]["missing"] == 1
        assert data["summary"]["needs_translation"] == 1

    def test_generate_html_report(self, sample_source_nodes, sample_target_nodes):
        """Test HTML report generation."""
        mappings = [
            NodeMapping(
                source_node=sample_source_nodes[0],
                target_node=sample_target_nodes[0],
                similarity=1.0,
                mapping_type="exact",
            ),
        ]

        result = ComparisonResult(
            structure_diff={
                "section": {"source": 1, "target": 1, "diff": 0, "coverage": 100.0}
            },
            content_changes=[],
            translation_pairs=[],
            coverage_stats={"overall": 1.0},
            mappings=mappings,
        )

        html = result.generate_html_report()
        assert "Translation Comparison Report" in html
        assert "100.0%" in html  # Coverage
        assert "Exact Matches" in html


class TestComparisonEngine:
    """Test ComparisonEngine functionality."""

    def test_calculate_similarity(self):
        """Test text similarity calculation."""
        engine = ComparisonEngine()

        # Identical texts
        assert engine._calculate_similarity("Hello", "Hello") == 1.0

        # Completely different
        assert engine._calculate_similarity("Hello", "Goodbye") < 0.5

        # Similar texts
        similarity = engine._calculate_similarity(
            "This is a test sentence.", "This is a test statement."
        )
        assert 0.7 < similarity < 0.95

        # Empty texts
        assert engine._calculate_similarity("", "") == 0.0
        assert engine._calculate_similarity("Hello", "") == 0.0

    def test_are_corresponding_files(self, sample_source_nodes, sample_target_nodes):
        """Test corresponding file detection."""
        engine = ComparisonEngine()

        # Same filename in different language directories
        assert (
            engine._are_corresponding_files(
                sample_source_nodes[0],  # docs/en/index.md
                sample_target_nodes[0],  # docs/ja/index.md
            )
            is True
        )

        # Different files
        node1 = DocumentNode(
            id="1",
            type=NodeType.SECTION,
            content="",
            file_path=Path("docs/en/guide.md"),
            line_number=1,
            content_hash="",
        )
        node2 = DocumentNode(
            id="2",
            type=NodeType.SECTION,
            content="",
            file_path=Path("docs/ja/index.md"),
            line_number=1,
            content_hash="",
        )
        assert engine._are_corresponding_files(node1, node2) is False

    def test_build_node_index(self, sample_source_nodes):
        """Test node index building."""
        engine = ComparisonEngine()
        index = engine._build_node_index(sample_source_nodes)

        # Check label indexing
        assert "label:intro" in index
        assert index["label:intro"].id == "src_1"

        # Check name indexing
        assert "name:example-code" in index
        assert index["name:example-code"].id == "src_3"

        # Check position indexing
        assert "position:index.md:1" in index

    def test_find_exact_match(self, sample_source_nodes, sample_target_nodes):
        """Test exact match finding."""
        engine = ComparisonEngine()
        target_map = engine._build_node_index(sample_target_nodes)
        used = set()

        # Match by label
        match = engine._find_exact_match(sample_source_nodes[0], target_map, used)
        assert match is not None
        assert match.id == "tgt_1"

        # No match for missing node
        match = engine._find_exact_match(sample_source_nodes[2], target_map, used)
        assert match is None

    def test_create_node_mappings(self, sample_source_nodes, sample_target_nodes):
        """Test node mapping creation."""
        engine = ComparisonEngine()
        mappings = engine._create_node_mappings(
            sample_source_nodes, sample_target_nodes
        )

        assert len(mappings) == 3  # All source nodes should have mappings

        # First node should have exact match (same label)
        assert mappings[0].mapping_type == "exact"
        assert mappings[0].target_node is not None

        # Third node should be missing (no code block in target)
        code_mapping = next(m for m in mappings if m.source_node.id == "src_3")
        assert code_mapping.mapping_type == "missing"
        assert code_mapping.target_node is None

    def test_calculate_coverage(self, sample_source_nodes, sample_target_nodes):
        """Test coverage calculation."""
        engine = ComparisonEngine()
        mappings = engine._create_node_mappings(
            sample_source_nodes, sample_target_nodes
        )
        coverage = engine._calculate_coverage(mappings)

        assert "overall" in coverage
        assert "counts" in coverage
        assert coverage["counts"]["total"] == 3
        # Code block OR paragraph is missing
        assert coverage["counts"]["missing"] in [1, 2]
        # Coverage should be either ~33% (1/3) or ~67% (2/3)
        assert 0.3 <= coverage["overall"] <= 0.7

    def test_compare(self, sample_source_nodes, sample_target_nodes):
        """Test full comparison."""
        engine = ComparisonEngine()
        result = engine.compare(sample_source_nodes, sample_target_nodes, "en", "ja")

        assert isinstance(result, ComparisonResult)
        assert result.source_lang == "en"
        assert result.target_lang == "ja"
        assert len(result.mappings) == 3
        assert result.coverage_stats["overall"] > 0
        assert len(result.translation_pairs) == 3

    def test_classify_change(self):
        """Test change classification."""
        engine = ComparisonEngine()

        assert engine._classify_change(0.98) == "minor"
        assert engine._classify_change(0.85) == "moderate"
        assert engine._classify_change(0.6) == "major"
        assert engine._classify_change(0.3) == "rewrite"
