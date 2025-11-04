"""
Document processing logic.
Extracts text from various file formats and chunks them for vector storage.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredExcelLoader,
    CSVLoader,
)
from langchain.schema import Document
from src.documents.helper_functions import replace_t_with_space
from typing import List,Dict, Any
from pathlib import Path
from src.core.config import settings
from src.core.logging_config import get_logger
import os

logger = get_logger("documents")


class DocumentProcessor:
    """Processes documents by extract and chunking text."""

    def __init__(self):
        """ Initialize the document processor"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = settings.CHUNK_SIZE,
            chunk_overlap = settings.CHUNK_OVERLAP,
            length_function = len,
            separators = ["", "", " ", "", ".", ",", ";", ":", "!", "?"]
        )
        logger.info("DocumentProcessor initialized")

    def load_document(self, file_path: str, file_type: str) -> List[Document]:
            """
            Load document based on file type.
            
            Args:
                file_path: Path to the document
                file_type: Type of file (pdf, docx, txt, xlsx)
                
            Returns:
                List of LangChain Document objects
            """
            file_type = file_type.lower()
            
            try:
                if file_type == "pdf":
                    loader = PyPDFLoader(file_path)
                elif file_type == "csv":
                    loader = CSVLoader(file_path)
                elif file_type == "xlsx":
                    loader = UnstructuredExcelLoader(file_path, mode="elements")
                else:
                    raise ValueError(f"Unsupported file type: {file_type}")
                
                documents = loader.load()
                logger.info(f"Loaded {len(documents)} page(s) from {file_type} file: {file_path}")
                
                return documents
                
            except Exception as e:
                logger.error(f"Error loading {file_type} file {file_path}: {str(e)}")
                raise

    def chunk_documents(
            self,
            documents: List[Document],
            metadata: Dict[str, Any] = None
            ) -> List[Document]:
            """ Split documents into chunks."""

            chunks = self.text_splitter.split_documents(documents)
      

            cleaned_texts = replace_t_with_space(chunks)

            if metadata:
                for chunk in cleaned_texts:
                    chunk.metadata.update(metadata)
            
            logger.info(f"Created {len(cleaned_texts)} chunks from {len(documents)} document(s)")

            return cleaned_texts
    
    def process_file(
        self,
        file_path: str,
        file_type: str,
        metadata: Dict[str, Any]
    ) -> List[Document]:
        """
        Complete document processing pipeline.
        
        Args:
            file_path: Path to the document
            file_type: Type of file
            metadata: Metadata to attach to chunks
            
        Returns:
            List of processed document chunks
        """
        logger.info(f"Processing file: {file_path}")
        
        # Load document
        documents = self.load_document(file_path, file_type)
        
        # Chunk documents
        chunks = self.chunk_documents(documents, metadata)
        
        logger.info(f"Processing complete: {len(chunks)} chunks ready for {file_path}")
        
        return chunks
    
    def validate_file(self, filename: str, file_size: int) -> tuple[bool, str]:
        """
        Validate file before processing.
        
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


        
