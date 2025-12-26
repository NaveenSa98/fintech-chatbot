"""
Business logic for chat operations.
Best practices: Separation of concerns, transaction management, clean interfaces.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from src.chat.models import Conversation, ChatMessage
from src.chat.rag_chain import get_rag_chain
from src.utils.formatting import format_sources, format_conversation_title
from src.utils.validators import validate_message_length, validate_message_content
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from src.core.logging_config import get_logger

logger = get_logger("chat")


class ChatService:
    """ Service class for chat operations. """

    @staticmethod
    def send_message(
        db: Session,
        user_id: int,
        user_role: str,
        message: str,
        conversation_id: Optional[int] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Process a chat message and generate response.
        
        Args:
            db: Database session
            user_id: ID of user sending message
            user_role: User's role
            message: User's message
            conversation_id: Optional existing conversation ID
            include_sources: Whether to include sources in response
            
        Returns:
            Response dictionary with message and metadata
        """
        # Step 1: Validate message
        is_valid, error = validate_message_length(message)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        is_valid, error = validate_message_content(message)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # Step 2: Get or create conversation
        if conversation_id:
            conversation = ChatService._get_conversation(db, conversation_id, user_id)
        else:
            conversation = ChatService._create_conversation(db, user_id, message)
        
        # Step 3: Save user message
        user_message = ChatMessage(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            message=message
        )
        db.add(user_message)
        db.commit()
        
        # Step 4: Get conversation history
        chat_history = ChatService._get_conversation_history(
            db,
            conversation.id,
            exclude_last=True  # Don't include the message we just added
        )
        
        # Step 5: Generate response using RAG
        try:
            rag_chain = get_rag_chain()
            result = rag_chain.process_query(
                question=message,
                user_role=user_role,
                chat_history=chat_history
            )
            
            # Step 6: Save assistant response
            assistant_message = ChatMessage(
                conversation_id=conversation.id,
                user_id=user_id,
                role="assistant",
                message=result["answer"],
                sources_used=json.dumps(result["sources"]) if result["sources"] else None,
                confidence_score=result["confidence"],
                tokens_used=result["tokens_used"]
            )
            db.add(assistant_message)
            
            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(assistant_message)
            
            logger.info(f"✅ Message processed for conversation {conversation.id}")
            
            # Step 7: Format and return response
            return {
                "message": result["answer"],
                "conversation_id": conversation.id,
                "message_id": assistant_message.id,
                "sources": format_sources(result["sources"]) if include_sources and result["sources"] else None,
                "confidence": result["confidence"],
                "tokens_used": result["tokens_used"],
                "timestamp": assistant_message.created_at
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error processing message: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating response: {str(e)}"
            )
        
    @staticmethod
    def _create_conversation(db: Session, user_id: int, first_message: str) -> Conversation:
        """Create a new conversation."""
        title = format_conversation_title(first_message)
        
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"📝 Created conversation {conversation.id}")
        
        return conversation
    
    @staticmethod
    def _get_conversation(db: Session, conversation_id: int, user_id: int) -> Conversation:
        """Get existing conversation with access check."""
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verify ownership
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this conversation"
            )
        
        return conversation
    
    @staticmethod
    def _get_conversation_history(
        db: Session,
        conversation_id: int,
        limit: Optional[int] = None,
        exclude_last: bool = False
    ) -> List[Dict[str, str]]:
        """Get conversation message history."""
        from src.core.config import settings
        
        limit = limit or settings.MAX_CONVERSATION_HISTORY
        
        query = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.desc())
        
        if exclude_last:
            query = query.offset(1)
        
        messages = query.limit(limit).all()
        
        # Reverse to get chronological order
        messages.reverse()
        
        # Format for RAG chain
        history = [
            {"role": msg.role, "message": msg.message}
            for msg in messages
        ]
        
        return history
    
    @staticmethod
    def get_user_conversations(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Get all conversations for a user."""
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.updated_at.desc()
        ).offset(skip).limit(limit).all()
        
        return conversations
    
    @staticmethod
    def get_conversation_with_messages(
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Get conversation with full message history."""
        conversation = ChatService._get_conversation(db, conversation_id, user_id)
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        # Format messages with sources
        formatted_messages = []
        for msg in messages:
            msg_dict = {
                "id": msg.id,
                "role": msg.role,
                "message": msg.message,
                "created_at": msg.created_at
            }
            
            # Add sources for assistant messages
            if msg.role == "assistant" and msg.sources_used:
                try:
                    sources = json.loads(msg.sources_used)
                    msg_dict["sources"] = format_sources(sources)
                except:
                    msg_dict["sources"] = None
            
            formatted_messages.append(msg_dict)
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "user_id": conversation.user_id,
            "created_at": conversation.created_at,
            "messages": formatted_messages
        }
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation and all its messages."""
        conversation = ChatService._get_conversation(db, conversation_id, user_id)
        
        # Delete conversation (cascade will delete messages)
        db.delete(conversation)
        db.commit()
        
        logger.info(f"🗑️ Deleted conversation {conversation_id}")
        
        return True
    
    @staticmethod
    def update_conversation_title(
        db: Session,
        conversation_id: int,
        user_id: int,
        new_title: str
    ) -> Conversation:
        """Update conversation title."""
        conversation = ChatService._get_conversation(db, conversation_id, user_id)
        
        conversation.title = new_title[:200]  # Limit length
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get chat statistics for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with user statistics
        """
        # Get total messages count
        total_messages = db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.user_id == user_id
        ).scalar() or 0

        # Get user questions count
        user_questions = db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.role == "user"
        ).scalar() or 0

        # Get assistant responses count
        assistant_responses = db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.role == "assistant"
        ).scalar() or 0

        # Get total conversations
        total_conversations = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == user_id
        ).scalar() or 0

        # Calculate average messages per conversation
        avg_messages = 0.0
        if total_conversations > 0:
            avg_messages = round(total_messages / total_conversations, 1)

        logger.info(
            f"User {user_id} stats: {total_messages} messages, "
            f"{user_questions} questions, {total_conversations} conversations"
        )

        return {
            "total_messages": total_messages,
            "user_questions": user_questions,
            "assistant_responses": assistant_responses,
            "total_conversations": total_conversations,
            "avg_messages_per_conversation": avg_messages
        }

