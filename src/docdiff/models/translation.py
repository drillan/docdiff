"""Translation unit model for managing translation states."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TranslationStatus(str, Enum):
    """Status of a translation unit."""

    PENDING = "pending"
    TRANSLATED = "translated"
    REVIEWED = "reviewed"
    OUTDATED = "outdated"


class TranslationUnit(BaseModel):
    """Represents a translation unit linking source and target content."""

    model_config = ConfigDict(
        use_enum_values=False,
        json_schema_extra={
            "example": {
                "id": "trans-123",
                "source_node_id": "node-123",
                "source_content": "Example content",
                "target_content": "翻訳例",
                "source_lang": "en",
                "target_lang": "ja",
                "status": "translated",
            }
        },
    )

    id: str = Field(..., description="Unique identifier for the translation unit")
    source_node_id: str = Field(..., description="ID of the source document node")
    source_content: str = Field(..., description="Source content to be translated")
    target_content: Optional[str] = Field(None, description="Translated content")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    status: TranslationStatus = Field(
        TranslationStatus.PENDING, description="Translation status"
    )
    source_hash: Optional[str] = Field(
        None, description="Hash of source content when translated"
    )
    translated_hash: Optional[str] = Field(
        None, description="Hash of content that was translated"
    )
    translated_at: Optional[datetime] = Field(
        None, description="Timestamp of translation"
    )
    reviewed_at: Optional[datetime] = Field(None, description="Timestamp of review")

    @property
    def is_outdated(self) -> bool:
        """Check if translation is outdated based on content hashes.

        Returns:
            True if source_hash differs from translated_hash
        """
        if self.source_hash and self.translated_hash:
            return self.source_hash != self.translated_hash
        return False


class TranslationPair(BaseModel):
    """Represents a translation relationship between nodes."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_node_id": "node-en-123",
                "target_node_id": "node-ja-456",
                "source_language": "en",
                "target_language": "ja",
                "status": "translated",
                "similarity_score": 0.95,
            }
        }
    )

    source_node_id: str = Field(description="ID of the source language node")
    target_node_id: Optional[str] = Field(
        None, description="ID of the target language node (None if not yet translated)"
    )
    source_language: str = Field(
        default="en", description="Source language code (ISO 639-1)"
    )
    target_language: str = Field(description="Target language code (ISO 639-1)")
    status: TranslationStatus = Field(
        default=TranslationStatus.PENDING, description="Current translation status"
    )
    similarity_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Structural similarity score between source and target",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When this translation pair was created",
    )
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
