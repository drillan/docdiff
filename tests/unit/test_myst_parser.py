"""Unit tests for MyST parser."""

from pathlib import Path

import pytest

from docdiff.models.node import NodeType
from docdiff.parsers.myst import MySTParser


class TestMySTParser:
    """Test MyST parser."""

    @pytest.fixture
    def parser(self) -> MySTParser:
        """Create a parser instance."""
        return MySTParser()

    def test_parse_simple_section(self, parser: MySTParser) -> None:
        """Test parsing a simple section."""
        content = "# Title\n\nParagraph content"
        nodes = parser.parse(content, Path("test.md"))

        assert len(nodes) == 2
        assert nodes[0].type == NodeType.SECTION
        assert nodes[0].title == "Title"
        assert nodes[0].level == 1
        assert nodes[1].type == NodeType.PARAGRAPH
        assert "Paragraph content" in nodes[1].content

    def test_parse_nested_sections(self, parser: MySTParser) -> None:
        """Test parsing nested sections."""
        content = """# Level 1
        
## Level 2

### Level 3"""
        nodes = parser.parse(content, Path("test.md"))

        sections = [n for n in nodes if n.type == NodeType.SECTION]
        assert len(sections) == 3
        assert sections[0].level == 1
        assert sections[1].level == 2
        assert sections[2].level == 3

    def test_parse_code_block_with_attributes(self, parser: MySTParser) -> None:
        """Test parsing code block with attributes."""
        content = """```{code-block} python
:name: example
:caption: Example Code

print("Hello")
```"""
        nodes = parser.parse(content, Path("test.md"))

        code_blocks = [n for n in nodes if n.type == NodeType.CODE_BLOCK]
        assert len(code_blocks) == 1
        code_block = code_blocks[0]
        assert code_block.language == "python"
        assert code_block.name == "example"
        assert code_block.caption == "Example Code"
        assert 'print("Hello")' in code_block.content

    def test_parse_section_label(self, parser: MySTParser) -> None:
        """Test parsing section with label."""
        content = """(my-label)=
# Labeled Section"""
        nodes = parser.parse(content, Path("test.md"))

        sections = [n for n in nodes if n.type == NodeType.SECTION]
        assert len(sections) == 1
        assert sections[0].label == "my-label"

    def test_parse_figure_directive(self, parser: MySTParser) -> None:
        """Test parsing figure directive."""
        content = """```{figure} image.png
:name: fig-example
:alt: Example Figure
:width: 80%

Caption text
```"""
        nodes = parser.parse(content, Path("test.md"))

        figures = [n for n in nodes if n.type == NodeType.FIGURE]
        assert len(figures) == 1
        figure = figures[0]
        assert figure.name == "fig-example"
        assert figure.metadata.get("alt") == "Example Figure"
        assert figure.metadata.get("width") == "80%"

    def test_parse_math_block(self, parser: MySTParser) -> None:
        """Test parsing math block."""
        content = """```{math}
:name: equation-1

E = mc^2
```"""
        nodes = parser.parse(content, Path("test.md"))

        math_blocks = [n for n in nodes if n.type == NodeType.MATH_BLOCK]
        assert len(math_blocks) == 1
        assert math_blocks[0].name == "equation-1"
        assert "E = mc^2" in math_blocks[0].content

    def test_parse_list(self, parser: MySTParser) -> None:
        """Test parsing lists."""
        content = """- Item 1
- Item 2
  - Nested 2.1
  - Nested 2.2
- Item 3"""
        nodes = parser.parse(content, Path("test.md"))

        lists = [n for n in nodes if n.type == NodeType.LIST]
        assert len(lists) >= 1

    def test_parse_table(self, parser: MySTParser) -> None:
        """Test parsing tables."""
        content = """| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |"""
        nodes = parser.parse(content, Path("test.md"))

        tables = [n for n in nodes if n.type == NodeType.TABLE]
        assert len(tables) == 1
        assert "Header 1" in tables[0].content

    def test_parse_admonition(self, parser: MySTParser) -> None:
        """Test parsing admonition."""
        content = """```{note}
This is a note.
```"""
        nodes = parser.parse(content, Path("test.md"))

        admonitions = [n for n in nodes if n.type == NodeType.ADMONITION]
        assert len(admonitions) == 1
        assert "This is a note" in admonitions[0].content
