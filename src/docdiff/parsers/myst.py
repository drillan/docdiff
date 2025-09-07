"""MyST (Markedly Structured Text) parser implementation."""

import hashlib
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# from myst_parser.parsers.parse import MystParser  # Not needed for simple parsing

from docdiff.models.node import DocumentNode, NodeType
from docdiff.parsers.base import BaseParser


class MySTParser(BaseParser):
    """Parser for MyST markdown documents."""

    def __init__(self) -> None:
        """Initialize the MyST parser."""
        # self.parser = MystParser()  # Simple implementation for now

    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file.

        Args:
            file_path: Path to check

        Returns:
            True if file has .md extension
        """
        return file_path.suffix.lower() == ".md"

    def parse(self, content: str, file_path: Path) -> List[DocumentNode]:
        """Parse MyST content and return document nodes.

        Args:
            content: MyST markdown content
            file_path: Path to the source file

        Returns:
            List of DocumentNodes
        """
        nodes: List[DocumentNode] = []
        lines = content.split("\n")
        current_line = 0
        current_label: Optional[str] = None

        while current_line < len(lines):
            line = lines[current_line]

            # Check for label
            label_match = re.match(r"^\(([^)]+)\)=$", line)
            if label_match:
                current_label = label_match.group(1)
                current_line += 1
                continue

            # Check for heading
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2)
                node = self._create_node(
                    type=NodeType.SECTION,
                    content=line,
                    file_path=file_path,
                    line_number=current_line + 1,
                    level=level,
                    title=title,
                    label=current_label,
                )
                nodes.append(node)
                current_label = None
                current_line += 1
                continue

            # Check for MyST directive
            if line.startswith("```{"):
                directive_nodes = self._parse_directive(lines, current_line, file_path)
                if directive_nodes:
                    nodes.extend(directive_nodes)
                    # Skip to end of directive
                    while current_line < len(lines) and not lines[
                        current_line
                    ].endswith("```"):
                        current_line += 1
                    current_line += 1
                    continue

            # Check for regular code block
            if line.startswith("```"):
                code_node = self._parse_code_block(lines, current_line, file_path)
                if code_node:
                    nodes.append(code_node)
                    # Skip to end of code block
                    current_line += 1
                    while (
                        current_line < len(lines) and not lines[current_line] == "```"
                    ):
                        current_line += 1
                    current_line += 1
                    continue

            # Check for list
            if re.match(r"^[\s]*[-*+]\s+", line) or re.match(r"^[\s]*\d+\.\s+", line):
                list_node = self._parse_list(lines, current_line, file_path)
                if list_node:
                    nodes.append(list_node)
                    # Skip processed list items
                    while current_line < len(lines) and (
                        re.match(r"^[\s]*[-*+]\s+", lines[current_line])
                        or re.match(r"^[\s]*\d+\.\s+", lines[current_line])
                        or (current_line > 0 and lines[current_line].startswith("  "))
                    ):
                        current_line += 1
                    continue

            # Check for table
            if (
                "|" in line
                and current_line + 1 < len(lines)
                and "|" in lines[current_line + 1]
            ):
                table_node = self._parse_table(lines, current_line, file_path)
                if table_node:
                    nodes.append(table_node)
                    # Skip table lines
                    while current_line < len(lines) and "|" in lines[current_line]:
                        current_line += 1
                    continue

            # Regular paragraph
            if line.strip() and not line.startswith("#"):
                para_lines = [line]
                current_line += 1
                while (
                    current_line < len(lines)
                    and lines[current_line].strip()
                    and not self._is_special_line(lines[current_line])
                ):
                    para_lines.append(lines[current_line])
                    current_line += 1

                if para_lines and any(line.strip() for line in para_lines):
                    para_content = "\n".join(para_lines)
                    node = self._create_node(
                        type=NodeType.PARAGRAPH,
                        content=para_content,
                        file_path=file_path,
                        line_number=current_line - len(para_lines) + 1,
                    )
                    nodes.append(node)
                continue

            current_line += 1

        return nodes

    def _is_special_line(self, line: str) -> bool:
        """Check if a line starts a special construct."""
        return (
            line.startswith("#")
            or line.startswith("```")
            or re.match(r"^[\s]*[-*+]\s+", line) is not None
            or re.match(r"^\(([^)]+)\)=$", line) is not None
            or "|" in line
        )

    def _parse_directive(
        self, lines: List[str], start_line: int, file_path: Path
    ) -> List[DocumentNode]:
        """Parse a MyST directive."""
        nodes: List[DocumentNode] = []
        line = lines[start_line]

        # Parse directive header
        directive_match = re.match(r"^```\{([^}]+)\}\s*(.*)$", line)
        if not directive_match:
            return nodes

        directive_type = directive_match.group(1)
        directive_args = directive_match.group(2).strip()

        # Parse directive options
        options: Dict[str, str] = {}
        content_lines = []
        current = start_line + 1

        while current < len(lines):
            if lines[current] == "```":
                break
            if lines[current].startswith(":") and ":" in lines[current][1:]:
                # Parse option
                option_match = re.match(r"^:([^:]+):\s*(.*)$", lines[current])
                if option_match:
                    options[option_match.group(1)] = option_match.group(2)
            else:
                content_lines.append(lines[current])
            current += 1

        content = "\n".join(content_lines).strip()

        # Create node based on directive type
        if directive_type == "code-block":
            node = self._create_node(
                type=NodeType.CODE_BLOCK,
                content=content,
                file_path=file_path,
                line_number=start_line + 1,
                language=directive_args or None,
                name=options.get("name"),
                caption=options.get("caption"),
            )
            nodes.append(node)
        elif directive_type == "figure":
            node = self._create_node(
                type=NodeType.FIGURE,
                content=content,
                file_path=file_path,
                line_number=start_line + 1,
                name=options.get("name"),
                caption=content if content else None,
                metadata={
                    "src": directive_args,
                    "alt": options.get("alt"),
                    "width": options.get("width"),
                    "height": options.get("height"),
                    "align": options.get("align"),
                },
            )
            nodes.append(node)
        elif directive_type == "math":
            node = self._create_node(
                type=NodeType.MATH_BLOCK,
                content=content,
                file_path=file_path,
                line_number=start_line + 1,
                name=options.get("name"),
            )
            nodes.append(node)
        elif directive_type in [
            "note",
            "warning",
            "tip",
            "caution",
            "attention",
            "error",
            "hint",
            "important",
            "admonition",
        ]:
            node = self._create_node(
                type=NodeType.ADMONITION,
                content=content,
                file_path=file_path,
                line_number=start_line + 1,
                metadata={"type": directive_type, "class": options.get("class")},
            )
            nodes.append(node)

        return nodes

    def _parse_code_block(
        self, lines: List[str], start_line: int, file_path: Path
    ) -> Optional[DocumentNode]:
        """Parse a regular code block."""
        line = lines[start_line]
        if not line.startswith("```"):
            return None

        # Extract language if present
        language = line[3:].strip() or None

        # Collect code content
        content_lines = []
        current = start_line + 1
        while current < len(lines) and lines[current] != "```":
            content_lines.append(lines[current])
            current += 1

        content = "\n".join(content_lines)

        return self._create_node(
            type=NodeType.CODE_BLOCK,
            content=content,
            file_path=file_path,
            line_number=start_line + 1,
            language=language,
        )

    def _parse_list(
        self, lines: List[str], start_line: int, file_path: Path
    ) -> Optional[DocumentNode]:
        """Parse a list."""
        list_lines = []
        current = start_line

        while current < len(lines):
            line = lines[current]
            if re.match(r"^[\s]*[-*+]\s+", line) or re.match(r"^[\s]*\d+\.\s+", line):
                list_lines.append(line)
            elif current > start_line and line.startswith("  "):
                # Continuation of list item
                list_lines.append(line)
            else:
                break
            current += 1

        if list_lines:
            content = "\n".join(list_lines)
            return self._create_node(
                type=NodeType.LIST,
                content=content,
                file_path=file_path,
                line_number=start_line + 1,
            )
        return None

    def _parse_table(
        self, lines: List[str], start_line: int, file_path: Path
    ) -> Optional[DocumentNode]:
        """Parse a table."""
        table_lines = []
        current = start_line

        while current < len(lines) and "|" in lines[current]:
            table_lines.append(lines[current])
            current += 1

        if table_lines:
            content = "\n".join(table_lines)
            return self._create_node(
                type=NodeType.TABLE,
                content=content,
                file_path=file_path,
                line_number=start_line + 1,
            )
        return None

    def _create_node(
        self,
        type: NodeType,
        content: str,
        file_path: Path,
        line_number: int,
        **kwargs: Any,
    ) -> DocumentNode:
        """Create a DocumentNode with generated ID and hash.

        Args:
            type: Node type
            content: Node content
            file_path: Source file path
            line_number: Line number in source
            **kwargs: Additional node attributes

        Returns:
            DocumentNode instance
        """
        # Generate deterministic ID based on content and location
        # This ensures the same node always gets the same ID
        id_components = [
            str(file_path),
            str(line_number),
            type.value,
            content[:100],  # Use first 100 chars to avoid huge IDs
        ]
        id_string = "|".join(id_components)
        node_id = hashlib.sha256(id_string.encode()).hexdigest()[:16]

        content_hash = hashlib.sha256(content.encode()).hexdigest()

        return DocumentNode(
            id=node_id,
            type=type,
            content=content,
            file_path=file_path,
            line_number=line_number,
            content_hash=content_hash,
            **kwargs,
        )
