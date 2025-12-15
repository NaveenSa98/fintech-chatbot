"""
ChromaDB vector store integration.
Handles document storage and retrieval using vector similarity.
"""

from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List, Dict, Any, Optional
from src.vectorstore.embeddings import get_embedding_function
from src.core.config import settings, DEPARTMENT_COLLECTIONS
from src.core.logging_config import get_logger
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = get_logger("vector_store")

class ChromaStore:
    """
    Manages ChromaDB vector store for document storage and retrieval.
    Separate collections for each department.

    """
    def __init__(self):
        """Initialize ChromaDB client"""

        self.persist_directory = settings.CHROMA_DB_DIR
        self.embedding_function = get_embedding_function()

        self.client = chromadb.PersistentClient(
            path = self.persist_directory,
            settings = ChromaSettings(
                anonymized_telemetry = False,
                allow_reset = True
            )
        )

        logger.info(f"ChromaDB client initialized at {self.persist_directory}")

    def get_collection(self, department: str) -> Chroma:
        """ Get or create a Chroma collection for a department. """

        collection_name = DEPARTMENT_COLLECTIONS.get(department, "general")

        # Get or create collection with Cosine similarity metric
        try:
            collection = self.client.get_collection(
                name=collection_name,
            )
            logger.info(f"Retrieved existing collection: {collection_name}")
        except Exception:
            # Create new collection with Cosine similarity
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use Cosine similarity for semantic search
            )
            logger.info(f"Created new collection: {collection_name} with Cosine similarity")

        vectorstore = Chroma(
            collection_name = collection_name,
            embedding_function = self.embedding_function,
            persist_directory = self.persist_directory,
            client = self.client
        )

        logger.info(f"Accessed collection: {collection_name} for department {department}")
        return vectorstore

    def add_documents(
            self,
            documents: List[Document],
            department: str,
    ) -> List[str]:

        """ Add documents to the vector store"""

        logger.info(f"Adding {len(documents)} documents to {department} collection")

        try:
            vectorstore = self.get_collection(department)
            ids = vectorstore.add_documents(documents)
            vectorstore.persist()

            logger.info(f"Successfully added {len(documents)} documents to {department} collection")
            return ids

        except Exception as e:
            logger.error(f"Error adding documents to {department} collection: {str(e)}")
            raise


    def similarity_search_with_score(
        self,
        query: str,
        department: str,
        k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        Semantic search with cosine similarity scores for reranking.

        Args:
            query: Search query
            department: Department to search in
            k: Number of results to return

        Returns:
            List of (document, distance) tuples
            Note: distance from ChromaDB (0=identical, 2=opposite)
                  Convert to similarity using: 1 - distance
        """
        logger.info(f"Semantic search in {department}: query='{query}', k={k}")

        try:
            vectorstore = self.get_collection(department)

            # Perform semantic search using cosine similarity
            results = vectorstore.similarity_search_with_score(
                query=query,
                k=k
            )

            logger.info(f"Found {len(results)} semantic results in {department} collection")
            return results

        except Exception as e:
            logger.error(f"Error during semantic search in {department}: {str(e)}")
            raise

    def delete_documents(
        self,
        department: str,
        ids: Optional[List[str]] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Delete documents from collection.

        Args:
            department: Department name
            ids: Optional list of document IDs to delete
            filter_metadata: Optional metadata filter for deletion
        """
        logger.info(f"Deleting documents from {department} collection")

        try:
            collection_name = DEPARTMENT_COLLECTIONS.get(department, "general")
            collection = self.client.get_collection(collection_name)

            if ids:
                collection.delete(ids=ids)
                logger.info(f"Deleted {len(ids)} documents by ID from {department} collection")
            elif filter_metadata:
                collection.delete(where=filter_metadata)
                logger.info(f"Deleted documents by filter from {department} collection: {filter_metadata}")

        except Exception as e:
            logger.error(f"Error deleting documents from {department} collection: {str(e)}")
            raise

    def get_collection_stats(self, department: str) -> Dict[str, Any]:
        """
        Get statistics about a collection.

        Args:
            department: Department name

        Returns:
            Dictionary with collection stats
        """
        collection_name = DEPARTMENT_COLLECTIONS.get(department, "general")

        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()

            logger.info(f"Collection stats for {department}: {count} documents")

            return {
                "department": department,
                "collection_name": collection_name,
                "document_count": count
            }
        except Exception as e:
            logger.warning(f"Error getting stats for {department} collection: {str(e)}")
            return {
                "department": department,
                "collection_name": collection_name,
                "document_count": 0,
                "error": str(e)
            }

    def reset_collection(self, department: str):
        """
        Reset (clear) a collection.

        Args:
            department: Department name
        """
        collection_name = DEPARTMENT_COLLECTIONS.get(department, "general")

        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Reset {department} collection successfully")
        except Exception as e:
            logger.warning(f"Could not reset {department} collection: {str(e)}")


# Global ChromaStore instance
_chroma_store = None


def get_chroma_store() -> ChromaStore:
    """
    Get the global ChromaStore instance.

    Returns:
        ChromaStore instance
    """
    global _chroma_store
    if _chroma_store is None:
        _chroma_store = ChromaStore()
    return _chroma_store



