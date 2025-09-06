"""Base parser interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from docdiff.models.node import DocumentNode


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, content: str, file_path: Path) -> List[DocumentNode]:
        """Parse document content and return nodes.

        Args:
            content: Document content to parse
            file_path: Path to the source file

        Returns:
            List of DocumentNodes representing the document structure
        """
        pass

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file.

        Args:
            file_path: Path to check

        Returns:
            True if this parser can handle the file
        """
        pass
