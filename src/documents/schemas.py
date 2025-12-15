"""
Pydantic schemas for document endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentUpload(BaseModel):
    """Schema for document upload metadata."""
    department: str = Field(..., description="Department this document belongs to")
    description: Optional[str] = Field(None, description="Document description")

class DocumentSearch(BaseModel):
    """Schema for document search requests."""
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")



class DocumentResponse(BaseModel):
    """Schema for document information in responses."""
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    department: str
    is_processed: bool
    chunk_count: int
    uploaded_by: int
    description: Optional[str]
    uploaded_at: datetime
    processed_at: Optional[datetime]
    source_file_type: Optional[str]
    converted_from: Optional[str]
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    """Schema for list of documents in responses."""
    total: int
    documents: list[DocumentResponse]

class DocumentChunk(BaseModel):
    """Schema for a document chunk."""
    content: str
    metadata: dict
    score: Optional[float] = None

class SearchResponse(BaseModel):
    """Schema for search response."""
    query: str
    results: list[DocumentChunk]
    total_results: int

class ProcessingStatus(BaseModel):
    """Schema for document processing status."""
    document_id: int
    filename: str
    is_processed: bool
    chunk_count: int
    message: str

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None
