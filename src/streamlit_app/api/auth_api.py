"""
Authentication API functions for Streamlit frontend.
"""
from typing import Dict, Any
from streamlit_app.api.client import get_api_client


def login(email: str, password: str) -> Dict[str, Any]:
    """
    Login user and get authentication token.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Login response with token and user data
    """
    client = get_api_client()
    
    response = client.post(
        "/auth/login",
        data={"email": email, "password": password},
        include_auth=False
    )
    
    return response


def register(
    email: str,
    password: str,
    full_name: str,
    role: str,
    department: str
) -> Dict[str, Any]:
    """
    Register a new user.
    
    Args:
        email: User email
        password: User password
        full_name: User's full name
        role: User's role
        department: User's department
        
    Returns:
        Registration response
    """
    client = get_api_client()
    
    response = client.post(
        "/auth/register",
        data={
            "email": email,
            "password": password,
            "full_name": full_name,
            "role": role,
            "department": department
        },
        include_auth=False
    )
    
    return response


def get_current_user() -> Dict[str, Any]:
    """
    Get current logged-in user information.
    
    Returns:
        User data
    """
    client = get_api_client()
    response = client.get("/auth/me")
    return response


def get_all_roles() -> Dict[str, Any]:
    """
    Get all available roles and their permissions.
    
    Returns:
        List of roles
    """
    client = get_api_client()
    response = client.get("/auth/roles")
    return response