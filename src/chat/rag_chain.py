"""
RAG Chain - Core retrieval-augmented generation pipeline.
Best practices: Modular design, clear flow, comprehensive error handling.

RAG Flow:
1. Retrieve relevant documents (retriever)
2. Format context (formatter)
3. Build prompt (prompt template)
4. Generate response (LLM)
5. Post-process and return (formatter)
"""

from typing import List, Dict, Any, Optional, Tuple
from src.chat.llm_manager import get_llm_manager
from src.chat.prompt_templates import (
    get_rag_prompt,
    get_standalone_question_prompt,
    format_no_context_response
)
from src.vectorstore.retriever import get_retriever
from src.utils.formatting import (
    format_context,
    format_chat_history,
    clean_response,
    calculate_confidence
)
from src.utils.validators import sanitize_input
from src.core.config import settings, ROLE_PERMISSIONS
from src.core.logging_config import get_logger

logger = get_logger("rag")


class RAGChain:
    """
    Retrieval-Augmented Generation chain.
    Orchestrates the entire RAG pipeline with best practices.
    """

    def __init__(self):
        """ Initialize RAG components. """
        self.llm_manager = get_llm_manager()
        self.retriever = get_retriever()
        self.rag_prompt = get_rag_prompt()
        self.standalone_prompt = get_standalone_question_prompt()

    def process_query(
        self,
        question: str,
        user_role: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the RAG pipeline.
        
        Args:
            question: User's question
            user_role: User's role (for access control)
            chat_history: Optional conversation history
            top_k: Number of documents to retrieve (default from settings)
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        # Step 0: Input validation and sanitization
        question = sanitize_input(question)
        top_k = top_k or settings.RAG_TOP_K
        
        logger.info(f"🔍 Processing query from {user_role}: {question[:50]}...")
        
        # Step 1: Contextualize question with history (if available)
        standalone_question = self._contextualize_question(question, chat_history)
        
        # Step 2: Retrieve relevant documents
        retrieved_docs = self._retrieve_documents(standalone_question, user_role, top_k)
        
        # Step 3: Check if we have relevant context
        if not retrieved_docs or not self._has_relevant_context(retrieved_docs):
            return self._handle_no_context(question, user_role)
        
        # Step 4: Format context and build prompt
        context = format_context(retrieved_docs)
        history = format_chat_history(chat_history) if chat_history else "No previous conversation"
        
        # Step 5: Generate response
        response = self._generate_response(
            question=question,
            context=context,
            user_role=user_role,
            chat_history=history
        )
        
        # Step 6: Post-process and package results
        result = self._package_response(response, retrieved_docs, question)
        
        logger.info("✅ Query processed successfully")
        
        return result
    
    def _contextualize_question(
        self,
        question: str,
        chat_history: Optional[List[Dict[str, str]]]
    ) -> str:
        """
        Contextualize question with chat history if available.
        Converts follow-up questions to standalone questions.
        
        Args:
            question: Current question
            chat_history: Chat history
            
        Returns:
            Standalone question
        """
        if not chat_history or not settings.ENABLE_CONVERSATION_HISTORY:
            return question
        
        try:
            # Format history
            history_text = format_chat_history(chat_history[-3:])  # Last 3 messages
            
            # Build prompt
            prompt = self.standalone_prompt.format(
                chat_history=history_text,
                question=question
            )
            
            # Generate standalone question
            standalone = self.llm_manager.generate_response(prompt)
            
            logger.info(f"📝 Contextualized question: {standalone[:50]}...")
            
            return standalone.strip()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to contextualize question: {e}")
            return question  # Fallback to original question
    
    def _retrieve_documents(
        self,
        question: str,
        user_role: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents based on user role.
        
        Args:
            question: User's question
            user_role: User's role
            top_k: Number of documents to retrieve
            
        Returns:
            List of retrieved documents
        """
        try:
            documents = self.retriever.retrieve_for_user(
                query=question,
                user_role=user_role,
                top_k=top_k
            )
            
            logger.info(f"📚 Retrieved {len(documents)} documents")
            
            return documents
            
        except Exception as e:
            logger.error(f"❌ Document retrieval failed: {e}")
            return []
    
    def _has_relevant_context(
        self,
        documents: List[Dict[str, Any]],
        min_score: float = None
    ) -> bool:
        """
        Check if retrieved documents are relevant enough.
        
        Args:
            documents: Retrieved documents
            min_score: Minimum relevance score (default from settings)
            
        Returns:
            True if documents are relevant
        """
        if not documents:
            return False
        
        min_score = min_score or settings.RAG_SIMILARITY_THRESHOLD
        
        # Check if best match exceeds threshold
        # Note: ChromaDB returns distance, lower is better
        best_score = 1 - documents[0].get("score", 1.0)  # Convert to similarity
        
        return best_score >= min_score
    
    def _generate_response(
        self,
        question: str,
        context: str,
        user_role: str,
        chat_history: str
    ) -> str:
        """
        Generate response using LLM.
        
        Args:
            question: User's question
            context: Formatted context from documents
            user_role: User's role
            chat_history: Formatted chat history
            
        Returns:
            Generated response
        """
        try:
            # Get accessible departments for user
            departments = ROLE_PERMISSIONS.get(user_role, {}).get("departments", [])
            
            # Build prompt
            prompt = self.rag_prompt.format(
                context=context,
                user_role=user_role,
                departments=", ".join(departments),
                chat_history=chat_history,
                question=question
            )
            
            # Check context limit
            if not self.llm_manager.check_context_limit(prompt):
                logger.warning("⚠️ Context exceeds limit, truncating...")
                # Truncate context if needed
                context = context[:10000]  # Keep first 10k chars
                prompt = self.rag_prompt.format(
                    context=context,
                    user_role=user_role,
                    departments=", ".join(departments),
                    chat_history=chat_history,
                    question=question
                )
            
            # Generate response
            response = self.llm_manager.generate_response(prompt)
            
            # Clean response
            cleaned = clean_response(response)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"❌ Response generation failed: {e}")
            raise
    
    def _handle_no_context(self, question: str, user_role: str) -> Dict[str, Any]:
        """
        Handle case when no relevant context is found.
        
        Args:
            question: User's question
            user_role: User's role
            
        Returns:
            Response dictionary
        """
        logger.info("ℹ️ No relevant context found")
        
        departments = ROLE_PERMISSIONS.get(user_role, {}).get("departments", [])
        response = format_no_context_response(question, departments)
        
        return {
            "answer": response,
            "sources": [],
            "confidence": 0.0,
            "tokens_used": self.llm_manager.estimate_tokens(response)
        }
    
    def _package_response(
        self,
        response: str,
        sources: List[Dict[str, Any]],
        question: str
    ) -> Dict[str, Any]:
        """
        Package the response with metadata.
        
        Args:
            response: Generated response
            sources: Source documents
            question: Original question
            
        Returns:
            Complete response package
        """
        confidence = calculate_confidence(sources)
        tokens = self.llm_manager.estimate_tokens(response + question)
        
        return {
            "answer": response,
            "sources": sources,
            "confidence": confidence,
            "tokens_used": tokens
        }
    
    def get_chain_info(self) -> Dict[str, Any]:
        """
        Get information about the RAG chain configuration.
        
        Returns:
            Dictionary with chain information
        """
        return {
            "llm_model": self.llm_manager.get_model_info(),
            "retrieval_config": {
                "top_k": settings.RAG_TOP_K,
                "similarity_threshold": settings.RAG_SIMILARITY_THRESHOLD,
                "conversation_history": settings.ENABLE_CONVERSATION_HISTORY,
                "max_history": settings.MAX_CONVERSATION_HISTORY
            }
        }


#Global RAG chain instance

_rag_chain = None


def get_rag_chain() -> RAGChain:
    """
    Get the global RAG chain instance.
    
    Returns:
        RAGChain instance
    """
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = RAGChain()
    return _rag_chain