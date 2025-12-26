"""
Utility functions for authentication.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.core.security import decode_access_token
from src.auth.models import User
from src.core.config import VALID_ROLES


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def validate_role(role: str) -> bool:
    """
    Validate if a role is valid.
    
    Args:
        role: Role string to validate
        
    Returns:
        True if valid, False otherwise
    """
    return role in VALID_ROLES


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    This is used as a dependency in protected routes.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object if token is valid
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    Note: User is already verified to be active by get_current_user() dependency.
    This is a convenience wrapper for route protection.

    Args:
        current_user: User from get_current_user dependency (already verified active)

    Returns:
        Authenticated, active User object
    """
    return current_user


def check_role_permission(user: User, required_role: str) -> bool:
    """
    Check if user has the required role.
    
    Args:
        user: User object
        required_role: Required role string
        
    Returns:
        True if user has required role or is C-Level
    """
    # C-Level has access to everything
    if user.role == "C-Level":
        return True
    
    # Check if user has the specific required role
    return user.role == required_role