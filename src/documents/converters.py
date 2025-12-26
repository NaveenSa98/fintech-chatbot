"""
Document format converters.
Converts PDF and DOCX files to Markdown format for optimal RAG processing.
Includes timeout management, streaming for large files, and comprehensive error handling.
"""

import os
from pathlib import Path
from typing import Tuple, Optional
import pymupdf4llm
import markitdown
from src.core.logging_config import get_logger
import signal
from functools import wraps

logger = get_logger("converters")

# Timeout handler for long-running conversions
class TimeoutError(Exception):
    """Raised when document conversion exceeds time limit."""
    pass

def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutError("Document conversion exceeded time limit (30 seconds)")

def with_timeout(seconds=30):
    """Decorator to add timeout to functions (Unix/Linux only, skipped on Windows)."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip timeout on Windows (signal.SIGALRM not available)
            if os.name != 'nt':
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                if os.name != 'nt':
                    signal.alarm(0)  # Cancel alarm
            return result
        return wrapper
    return decorator


class DocumentToMarkdownConverter:
    """Converts PDF and DOCX files to Markdown format for better LLM parsing."""

    def __init__(self):
        """Initialize the document converter."""
        logger.info("DocumentToMarkdownConverter initialized")

    @with_timeout(seconds=60)  # 60 second timeout for large PDFs
    def convert_pdf_to_markdown(self, pdf_path: str, output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Convert PDF to Markdown using pymupdf4llm with timeout protection.

        For large PDFs (40+ pages), conversion may take time. This method
        includes timeout handling to prevent indefinite blocking.

        Args:
            pdf_path: Path to input PDF file
            output_path: Path where Markdown file will be saved

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            logger.info(f"Converting PDF to Markdown: {pdf_path}")

            # Validate input file exists and is readable
            if not os.path.exists(pdf_path):
                error_msg = f"PDF file not found: {pdf_path}"
                logger.error(error_msg)
                return False, error_msg

            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            logger.info(f"PDF file size: {file_size_mb:.2f} MB")

            # Convert PDF to Markdown using pymupdf4llm
            # This is the main processing step that may take time on large PDFs
            md_text = pymupdf4llm.to_markdown(pdf_path)

            # Validate converted content
            if not md_text or not md_text.strip():
                error_msg = "PDF conversion produced empty content. The PDF may be corrupted or image-only."
                logger.warning(error_msg)
                return False, error_msg

            # Clean up content - remove excessive whitespace while preserving structure
            # This helps with PDFs that have complex formatting
            md_text = self._clean_markdown_content(md_text)

            # Validate after cleaning
            if not md_text or not md_text.strip():
                error_msg = "PDF conversion resulted in empty content after cleaning"
                logger.warning(error_msg)
                return False, error_msg

            # Write markdown to file with proper error handling
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_text)
                    f.flush()  # Ensure data is written to disk
            except IOError as io_err:
                error_msg = f"Failed to write markdown file: {str(io_err)}"
                logger.error(error_msg)
                return False, error_msg

            # Validate written file
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                error_msg = "Written markdown file is empty"
                logger.error(error_msg)
                return False, error_msg

            logger.info(f"Successfully converted PDF to Markdown: {output_path} ({file_size} bytes)")
            return True, None

        except TimeoutError as te:
            error_msg = f"PDF conversion timeout for large file: {str(te)} - Consider uploading smaller PDFs or splitting this document"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to convert PDF to Markdown: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    @with_timeout(seconds=60)  # 60 second timeout for large DOCX files
    def convert_docx_to_markdown(self, docx_path: str, output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Convert DOCX to Markdown using markitdown with comprehensive validation.

        Args:
            docx_path: Path to input DOCX file
            output_path: Path where Markdown file will be saved

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            logger.info(f"Converting DOCX to Markdown: {docx_path}")

            # Validate input file exists
            if not os.path.exists(docx_path):
                error_msg = f"DOCX file not found: {docx_path}"
                logger.error(error_msg)
                return False, error_msg

            # Convert DOCX to Markdown using markitdown
            md_text = markitdown.markitdown(docx_path)

            # Validate converted content
            if not md_text or not md_text.strip():
                error_msg = "DOCX conversion produced empty content. The document may be corrupted or empty."
                logger.warning(error_msg)
                return False, error_msg

            # Clean up content
            md_text = self._clean_markdown_content(md_text)

            # Validate after cleaning
            if not md_text or not md_text.strip():
                error_msg = "DOCX conversion resulted in empty content after cleaning"
                logger.warning(error_msg)
                return False, error_msg

            # Write markdown to file with error handling
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_text)
                    f.flush()  # Ensure data is written to disk
            except IOError as io_err:
                error_msg = f"Failed to write markdown file: {str(io_err)}"
                logger.error(error_msg)
                return False, error_msg

            # Validate written file
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                error_msg = "Written markdown file is empty"
                logger.error(error_msg)
                return False, error_msg

            logger.info(f"Successfully converted DOCX to Markdown: {output_path} ({file_size} bytes)")
            return True, None

        except TimeoutError as te:
            error_msg = f"DOCX conversion timeout: {str(te)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to convert DOCX to Markdown: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def convert_with_fallback(
        self,
        file_path: str,
        file_type: str,
        output_path: str
    ) -> Tuple[bool, Optional[str], str]:
        """
        Convert file to Markdown with fallback to original on failure.

        This method handles conversion failures gracefully by:
        1. Attempting conversion with proper validation
        2. Falling back to original file if conversion fails
        3. Cleaning up any partial/invalid converted files

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
        logger.info(f"Starting conversion with fallback: {file_path} ({file_type})")

        if file_type == "pdf":
            success, error = self.convert_pdf_to_markdown(file_path, output_path)
        elif file_type == "docx":
            success, error = self.convert_docx_to_markdown(file_path, output_path)
        else:
            error = f"Unsupported file type for conversion: {file_type}"
            logger.warning(error)
            return False, error, file_path

        if success:
            # Validate converted file before using it
            if self._validate_markdown_file(output_path):
                logger.info(f"Conversion successful and validated: {output_path}")
                return True, None, output_path
            else:
                error_msg = "Converted markdown file validation failed (file too small or empty)"
                logger.warning(error_msg)
                # Clean up invalid markdown file to avoid using corrupted data
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                        logger.info(f"Cleaned up invalid markdown file: {output_path}")
                except Exception as cleanup_err:
                    logger.warning(f"Failed to clean up markdown file {output_path}: {str(cleanup_err)}")
                return False, error_msg, file_path
        else:
            # Conversion failed - clean up any partial markdown file
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
                    logger.info(f"Cleaned up partial markdown file after conversion failure: {output_path}")
            except Exception as cleanup_err:
                logger.warning(f"Failed to clean up markdown file {output_path}: {str(cleanup_err)}")

            logger.warning(f"Conversion failed, falling back to original file: {error}")
            return False, error, file_path

    @staticmethod
    def _clean_markdown_content(md_text: str) -> str:
        """
        Clean up markdown content for better processing.

        Args:
            md_text: Raw markdown text from converter

        Returns:
            Cleaned markdown text
        """
        try:
            lines = md_text.split('\n')
            cleaned_lines = []
            empty_count = 0

            for line in lines:
                stripped = line.strip()

                # Skip excessive blank lines (max 2 consecutive blanks)
                if not stripped:
                    empty_count += 1
                    if empty_count <= 2:
                        cleaned_lines.append(line)
                else:
                    empty_count = 0
                    cleaned_lines.append(line)

            # Remove trailing blank lines
            while cleaned_lines and not cleaned_lines[-1].strip():
                cleaned_lines.pop()

            return '\n'.join(cleaned_lines)
        except Exception as e:
            logger.warning(f"Error cleaning markdown content: {str(e)}, returning original")
            return md_text

    @staticmethod
    def _validate_markdown_file(md_path: str, min_size: int = 50) -> bool:
        """
        Validate converted markdown file.

        Args:
            md_path: Path to markdown file
            min_size: Minimum file size in bytes (50 bytes is reasonable for minimal content)

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

            # Try to read file to ensure it's valid UTF-8
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content or not content.strip():
                        logger.warning(f"Markdown file is empty or contains only whitespace: {md_path}")
                        return False
            except UnicodeDecodeError as ue:
                logger.error(f"Markdown file has encoding issues: {md_path} - {str(ue)}")
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
