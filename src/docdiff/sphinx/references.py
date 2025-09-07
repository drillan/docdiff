"""Cross-reference tracking and management for Sphinx documentation."""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class ReferenceType(Enum):
    """Types of cross-references in Sphinx documentation."""

    REF = "ref"  # Label references
    DOC = "doc"  # Document references
    TERM = "term"  # Glossary term references
    NUMREF = "numref"  # Numbered references
    CITATION = "citation"  # Citation references
    FOOTNOTE = "footnote"  # Footnote references
    DOWNLOAD = "download"  # Download references
    ANY = "any"  # Any type of reference


@dataclass
class Reference:
    """Represents a cross-reference in documentation."""

    ref_type: ReferenceType
    target: str  # Label, document path, or term name
    source_file: Path
    line_number: int
    node_id: str = ""
    display_text: Optional[str] = None  # Custom display text
    resolved: bool = False
    context: str = ""  # Surrounding text for context

    def __hash__(self) -> int:
        """Make Reference hashable for use in sets."""
        return hash(
            (self.ref_type, self.target, str(self.source_file), self.line_number)
        )

    def __eq__(self, other: object) -> bool:
        """Check equality based on type, target, and location."""
        if not isinstance(other, Reference):
            return False
        return (
            self.ref_type == other.ref_type
            and self.target == other.target
            and self.source_file == other.source_file
            and self.line_number == other.line_number
        )


@dataclass
class BrokenReference:
    """Represents a reference that could not be resolved."""

    reference: Reference
    reason: str  # Why the reference couldn't be resolved
    suggestions: List[str] = field(default_factory=list)  # Possible fixes


