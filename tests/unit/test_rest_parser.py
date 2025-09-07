"""Unit tests for ReSTParser."""

from pathlib import Path

import pytest

from docdiff.models.node import NodeType
from docdiff.parsers.rest import ReSTParser


@pytest.fixture
def parser():
    """Create a ReSTParser instance."""
    return ReSTParser()



class TestReSTParserCanParse:
    """Test the can_parse method."""

    def test_can_parse_rst_file(self, parser):
        """Test that .rst files are recognized."""
        assert parser.can_parse(Path("document.rst")) is True
        assert parser.can_parse(Path("document.RST")) is True
        assert parser.can_parse(Path("/path/to/document.rst")) is True

    def test_cannot_parse_non_rst_file(self, parser):
        """Test that non-.rst files are not recognized."""
        assert parser.can_parse(Path("document.md")) is False
        assert parser.can_parse(Path("document.txt")) is False
        assert parser.can_parse(Path("document.py")) is False
        assert parser.can_parse(Path("document")) is False


class TestReSTParserParse:
    """Test the parse method."""

    def test_parse_empty_document(self, parser):
        """Test parsing an empty document."""
        content = ""
        nodes = parser.parse(content, Path("test.rst"))
        assert nodes == []

    def test_parse_simple_paragraph(self, parser):
        """Test parsing a simple paragraph."""
        content = "This is a simple paragraph."
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 1
        assert nodes[0].type == NodeType.PARAGRAPH
        assert nodes[0].content == "This is a simple paragraph."
        assert nodes[0].line_number == 1

    def test_parse_multiple_paragraphs(self, parser):
        """Test parsing multiple paragraphs."""
        content = """First paragraph.

Second paragraph.

Third paragraph."""
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 3
        assert all(node.type == NodeType.PARAGRAPH for node in nodes)
        assert nodes[0].content == "First paragraph."
        assert nodes[1].content == "Second paragraph."
        assert nodes[2].content == "Third paragraph."

    def test_parse_section_with_equal_underline(self, parser):
        """Test parsing a section with = underline (level 1)."""
        content = """Title
=====

Some content."""
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 2
        assert nodes[0].type == NodeType.SECTION
        assert nodes[0].title == "Title"
        assert nodes[0].level == 1
        assert nodes[0].content == "Title\n====="
        assert nodes[1].type == NodeType.PARAGRAPH

    def test_parse_section_with_dash_underline(self, parser):
        """Test parsing a section with - underline (level 2)."""
        content = """Subtitle
--------

Some content."""
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 2
        assert nodes[0].type == NodeType.SECTION
        assert nodes[0].title == "Subtitle"
        assert nodes[0].level == 2

    def test_parse_multiple_level_sections(self, parser):
        """Test parsing sections with different levels."""
        content = """Main Title
==========

Level 1 content.

Subtitle
--------

Level 2 content.

Sub-subtitle
~~~~~~~~~~~~

Level 3 content."""
        nodes = parser.parse(content, Path("test.rst"))

        sections = [n for n in nodes if n.type == NodeType.SECTION]
        assert len(sections) == 3
        assert sections[0].level == 1
        assert sections[1].level == 2
        assert sections[2].level == 3

    def test_parse_section_with_label(self, parser):
        """Test parsing a labeled section."""
        content = """.. _my-label:

Labeled Section
===============

Content."""
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 2
        assert nodes[0].type == NodeType.SECTION
        assert nodes[0].label == "my-label"
        assert nodes[0].title == "Labeled Section"

    def test_parse_code_block_directive(self, parser):
        """Test parsing a code-block directive."""
        content = """.. code-block:: python
   :name: example
   :caption: Example code

   def hello():
       print("Hello, World!")"""
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 1
        assert nodes[0].type == NodeType.CODE_BLOCK
        assert nodes[0].language == "python"
        assert nodes[0].name == "example"
        assert nodes[0].caption == "Example code"
        assert "def hello():" in nodes[0].content
        assert 'print("Hello, World!")' in nodes[0].content

    def test_parse_figure_directive(self, parser):
        """Test parsing a figure directive."""
        content = """.. figure:: /path/to/image.png
   :name: fig1
   :alt: Alternative text
   :width: 500px
   :height: 300px
   :align: center

   Figure caption text."""
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 1
        assert nodes[0].type == NodeType.FIGURE
        assert nodes[0].name == "fig1"
        assert nodes[0].metadata["src"] == "/path/to/image.png"
        assert nodes[0].metadata["alt"] == "Alternative text"
        assert nodes[0].metadata["width"] == "500px"
        assert nodes[0].metadata["height"] == "300px"
        assert nodes[0].metadata["align"] == "center"
        assert nodes[0].content == "Figure caption text."

    def test_parse_math_directive(self, parser):
        """Test parsing a math directive."""
        content = """.. math::
   :name: equation1

   E = mc^2"""
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 1
        assert nodes[0].type == NodeType.MATH_BLOCK
        assert nodes[0].name == "equation1"
        assert nodes[0].content == "E = mc^2"

    def test_parse_admonition_directives(self, parser):
        """Test parsing various admonition directives."""
        content = """.. note::

   This is a note.

.. warning::

   This is a warning.

.. tip::

   This is a tip."""
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 3
        assert all(node.type == NodeType.ADMONITION for node in nodes)
        assert nodes[0].metadata["type"] == "note"
        assert nodes[0].content == "This is a note."
        assert nodes[1].metadata["type"] == "warning"
        assert nodes[1].content == "This is a warning."
        assert nodes[2].metadata["type"] == "tip"
        assert nodes[2].content == "This is a tip."

    def test_parse_literal_block(self, parser):
        """Test parsing a literal block."""
        content = """Here is some code::

   def example():
       return 42

Back to normal text."""
        nodes = parser.parse(content, Path("test.rst"))

        # The parser treats "Here is some code::" as the start of a literal block
        # and doesn't create a separate paragraph for it
        assert len(nodes) == 2
        assert nodes[0].type == NodeType.CODE_BLOCK
        assert nodes[0].content == "def example():\n    return 42"
        assert nodes[1].type == NodeType.PARAGRAPH
        assert nodes[1].content == "Back to normal text."

    def test_parse_empty_literal_block(self, parser):
        """Test parsing an empty literal block."""
        content = """Code follows::

Normal text."""
        nodes = parser.parse(content, Path("test.rst"))

        # Should only have paragraphs, no code block
        assert len(nodes) == 2
        assert all(node.type == NodeType.PARAGRAPH for node in nodes)

    def test_parse_complex_document(self, parser):
        """Test parsing a complex document with mixed elements."""
        content = """.. _intro:

Introduction
============

This is the introduction paragraph.

.. note::

   Important information here.

Basic Usage
-----------

Here's how to use it::

   command --option value

.. code-block:: python
   :caption: Python example

   import sys
   print(sys.version)

.. figure:: diagram.png
   :alt: System diagram

   System architecture overview.

Conclusion
----------

Final thoughts."""
        nodes = parser.parse(content, Path("test.rst"))

        # Check node types
        node_types = [node.type for node in nodes]
        assert NodeType.SECTION in node_types
        assert NodeType.PARAGRAPH in node_types
        assert NodeType.ADMONITION in node_types
        assert NodeType.CODE_BLOCK in node_types
        assert NodeType.FIGURE in node_types

        # Check labeled section
        sections = [n for n in nodes if n.type == NodeType.SECTION]
        assert sections[0].label == "intro"
        assert sections[0].title == "Introduction"


