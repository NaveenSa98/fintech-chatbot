"""
Input validation utilities for chat system.
Best practices: Validate early, fail fast with clear messages.
"""
from typing import Tuple
import re


def validate_message_length(message: str, max_length: int = 2000) -> Tuple[bool, str]:
    """
    Validate message length.
    
    Args:
        message: User message
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message or not message.strip():
        return False, "Message cannot be empty"
    
    if len(message) > max_length:
        return False, f"Message too long. Maximum {max_length} characters allowed"
    
    return True, ""


def validate_message_content(message: str) -> Tuple[bool, str]:
    """
    Validate message content for malicious input.
    
    Args:
        message: User message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for SQL injection patterns (basic)
    sql_patterns = [
        r"(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b).*\bTABLE\b",
        r";\s*(DROP|DELETE|INSERT|UPDATE)",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return False, "Invalid characters or patterns detected"
    
    # Check for excessive special characters
    special_char_ratio = sum(not c.isalnum() and not c.isspace() for c in message) / len(message)
    if special_char_ratio > 0.3:
        return False, "Message contains too many special characters"
    
    return True, ""


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially harmful content.
    
    Args:
        text: User input text
        
    Returns:
        Sanitized text
    """
    # Remove control characters except newlines and tabs
    sanitized = "".join(char for char in text if ord(char) >= 32 or char in ['\n', '\t'])
    
    # Normalize whitespace
    sanitized = " ".join(sanitized.split())
    
    return sanitized.strip()


def is_question(message: str) -> bool:
    """
    Determine if message is a question.
    Helps with prompt engineering.
    
    Args:
        message: User message
        
    Returns:
        True if message appears to be a question
    """
    question_indicators = [
        '?',
        'what', 'where', 'when', 'why', 'how', 'who',
        'can you', 'could you', 'would you',
        'is there', 'are there', 'help me', 'need to know',
        'tell me', 'show me', 'explain', 'define', 'describe',
        'list', 'give me', 'provide', 'suggest', 'recommend',
        'do you know', 'is it possible'
    ]
    
    message_lower = message.lower()
    
    # Check for question mark
    if '?' in message:
        return True
    
    # Check for question words at start
    for indicator in question_indicators:
        if message_lower.startswith(indicator):
            return True
    
    return False