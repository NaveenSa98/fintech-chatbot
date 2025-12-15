"""
Query Augmentation Engine for RAG System.

Improves retrieval accuracy by generating multiple query variations before vector search.
Uses LLM for primary augmentation with fallback to synonym-based expansion.
"""

from typing import List, Dict, Any, Optional
from src.chat.llm_manager import get_llm_manager
from src.core.config import settings
from src.core.logging_config import get_logger
import hashlib

logger = get_logger("query_augmentation")


class QueryAugmentationEngine:
    """
    Generates multiple query variations to improve document retrieval.

    How it works:
    1. Primary: Uses LLM (Groq) to generate natural query alternatives
    2. Fallback: If LLM fails, uses domain synonyms for robustness
    3. Caching: Caches results to avoid redundant LLM calls
    """

    # Domain-specific synonyms mapping
    # Used as fallback when LLM augmentation fails
    DOMAIN_SYNONYMS = {
        # Leave/Time Off domain
        "leave": ["time off", "vacation", "PTO", "days off", "absence request"],
        "vacation": ["leave", "time off", "days off", "paid leave"],
        "pto": ["paid time off", "leave", "vacation days"],
        "leave request": ["time off request", "vacation application"],

        # Benefits domain
        "benefits": ["compensation package", "perks", "employee benefits", "entitlements"],
        "salary": ["compensation", "pay", "earnings", "remuneration"],
        "insurance": ["health coverage", "medical plan", "health insurance"],
        "health insurance": ["medical plan", "health coverage", "insurance benefits"],

        # Policies domain
        "policy": ["procedure", "guidelines", "rules", "standards", "process"],
        "process": ["procedure", "workflow", "steps", "instructions"],
        "guidelines": ["standards", "rules", "policy", "procedures"],

        # Onboarding domain
        "onboarding": ["employee setup", "induction", "orientation", "getting started"],
        "hiring": ["recruitment", "employment", "staff acquisition"],
        "new employee": ["onboarding", "new hire", "employee setup"],

        # General/Common
        "how do i": ["what's the process for", "steps to", "guide for"],
        "can i": ["am i able to", "is it possible to", "what's the process for"],
        "what is": ["explain", "tell me about", "describe"],
    }

    def __init__(self, enable: bool = True, num_augmentations: int = 2):
        """
        Initialize Query Augmentation Engine.

        Args:
            enable: Whether to enable query augmentation (default: True)
            num_augmentations: Number of alternative queries to generate (1-4, default: 2)
        """
        self.llm_manager = get_llm_manager()
        self.enable = enable
        self.num_augmentations = max(1, min(num_augmentations, 4))  # Constrain to 1-4
        self._cache = {}

        logger.info(
            f"QueryAugmentationEngine initialized: "
            f"enabled={enable}, augmentations={self.num_augmentations}"
        )

    def augment(self, query: str, user_role: str = None) -> Dict[str, Any]:
        """
        Generate augmented query variations.

        Args:
            query: User's original query
            user_role: Optional user role for context-aware augmentation

        Returns:
            Dictionary containing:
            - 'original': Original query
            - 'augmented': List of alternative phrasings
            - 'all_queries': [original] + augmented queries
        """
        if not self.enable or not query:
            return {
                "original": query,
                "augmented": [],
                "all_queries": [query]
            }

        # Check cache to avoid redundant calls
        cache_key = self._make_cache_key(query, user_role)
        if cache_key in self._cache:
            logger.debug(f"Cache hit for query: {query[:40]}...")
            return self._cache[cache_key]

        logger.info(f"Augmenting query: {query[:50]}...")

        try:
            # Primary: LLM-based augmentation (Groq)
            augmented = self._augment_with_llm(query, user_role)
        except Exception as e:
            logger.warning(f"LLM augmentation failed, using fallback: {e}")
            # Fallback: Synonym-based augmentation
            augmented = self._augment_with_synonyms(query)

        result = {
            "original": query,
            "augmented": augmented,
            "all_queries": [query] + augmented
        }

        # Cache the result
        self._cache[cache_key] = result

        logger.info(f"Generated {len(augmented)} augmented queries")
        return result

    def _augment_with_llm(self, query: str, user_role: str = None) -> List[str]:
        """
        Generate augmented queries using LLM (Groq llama-3.1-8b-instant).

        Args:
            query: Original query
            user_role: User role for context (optional)

        Returns:
            List of augmented queries
        """
        # Build context string from user role if available
        role_context = ""
        if user_role:
            role_context = f"\nUser role: {user_role}\n"

        # Create prompt for LLM
        prompt = f"""Generate {self.num_augmentations} alternative ways to ask this question.
Each should be a natural, slightly different phrasing of the same intent.
These will be used to search documents for better retrieval.

{role_context}
Original question: "{query}"

Output exactly {self.num_augmentations} questions, one per line.
Do NOT include numbers, bullets, or explanations - just the questions."""

        # Call LLM
        response = self.llm_manager.generate_response(prompt)

        # Parse response into list of queries
        augmented = self._parse_queries(response)

        # Return only requested number of augmentations
        return augmented[:self.num_augmentations]

    def _augment_with_synonyms(self, query: str) -> List[str]:
        """
        Generate augmented queries using domain synonym replacement.
        Used as fallback when LLM augmentation fails.

        Args:
            query: Original query

        Returns:
            List of augmented queries
        """
        augmented = []
        query_lower = query.lower()

        # Strategy 1: Direct synonym replacement
        for word, synonyms in self.DOMAIN_SYNONYMS.items():
            if word in query_lower and len(augmented) < self.num_augmentations:
                for synonym in synonyms:
                    new_query = query.replace(word, synonym, 1)
                    if new_query != query and new_query not in augmented:
                        augmented.append(new_query)
                        break
                if len(augmented) >= self.num_augmentations:
                    break

        # Strategy 2: Reorder question structure
        if len(augmented) < self.num_augmentations:
            if query.startswith("How "):
                # "How to X?" → "X - process and steps"
                remaining = query[5:].rstrip("?")
                reordered = f"{remaining} procedure and guidelines"
                if reordered not in augmented:
                    augmented.append(reordered)

            elif query.startswith("What "):
                # "What is X?" → "Tell me about X"
                remaining = query[5:].rstrip("?")
                reordered = f"Tell me about {remaining}"
                if reordered not in augmented:
                    augmented.append(reordered)

        # Strategy 3: Add clarifying context
        if len(augmented) < self.num_augmentations:
            domain_terms = ["employee", "company policy", "guidelines", "procedure"]
            for term in domain_terms:
                if term not in query_lower and len(augmented) < self.num_augmentations:
                    contextual = f"{query} for {term}"
                    if contextual not in augmented:
                        augmented.append(contextual)

        return augmented[:self.num_augmentations]

    def _parse_queries(self, response: str) -> List[str]:
        """
        Parse LLM response into list of queries.

        Args:
            response: LLM response text

        Returns:
            List of parsed queries (cleaned)
        """
        # Split by newlines and filter empty lines
        lines = response.split('\n')
        queries = []

        for line in lines:
            line = line.strip()

            # Skip empty lines and common formatting
            if not line:
                continue
            if line[0] in ('1', '2', '3', '4', '5', '-', '•', '*'):
                line = line.lstrip('0123456789.-•* ').strip()

            # Skip if still empty after cleaning
            if line:
                queries.append(line)

        return queries

    def _make_cache_key(self, query: str, user_role: str = None) -> str:
        """
        Create cache key from query and user role.

        Args:
            query: Query string
            user_role: User role string

        Returns:
            Cache key (MD5 hash)
        """
        combined = f"{query}:{user_role or 'none'}"
        return hashlib.md5(combined.encode()).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about query augmentation engine.

        Returns:
            Dictionary with stats
        """
        return {
            "enabled": self.enable,
            "num_augmentations": self.num_augmentations,
            "cache_size": len(self._cache),
            "cache_max_size": 1000
        }

    def clear_cache(self) -> None:
        """Clear the augmentation cache."""
        old_size = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared augmentation cache ({old_size} items)")


# Global engine instance
_augmentation_engine = None


def get_query_augmentation_engine() -> QueryAugmentationEngine:
    """
    Get global QueryAugmentationEngine instance (singleton).

    Returns:
        QueryAugmentationEngine instance
    """
    global _augmentation_engine

    if _augmentation_engine is None:
        enable = getattr(settings, 'ENABLE_QUERY_AUGMENTATION', True)
        num_aug = getattr(settings, 'NUM_QUERY_AUGMENTATIONS', 2)
        _augmentation_engine = QueryAugmentationEngine(enable=enable, num_augmentations=num_aug)

    return _augmentation_engine
