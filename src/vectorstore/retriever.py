"""
Document retriever with role-based access control and semantic search.
Retrieves relevant documents based on user role, query, and semantic similarity.
"""
from typing import List, Dict, Any
from src.vectorstore.chroma_store import get_chroma_store
from src.core.config import ROLE_PERMISSIONS
from src.core.logging_config import get_logger

logger = get_logger("vector_store")


class DocumentRetriever:
    """
    Retrieves documents with role-based access control and semantic reranking.
    Ensures users can only access documents they are permitted to view.
    """

    def __init__(self):
        """Initialize the retriever with semantic search capability."""
        self.chroma_store = get_chroma_store()
        logger.info("DocumentRetriever initialized with semantic search (threshold disabled)")

    def retrieve_for_user(
        self,
        query: str,
        user_role: str,
        top_k: int = 8,
        queries: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents based on user role and semantic similarity.
        Searches across all accessible departments and reranks by relevance.

        Supports both single query and multiple augmented queries for better retrieval.

        Args:
            query: Primary search query
            user_role: Role of the user
            top_k: Number of top documents to retrieve
            queries: Optional list of additional queries (from query augmentation)

        Returns:
            List of relevant documents sorted by semantic relevance
        """
        # Build list of queries to search
        search_queries = [query]
        if queries:
            search_queries.extend(queries)

        logger.info(
            f"Semantic search for role '{user_role}': "
            f"{len(search_queries)} queries, top_k={top_k}"
        )

        # Get allowed departments for user
        allowed_departments = ROLE_PERMISSIONS.get(user_role, {}).get("departments", [])

        if not allowed_departments:
            logger.warning(f"No departments accessible for role: {user_role}")
            return []

        all_results = {}  # Use dict to deduplicate by content

        # Search each query across all accessible departments
        for search_query in search_queries:
            for department in allowed_departments:
                try:
                    results = self.chroma_store.similarity_search_with_score(
                        query=search_query,
                        department=department,
                        k=top_k
                    )

                    # Convert ChromaDB distance to similarity score
                    for doc, distance in results:
                        # ChromaDB returns distance, convert to similarity (1 - distance for cosine)
                        similarity_score = max(0.0, 1.0 - distance)

                        # Use content hash as key to deduplicate
                        doc_hash = hash(doc.page_content)

                        # Keep highest score for duplicate documents
                        if doc_hash not in all_results or similarity_score > all_results[doc_hash]["score"]:
                            all_results[doc_hash] = {
                                "content": doc.page_content,
                                "metadata": doc.metadata,
                                "score": round(similarity_score, 4),
                                "department": department
                            }

                except Exception as e:
                    logger.error(f"Error retrieving from {department}: {str(e)}")
                    continue

        # Convert dict to list and sort by score (highest relevance first)
        results_list = list(all_results.values())
        results_list.sort(key=lambda x: x["score"], reverse=True)

        # Return top-k results (no threshold filtering - LLM filters irrelevant content)
        final_results = results_list[:top_k]

        logger.info(
            f"Semantic search complete: {len(final_results)} results "
            f"from {len(search_queries)} queries"
        )

        return final_results

    def retrieve_from_department(
        self,
        query: str,
        department: str,
        top_k: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents from a specific department with semantic search.

        Args:
            query: Search query
            department: Department name
            top_k: Number of results

        Returns:
            List of documents sorted by semantic relevance
        """
        logger.info(f"Semantic search in {department}: query='{query}', top_k={top_k}")

        try:
            # Perform semantic search
            results = self.chroma_store.similarity_search_with_score(
                query=query,
                department=department,
                k=top_k
            )

            # Convert to results with similarity scores
            formatted_results = []
            for doc, distance in results:
                # Convert ChromaDB distance to similarity score
                similarity_score = max(0.0, 1.0 - distance)

                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": round(similarity_score, 4),
                    "department": department
                }
                formatted_results.append(result)

            logger.info(f"Semantic search in {department}: {len(formatted_results)} results retrieved")
            return formatted_results

        except Exception as e:
            logger.error(f"Error retrieving from {department}: {str(e)}")
            raise



# Global retriever instance
_retriever = None


def get_retriever() -> DocumentRetriever:
    """
    Get the global DocumentRetriever instance.

    Returns:
        DocumentRetriever instance
    """
    global _retriever
    if _retriever is None:
        _retriever = DocumentRetriever()
    return _retriever
