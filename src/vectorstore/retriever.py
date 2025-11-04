"""
Document retriever with role-based access control.
Retrieves relevant documents based on user role and query.
"""
from typing import List, Dict, Any
from src.vectorstore.chroma_store import get_chroma_store
from src.core.config import ROLE_PERMISSIONS
from src.core.logging_config import get_logger
from langchain.schema import Document

logger = get_logger("vector_store")

class DocumentRetriever:
    """
    Retrieves documents with role-based access control.
    Ensures users can only access documents they are permitted to view.

    """

    def __init__(self):
        """Initialize the retriever"""
        self.chroma_store = get_chroma_store()
        logger.info("DocumentRetriever initialized")

    def retrieve_for_user(
            self,
            query: str,
            user_role: str,
            top_k: int = 5
    ) -> List[Document]:
        """
        Retrieve documents based on user role and query.

        Args:
            query: Search query
            user_role: Role of the user (e.g., 'admin', 'user')
            top_k: Number of top documents to retrieve

        Returns:
            List of relevant documents
        """
        logger.info(f"Retrieving documents for role '{user_role}' with query: '{query}', top_k={top_k}")

        allowed_departments = ROLE_PERMISSIONS.get(user_role, {}).get("departments", [])

        if not allowed_departments:
            logger.warning(f"No departments accessible for role: {user_role}")
            return []

        all_results = []

        for department in allowed_departments:
            try:
                results = self.chroma_store.similarity_search_with_score(
                    query=query,
                    department=department,
                    k=top_k
                )

                for doc, score in results:
                    all_results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": float(score),
                        "department": department
                    })

                logger.info(f"Retrieved {len(results)} results from {department} department")

            except Exception as e:
                logger.error(f"Error retrieving from department {department}: {str(e)}")
                continue

        all_results.sort(key=lambda x: x["score"], reverse=False)

        final_results = all_results[:top_k]
        logger.info(f"Returning {len(final_results)} total results for role '{user_role}'")

        return final_results

    def retrieve_from_department(
        self,
        query: str,
        department: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents from a specific department.

        Args:
            query: Search query
            department: Department name
            top_k: Number of results

        Returns:
            List of retrieved documents
        """
        logger.info(f"Retrieving from department '{department}' with query: '{query}', top_k={top_k}")

        try:
            results = self.chroma_store.similarity_search_with_score(
                query=query,
                department=department,
                k=top_k
            )

            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                    "department": department
                })

            logger.info(f"Retrieved {len(formatted_results)} results from {department}")
            return formatted_results

        except Exception as e:
            logger.error(f"Error retrieving from department {department}: {str(e)}")
            raise

    def _collection_to_department(self, collection: str) -> str:
        """
        Convert collection name to department name.

        Args:
            collection: Collection name (lowercase)

        Returns:
            Department name (capitalized)
        """
        mapping = {
            "finance": "Finance",
            "marketing": "Marketing",
            "hr": "HR",
            "engineering": "Engineering",
            "general": "General"
        }
        return mapping.get(collection, "General")

    def get_accessible_departments(self, user_role: str) -> List[str]:
        """
        Get list of departments accessible to a role.

        Args:
            user_role: User's role

        Returns:
            List of department names
        """
        return ROLE_PERMISSIONS.get(user_role, {}).get("departments", [])


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
