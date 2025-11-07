"""
LLM Manager for handling language model interactions.
Best practices: Singleton pattern, error handling, configuration management.

"""

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from typing import List, Dict, Any, Optional
from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger("llm")

class LLMManager:
    """
    Manages LLM initialization and interactions.
    Implements singleton pattern for efficient resource usage.
    """
    _instance = None
    _llm = None

    def __new__(cls):
        """Singleton pattern to reuse LLM instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize LLM if not already initialized."""
        if self._llm is None:
            self._initialize_llm()

    def _initialize_llm(self):
        """
        Initialize the language model.
        Handles errors gracefully and provides fallbacks.
        """
        if not settings.GROQ_API_KEY:
            logger.error("❌ GROQ_API_KEY not found in environment variables")
            raise ValueError(
                "GROQ_API_KEY is required."
            )
        
        try:
            logger.info(f"🤖 Initializing LLM: {settings.LLM_MODEL}")
            
            self._llm = ChatGroq(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                groq_api_key=settings.GROQ_API_KEY,
                timeout=30.0,  # Timeout in seconds
                # Additional parameters passed via model_kwargs
                model_kwargs={
                    "top_p": 0.9,  # Nucleus sampling
                }
            )
            
            logger.info("✅ LLM initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            raise
    
    def get_llm(self) -> ChatGroq:
        """
        Get the LLM instance.
        
        Returns:
            ChatGroq instance
        """
        if self._llm is None:
            self._initialize_llm()
        return self._llm
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User's question or prompt
            system_prompt: Optional system prompt for context
            chat_history: Optional chat history for context
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Generated response text
        """
        try:
            # Build messages list
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["message"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["message"]))
            
            # Add current prompt
            messages.append(HumanMessage(content=prompt))
            
            # Generate response
            logger.info(f"🤔 Generating response for query: {prompt[:50]}...")
            response = self._llm.invoke(messages, **kwargs)
            
            # Extract text from response
            response_text = response.content
            
            logger.info(f"✅ Response generated successfully")
            
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            raise
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Rough estimation: ~4 characters per token for English.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        return len(text) // 4

    def check_context_limit(self, total_text: str) -> bool:
        """
        Check if text fits within model's context limit.
        
        Args:
            total_text: Combined text (context + question + history)
            
        Returns:
            True if within limit, False otherwise
        """
        estimated_tokens = self.estimate_tokens(total_text)
        
        # Get model's context limit
        model_limits = {
            "llama-3.1-8b-instant": 8000
    
        }
        
        limit = model_limits.get(settings.LLM_MODEL, 8000)
        
        # Leave room for response (reserve 25% of context)
        available = limit * 0.75
        
        return estimated_tokens <= available
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "llm_model": settings.LLM_MODEL,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
            "provider": "Groq (Free)"
        }

_llm_manager = None


def get_llm_manager() -> LLMManager:
    """
    Get the global LLM manager instance.
    
    Returns:
        LLMManager instance
    """
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager


def get_llm() -> ChatGroq:
    """
    Quick access to LLM instance.
    
    Returns:
        ChatGroq instance
    """
    manager = get_llm_manager()
    return manager.get_llm()