"""
Embedding functions for converting text to vectors.
Uses sentence-transformers for local embeddings.
"""
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.core.config import settings
from src.core.logging_config import get_logger
from typing import List

logger = get_logger("vector_store")

class Embeddings:
    """Class for managing text embeddings using sentence-transformers."""

    _instance = None
    _embeddings = None

    def __new__(cls):
        """Singleton pattern to reuse the embeddings instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        """Initialize the embeddings model."""
        if self._embeddings is None:
            self._load_embeddings()

    def _load_embeddings(self):
        """Load the embeddings model from sentence-transformers."""
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

    def embed_text(self, text: str) -> List[float]:
        """Embed a single piece of text."""

        try:
            return self._embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""

        try:
            logger.info(f"Embedding {len(texts)} documents")
            return self._embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}")
            raise

# Global embedding manager instance
def get_embedding_function():
    """
    Get the global embedding function.

    Returns:
        HuggingFaceEmbeddings instance
    """
    manager = Embeddings()

    return manager.get_embeddings()



