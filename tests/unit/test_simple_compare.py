"""Tests for simple_compare command."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch


from docdiff.cli.simple_compare import (
    _compare_structure,
    _parse_directory,
    simple_compare_command,
)
from docdiff.models import DocumentNode, NodeType


class TestParseDirectory:
    """Test _parse_directory function."""

    def test_parse_empty_directory(self):
        """Test parsing an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nodes = _parse_directory(Path(tmpdir))
            assert nodes == []

    def test_parse_nonexistent_directory(self, capsys):
        """Test parsing a non-existent directory."""
        nodes = _parse_directory(Path("/nonexistent"))
        assert nodes == []

        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "does not exist" in captured.out

    def test_parse_directory_with_md_files(self):
        """Test parsing directory with markdown files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple markdown file
            md_file = Path(tmpdir) / "test.md"
            md_file.write_text("# Test\n\nThis is a test.")

            nodes = _parse_directory(Path(tmpdir))

            # Should have at least one node (the section)
            assert len(nodes) > 0
            assert any(node.type == NodeType.SECTION for node in nodes)

    def test_parse_directory_with_rst_files(self):
        """Test parsing directory with RST files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple RST file
            rst_file = Path(tmpdir) / "test.rst"
            rst_file.write_text("Test\n====\n\nThis is a test.")

            nodes = _parse_directory(Path(tmpdir))

            # Should have at least one node
            assert len(nodes) > 0

    def test_parse_directory_with_error(self, capsys):
        """Test parsing directory when parser raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file that will cause an error
            bad_file = Path(tmpdir) / "bad.md"
            bad_file.write_text("")  # Empty file might cause issues

            with patch("docdiff.cli.simple_compare.MySTParser.parse") as mock_parse:
                mock_parse.side_effect = Exception("Parse error")

                _ = _parse_directory(Path(tmpdir))

                captured = capsys.readouterr()
                assert "Error parsing" in captured.out


class TestCompareStructure:
    """Test _compare_structure function."""

    def test_compare_empty_lists(self):
        """Test comparing empty node lists."""
        result = _compare_structure([], [])

        assert result["source_total"] == 0
        assert result["target_total"] == 0
        assert result["by_type"] == {}
        assert result["summary"]["added_types"] == []
        assert result["summary"]["removed_types"] == []
        assert result["summary"]["changed_types"] == []

    def test_compare_identical_structures(self):
        """Test comparing identical structures."""
        source_nodes = [
            DocumentNode.create_with_hash(
                id="1",
                type=NodeType.SECTION,
                content="# Test",
                file_path=Path("test.md"),
                line_number=1,
            ),
            DocumentNode.create_with_hash(
                id="2",
                type=NodeType.PARAGRAPH,
                content="Test paragraph",
                file_path=Path("test.md"),
                line_number=3,
            ),
        ]

        target_nodes = [
            DocumentNode.create_with_hash(
                id="3",
                type=NodeType.SECTION,
                content="# Test",
                file_path=Path("test2.md"),
                line_number=1,
            ),
            DocumentNode.create_with_hash(
                id="4",
                type=NodeType.PARAGRAPH,
                content="Test paragraph",
                file_path=Path("test2.md"),
                line_number=3,
            ),
        ]

        result = _compare_structure(source_nodes, target_nodes)

        assert result["source_total"] == 2
        assert result["target_total"] == 2
        assert result["by_type"]["section"]["diff"] == 0
        assert result["by_type"]["paragraph"]["diff"] == 0
        assert result["summary"]["changed_types"] == []

    def test_compare_different_structures(self):
        """Test comparing different structures."""
        source_nodes = [
            DocumentNode.create_with_hash(
                id="1",
                type=NodeType.SECTION,
                content="# Test",
                file_path=Path("test.md"),
                line_number=1,
            ),
        ]

        target_nodes = [
            DocumentNode.create_with_hash(
                id="2",
                type=NodeType.SECTION,
                content="# Test",
                file_path=Path("test2.md"),
                line_number=1,
            ),
            DocumentNode.create_with_hash(
                id="3",
                type=NodeType.CODE_BLOCK,
                content="```python\nprint('test')\n```",
                file_path=Path("test2.md"),
                line_number=3,
            ),
        ]

        result = _compare_structure(source_nodes, target_nodes)

        assert result["source_total"] == 1
        assert result["target_total"] == 2
        assert result["by_type"]["section"]["diff"] == 0
        assert result["by_type"]["code_block"]["diff"] == 1
        assert "code_block" in result["summary"]["added_types"]

    def test_compare_with_removed_types(self):
        """Test comparing with removed node types."""
        source_nodes = [
            DocumentNode.create_with_hash(
                id="1",
                type=NodeType.SECTION,
                content="# Test",
                file_path=Path("test.md"),
                line_number=1,
            ),
            DocumentNode.create_with_hash(
                id="2",
                type=NodeType.TABLE,
                content="| a | b |",
                file_path=Path("test.md"),
                line_number=3,
            ),
        ]

        target_nodes = [
            DocumentNode.create_with_hash(
                id="3",
                type=NodeType.SECTION,
                content="# Test",
                file_path=Path("test2.md"),
                line_number=1,
            ),
        ]

        result = _compare_structure(source_nodes, target_nodes)

        assert result["by_type"]["table"]["diff"] == -1
        assert "table" in result["summary"]["removed_types"]


class TestSimpleCompareCommand:
    """Test simple_compare_command function."""

    @patch("docdiff.cli.simple_compare._parse_directory")
    @patch("docdiff.cli.simple_compare._compare_structure")
    def test_simple_compare_basic(self, mock_compare, mock_parse, capsys):
        """Test basic simple_compare_command execution."""
        # Setup mocks
        mock_parse.return_value = []
        mock_compare.return_value = {
            "source_total": 0,
            "target_total": 0,
            "by_type": {},
            "summary": {
                "added_types": [],
                "removed_types": [],
                "changed_types": [],
            },
        }

        # Run command with None for optional argument
        simple_compare_command(Path("source"), Path("target"), None)

        # Check output
        captured = capsys.readouterr()
        assert "Simple Structure Comparison" in captured.out
        assert "Source: source" in captured.out
        assert "Target: target" in captured.out

    @patch("docdiff.cli.simple_compare._parse_directory")
    @patch("docdiff.cli.simple_compare._compare_structure")
    def test_simple_compare_with_output_file(self, mock_compare, mock_parse):
        """Test simple_compare_command with output file."""
        # Setup mocks
        mock_parse.return_value = []
        mock_compare.return_value = {
            "source_total": 5,
            "target_total": 7,
            "by_type": {
                "section": {"source": 2, "target": 3, "diff": 1},
            },
            "summary": {
                "added_types": [],
                "removed_types": [],
                "changed_types": ["section"],
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            output_path = Path(tmp.name)

        # Run command
        simple_compare_command(Path("source"), Path("target"), output_path)

        # Check output file was created
        assert output_path.exists()

        # Check content
        with open(output_path) as f:
            data = json.load(f)
            assert data["source_total"] == 5
            assert data["target_total"] == 7
            assert "section" in data["by_type"]

        output_path.unlink()

    @patch("docdiff.cli.simple_compare._parse_directory")
    @patch("docdiff.cli.simple_compare._compare_structure")
    def test_simple_compare_with_summary(self, mock_compare, mock_parse, capsys):
        """Test simple_compare_command with summary output."""
        # Setup mocks
        mock_parse.return_value = []
        mock_compare.return_value = {
            "source_total": 10,
            "target_total": 12,
            "by_type": {
                "section": {"source": 3, "target": 3, "diff": 0},
                "paragraph": {"source": 5, "target": 4, "diff": -1},
                "code_block": {"source": 2, "target": 5, "diff": 3},
            },
            "summary": {
                "added_types": [],
                "removed_types": [],
                "changed_types": ["paragraph", "code_block"],
            },
        }

        # Run command with None for optional argument
        simple_compare_command(Path("source"), Path("target"), None)

        # Check output
        captured = capsys.readouterr()
        assert "Total: Source: 10, Target: 12" in captured.out
        assert "Changed types: paragraph, code_block" in captured.out
