"""
Database models for chat history and conversations.
Tracks user queries and AI responses for context maintenance.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database.connection import Base


class Conversation(Base):
    """
    Conversation model for tracking chat sessions.
    Groups related messages together.
    """
    __tablename__ = "conversations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User who owns this conversation
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Conversation metadata
    title = Column(String, nullable=True)  # Auto-generated or user-provided
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"


class ChatMessage(Base):
    """
    Chat message model for storing individual messages.
    Tracks both user queries and AI responses.
    """
    __tablename__ = "chat_messages"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    
    # RAG metadata (for assistant messages)
    sources_used = Column(Text, nullable=True)  # JSON string of source documents
    confidence_score = Column(Float, nullable=True)  # Relevance confidence
    tokens_used = Column(Integer, nullable=True)  # For tracking usage
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role})>"