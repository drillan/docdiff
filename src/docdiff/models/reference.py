"""Reference model for tracking cross-references in documents."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReferenceType(str, Enum):
    """Types of references in documents."""

    REF = "ref"  # {ref}`label`
    DOC = "doc"  # {doc}`document`
    TERM = "term"  # {term}`glossary-term`
    NUMREF = "numref"  # {numref}`figure-label`


class Reference(BaseModel):
    """Represents a cross-reference in a document."""

    model_config = ConfigDict(
        use_enum_values=False,
        json_schema_extra={
            "example": {
                "id": "ref-123",
                "from_node_id": "node-456",
                "to_label": "target-label",
                "to_node_id": "node-789",
                "reference_type": "ref",
                "line_number": 42,
                "file_path": "/path/to/doc.md",
            }
        },
    )

    id: str = Field(..., description="Unique identifier for the reference")
    from_node_id: str = Field(
        ..., description="ID of the node containing the reference"
    )
    to_label: str = Field(..., description="Target label being referenced")
    to_node_id: Optional[str] = Field(
        None, description="ID of the target node (when resolved)"
    )
    reference_type: ReferenceType = Field(..., description="Type of reference")
    line_number: int = Field(..., description="Line number of the reference")
    file_path: Optional[str] = Field(
        None, description="File path containing the reference"
    )

    @property
    def is_resolved(self) -> bool:
        """Check if the reference has been resolved to a target node.

        Returns:
            True if to_node_id is set
        """
        return self.to_node_id is not None