class ReferenceDatabase:
    """Database for tracking and validating cross-references."""

    # Patterns for reStructuredText references
    RST_REF_PATTERNS = {
        ReferenceType.REF: re.compile(r":ref:`(?:([^<>`]+?)\s*<([^>`]+)>|([^>`]+))`"),
        ReferenceType.DOC: re.compile(r":doc:`(?:([^<>`]+?)\s*<([^>`]+)>|([^>`]+))`"),
        ReferenceType.TERM: re.compile(r":term:`([^`]+)`"),
        ReferenceType.NUMREF: re.compile(
            r":numref:`(?:([^<>`]+?)\s*<([^>`]+)>|([^>`]+))`"
        ),
        ReferenceType.CITATION: re.compile(r":cite:`([^`]+)`"),
        ReferenceType.FOOTNOTE: re.compile(r"\[#([^\]]+)\]_"),
        ReferenceType.DOWNLOAD: re.compile(
            r":download:`(?:([^<>`]+?)\s*<([^>`]+)>|([^>`]+))`"
        ),
        ReferenceType.ANY: re.compile(r":any:`([^`]+)`"),
    }

    # Patterns for MyST references
    MYST_REF_PATTERNS = {
        ReferenceType.REF: re.compile(r"\{ref\}`(?:([^<>`]+?)\s*<([^>`]+)>|([^>`]+))`"),
        ReferenceType.DOC: re.compile(r"\{doc\}`(?:([^<>`]+?)\s*<([^>`]+)>|([^>`]+))`"),
        ReferenceType.TERM: re.compile(r"\{term\}`([^`]+)`"),
        ReferenceType.NUMREF: re.compile(
            r"\{numref\}`(?:([^<>`]+?)\s*<([^>`]+)>|([^>`]+))`"
        ),
        ReferenceType.CITATION: re.compile(r"\{cite\}`([^`]+)`"),
        ReferenceType.DOWNLOAD: re.compile(
            r"\{download\}`(?:([^<>`]+?)\s*<([^>`]+)>|([^>`]+))`"
        ),
        ReferenceType.ANY: re.compile(r"\{any\}`([^`]+)`"),
    }

    # Pattern for reference labels
    RST_LABEL_PATTERN = re.compile(r"^\.\.\s+_([^:]+):\s*$", re.MULTILINE)
    MYST_LABEL_PATTERN = re.compile(r"^\(([^)]+)\)=\s*$", re.MULTILINE)

    # Pattern for figure/table labels in directives
    RST_NAME_PATTERN = re.compile(
        r"^\.\.\s+(figure|table|code-block|literalinclude|math)::\s*.*?\n\s+:name:\s+(\S+)",
        re.MULTILINE | re.DOTALL,
    )
    MYST_NAME_PATTERN = re.compile(
        r"^```\{(figure|table|code-block|literalinclude|math)\}\s+.*?\n:name:\s+(\S+)",
        re.MULTILINE | re.DOTALL,
    )

    def __init__(self) -> None:
        """Initialize the reference database."""
        self.labels: Dict[str, str] = {}  # label -> node_id or file path
        self.references: List[Reference] = []
        self.documents: Set[Path] = set()  # Track known documents

    def add_label(
        self, label: str, node_id: str, file_path: Optional[Path] = None
    ) -> None:
        """Register a referenceable label.

        Args:
            label: The label name
            node_id: Unique identifier for the labeled element
            file_path: Optional file path where label is defined
        """
        self.labels[label] = node_id
        if file_path:
            self.documents.add(file_path)

    def add_reference(self, ref: Reference) -> None:
        """Track a reference usage.

        Args:
            ref: The reference to track
        """
        self.references.append(ref)

        # Try to resolve the reference
        if ref.ref_type == ReferenceType.REF:
            ref.resolved = ref.target in self.labels
        elif ref.ref_type == ReferenceType.DOC:
            # Document references need path resolution
            target_path = Path(ref.target)
            ref.resolved = any(
                doc.name == target_path.name or doc.stem == target_path.stem
                for doc in self.documents
            )

    def extract_labels_from_rst(self, content: str, file_path: Path) -> None:
        """Extract reference labels from reStructuredText content.

        Args:
            content: The RST content to parse
            file_path: Path to the source file
        """
        # Extract standard labels
        for match in self.RST_LABEL_PATTERN.finditer(content):
            label = match.group(1)
            line_num = content[: match.start()].count("\n") + 1
            node_id = f"{file_path}:{line_num}"
            self.add_label(label, node_id, file_path)

        # Extract directive :name: labels
        for match in self.RST_NAME_PATTERN.finditer(content):
            label = match.group(2)
            line_num = content[: match.start()].count("\n") + 1
            node_id = f"{file_path}:{line_num}:{match.group(1)}"
            self.add_label(label, node_id, file_path)

    def extract_labels_from_myst(self, content: str, file_path: Path) -> None:
        """Extract reference labels from MyST Markdown content.

        Args:
            content: The MyST content to parse
            file_path: Path to the source file
        """
        # Extract MyST-style labels
        for match in self.MYST_LABEL_PATTERN.finditer(content):
            label = match.group(1)
            line_num = content[: match.start()].count("\n") + 1
            node_id = f"{file_path}:{line_num}"
            self.add_label(label, node_id, file_path)

        # Extract directive :name: labels
        for match in self.MYST_NAME_PATTERN.finditer(content):
            label = match.group(2)
            line_num = content[: match.start()].count("\n") + 1
            node_id = f"{file_path}:{line_num}:{match.group(1)}"
            self.add_label(label, node_id, file_path)

    def extract_references_from_rst(
        self, content: str, file_path: Path
    ) -> List[Reference]:
        """Extract cross-references from reStructuredText content.

        Args:
            content: The RST content to parse
            file_path: Path to the source file

        Returns:
            List of extracted references
        """
        refs = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for ref_type, pattern in self.RST_REF_PATTERNS.items():
                for match in pattern.finditer(line):
                    # Handle references with custom display text
                    if ref_type in [
                        ReferenceType.REF,
                        ReferenceType.DOC,
                        ReferenceType.NUMREF,
                        ReferenceType.DOWNLOAD,
                    ]:
                        # Pattern has three groups: text<target> or simple target
                        if match.group(2):  # text<target> format
                            display_text = match.group(1)
                            target = match.group(2)
                        else:  # simple format
                            display_text = None
                            target = match.group(3)
                    else:
                        display_text = None
                        target = match.group(1)

                    ref = Reference(
                        ref_type=ref_type,
                        target=target,
                        source_file=file_path,
                        line_number=line_num,
                        node_id=f"{file_path}:{line_num}",
                        display_text=display_text,
                        context=line.strip(),
                    )
                    refs.append(ref)
                    self.add_reference(ref)

        return refs

    def extract_references_from_myst(
        self, content: str, file_path: Path
    ) -> List[Reference]:
        """Extract cross-references from MyST Markdown content.

        Args:
            content: The MyST content to parse
            file_path: Path to the source file

        Returns:
            List of extracted references
        """
        refs = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for ref_type, pattern in self.MYST_REF_PATTERNS.items():
                for match in pattern.finditer(line):
                    # Handle references with custom display text
                    if ref_type in [
                        ReferenceType.REF,
                        ReferenceType.DOC,
                        ReferenceType.NUMREF,
                        ReferenceType.DOWNLOAD,
                    ]:
                        # Pattern has three groups: text<target> or simple target
                        if match.group(2):  # text<target> format
                            display_text = match.group(1)
                            target = match.group(2)
                        else:  # simple format
                            display_text = None
                            target = match.group(3)
                    else:
                        display_text = None
                        target = match.group(1)

                    ref = Reference(
                        ref_type=ref_type,
                        target=target,
                        source_file=file_path,
                        line_number=line_num,
                        node_id=f"{file_path}:{line_num}",
                        display_text=display_text,
                        context=line.strip(),
                    )
                    refs.append(ref)
                    self.add_reference(ref)

        return refs

    def validate(self) -> List[BrokenReference]:
        """Find and report unresolved references.

        Returns:
            List of broken references with diagnostic information
        """
        broken = []

        for ref in self.references:
            if not ref.resolved:
                reason = ""
                suggestions = []

                if ref.ref_type == ReferenceType.REF:
                    reason = f"Label '{ref.target}' not found"
                    # Find similar labels
                    similar = [
                        label
                        for label in self.labels
                        if label.lower().startswith(ref.target.lower()[:3])
                    ]
                    if similar:
                        suggestions = similar[:3]  # Top 3 suggestions

                elif ref.ref_type == ReferenceType.DOC:
                    reason = f"Document '{ref.target}' not found"
                    # Find similar documents
                    target_stem = Path(ref.target).stem
                    similar = [
                        str(doc)
                        for doc in self.documents
                        if target_stem.lower() in doc.stem.lower()
                    ]
                    if similar:
                        suggestions = similar[:3]

                elif ref.ref_type == ReferenceType.TERM:
                    reason = f"Glossary term '{ref.target}' not defined"

                else:
                    reason = f"{ref.ref_type.value} target '{ref.target}' not found"

                broken.append(
                    BrokenReference(
                        reference=ref, reason=reason, suggestions=suggestions
                    )
                )

        return broken

    def get_reference_graph(self) -> Dict[str, List[str]]:
        """Build a graph of references between documents.

        Returns:
            Dictionary mapping source files to list of referenced targets
        """
        graph: Dict[str, List[str]] = {}

        for ref in self.references:
            source = str(ref.source_file)
            if source not in graph:
                graph[source] = []

            if ref.ref_type == ReferenceType.DOC:
                graph[source].append(ref.target)
            elif ref.resolved and ref.ref_type == ReferenceType.REF:
                # Find which document contains the label
                node_id = self.labels.get(ref.target, "")
                if ":" in node_id:
                    target_file = node_id.split(":")[0]
                    if target_file != source:
                        graph[source].append(target_file)

        return graph

    def export_reference_context(self) -> Dict:
        """Export reference data for JSON output.

        Returns:
            Dictionary containing reference context
        """
        broken_refs = self.validate()

        return {
            "labels": {label: node_id for label, node_id in self.labels.items()},
            "cross_references": [
                {
                    "from": ref.node_id,
                    "to": ref.target,
                    "type": ref.ref_type.value,
                    "resolved": ref.resolved,
                    "display_text": ref.display_text,
                    "source": str(ref.source_file),
                    "line": ref.line_number,
                }
                for ref in self.references
            ],
            "broken_references": [
                {
                    "target": br.reference.target,
                    "type": br.reference.ref_type.value,
                    "source": str(br.reference.source_file),
                    "line": br.reference.line_number,
                    "reason": br.reason,
                    "suggestions": br.suggestions,
                }
                for br in broken_refs
            ],
            "statistics": {
                "total_references": len(self.references),
                "resolved_references": sum(
                    1 for ref in self.references if ref.resolved
                ),
                "broken_references": len(broken_refs),
                "total_labels": len(self.labels),
                "documents": len(self.documents),
            },
        }
