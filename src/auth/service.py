"""
Business logic for authentication operations.
This layer handles the actual operations between API and database.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.auth.models import User
from src.auth.schemas import UserCreate, UserUpdate
from src.core.security import hash_password, verify_password, create_access_token
from src.auth.utils import validate_role
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    ResourceNotFoundError,
    DatabaseError
)
from src.core.logging_config import get_logger
from datetime import timedelta
from src.core.config import settings

logger = get_logger("auth")


class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """
        Authenticate a user with email and password.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            User object if authentication successful

        Raises:
            AuthenticationError: If credentials are invalid
            AuthorizationError: If user account is inactive
            DatabaseError: If database operation fails
        """
        try:
            # Find user by email
            user = db.query(User).filter(User.email == email).first()

            if not user:
                logger.warning(f"Login attempt with non-existent email: {email}")
                raise AuthenticationError("Incorrect email or password")

            # Verify password
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Failed login attempt for user: {email}")
                raise AuthenticationError("Incorrect email or password")

            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt by inactive user: {email}")
                raise AuthorizationError("User account is inactive")

            logger.info(f"User logged in successfully: {email}")
            return user

        except (AuthenticationError, AuthorizationError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error during authentication: {str(e)}")
            raise DatabaseError("Authentication failed due to system error")
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            raise DatabaseError("Authentication failed")
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user in the database.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created User object

        Raises:
            ValidationError: If email already exists or role is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                logger.warning(f"Registration attempt with existing email: {user_data.email}")
                raise ValidationError("Email already registered")

            # Validate role
            if not validate_role(user_data.role):
                logger.warning(f"Registration attempt with invalid role: {user_data.role}")
                raise ValidationError(
                    f"Invalid role. Must be one of: {', '.join(['Finance', 'Marketing', 'HR', 'Engineering', 'C-Level', 'Employee'])}"
                )

            # Create new user
            new_user = User(
                email=user_data.email,
                hashed_password=hash_password(user_data.password),
                full_name=user_data.full_name,
                role=user_data.role,
                department=user_data.department,
                is_active=True,
                is_verified=True
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            logger.info(f"New user registered successfully: {user_data.email}")
            return new_user

        except ValidationError:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during user creation: {str(e)}")
            raise DatabaseError("User registration failed due to system error")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error during user creation: {str(e)}")
            raise DatabaseError("User registration failed")
    
    @staticmethod
    def generate_token(user: User) -> str:
        """
        Generate JWT access token for user.

        Args:
            user: User object

        Returns:
            JWT token string

        Raises:
            DatabaseError: If token generation fails
        """
        try:
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

            # Data to encode in token
            token_data = {
                "sub": user.email,
                "role": user.role,
                "department": user.department
            }

            access_token = create_access_token(
                data=token_data,
                expires_delta=access_token_expires
            )

            logger.info(f"Token generated for user: {user.email}")
            return access_token

        except Exception as e:
            logger.error(f"Error generating token for user {user.email}: {str(e)}")
            raise DatabaseError("Token generation failed")
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """
        Get user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """
        Update user information.

        Args:
            db: Database session
            user_id: User ID
            user_data: Updated user data

        Returns:
            Updated User object

        Raises:
            ResourceNotFoundError: If user not found
            ValidationError: If role is invalid
            DatabaseError: If database operation fails
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                logger.warning(f"Update attempt for non-existent user ID: {user_id}")
                raise ResourceNotFoundError("User not found")

            # Update fields if provided
            if user_data.full_name is not None:
                user.full_name = user_data.full_name

            if user_data.role is not None:
                if not validate_role(user_data.role):
                    logger.warning(f"Update attempt with invalid role for user {user_id}")
                    raise ValidationError("Invalid role")
                user.role = user_data.role

            if user_data.department is not None:
                user.department = user_data.department

            if user_data.is_active is not None:
                user.is_active = user_data.is_active

            db.commit()
            db.refresh(user)

            logger.info(f"User updated successfully: {user.email}")
            return user

        except (ResourceNotFoundError, ValidationError):
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during user update: {str(e)}")
            raise DatabaseError("User update failed due to system error")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error during user update: {str(e)}")
            raise DatabaseError("User update failed")