class TestReSTParserHelpers:
    """Test helper methods."""

    def test_get_heading_level(self, parser):
        """Test heading level detection."""
        assert parser._get_heading_level("=") == 1
        assert parser._get_heading_level("-") == 2
        assert parser._get_heading_level("~") == 3
        assert parser._get_heading_level("`") == 4
        assert parser._get_heading_level("#") == 5
        assert parser._get_heading_level("*") == 6
        assert parser._get_heading_level("+") == 7
        assert parser._get_heading_level("x") == 1  # Unknown defaults to 1

    def test_is_title_underline(self, parser):
        """Test title underline detection."""
        lines = [
            "Title",
            "=====",
            "",
            "Subtitle",
            "--------",
            "Not a title",
            "Just text",
        ]

        assert parser._is_title_underline(lines, 1) is True
        assert parser._is_title_underline(lines, 4) is True
        assert parser._is_title_underline(lines, 6) is False
        assert parser._is_title_underline(lines, 0) is False
        assert parser._is_title_underline(lines, 100) is False

    def test_is_title_underline_length_check(self, parser):
        """Test that underline must be at least as long as title."""
        lines = [
            "Long Title Here",
            "====",  # Too short
            "",
            "Short",
            "===============",  # Longer is OK
        ]

        assert parser._is_title_underline(lines, 1) is False
        assert parser._is_title_underline(lines, 4) is True

    def test_create_node_with_hash(self, parser):
        """Test node creation with content hash."""
        node = parser._create_node(
            type=NodeType.PARAGRAPH,
            content="Test content",
            file_path=Path("test.rst"),
            line_number=1,
        )

        assert node.type == NodeType.PARAGRAPH
        assert node.content == "Test content"
        assert node.file_path == Path("test.rst")
        assert node.line_number == 1
        assert node.content_hash is not None
        assert len(node.content_hash) == 64  # SHA256 hex length

    def test_create_node_with_kwargs(self, parser):
        """Test node creation with additional kwargs."""
        node = parser._create_node(
            type=NodeType.SECTION,
            content="Section",
            file_path=Path("test.rst"),
            line_number=1,
            title="My Title",
            level=2,
            label="my-label",
        )

        assert node.title == "My Title"
        assert node.level == 2
        assert node.label == "my-label"


