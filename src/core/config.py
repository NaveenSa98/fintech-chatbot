"""
Configuration settings for the application.
Loads environment variables and provides centralized config.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

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
    PROCESSED_DIR: str = "data/processed"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: list[str] = ["pdf", "docx", "csv", "xlsx"]

    #Vector Store
    CHROMA_DB_DIR: str = "data/chroma_db"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-mpnet-base-v2"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # OpenAI (Optional)
    OPENAI_API_KEY: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }

settings = Settings()

# Create necessary directories
def create_directories():
    """Create required directories if they don't exist."""
    directories = [
        settings.UPLOAD_DIR,
        settings.PROCESSED_DIR,
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
    "HR": "hr",
    "Engineering": "engineering",
    "General": "general"
}
