"""
API routes for document management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from src.database.connection import get_db
from src.auth.utils import get_current_active_user
from src.auth.models import User
from src.documents.schemas import (
    DocumentResponse,
    DocumentListResponse,
    DocumentSearch,
    SearchResponse,
    DocumentChunk,
    MessageResponse
)
from src.documents.service import DocumentService
from src.core.logging_config import get_logger

logger = get_logger("documents")

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form(...),
    description: str = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document.

    - **file**: Document file (PDF, DOCX, TXT, XLSX, CSV)
    - **department**: Department this document belongs to (Finance, Marketing, HR, Engineering, General)
    - **description**: Optional document description

    The document will be automatically processed and indexed in the vector database.
    """
    logger.info(f"Upload document request: {file.filename} by user {current_user.email} for {department}")

    # Validate department access
    from src.core.config import ROLE_PERMISSIONS
    accessible_depts = ROLE_PERMISSIONS.get(current_user.role, {}).get("departments", [])

    if department not in accessible_depts and current_user.role != "C-Level":
        logger.warning(f"Access denied: user {current_user.email} attempted to upload to {department}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have access to upload documents to {department} department"
        )

    document = DocumentService.upload_and_process_document(
        db=db,
        file=file,
        department=department,
        user_id=current_user.id,
        description=description
    )

    return document

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List documents accessible to the current user based on their role.

    - **skip**: Number of documents to skip (pagination)
    - **limit**: Maximum number of documents to return
    """
    logger.info(f"List documents request by user {current_user.email}")

    documents = DocumentService.get_user_documents(
        db=db,
        user_id=current_user.id,
        user_role=current_user.role,
        skip=skip,
        limit=limit
    )

    return {
        "total": len(documents),
        "documents": documents
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific document.

    - **document_id**: ID of the document
    """
    logger.info(f"Get document request: document ID {document_id} by user {current_user.email}")

    document = DocumentService.get_document_by_id(db, document_id)

    if not document:
        logger.warning(f"Document not found: ID {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check if user has access to this department
    from src.core.config import ROLE_PERMISSIONS
    accessible_depts = ROLE_PERMISSIONS.get(current_user.role, {}).get("departments", [])

    if document.department not in accessible_depts and current_user.role != "C-Level":
        logger.warning(f"Access denied: user {current_user.email} attempted to access document {document_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this document"
        )

    return document


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    search_request: DocumentSearch,
    current_user: User = Depends(get_current_active_user)
):
    """
    Search documents using semantic similarity.
    Returns relevant document chunks based on the query.

    - **query**: Search query text
    - **top_k**: Number of results to return (1-20)
    """
    logger.info(f"Search request: '{search_request.query}' by user {current_user.email}")

    results = DocumentService.search_documents(
        query=search_request.query,
        user_role=current_user.role,
        top_k=search_request.top_k
    )

    # Format results
    formatted_results = [
        DocumentChunk(
            content=result["content"],
            metadata=result["metadata"],
            score=result["score"]
        )
        for result in results
    ]

    return {
        "query": search_request.query,
        "results": formatted_results,
        "total_results": len(formatted_results)
    }


@router.delete("/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document.
    Removes the document from database, disk, and vector store.

    - **document_id**: ID of the document to delete
    """
    logger.info(f"Delete document request: document ID {document_id} by user {current_user.email}")

    success = DocumentService.delete_document(
        db=db,
        doc_id=document_id,
        user_id=current_user.id
    )

    if success:
        return {
            "message": "Document deleted successfully",
            "detail": f"Document {document_id} has been removed"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.get("/stats/collections", response_model=List[dict])
async def get_collection_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get statistics for all vector store collections.
    Shows document counts per department.

    Only C-Level users can see all collection stats.
    """
    logger.info(f"Collection statistics request by user {current_user.email}")

    if current_user.role != "C-Level":
        logger.warning(f"Access denied: user {current_user.email} attempted to view collection stats")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only C-Level users can view collection statistics"
        )

    stats = DocumentService.get_collection_stats()
    return stats
