"""
Chat API functions for Streamlit frontend.
"""
from typing import Dict, Any, Optional
from streamlit_app.api.client import get_api_client


def send_message(
    message: str,
    conversation_id: Optional[int] = None,
    include_sources: bool = True
) -> Dict[str, Any]:
    """
    Send a message to the chatbot.
    
    Args:
        message: User's message
        conversation_id: Optional conversation ID
        include_sources: Whether to include source documents
        
    Returns:
        Chat response with answer and metadata
    """
    client = get_api_client()
    
    response = client.post(
        "/chat/",
        data={
            "message": message,
            "conversation_id": conversation_id,
            "include_sources": include_sources
        }
    )
    
    return response


def list_conversations(skip: int = 0, limit: int = 50) -> Dict[str, Any]:
    """
    List all user conversations.
    
    Args:
        skip: Number of conversations to skip
        limit: Maximum number to return
        
    Returns:
        List of conversations
    """
    client = get_api_client()
    
    response = client.get(
        "/chat/conversations",
        params={"skip": skip, "limit": limit}
    )
    
    return response


def get_conversation(conversation_id: int) -> Dict[str, Any]:
    """
    Get a conversation with all messages.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Conversation with messages
    """
    client = get_api_client()
    response = client.get(f"/chat/conversations/{conversation_id}")
    return response


def delete_conversation(conversation_id: int) -> Dict[str, Any]:
    """
    Delete a conversation.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Deletion response
    """
    client = get_api_client()
    response = client.delete(f"/chat/conversations/{conversation_id}")
    return response


def update_conversation_title(conversation_id: int, title: str) -> Dict[str, Any]:
    """
    Update conversation title.
    
    Args:
        conversation_id: Conversation ID
        title: New title
        
    Returns:
        Updated conversation
    """
    client = get_api_client()
    response = client.patch(
        f"/chat/conversations/{conversation_id}/title",
        data={"title": title}
    )
    return response


def check_chat_health() -> Dict[str, Any]:
    """
    Check if chat system is operational.
    
    Returns:
        Health check response
    """
    client = get_api_client()
    response = client.get("/chat/health")
    return response