"""
API routes for chat endpoints.
Best practices: Clear documentation, proper status codes, comprehensive examples.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database.connection import get_db
from src.auth.utils import get_current_active_user
from src.auth.models import User
from src.chat.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    ConversationListResponse,
    ChatHealthCheck,
    MessageResponse
)
from src.chat.service import ChatService
from src.chat.llm_manager import get_llm_manager
from src.vectorstore.chroma_store import get_chroma_store
from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger("chat")


# Create router
router = APIRouter(
    prefix="/chat",
    tags=["Chat & RAG"]
)

@router.post("/", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the chatbot and get an AI-generated response.

    The chatbot uses RAG (Retrieval-Augmented Generation) to:
    1. Search relevant documents based on your role
    2. Generate contextual responses using retrieved information
    3. Cite sources in the response

    - **message**: Your question or message (max 2000 chars)
    - **conversation_id**: Optional - continue an existing conversation
    - **include_sources**: Whether to include source documents (default: true)

    Example:
    ```json
    {
      "message": "What was our Q4 revenue?",
      "conversation_id": null,
      "include_sources": true
    }
    ```
    """
    logger.info(f"Chat message request from user {current_user.email}: '{request.message[:50]}...'")

    response = ChatService.send_message(
        db=db,
        user_id=current_user.id,
        user_role=current_user.role,
        message=request.message,
        conversation_id=request.conversation_id,
        include_sources=request.include_sources
    )

    return response


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.

    Conversations group related messages together and maintain context.
    If you don't create one manually, it's auto-created with your first message.

    - **title**: Optional conversation title
    """
    logger.info(f"Create conversation request from user {current_user.email}")

    from src.chat.models import Conversation

    conv = Conversation(
        user_id=current_user.id,
        title=conversation.title or "New Conversation"
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    logger.info(f"Created conversation {conv.id}: '{conv.title}'")

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        user_id=conv.user_id,
        message_count=0,
        created_at=conv.created_at,
        updated_at=conv.updated_at
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all your conversations.

    Returns conversations ordered by most recently updated.

    - **skip**: Number of conversations to skip (pagination)
    - **limit**: Maximum number of conversations to return
    """
    logger.info(f"List conversations request from user {current_user.email}")

    conversations = ChatService.get_user_conversations(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    # Format response with message counts
    conv_responses = []
    for conv in conversations:
        conv_responses.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            user_id=conv.user_id,
            message_count=len(conv.messages),
            created_at=conv.created_at,
            updated_at=conv.updated_at
        ))

    logger.info(f"Returning {len(conv_responses)} conversations for user {current_user.email}")

    return {
        "total": len(conv_responses),
        "conversations": conv_responses
    }


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation with full message history.

    Returns all messages in chronological order.

    - **conversation_id**: ID of the conversation
    """
    logger.info(f"Get conversation {conversation_id} request from user {current_user.email}")

    conversation = ChatService.get_conversation_with_messages(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id
    )

    return conversation


@router.delete("/conversations/{conversation_id}", response_model=MessageResponse)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a conversation and all its messages.

    This action cannot be undone.

    - **conversation_id**: ID of the conversation to delete
    """
    logger.info(f"Delete conversation {conversation_id} request from user {current_user.email}")

    success = ChatService.delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id
    )

    if success:
        return {
            "message": "Conversation deleted successfully",
            "detail": f"Conversation {conversation_id} and all its messages have been removed"
        }


@router.patch("/conversations/{conversation_id}/title", response_model=ConversationResponse)
async def update_conversation_title(
    conversation_id: int,
    title: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update conversation title.

    - **conversation_id**: ID of the conversation
    - **title**: New title (max 200 characters)
    """
    logger.info(f"Update conversation {conversation_id} title request from user {current_user.email}")

    conversation = ChatService.update_conversation_title(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        new_title=title
    )

    logger.info(f"Updated conversation {conversation_id} title to: '{title}'")

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        user_id=conversation.user_id,
        message_count=len(conversation.messages),
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.get("/health", response_model=ChatHealthCheck)
async def chat_health_check(current_user: User = Depends(get_current_active_user)):
    """
    Check if chat system is operational.

    Verifies:
    - LLM is initialized and accessible
    - Vector store is available
    - Returns current model information
    """
    logger.info(f"Health check request from user {current_user.email}")

    try:
        # Check LLM
        llm_manager = get_llm_manager()
        llm_info = llm_manager.get_model_info()
        llm_available = True
        logger.info("LLM is available and healthy")
    except Exception as e:
        llm_available = False
        llm_info = {"error": str(e)}
        logger.error(f"LLM health check failed: {str(e)}")

    try:
        # Check vector store
        chroma = get_chroma_store()
        vector_available = True
        logger.info("Vector store is available and healthy")
    except Exception as e:
        vector_available = False
        logger.error(f"Vector store health check failed: {str(e)}")

    health_status = "healthy" if (llm_available and vector_available) else "degraded"
    logger.info(f"Chat system health: {health_status}")

    return {
        "status": health_status,
        "llm_available": llm_available,
        "vector_store_available": vector_available,
        "llm_model": llm_info.get("llm_model", "Unknown")
    }
