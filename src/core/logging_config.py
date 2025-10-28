"""
Simple logging configuration for the application.
Provides both file and console logging with proper formatting.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log file name with date
LOG_FILE = LOGS_DIR / f"fintech_chatbot_{datetime.now().strftime('%Y%m%d')}.log"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging():
    """Configure logging for the application."""

    # Root logger configuration
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            # File handler - logs everything to file
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            # Console handler - logs to console
            logging.StreamHandler()
        ]
    )

    # Create specific loggers
    auth_logger = logging.getLogger("auth")
    auth_logger.setLevel(logging.INFO)

    db_logger = logging.getLogger("database")
    db_logger.setLevel(logging.INFO)

    return logging.getLogger(__name__)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance by name."""
    return logging.getLogger(name)
