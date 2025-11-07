"""
Document API functions for Streamlit frontend.
"""
from typing import Dict, Any, Optional
from streamlit_app.api.client import get_api_client
import io


def upload_document(
    file_bytes: bytes,
    filename: str,
    department: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload a document.
    
    Args:
        file_bytes: File content as bytes
        filename: Name of the file
        department: Department the document belongs to
        description: Optional document description
        
    Returns:
        Upload response with document metadata
    """
    client = get_api_client()
    
    files = {"file": (filename, io.BytesIO(file_bytes))}
    data = {"department": department}
    
    if description:
        data["description"] = description
    
    response = client.post(
        "/documents/upload",
        data=data,
        files=files
    )
    
    return response


def list_documents(skip: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    List all accessible documents.
    
    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        
    Returns:
        List of documents
    """
    client = get_api_client()
    
    response = client.get(
        "/documents/",
        params={"skip": skip, "limit": limit}
    )
    
    return response


def get_document(document_id: int) -> Dict[str, Any]:
    """
    Get details of a specific document.
    
    Args:
        document_id: Document ID
        
    Returns:
        Document details
    """
    client = get_api_client()
    response = client.get(f"/documents/{document_id}")
    return response


def search_documents(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search documents using semantic similarity.
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Returns:
        Search results
    """
    client = get_api_client()
    
    response = client.post(
        "/documents/search",
        data={"query": query, "top_k": top_k}
    )
    
    return response


def delete_document(document_id: int) -> Dict[str, Any]:
    """
    Delete a document.
    
    Args:
        document_id: Document ID
        
    Returns:
        Deletion response
    """
    client = get_api_client()
    response = client.delete(f"/documents/{document_id}")
    return response


def get_collection_stats() -> Dict[str, Any]:
    """
    Get statistics for all collections.
    
    Returns:
        Collection statistics
    """
    client = get_api_client()
    response = client.get("/documents/stats/collections")
    return response