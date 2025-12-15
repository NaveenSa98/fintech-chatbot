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
from typing import List, Dict, Any
from datetime import datetime
import uuid
import os
import hashlib

logger = get_logger("documents")


class DocumentService:
    """Service class for document operations."""

    @staticmethod
    def upload_and_process_document(
        db: Session,
        file: UploadFile,
        department: str,
        user_id: int,
        description: str = None
    ) -> DocumentModel:
        """
        Upload and process a document.

        Args:
            db: Database session
            file: Uploaded file
            department: Department the document belongs to
            user_id: ID of user uploading the file
            description: Optional document description

        Returns:
            Created Document model
        """
        logger.info(f"Document upload request: {file.filename} by user {user_id} for {department} department")

        processor = get_document_processor()
        chroma_store = get_chroma_store()

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

        # Check if file already exists in uploads folder
        if os.path.exists(settings.UPLOAD_DIR):
            for existing_file in os.listdir(settings.UPLOAD_DIR):
                existing_path = os.path.join(settings.UPLOAD_DIR, existing_file)
                if os.path.isfile(existing_path):
                    with open(existing_path, 'rb') as f:
                        existing_hash = hashlib.md5(f.read()).hexdigest()

                    if existing_hash == file_hash:
                        logger.info(f"Duplicate file detected: {file.filename} matches existing file {existing_file}")

                        # Try to find existing document record
                        existing_doc = db.query(DocumentModel).filter(
                            DocumentModel.filename == existing_file
                        ).first()

                        if existing_doc:
                            logger.info(f"File already exists. Returning existing document record: ID {existing_doc.id}")
                            return existing_doc
                        else:
                            logger.warning(f"File exists in uploads folder but no database record found. Will create new record.")
                            # Remove the orphaned file and continue with upload
                            os.remove(existing_path)
                            break

        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Save file
        file_path = processor.save_uploaded_file(file_content, unique_filename)

        # Convert PDF or DOCX to Markdown if applicable
        converted_file_path = file_path
        source_file_type = file_extension
        converted_from = None

        if file_extension.lower() in ["pdf", "docx"]:
            from src.documents.converters import get_document_converter


            if (file_extension.lower() == "pdf" and settings.CONVERT_PDF_TO_MARKDOWN) or \
               (file_extension.lower() == "docx" and settings.CONVERT_DOCX_TO_MARKDOWN):

                logger.info(f"{file_extension.upper()} detected, converting to Markdown: {file.filename}")

                # Generate markdown filename
                md_filename = f"{unique_filename.rsplit('.', 1)[0]}.md"
                md_path = os.path.join(settings.UPLOAD_DIR, md_filename)

                # Convert to markdown
                converter = get_document_converter()
                success, error, file_to_process = converter.convert_with_fallback(
                    file_path=file_path,
                    file_type=file_extension,
                    output_path=md_path
                )

                if success:
                    logger.info(f"Successfully converted {file_extension.upper()} to Markdown: {md_filename}")
                    converted_file_path = file_to_process
                    file_extension = "md"  # Update to markdown for processing
                    converted_from = source_file_type
                else:
                    logger.warning(f"{file_extension.upper()} conversion failed, using original file: {error}")
                    # Continue with original file

        # Create database record
        try:
            doc_record = DocumentModel(
                filename=unique_filename,
                original_filename=file.filename,
                file_size=file_size,
                file_type=file_extension,
                source_file_type=source_file_type,
                converted_from=converted_from,
                department=department,
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

        # Process document asynchronously (in real app, use background task)
        try:
            # Prepare metadata
            metadata = {
                "document_id": doc_record.id,
                "filename": file.filename,
                "department": department,
                "uploaded_by": user_id,
                "upload_date": str(doc_record.uploaded_at)
            }

            # Process file (use converted file path if available)
            chunks = processor.process_file(
                file_path=converted_file_path,
                file_type=file_extension,
                metadata=metadata
            )

            # Add to vector store
            chroma_store.add_documents(chunks, department)

            # Update document record
            doc_record.is_processed = True
            doc_record.chunk_count = len(chunks)
            doc_record.processed_at = datetime.utcnow()

            db.commit()
            db.refresh(doc_record)

            logger.info(f"Document processed and indexed successfully: {file.filename} ({len(chunks)} chunks)")

        except Exception as e:
            logger.error(f"Error processing document {file.filename}: {str(e)}")
            doc_record.is_processed = False
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing document: {str(e)}"
            )

        return doc_record

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

