"""
Document format converters.
Converts PDF and DOCX files to Markdown format for optimal RAG processing.
"""

import os
from pathlib import Path
from typing import Tuple, Optional
import pymupdf4llm
import markitdown
from src.core.logging_config import get_logger

logger = get_logger("converters")


class DocumentToMarkdownConverter:
    """Converts PDF and DOCX files to Markdown format for better LLM parsing."""

    def __init__(self):
        """Initialize the document converter."""
        logger.info("DocumentToMarkdownConverter initialized")

    def convert_pdf_to_markdown(self, pdf_path: str, output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Convert PDF to Markdown using pymupdf4llm.

        Args:
            pdf_path: Path to input PDF file
            output_path: Path where Markdown file will be saved

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            logger.info(f"Converting PDF to Markdown: {pdf_path}")

            # Convert PDF to Markdown using pymupdf4llm
            md_text = pymupdf4llm.to_markdown(pdf_path)

            # Write markdown to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_text)

            logger.info(f"Successfully converted PDF to Markdown: {output_path}")
            return True, None

        except Exception as e:
            error_msg = f"Failed to convert PDF to Markdown: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def convert_docx_to_markdown(self, docx_path: str, output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Convert DOCX to Markdown using markitdown.

        Args:
            docx_path: Path to input DOCX file
            output_path: Path where Markdown file will be saved

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            logger.info(f"Converting DOCX to Markdown: {docx_path}")

            # Convert DOCX to Markdown using markitdown
            md_text = markitdown.markitdown(docx_path)

            # Write markdown to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_text)

            logger.info(f"Successfully converted DOCX to Markdown: {output_path}")
            return True, None

        except Exception as e:
            error_msg = f"Failed to convert DOCX to Markdown: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def convert_with_fallback(
        self,
        file_path: str,
        file_type: str,
        output_path: str
    ) -> Tuple[bool, Optional[str], str]:
        """
        Convert file to Markdown with fallback to original on failure.

        Args:
            file_path: Path to original file
            file_type: Type of file (pdf or docx)
            output_path: Path where Markdown will be saved

        Returns:
            Tuple of (success: bool, error_message: Optional[str], file_to_use: str)
            - success: Whether conversion was successful
            - error_message: Error message if conversion failed
            - file_to_use: Path to file to use for processing (markdown if successful, original if failed)
        """
        file_type = file_type.lower()

        if file_type == "pdf":
            success, error = self.convert_pdf_to_markdown(file_path, output_path)
        elif file_type == "docx":
            success, error = self.convert_docx_to_markdown(file_path, output_path)
        else:
            error = f"Unsupported file type for conversion: {file_type}"
            logger.warning(error)
            return False, error, file_path

        if success:
            # Validate converted file
            if self._validate_markdown_file(output_path):
                logger.info(f"Conversion successful and validated: {output_path}")
                return True, None, output_path
            else:
                error = "Converted markdown file validation failed (file too small or empty)"
                logger.warning(error)
                # Clean up invalid markdown file
                if os.path.exists(output_path):
                    os.remove(output_path)
                return False, error, file_path
        else:
            logger.warning(f"Conversion failed, falling back to original file: {error}")
            return False, error, file_path

    @staticmethod
    def _validate_markdown_file(md_path: str, min_size: int = 100) -> bool:
        """
        Validate converted markdown file.

        Args:
            md_path: Path to markdown file
            min_size: Minimum file size in bytes

        Returns:
            True if file is valid, False otherwise
        """
        try:
            if not os.path.exists(md_path):
                logger.warning(f"Markdown file does not exist: {md_path}")
                return False

            file_size = os.path.getsize(md_path)
            if file_size < min_size:
                logger.warning(f"Markdown file too small ({file_size} bytes, min {min_size}): {md_path}")
                return False

            # Try to read file to ensure it's valid
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    logger.warning(f"Markdown file is empty: {md_path}")
                    return False

            logger.info(f"Markdown file validated successfully: {md_path} ({file_size} bytes)")
            return True

        except Exception as e:
            logger.error(f"Error validating markdown file {md_path}: {str(e)}")
            return False


# Global converter instance
_converter = None


def get_document_converter() -> DocumentToMarkdownConverter:
    """
    Get the global DocumentToMarkdownConverter instance.

    Returns:
        DocumentToMarkdownConverter instance
    """
    global _converter
    if _converter is None:
        _converter = DocumentToMarkdownConverter()
    return _converter
