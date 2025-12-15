"""
Configuration settings for the application.
Loads environment variables and provides centralized config.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from typing import Optional, Union
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)  
except ImportError:
    pass  

class Settings(BaseSettings):
    """Application configuration settings."""

    #Application
    APP_NAME: str = "Fintech Chatbot"
    DEBUG: bool = True
    API_VERSION: str = "v1"

    #Database
    DATABASE_URL: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "fintech_database"
    DB_USER: str = "postgres"
    DB_PASSWORD: str

    #JWT Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    #Document processing
    UPLOAD_DIR: str = "data/uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: list[str] = ["pdf", "docx", "csv", "xlsx", "md"]

    # PDF & DOCX to Markdown conversion
    CONVERT_PDF_TO_MARKDOWN: bool = True
    CONVERT_DOCX_TO_MARKDOWN: bool = True

    #Vector Store
    CHROMA_DB_DIR: str = "data/chroma_db"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-base-en-v1.5"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    #LLM Configuration
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "llama-3.1-8b-instant"  
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1024

     # RAG Configuration
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.6
    ENABLE_CONVERSATION_HISTORY: bool = True
    MAX_CONVERSATION_HISTORY: int = 10

    # Query Augmentation Configuration
    ENABLE_QUERY_AUGMENTATION: bool = True
    NUM_QUERY_AUGMENTATIONS: int = 2
    

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables not defined in Settings
    )

settings = Settings()

# Create necessary directories
def create_directories():
    """Create required directories if they don't exist."""
    directories = [
        settings.UPLOAD_DIR,
        settings.CHROMA_DB_DIR
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)



ROLE_PERMISSIONS = {
    "Finance": {
        "departments": ["Finance"],
        "description": "Access to financial reports, expenses, and budgets"
    },
    "Marketing": {
        "departments": ["Marketing"],
        "description": "Access to campaign data, customer feedback, and sales metrics"
    },
    "HR": {
        "departments": ["HR"],
        "description": "Access to employee data, attendance, payroll, and performance"
    },
    "Engineering": {
        "departments": ["Engineering"],
        "description": "Access to technical architecture and development processes"
    },
    "C-Level": {
        "departments": ["Finance", "Marketing", "HR", "Engineering", "General"],
        "description": "Full access to all company data"
    },
    "Employee": {
        "departments": ["General"],
        "description": "Access to general company policies, events, and FAQs"
    }
}

VALID_ROLES = list(ROLE_PERMISSIONS.keys())

# Department to collection mapping
DEPARTMENT_COLLECTIONS = {
    "Finance": "finance",
    "Marketing": "marketing",
    "HR": "hr_dept",
    "Engineering": "engineering",
    "General": "general"
}
