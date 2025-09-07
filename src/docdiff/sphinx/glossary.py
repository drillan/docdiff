"""Glossary extraction and management for Sphinx documentation."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class GlossaryTerm:
    """Represents a glossary term definition."""

    term: str
    aliases: List[str]
    definition: str
    source_file: Path
    line_number: int
    translations: Dict[str, str] = field(default_factory=dict)

    def __hash__(self) -> int:
        """Make GlossaryTerm hashable for use in sets."""
        return hash((self.term, str(self.source_file), self.line_number))

    def __eq__(self, other: object) -> bool:
        """Check equality based on term and location."""
        if not isinstance(other, GlossaryTerm):
            return False
        return (
            self.term == other.term
            and self.source_file == other.source_file
            and self.line_number == other.line_number
        )


@dataclass
class TermReference:
    """Represents a reference to a glossary term in documentation."""

    term: str
    node_id: str
    file_path: Path
    line_number: int
    resolved: bool = False
    context: str = ""  # Surrounding text for better translation context


class GlossaryExtractor:
    """Extracts glossary terms and references from documentation."""

    # Patterns for reStructuredText glossary
    RST_GLOSSARY_START = re.compile(r"^\.\.\s+glossary::\s*$", re.MULTILINE)
    RST_GLOSSARY_OPTIONS = re.compile(r"^\s+:(sorted|strict):\s*$", re.MULTILINE)
    RST_TERM_PATTERN = re.compile(r"^(\s{3,})(\S[^\n]*?)$", re.MULTILINE)
    RST_DEFINITION_PATTERN = re.compile(r"^(\s{6,})(.+?)$", re.MULTILINE)

    # Patterns for MyST glossary
    MYST_GLOSSARY_START = re.compile(r"^```\{glossary\}", re.MULTILINE)
    MYST_GLOSSARY_END = re.compile(r"^```$", re.MULTILINE)

    # Patterns for term references
    RST_TERM_REF = re.compile(r":term:`([^`]+)`")
    MYST_TERM_REF = re.compile(r"\{term\}`([^`]+)`")

    def __init__(self) -> None:
        """Initialize the glossary extractor."""
        self.terms: Dict[str, GlossaryTerm] = {}
        self.references: List[TermReference] = []

    def extract_from_rst(self, content: str, source_file: Path) -> List[GlossaryTerm]:
        """Extract glossary terms from reStructuredText content.

        Args:
            content: The RST content to parse
            source_file: Path to the source file

        Returns:
            List of extracted glossary terms
        """
        terms = []
        lines = content.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for glossary directive
            if self.RST_GLOSSARY_START.match(line):
                i += 1
                # Skip options
                while i < len(lines) and (
                    not lines[i].strip() or self.RST_GLOSSARY_OPTIONS.match(lines[i])
                ):
                    i += 1

                # Extract terms and definitions
                while i < len(lines):
                    if not lines[i].strip():
                        i += 1
                        continue

                    # Check if we've exited the glossary
                    if lines[i] and not lines[i].startswith(" "):
                        break

                    # Look for term (3+ spaces indentation)
                    term_match = self.RST_TERM_PATTERN.match(lines[i])
                    if term_match:
                        term_line = i
                        term_text = term_match.group(2).strip()

                        # Handle multiple terms (aliases) on separate lines
                        aliases = []
                        i += 1
                        while i < len(lines):
                            # Check for another term at the same indentation
                            next_term = self.RST_TERM_PATTERN.match(lines[i])
                            if next_term and len(next_term.group(1)) == len(
                                term_match.group(1)
                            ):
                                aliases.append(next_term.group(2).strip())
                                i += 1
                            else:
                                break

                        # Extract definition (6+ spaces indentation)
                        definition_lines = []
                        while i < len(lines):
                            if not lines[i].strip():
                                # Empty line might be part of definition
                                if i + 1 < len(lines) and lines[i + 1].startswith(
                                    "      "
                                ):
                                    definition_lines.append("")
                                    i += 1
                                else:
                                    break
                            elif lines[i].startswith(
                                "      "
                            ):  # Definition continuation
                                definition_lines.append(lines[i][6:])
                                i += 1
                            else:
                                break

                        if definition_lines:
                            definition = "\n".join(definition_lines).strip()
                            term = GlossaryTerm(
                                term=term_text,
                                aliases=aliases,
                                definition=definition,
                                source_file=source_file,
                                line_number=term_line + 1,  # 1-based line numbering
                            )
                            terms.append(term)
                            self.terms[term_text] = term
                            for alias in aliases:
                                self.terms[alias] = term
                    else:
                        i += 1
            else:
                i += 1

        return terms

    def extract_from_myst(self, content: str, source_file: Path) -> List[GlossaryTerm]:
        """Extract glossary terms from MyST Markdown content.

        Args:
            content: The MyST content to parse
            source_file: Path to the source file

        Returns:
            List of extracted glossary terms
        """
        terms = []
        lines = content.split("\n")

        i = 0
        while i < len(lines):
            # Look for MyST glossary blocks
            if "```{glossary}" in lines[i]:
                start_line = i
                i += 1

                # Find the end of the glossary block
                glossary_content = []
                while i < len(lines):
                    if "```" == lines[i].strip():
                        break
                    glossary_content.append(lines[i])
                    i += 1

                # Parse glossary content (Markdown definition list style)
                j = 0
                while j < len(glossary_content):
                    line = glossary_content[j]

                    # Term is typically on its own line, not indented
                    if line and not line.startswith(" "):
                        term_text = line.strip()
                        term_line = start_line + j + 1
                        aliases = []

                        # Check for aliases on following lines
                        j += 1
                        while (
                            j < len(glossary_content)
                            and glossary_content[j]
                            and not glossary_content[j].startswith(" ")
                            and not glossary_content[j].startswith(":")
                        ):
                            aliases.append(glossary_content[j].strip())
                            j += 1

                        # Definition follows with indentation (typically `:` prefix)
                        definition_lines = []
                        while j < len(glossary_content):
                            if glossary_content[j].startswith(":"):
                                # Strip the leading ':' and spaces
                                def_text = glossary_content[j][1:].strip()
                                definition_lines.append(def_text)
                                j += 1
                            elif glossary_content[j].startswith("  "):
                                # Continuation of definition
                                definition_lines.append(glossary_content[j].strip())
                                j += 1
                            else:
                                break

                        if definition_lines:
                            definition = " ".join(definition_lines)
                            term = GlossaryTerm(
                                term=term_text,
                                aliases=aliases,
                                definition=definition,
                                source_file=source_file,
                                line_number=term_line,
                            )
                            terms.append(term)
                            self.terms[term_text] = term
                            for alias in aliases:
                                self.terms[alias] = term
                    else:
                        j += 1
            i += 1

        return terms

    def find_term_references(
        self, content: str, file_path: Path, node_id: str = ""
    ) -> List[TermReference]:
        """Find all glossary term references in content.

        Args:
            content: The content to search for references
            file_path: Path to the file being searched
            node_id: Optional node ID for tracking

        Returns:
            List of term references found
        """
        references = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Find RST-style references
            for match in self.RST_TERM_REF.finditer(line):
                term_name = match.group(1)
                ref = TermReference(
                    term=term_name,
                    node_id=node_id or f"{file_path}:{line_num}",
                    file_path=file_path,
                    line_number=line_num,
                    resolved=term_name in self.terms,
                    context=line.strip(),
                )
                references.append(ref)
                self.references.append(ref)

            # Find MyST-style references
            for match in self.MYST_TERM_REF.finditer(line):
                term_name = match.group(1)
                ref = TermReference(
                    term=term_name,
                    node_id=node_id or f"{file_path}:{line_num}",
                    file_path=file_path,
                    line_number=line_num,
                    resolved=term_name in self.terms,
                    context=line.strip(),
                )
                references.append(ref)
                self.references.append(ref)

        return references

    def get_undefined_terms(self) -> Set[str]:
        """Get list of referenced terms that are not defined in glossary.

        Returns:
            Set of undefined term names
        """
        undefined = set()
        for ref in self.references:
            if not ref.resolved:
                undefined.add(ref.term)
        return undefined

    def validate_glossary(
        self,
    ) -> Tuple[List[GlossaryTerm], List[TermReference], Set[str]]:
        """Validate glossary completeness and consistency.

        Returns:
            Tuple of (defined_terms, all_references, undefined_terms)
        """
        defined_terms = list(set(self.terms.values()))  # Unique terms
        undefined = self.get_undefined_terms()
        return defined_terms, self.references, undefined

    def export_glossary_context(self) -> Dict:
        """Export glossary data for JSON output.

        Returns:
            Dictionary containing glossary context
        """
        defined_terms = list(set(self.terms.values()))
        undefined = self.get_undefined_terms()

        return {
            "terms": [
                {
                    "term": term.term,
                    "definition": term.definition,
                    "aliases": term.aliases,
                    "usage_count": sum(
                        1 for ref in self.references if ref.term == term.term
                    ),
                    "source": str(term.source_file),
                    "line": term.line_number,
                    "translations": term.translations,
                }
                for term in defined_terms
            ],
            "undefined_references": list(undefined),
            "total_references": len(self.references),
            "resolved_references": sum(1 for ref in self.references if ref.resolved),
        }
