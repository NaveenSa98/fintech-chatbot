"""
Formatting utilities for responses and data presentation.
Best practices: Clean, reusable formatting functions.
"""
from typing import List, Dict, Any
import json


def format_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format source documents for response.
    Cleans and structures source information.
    
    Args:
        sources: Raw source documents from retriever
        
    Returns:
        Formatted source documents
    """
    formatted_sources = []
    
    for source in sources:
        formatted_source = {
            "content": source.get("content", "")[:500],  # Limit to 500 chars
            "document_name": source.get("metadata", {}).get("filename", "Unknown"),
            "department": source.get("metadata", {}).get("department", "Unknown"),
            "relevance_score": round(1 - source.get("score", 1.0), 3),  # Convert distance to similarity
            "page_number": source.get("metadata", {}).get("page", None)
        }
        formatted_sources.append(formatted_source)
    
    return formatted_sources

def format_conversation_title(first_message: str, max_length: int = 50) -> str:
    """
    Generate a conversation title from the first message.
    
    Args:
        first_message: First user message
        max_length: Maximum title length
        
    Returns:
        Formatted conversation title
    """
    # Clean the message
    title = first_message.strip()
    
    # Truncate if too long
    if len(title) > max_length:
        title = title[:max_length - 3] + "..."
    
    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:]
    
    return title 

def format_chat_history(messages: List[Dict[str, Any]]) -> str:
    """
    Format chat history for inclusion in prompts.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Formatted chat history string
    """
    history_lines = []
    
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("message", "")
        
        if role == "user":
            history_lines.append(f"User: {content}")
        elif role == "assistant":
            history_lines.append(f"Assistant: {content}")
    
    return "\n".join(history_lines)

def format_context(retrieved_docs: List[Dict[str, Any]]) -> str:
    """
    Format retrieved documents into context string for LLM.
    
    Args:
        retrieved_docs: Retrieved document chunks
        
    Returns:
        Formatted context string
    """
    context_parts = []
    
    for i, doc in enumerate(retrieved_docs, 1):
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        source = metadata.get("filename", "Unknown")
        dept = metadata.get("department", "Unknown")
        
        context_parts.append(
            f"[Source {i} - {source} from {dept} department]\n{content}"
        )
    
    return "\n\n".join(context_parts)

def clean_response(response: str) -> str:
    """
    Clean and format LLM response.
    Removes unnecessary whitespace and formatting artifacts.
    
    Args:
        response: Raw LLM response
        
    Returns:
        Cleaned response
    """
    # Remove extra whitespace
    response = " ".join(response.split())
    
    # Remove common artifacts
    artifacts_to_remove = [
        "Answer:",
        "Response:",
        "AI:",
        "Assistant:"
    ]
    
    for artifact in artifacts_to_remove:
        if response.startswith(artifact):
            response = response[len(artifact):].strip()
    
    return response

def calculate_confidence(sources: List[Dict[str, Any]]) -> float:
    """
    Calculate confidence score based on source relevance.
    
    Args:
        sources: Retrieved source documents with scores
        
    Returns:
        Confidence score (0-1)
    """
    if not sources:
        return 0.0
    
    # Use average of top sources (converted from distance to similarity)
    scores = [1 - source.get("score", 1.0) for source in sources]
    avg_score = sum(scores) / len(scores)
    
    # Normalize to 0-1 range
    confidence = max(0.0, min(1.0, avg_score))
    
    return round(confidence, 3)