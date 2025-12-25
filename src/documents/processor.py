"""
Document processing logic.
Extracts text from various file formats and chunks them for vector storage.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    UnstructuredExcelLoader,
    CSVLoader,
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.schema import Document
from src.documents.loaders import MarkdownLoader
from typing import List, Dict, Any
from src.core.config import settings
from src.core.logging_config import get_logger
import os

logger = get_logger("documents")


class DocumentProcessor:
    """Processes documents by extracting and chunking text using recursive strategy."""

    def __init__(self):
        """Initialize the document processor with recursive text splitting."""
        # Hierarchical separators for recursive chunking
        # Markdown files: split by headers first to preserve structure
        # Then paragraph breaks, sentences, words, characters
        # This prevents splitting headers from their content
        separators = [
            "\n## ",     # Markdown H2 header (preserve structure)
            "\n### ",    # Markdown H3 header (preserve structure)
            "\n\n",      # Paragraph breaks
            "\n",        # Line breaks
            ". ",        # Sentences
            " ",         # Words
            ""           # Characters (last resort)
        ]

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=separators,
            length_function=len
        )
        logger.info(
            "DocumentProcessor initialized with recursive chunking "
            "(includes markdown-aware separators for header preservation)"
        )

    def load_document(self, file_path: str, file_type: str) -> List[Document]:
        """
        Load document based on file type.

        Args:
            file_path: Path to the document
            file_type: Type of file (md, csv, xlsx, pdf, docx)

        Returns:
            List of LangChain Document objects
        """
        file_type = file_type.lower()

        # Normalize file path to use forward slashes (cross-platform compatibility)
        # This prevents issues on Windows where os.path.join uses backslashes
        file_path = file_path.replace("\\", "/")

        try:
            # Select appropriate loader based on file type
            if file_type in ["md", "markdown"]:
                loader = MarkdownLoader(file_path)
            elif file_type == "csv":
                loader = CSVLoader(file_path)
            elif file_type == "xlsx":
                loader = UnstructuredExcelLoader(file_path, mode="elements")
            elif file_type == "pdf":
                logger.info(f"Using PyPDFLoader for PDF file (fallback from markdown conversion)")
                loader = PyPDFLoader(file_path)
            elif file_type == "docx":
                logger.info(f"Using UnstructuredWordDocumentLoader for DOCX file (fallback from markdown conversion)")
                loader = UnstructuredWordDocumentLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}. Supported types: md, csv, xlsx, pdf, docx")

            # Load documents
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} document(s) from {file_type} file: {file_path}")

            return documents

        except Exception as e:
            logger.error(f"Error loading {file_type} file {file_path}: {str(e)}")
            raise

    def chunk_documents(
        self,
        documents: List[Document],
        metadata: Dict[str, Any] = None
    ) -> List[Document]:
        """
        Split documents into chunks using recursive text splitting.

        Args:
            documents: List of Document objects to chunk
            metadata: Optional metadata to attach to all chunks

        Returns:
            List of chunked Document objects
        """
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)

        # Attach metadata to chunks if provided
        if metadata:
            for chunk in chunks:
                chunk.metadata.update(metadata)

        logger.info(f"Created {len(chunks)} chunks from {len(documents)} document(s)")
        return chunks
    
    def process_file(
        self,
        file_path: str,
        file_type: str,
        metadata: Dict[str, Any]
    ) -> List[Document]:
        """
        Complete document processing pipeline: load → chunk → attach metadata.

        Args:
            file_path: Path to the document
            file_type: Type of file (md, csv, xlsx)
            metadata: Metadata to attach to chunks

        Returns:
            List of processed document chunks
        """
        logger.info(f"Processing file: {file_path}")

        # Load document from disk
        documents = self.load_document(file_path, file_type)

        # Chunk documents using recursive text splitting
        chunks = self.chunk_documents(documents, metadata)

        logger.info(f"Processing complete: {len(chunks)} chunks ready for {file_path}")

        return chunks
    
    def validate_file(self, filename: str, file_size: int) -> tuple[bool, str]:
        """
        Validate file type and size before processing.

        Args:
            filename: Name of the file
            file_size: Size of file in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        file_extension = filename.split('.')[-1].lower()
        allowed_extensions = settings.ALLOWED_FILE_TYPES

        if file_extension not in allowed_extensions:
            logger.warning(f"File validation failed: {filename} - unsupported file type")
            return False, f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"

        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            logger.warning(f"File validation failed: {filename} - file too large ({file_size} bytes)")
            return False, f"File too large. Maximum size: {max_size_mb}MB"

        logger.info(f"File validation passed: {filename}")
        return True, ""
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to disk.

        Args:
            file_content: File content bytes
            filename: Name for the file

        Returns:
            Path where file was saved
        """
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        logger.info(f"File saved: {file_path}")

        return file_path


# Global processor instance
_processor = None


def get_document_processor() -> DocumentProcessor:
    """
    Get the global DocumentProcessor instance.

    Returns:
        DocumentProcessor instance
    """
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor
