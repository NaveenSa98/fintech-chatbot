"""
Custom document loaders for different file formats.
Specialized loaders that preserve document structure and metadata.
"""

from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from typing import List
from src.core.logging_config import get_logger
import re

logger = get_logger("loaders")


class MarkdownLoader(TextLoader):
    """
    Custom loader for Markdown files that preserves structure.
    Extends TextLoader with Markdown-specific handling.

    Preserves header hierarchy and attaches section metadata to maintain
    semantic meaning during chunking (e.g., "this content is under Finance Data").
    """

    def __init__(self, file_path: str, **kwargs):
        """Initialize MarkdownLoader with normalized file path."""
        # Normalize file path to use forward slashes (cross-platform compatibility)
        normalized_path = file_path.replace("\\", "/")
        super().__init__(normalized_path, **kwargs)

    def load(self) -> List[Document]:
        """
        Load Markdown file and preserve header hierarchy.

        Strategy:
        1. Split by markdown headers (# ## ###) to preserve structure
        2. Attach header hierarchy as metadata to each section
        3. Include parent headers with content for semantic context

        Returns:
            List of Document objects with preserved structure
        """
        logger.info(f"Loading Markdown file: {self.file_path}")

        # Use parent TextLoader to read file
        documents = super().load()

        enhanced_docs = []

        for doc in documents:
            # Split markdown content while preserving header hierarchy
            sections = self._split_by_headers(doc.page_content)

            for section in sections:
                new_doc = Document(
                    page_content=section["content"],
                    metadata={
                        **doc.metadata,
                        "format": "markdown",
                        "loader_type": "MarkdownLoader",
                        "header": section.get("header", ""),
                        "header_level": section.get("header_level", 0),
                        "section_path": section.get("section_path", "")
                    }
                )
                enhanced_docs.append(new_doc)

        logger.info(
            f"Loaded Markdown file with {len(documents)} document(s), "
            f"preserved header structure: {len(enhanced_docs)} sections"
        )
        return enhanced_docs

    def _split_by_headers(self, content: str) -> List[dict]:
        """
        Split markdown content by headers while preserving hierarchy.

        Args:
            content: Raw markdown content

        Returns:
            List of sections with header metadata
        """
        sections = []
        header_stack = []  # Track header hierarchy [H1, H2, H3...]
        current_section = None

        # Split by markdown headers (# ## ###, etc.)
        # Pattern: line starting with one or more # followed by space and text
        lines = content.split("\n")

        for line in lines:
            header_match = re.match(r"^(#+)\s+(.+)$", line)

            if header_match:
                # Found a header
                header_level = len(header_match.group(1))  # Count of # symbols
                header_text = header_match.group(2).strip()

                # Save previous section if exists
                if current_section and current_section["content"].strip():
                    sections.append(current_section)

                # Update header stack (remove headers of same or higher level)
                while header_stack and header_stack[-1][0] >= header_level:
                    header_stack.pop()

                # Add new header to stack
                header_stack.append((header_level, header_text))

                # Create new section
                section_path = " > ".join([h[1] for h in header_stack])
                current_section = {
                    "header": header_text,
                    "header_level": header_level,
                    "section_path": section_path,
                    "content": f"{line}\n"  # Include header in content for context
                }
            else:
                # Regular content line
                if current_section is None:
                    # Content before any header
                    current_section = {
                        "header": "",
                        "header_level": 0,
                        "section_path": "",
                        "content": line + "\n"
                    }
                else:
                    current_section["content"] += line + "\n"

        # Save final section
        if current_section and current_section["content"].strip():
            sections.append(current_section)

        # If no headers found, return entire content as one section
        if not sections:
            sections = [{
                "header": "",
                "header_level": 0,
                "section_path": "",
                "content": content
            }]

        return sections
