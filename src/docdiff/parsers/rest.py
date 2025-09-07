"""reStructuredText parser implementation."""

import hashlib
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# from docutils.parsers.rst import Parser as RSTParser  # type: ignore

from docdiff.models.node import DocumentNode, NodeType
from docdiff.parsers.base import BaseParser


class ReSTParser(BaseParser):
    """Parser for reStructuredText documents."""

    def __init__(self) -> None:
        """Initialize the ReST parser."""
        # self.parser = RSTParser()  # Simple implementation for now

    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file.

        Args:
            file_path: Path to check

        Returns:
            True if file has .rst extension
        """
        return file_path.suffix.lower() == ".rst"

    def parse(self, content: str, file_path: Path) -> List[DocumentNode]:
        """Parse reStructuredText content and return document nodes.

        Args:
            content: reStructuredText content
            file_path: Path to the source file

        Returns:
            List of DocumentNodes
        """
        # For now, return a simple implementation
        # Full docutils integration would be more complex
        nodes_list: List[DocumentNode] = []
        lines = content.split("\n")
        current_line = 0
        current_label: Optional[str] = None

        while current_line < len(lines):
            line = lines[current_line]

            # Check for label/target
            if line.startswith(".. _") and line.endswith(":"):
                current_label = line[4:-1].strip()
                current_line += 1
                continue

            # Check for title with underline
            if (
                current_line + 1 < len(lines)
                and line.strip()
                and lines[current_line + 1].strip()
                and all(c in "=-~`#*+" for c in lines[current_line + 1].strip())
                and len(lines[current_line + 1].strip()) >= len(line.strip())
            ):
                title = line.strip()
                underline_char = lines[current_line + 1][0]
                level = self._get_heading_level(underline_char)

                node = self._create_node(
                    type=NodeType.SECTION,
                    content=f"{line}\n{lines[current_line + 1]}",
                    file_path=file_path,
                    line_number=current_line + 1,
                    level=level,
                    title=title,
                    label=current_label,
                )
                nodes_list.append(node)
                current_label = None
                current_line += 2
                continue

            # Check for directive
            if line.startswith(".. ") and "::" in line:
                directive_nodes = self._parse_directive(lines, current_line, file_path)
                if directive_nodes:
                    nodes_list.extend(directive_nodes)
                    # Skip directive content
                    current_line += 1
                    while current_line < len(lines) and (
                        lines[current_line].startswith("   ")
                        or lines[current_line].strip() == ""
                    ):
                        current_line += 1
                    continue

            # Check for literal block
            if line.endswith("::"):
                code_node = self._parse_literal_block(lines, current_line, file_path)
                if code_node:
                    nodes_list.append(code_node)
                    # Skip literal block
                    current_line += 1
                    while current_line < len(lines) and (
                        lines[current_line].startswith("   ")
                        or lines[current_line].strip() == ""
                    ):
                        current_line += 1
                    continue

            # Regular paragraph
            if line.strip() and not line.startswith(".. "):
                para_lines = [line]
                current_line += 1
                while (
                    current_line < len(lines)
                    and lines[current_line].strip()
                    and not lines[current_line].startswith(".. ")
                    and not self._is_title_underline(lines, current_line)
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
                    nodes_list.append(node)
                continue

            current_line += 1

        return nodes_list

    def _get_heading_level(self, char: str) -> int:
        """Get heading level from underline character."""
        level_map = {
            "=": 1,
            "-": 2,
            "~": 3,
            "`": 4,
            "#": 5,
            "*": 6,
            "+": 7,
        }
        return level_map.get(char, 1)

    def _is_title_underline(self, lines: List[str], line_idx: int) -> bool:
        """Check if current line is a title underline."""
        if line_idx == 0 or line_idx >= len(lines):
            return False

        line = lines[line_idx]
        prev_line = lines[line_idx - 1]

        return bool(
            line.strip()
            and prev_line.strip()
            and all(c in "=-~`#*+" for c in line.strip())
            and len(line.strip()) >= len(prev_line.strip())
        )

    def _parse_directive(
        self, lines: List[str], start_line: int, file_path: Path
    ) -> List[DocumentNode]:
        """Parse a reStructuredText directive."""
        nodes_list: List[DocumentNode] = []
        line = lines[start_line]

        # Parse directive
        directive_match = re.match(r"^\.\. ([^:]+)::\s*(.*)$", line)
        if not directive_match:
            return nodes_list

        directive_type = directive_match.group(1).strip()
        directive_args = directive_match.group(2).strip()

        # Parse options and content
        options: Dict[str, str] = {}
        content_lines = []
        current = start_line + 1
        in_options = True

        while current < len(lines):
            if not lines[current].startswith("   ") and lines[current].strip():
                break

            if lines[current].strip() == "":
                in_options = False
            elif in_options and lines[current].strip().startswith(":"):
                # Parse option
                option_match = re.match(r"^\s*:([^:]+):\s*(.*)$", lines[current])
                if option_match:
                    options[option_match.group(1)] = option_match.group(2)
            else:
                content_lines.append(lines[current].strip())
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
            nodes_list.append(node)
        elif directive_type == "figure":
            node = self._create_node(
                type=NodeType.FIGURE,
                content=content,
                file_path=file_path,
                line_number=start_line + 1,
                name=options.get("name"),
                metadata={
                    "src": directive_args,
                    "alt": options.get("alt"),
                    "width": options.get("width"),
                    "height": options.get("height"),
                    "align": options.get("align"),
                },
            )
            nodes_list.append(node)
        elif directive_type == "math":
            node = self._create_node(
                type=NodeType.MATH_BLOCK,
                content=content,
                file_path=file_path,
                line_number=start_line + 1,
                name=options.get("name"),
            )
            nodes_list.append(node)
        elif directive_type in [
            "note",
            "warning",
            "tip",
            "caution",
            "attention",
            "error",
            "hint",
            "important",
        ]:
            node = self._create_node(
                type=NodeType.ADMONITION,
                content=content,
                file_path=file_path,
                line_number=start_line + 1,
                metadata={"type": directive_type},
            )
            nodes_list.append(node)

        return nodes_list

    def _parse_literal_block(
        self, lines: List[str], start_line: int, file_path: Path
    ) -> Optional[DocumentNode]:
        """Parse a literal block (code block)."""
        if not lines[start_line].endswith("::"):
            return None

        # Collect indented content
        content_lines = []
        current = start_line + 1

        # Skip empty lines
        while current < len(lines) and lines[current].strip() == "":
            current += 1

        # Collect indented lines
        while current < len(lines) and lines[current].startswith("   "):
            content_lines.append(lines[current][3:])  # Remove indentation
            current += 1

        if content_lines:
            content = "\n".join(content_lines)
            return self._create_node(
                type=NodeType.CODE_BLOCK,
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
