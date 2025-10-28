"""
Database models for authentication and user management.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from src.database.connection import Base

class User(Base):
    """
    User model representing users in the system.
    Each user has a role that determines their access permissions.
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User credentials
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # User information
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Finance, Marketing, HR, etc. (need to put dropdown for frontend)
    department = Column(String, nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(email={self.email}, role={self.role})>"