class TestReSTParserEdgeCases:
    """Test edge cases and error handling."""

    def test_parse_malformed_directive(self, parser):
        """Test parsing malformed directives."""
        content = """.. invalid directive without double colon

.. :also:invalid:

Normal paragraph."""
        nodes = parser.parse(content, Path("test.rst"))

        # Should only parse the normal paragraph
        assert len(nodes) == 1
        assert nodes[0].type == NodeType.PARAGRAPH
        assert nodes[0].content == "Normal paragraph."

    def test_parse_incomplete_section(self, parser):
        """Test parsing incomplete section (title without underline)."""
        content = """Title without underline
Some text here."""
        nodes = parser.parse(content, Path("test.rst"))

        # Should be parsed as a single paragraph
        assert len(nodes) == 1
        assert nodes[0].type == NodeType.PARAGRAPH
        assert "Title without underline" in nodes[0].content

    def test_parse_mixed_indentation(self, parser):
        """Test parsing with mixed indentation."""
        content = """.. code-block:: python

   def foo():
       pass
    # Wrong indentation
      # Also wrong

Normal text."""
        nodes = parser.parse(content, Path("test.rst"))

        # Should still parse the code block
        code_blocks = [n for n in nodes if n.type == NodeType.CODE_BLOCK]
        assert len(code_blocks) == 1

    def test_parse_nested_directives(self, parser):
        """Test that nested directives are not supported."""
        content = """.. note::

   .. warning::

      Nested warning inside note.

   Back to note content."""
        nodes = parser.parse(content, Path("test.rst"))

        # Should only parse the outer note
        assert len(nodes) == 1
        assert nodes[0].type == NodeType.ADMONITION
        assert nodes[0].metadata["type"] == "note"

    def test_parse_unicode_content(self, parser):
        """Test parsing content with Unicode characters."""
        content = """Unicode Title 中文
=================

Unicode content: 日本語, العربية, 🎉"""
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 2
        assert nodes[0].type == NodeType.SECTION
        assert nodes[0].title == "Unicode Title 中文"
        assert "🎉" in nodes[1].content

    def test_parse_windows_line_endings(self, parser):
        """Test parsing content with Windows line endings."""
        content = "Title\r\n=====\r\n\r\nParagraph."
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 2
        assert nodes[0].type == NodeType.SECTION
        assert nodes[1].type == NodeType.PARAGRAPH

    def test_parse_directive_without_content(self, parser):
        """Test parsing directive without content."""
        content = """.. note::

.. warning::

   Warning with content."""
        nodes = parser.parse(content, Path("test.rst"))

        # Both should be parsed
        assert len(nodes) == 2
        assert nodes[0].type == NodeType.ADMONITION
        assert nodes[0].content == ""
        assert nodes[1].type == NodeType.ADMONITION
        assert nodes[1].content == "Warning with content."

    def test_parse_code_block_without_language(self, parser):
        """Test parsing code-block without language specification."""
        content = """.. code-block::

   plain code
   without language"""
        nodes = parser.parse(content, Path("test.rst"))

        assert len(nodes) == 1
        assert nodes[0].type == NodeType.CODE_BLOCK
        assert nodes[0].language is None
        assert "plain code" in nodes[0].content
