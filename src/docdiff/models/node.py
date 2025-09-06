"""Document node model representing a structural element in a document."""

import hashlib
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NodeType(str, Enum):
    """Types of document nodes."""

    SECTION = "section"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    MATH_BLOCK = "math_block"
    TABLE = "table"
    FIGURE = "figure"
    ADMONITION = "admonition"
    LIST = "list"
    LIST_ITEM = "list_item"


class DocumentNode(BaseModel):
    """Represents a structural element in a document."""

    model_config = ConfigDict(
        use_enum_values=False,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "node-123",
                "type": "section",
                "content": "# Example Section",
                "level": 1,
                "file_path": "/path/to/doc.md",
                "line_number": 10,
                "content_hash": "abc123...",
            }
        },
    )

    id: str = Field(..., description="Unique identifier for the node")
    type: NodeType = Field(..., description="Type of the document node")
    content: str = Field(..., description="Raw content of the node")
    level: Optional[int] = Field(None, description="Section hierarchy level")
    title: Optional[str] = Field(None, description="Section title")
    label: Optional[str] = Field(None, description="Reference label")
    name: Optional[str] = Field(None, description=":name: attribute")
    caption: Optional[str] = Field(None, description=":caption: attribute")
    language: Optional[str] = Field(None, description="Code block language")
    parent_id: Optional[str] = Field(None, description="Parent node ID")
    children_ids: List[str] = Field(default_factory=list, description="Child node IDs")
    file_path: Path = Field(..., description="Source file path")
    line_number: int = Field(..., description="Line number in source file")
    content_hash: str = Field(..., description="SHA256 hash of content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    # New fields for multi-language support
    doc_language: str = Field(
        default="en", description="Language code of the document (ISO 639-1)"
    )
    source_file_hash: Optional[str] = Field(
        None, description="Hash of the entire source file for change detection"
    )
    last_modified: Optional[datetime] = Field(
        None, description="Last modification timestamp of the source file"
    )

    @classmethod
    def create_with_hash(
        cls,
        id: str,
        type: NodeType,
        content: str,
        file_path: Path,
        line_number: int,
        **kwargs: Any,
    ) -> "DocumentNode":
        """Create a DocumentNode with auto-generated content hash.

        Args:
            id: Unique identifier
            type: Node type
            content: Node content
            file_path: Source file path
            line_number: Line number
            **kwargs: Additional fields

        Returns:
            DocumentNode with generated content_hash
        """
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        return cls(
            id=id,
            type=type,
            content=content,
            file_path=file_path,
            line_number=line_number,
            content_hash=content_hash,
            **kwargs,
        )
