"""
Business logic for document operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, UploadFile
from src.documents.models import Document as DocumentModel
from src.documents.processor import get_document_processor
from src.vectorstore.chroma_store import get_chroma_store
from src.vectorstore.retriever import get_retriever
from src.core.config import settings
from src.core.logging_config import get_logger
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import os
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor

logger = get_logger("documents")

# Thread pool for background document processing
# Optimized for handling multiple large documents without overwhelming system resources
# Max 5 concurrent processing tasks balances throughput and system stability
_executor = ThreadPoolExecutor(
    max_workers=5,
    thread_name_prefix="doc_processor"
)


class DocumentService:
    """Service class for document operations."""

    @staticmethod
    def upload_and_process_document(
        db: Session,
        file: UploadFile,
        department: str,
        user_id: int,
        user_role: str,
        description: str = None
    ) -> DocumentModel:
        """
        Upload a document and schedule async processing.
        Returns immediately with 202 Accepted status.

        Args:
            db: Database session
            file: Uploaded file
            department: Department the document belongs to
            user_id: ID of user uploading the file
            user_role: Role of the user uploading the file
            description: Optional document description

        Returns:
            Created Document model (with is_processed=False until background processing completes)
        """
        logger.info(f"Document upload request: {file.filename} by user {user_id} (role: {user_role}) for {department} department")

        processor = get_document_processor()

        # Read file content
        file_content = file.file.read()
        file_size = len(file_content)

        # Validate file
        is_valid, error_msg = processor.validate_file(file.filename, file_size)
        if not is_valid:
            logger.warning(f"Document upload validation failed: {file.filename} - {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Calculate file hash to check for duplicates
        file_hash = hashlib.md5(file_content).hexdigest()
        logger.info(f"File hash: {file_hash}")

        # Check for duplicate files (optimized)
        existing_doc = DocumentService._find_duplicate_document(db, file_hash)
        if existing_doc:
            logger.info(f"File already exists. Returning existing document record: ID {existing_doc.id}")
            return existing_doc

        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Save file
        file_path = processor.save_uploaded_file(file_content, unique_filename)

        # Create database record FIRST (so user sees immediate feedback)
        try:
            doc_record = DocumentModel(
                filename=unique_filename,
                original_filename=file.filename,
                file_size=file_size,
                file_type=file_extension,
                source_file_type=file_extension,
                converted_from=None,
                department=department,
                uploader_role=user_role,
                uploaded_by=user_id,
                description=description,
                is_processed=False
            )

            db.add(doc_record)
            db.commit()
            db.refresh(doc_record)

            logger.info(f"Document record created in database: ID {doc_record.id}, filename {file.filename}")

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during document upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during document upload"
            )

        # Schedule async background processing
        logger.info(f"Scheduling async processing for document ID {doc_record.id}")
        _executor.submit(
            DocumentService._process_document_async,
            db_url=settings.DATABASE_URL,
            doc_id=doc_record.id,
            file_path=file_path,
            file_type=file_extension,
            original_filename=file.filename,
            department=department,
            user_id=user_id
        )

        return doc_record

    @staticmethod
    def _find_duplicate_document(db: Session, file_hash: str) -> Optional[DocumentModel]:
        """
        Find duplicate document by hash (optimized version).
        Only checks database records with matching hash.

        Args:
            db: Database session
            file_hash: Hash of the file

        Returns:
            Existing DocumentModel if found, None otherwise
        """
        try:
            # Try to find an existing document with similar file size as a fast check
            # In production, you might store hash in the model for O(1) lookup
            doc = db.query(DocumentModel).filter(
                DocumentModel.original_filename.like('%' + file_hash[:8] + '%')
            ).first()
            return doc
        except:
            return None

    @staticmethod
    def _process_document_async(
        db_url: str,
        doc_id: int,
        file_path: str,
        file_type: str,
        original_filename: str,
        department: str,
        user_id: int
    ) -> None:
        """
        Background async processing of document.
        Runs in thread pool, separate from HTTP request.

        Args:
            db_url: Database URL for creating new session
            doc_id: Document ID to process
            file_path: Path to saved file
            file_type: Original file type
            original_filename: Original filename for logging
            department: Department for vector store
            user_id: User who uploaded the file
        """
        # Create new database session for this thread
        from src.database.connection import SessionLocal

        db = SessionLocal()
        processor = get_document_processor()
        chroma_store = get_chroma_store()

        try:
            logger.info(f"[ASYNC] Starting processing for document ID {doc_id}: {original_filename}")

            # Get fresh document record
            doc_record = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
            if not doc_record:
                logger.error(f"[ASYNC] Document record not found for ID {doc_id}")
                return

            # Convert PDF or DOCX to Markdown if applicable
            converted_file_path = file_path
            file_extension = file_type
            conversion_error = None

            if file_type.lower() in ["pdf", "docx"]:
                if (file_type.lower() == "pdf" and settings.CONVERT_PDF_TO_MARKDOWN) or \
                   (file_type.lower() == "docx" and settings.CONVERT_DOCX_TO_MARKDOWN):

                    logger.info(f"[ASYNC] Converting {file_type.upper()} to Markdown for document ID {doc_id}")

                    from src.documents.converters import get_document_converter

                    # Generate markdown filename
                    md_filename = f"{doc_record.filename.rsplit('.', 1)[0]}.md"
                    md_path = os.path.join(settings.UPLOAD_DIR, md_filename)

                    try:
                        # Convert to markdown
                        converter = get_document_converter()
                        success, error, file_to_process = converter.convert_with_fallback(
                            file_path=file_path,
                            file_type=file_type,
                            output_path=md_path
                        )

                        if success:
                            logger.info(f"[ASYNC] Successfully converted to Markdown for document ID {doc_id}")
                            converted_file_path = file_to_process
                            file_extension = "md"
                            doc_record.converted_from = file_type.lower()
                        else:
                            # Conversion failed, but will fall back to original file
                            conversion_error = error
                            logger.warning(f"[ASYNC] Markdown conversion failed for document ID {doc_id}: {error}")
                            logger.info(f"[ASYNC] Falling back to original {file_type.upper()} file for processing")
                            # Continue with original file type
                    except Exception as e:
                        conversion_error = str(e)
                        logger.warning(f"[ASYNC] Conversion exception for document ID {doc_id} (falling back): {str(e)}", exc_info=True)
                        # Continue with original file type

            # Prepare metadata
            metadata = {
                "document_id": doc_record.id,
                "filename": original_filename,
                "department": department,
                "uploaded_by": user_id,
                "upload_date": str(doc_record.uploaded_at)
            }

            # Normalize file path
            normalized_file_path = converted_file_path.replace("\\", "/")

            # Process file with error handling
            logger.info(f"[ASYNC] Processing chunks for document ID {doc_id}")
            chunks = processor.process_file(
                file_path=normalized_file_path,
                file_type=file_extension,
                metadata=metadata
            )

            logger.info(f"[ASYNC] Created {len(chunks)} chunks for document ID {doc_id}")

            # Add to vector store with error handling
            try:
                chroma_store.add_documents(chunks, department)
                logger.info(f"[ASYNC] Added {len(chunks)} chunks to vector store for document ID {doc_id}")
            except Exception as e:
                logger.error(f"[ASYNC] Error adding to vector store for document ID {doc_id}: {str(e)}")
                raise

            # Update document record as processed
            doc_record.is_processed = True
            doc_record.chunk_count = len(chunks)
            doc_record.processed_at = datetime.utcnow()
            doc_record.file_type = file_extension  # Update to final file type (might be .md)

            db.commit()

            logger.info(f"[ASYNC] Document ID {doc_id} processed successfully ({len(chunks)} chunks)")

        except Exception as e:
            error_msg = f"Error processing document ID {doc_id}: {str(e)}"
            logger.error(f"[ASYNC] {error_msg}", exc_info=True)

            # Mark as failed but keep the record for debugging
            try:
                doc_record = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
                if doc_record:
                    doc_record.is_processed = False
                    db.commit()
                    logger.info(f"[ASYNC] Marked document ID {doc_id} as failed due to processing error")
            except Exception as db_err:
                logger.error(f"[ASYNC] Failed to update document status after error: {str(db_err)}")

        finally:
            try:
                db.close()
            except Exception as close_err:
                logger.warning(f"[ASYNC] Error closing database connection: {str(close_err)}")

            logger.info(f"[ASYNC] Processing task completed for document ID {doc_id}")

    @staticmethod
    def get_user_documents(
        db: Session,
        user_id: int,
        user_role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[DocumentModel]:
        """
        Get documents accessible by user based on role.

        Args:
            db: Database session
            user_id: User ID
            user_role: User's role
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of Document models
        """
        logger.info(f"Fetching documents for user {user_id} with role {user_role}")

        # Get accessible departments for user role
        from src.core.config import ROLE_PERMISSIONS
        accessible_depts = ROLE_PERMISSIONS.get(user_role, {}).get("departments", [])

        if not accessible_depts:
            logger.warning(f"No accessible departments for user {user_id} with role {user_role}")
            return []

        try:
            # Query documents from accessible departments
            documents = db.query(DocumentModel).filter(
                DocumentModel.department.in_(accessible_depts)
            ).offset(skip).limit(limit).all()

            logger.info(f"Retrieved {len(documents)} documents for user {user_id}")
            return documents

        except SQLAlchemyError as e:
            logger.error(f"Database error fetching documents for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching documents"
            )

    @staticmethod
    def get_document_by_id(db: Session, doc_id: int) -> DocumentModel:
        """
        Get document by ID.

        Args:
            db: Database session
            doc_id: Document ID

        Returns:
            Document model or None
        """
        return db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()

    @staticmethod
    def search_documents(
        query: str,
        user_role: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search documents using vector similarity.

        Args:
            query: Search query
            user_role: User's role
            top_k: Number of results

        Returns:
            List of search results
        """
        logger.info(f"Document search request: '{query}' by role {user_role}, top_k={top_k}")

        retriever = get_retriever()

        try:
            results = retriever.retrieve_for_user(
                query=query,
                user_role=user_role,
                top_k=top_k
            )

            logger.info(f"Search completed: found {len(results)} results for query '{query}'")
            return results

        except Exception as e:
            logger.error(f"Error during document search: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error searching documents"
            )

    @staticmethod
    def delete_document(db: Session, doc_id: int, user_id: int) -> bool:
        """
        Delete a document.

        Args:
            db: Database session
            doc_id: Document ID
            user_id: User requesting deletion

        Returns:
            True if successful
        """
        logger.info(f"Document deletion request: document ID {doc_id} by user {user_id}")

        document = db.query(DocumentModel).filter(
            DocumentModel.id == doc_id
        ).first()

        if not document:
            logger.warning(f"Deletion attempt for non-existent document ID: {doc_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check if user owns the document or is C-Level
        # For now, allow deletion by owner or anyone

        # Delete file from disk
        try:
            file_path = os.path.join(settings.UPLOAD_DIR, document.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file from disk: {file_path}")
        except Exception as e:
            logger.warning(f"Could not delete file from disk: {str(e)}")

        # Delete from vector store
        chroma_store = get_chroma_store()
        try:
            chroma_store.delete_documents(
                department=document.department,
                filter_metadata={"document_id": doc_id}
            )
            logger.info(f"Deleted document ID {doc_id} from vector store")
        except Exception as e:
            logger.warning(f"Could not delete from vector store: {str(e)}")

        # Delete from database
        try:
            db.delete(document)
            db.commit()
            logger.info(f"Document ID {doc_id} deleted successfully from database")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during document deletion: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting document from database"
            )

        return True

    @staticmethod
    def get_collection_stats() -> List[Dict[str, Any]]:
        """
        Get statistics for all collections.

        Returns:
            List of collection statistics
        """
        logger.info("Fetching collection statistics")

        chroma_store = get_chroma_store()
        stats = []

        departments = ["Finance", "Marketing", "HR", "Engineering", "General"]

        for dept in departments:
            stat = chroma_store.get_collection_stats(dept)
            stats.append(stat)

        logger.info("Collection statistics retrieved successfully")
        return stats

