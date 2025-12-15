"""
Embedding functions for converting text to vectors.
Uses Sentence Transformers (HuggingFace) for semantic embeddings.
"""
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger("vector_store")


class EmbeddingManager:
    """Singleton class for managing text embeddings using Sentence Transformers."""

    _instance = None
    _embeddings = None

    def __new__(cls):
        """Singleton pattern to reuse embeddings instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the embeddings model."""
        if self._embeddings is None:
            self._load_embeddings()

    def _load_embeddings(self):
        """Load the embeddings model from Sentence Transformers."""
        logger.info(f"Loading embeddings model: {settings.EMBEDDING_MODEL_NAME}")

        try:
            self._embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
            logger.info("Embeddings model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading embeddings model: {str(e)}")
            raise

    def get_embeddings(self):
        """Get the embeddings instance."""
        return self._embeddings


def get_embedding_function():
    """
    Get the global embedding function for semantic embeddings.

    Returns:
        HuggingFaceEmbeddings instance for text-to-vector conversion
    """
    manager = EmbeddingManager()
    return manager.get_embeddings()

