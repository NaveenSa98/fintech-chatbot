"""
Pydantic schemas for chat endpoints.
Clean request/response models following best practices.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Request Schemas
# ============================================================================

class ChatRequest(BaseModel):
    """
    Schema for chat query request.
    User sends a message to the chatbot.
    """
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=2000,
        description="User's question or message"
    )
    conversation_id: Optional[int] = Field(
        None,
        description="ID of existing conversation (for context)"
    )
    include_sources: bool = Field(
        True,
        description="Whether to include source documents in response"
    )


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    title: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional conversation title"
    )


# ============================================================================
# Response Schemas
# ============================================================================

class SourceDocument(BaseModel):
    """Schema for source document information."""
    content: str = Field(..., description="Document chunk content")
    document_name: str = Field(..., description="Source document filename")
    department: str = Field(..., description="Department the document belongs to")
    relevance_score: float = Field(..., description="Similarity score (0-1)")
    page_number: Optional[int] = Field(None, description="Page number if available")


class ChatResponse(BaseModel):
    """
    Schema for chatbot response.
    Contains the AI-generated answer with metadata.
    """
    message: str = Field(..., description="AI-generated response")
    conversation_id: int = Field(..., description="Conversation this message belongs to")
    message_id: int = Field(..., description="Unique message ID")
    sources: Optional[List[SourceDocument]] = Field(
        None,
        description="Source documents used to generate response"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score of the response (0-1)"
    )
    tokens_used: Optional[int] = Field(
        None,
        description="Number of tokens used in generation"
    )
    timestamp: datetime = Field(..., description="Response timestamp")


class MessageHistory(BaseModel):
    """Schema for a single message in history."""
    id: int
    role: str  # 'user' or 'assistant'
    message: str
    created_at: datetime
    sources: Optional[List[SourceDocument]] = None
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Schema for conversation details."""
    id: int
    title: Optional[str]
    user_id: int
    message_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConversationWithMessages(BaseModel):
    """Schema for conversation with full message history."""
    id: int
    title: Optional[str]
    user_id: int
    created_at: datetime
    messages: List[MessageHistory]


class ConversationListResponse(BaseModel):
    """Schema for list of conversations."""
    total: int
    conversations: List[ConversationResponse]


# ============================================================================
# Utility Schemas
# ============================================================================

class ChatHealthCheck(BaseModel):
    """Schema for chat system health check."""
    status: str
    llm_available: bool
    vector_store_available: bool
    llm_model: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None