"""
API routes for authentication endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.auth.schemas import (
    UserLogin, UserCreate, UserResponse,
    LoginResponse, RoleInfo, MessageResponse
)
from src.auth.service import AuthService
from src.auth.utils import get_current_active_user
from src.auth.models import User
from src.core.config import ROLE_PERMISSIONS
from src.core.exceptions import ResourceNotFoundError
from src.core.logging_config import get_logger

logger = get_logger("auth")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    Args:
        user_data: User creation data
        db: Database session

    Returns:
        Created User object
    """
    logger.info(f"Registration request for email: {user_data.email}")
    user = AuthService.create_user(db, user_data)
    return user

@router.post("/login", response_model=LoginResponse)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.

    Args:
        login_data: User login data
        db: Database session
    Returns:
        Access token and token type
    """
    logger.info(f"Login request for email: {login_data.email}")
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)

    access_token = AuthService.generate_token(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)

async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.
    
    Args:
        current_user: Current authenticated user (injected dependency)
        
    Returns:
        User object
    """
    return current_user


@router.get("/roles", response_model=list[RoleInfo])

async def get_all_roles():
    """
    Get list of all available roles and their permissions.
    Public endpoint - no authentication required.
    """
    roles = []
    for role, info in ROLE_PERMISSIONS.items():
        roles.append({
            "role": role,
            "departments": info["departments"],
            "description": info["description"]
        })
    return roles

@router.get("/role/{role_name}", response_model=RoleInfo)
async def get_role_info(role_name: str):
    """
    Get information about a specific role.
    Public endpoint - no authentication required.

    - **role_name**: Name of the role to get info about
    """
    if role_name not in ROLE_PERMISSIONS:
        logger.warning(f"Request for non-existent role: {role_name}")
        raise ResourceNotFoundError(f"Role '{role_name}' not found")

    info = ROLE_PERMISSIONS[role_name]
    return {
        "role": role_name,
        "departments": info["departments"],
        "description": info["description"]
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout current user.

    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token. This endpoint confirms the action.
    """
    logger.info(f"User logged out: {current_user.email}")
    return {
        "message": "Successfully logged out",
        "detail": f"User {current_user.email} has been logged out"
    }
