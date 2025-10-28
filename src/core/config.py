"""
Configuration settings for the application.
Loads environment variables and provides centralized config.
"""

from pydantic_settings import BaseSettings
from typing import Optional

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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }

settings = Settings()

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

