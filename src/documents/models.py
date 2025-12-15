"""
Database models for document management.
Tracks uploaded and processed documents.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database.connection import Base

class Document(Base):
    """
    Document model for tracking uploaded and processed documents."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)

    # Document conversion tracking
    source_file_type = Column(String, nullable=True)  # Original uploaded type (e.g., "pdf", "docx")
    converted_from = Column(String, nullable=True)  # "pdf" or "docx" if converted, None otherwise

    department = Column(String, nullable=False)  # Department associated with the document

    is_processed = Column(Boolean, default=False)  # Processing status
    chunk_count = Column(Integer, default=0)  # Number of chunks after processing
    top_k = Column(Integer, default=0)  # Top K value for retrieval

    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    description = Column(Text, nullable=True)  # Optional description of the document

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    uploader = relationship("User", backref="documents")

def __repr__(self):
        return f"<Document(filename={self.filename}, department={self.department})>"