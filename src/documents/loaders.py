"""
Custom document loaders for different file formats.
Specialized loaders that preserve document structure and metadata.
"""

from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from typing import List
from src.core.logging_config import get_logger

logger = get_logger("loaders")


class MarkdownLoader(TextLoader):
    """
    Custom loader for Markdown files that preserves structure.
    Extends TextLoader with Markdown-specific handling.
    """

    def load(self) -> List[Document]:
        """
        Load Markdown file and return as Document objects.

        Returns:
            List of Document objects
        """
        logger.info(f"Loading Markdown file: {self.file_path}")

        # Use parent TextLoader to read file
        documents = super().load()

        # Add markdown-specific metadata
        for doc in documents:
            doc.metadata["format"] = "markdown"
            doc.metadata["loader_type"] = "MarkdownLoader"

        logger.info(f"Loaded Markdown file with {len(documents)} document(s)")
        return documents
