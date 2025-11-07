"""
Chat interface components.
Beautiful chat UI with message display and input.
"""
import streamlit as st
from streamlit_app.api.chat_api import send_message, list_conversations, get_conversation, delete_conversation
from streamlit_app.components.utils import render_source_card, format_datetime


def render_message(role: str, content: str, sources: list = None, timestamp: str = None):
    """
    Render a chat message.
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
        sources: Source documents (for assistant messages)
        timestamp: Message timestamp
    """
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>👤 You</strong><br/>
            {content}
            {f'<div style="font-size: 11px; color: #6B7280; margin-top: 5px;">{format_datetime(timestamp)}</div>' if timestamp else ''}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>🤖 Assistant</strong><br/>
            {content}
            {f'<div style="font-size: 11px; color: #6B7280; margin-top: 5px;">{format_datetime(timestamp)}</div>' if timestamp else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Show sources if available
        if sources:
            with st.expander(f"📚 Sources ({len(sources)})"):
                for source in sources:
                    render_source_card(source)


def render_conversation_history():
    """Render conversation history in sidebar."""
    st.sidebar.markdown("### History")

    # Small new conversation button at top
    if st.sidebar.button("➕ New", key="new_conv_btn", help="Start a new conversation"):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()

    st.sidebar.markdown("---")

    try:
        response = list_conversations(limit=10)
        conversations = response.get("conversations", [])

        if not conversations:
            st.sidebar.info("No conversations yet")
            return

        # Simple list of conversations
        for conv in conversations:
            col1, col2 = st.sidebar.columns([5, 1])

            with col1:
                # Simple text button for conversation title
                title = conv['title'][:35] + "..." if len(conv['title']) > 35 else conv['title']
                if st.button(
                    title,
                    key=f"conv_{conv['id']}",
                    use_container_width=True,
                    help=conv['title']
                ):
                    load_conversation(conv['id'])

            with col2:
                # Small delete button
                if st.button("🗑️", key=f"del_{conv['id']}", help="Delete conversation"):
                    try:
                        delete_conversation(conv['id'])
                        st.success("✓")
                        st.rerun()
                    except Exception as e:
                        st.error("✗")

    except Exception as e:
        st.sidebar.error(f"Error: {str(e)[:50]}")


def load_conversation(conversation_id: int):
    """
    Load a conversation and its messages.
    
    Args:
        conversation_id: Conversation ID to load
    """
    try:
        response = get_conversation(conversation_id)
        
        st.session_state.conversation_id = conversation_id
        st.session_state.messages = []
        
        # Load messages
        for msg in response.get("messages", []):
            message_data = {
                "role": msg["role"],
                "content": msg["message"],
                "timestamp": msg.get("created_at")
            }
            
            if msg["role"] == "assistant" and msg.get("sources"):
                message_data["sources"] = msg["sources"]
            
            st.session_state.messages.append(message_data)
        
        st.rerun()
    
    except Exception as e:
        st.error(f"Error loading conversation: {e}")


def render_chat_interface():
    """Render complete chat interface."""
    # Display conversation history
    render_conversation_history()
    
    # Chat header
    if st.session_state.conversation_id:
        st.markdown("### Chat")
    else:
        st.markdown("### New Conversation")
    
    # Display messages
    for message in st.session_state.messages:
        render_message(
            role=message["role"],
            content=message["content"],
            sources=message.get("sources"),
            timestamp=message.get("timestamp")
        )
    
    # Chat input
    st.markdown("---")
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Ask a question...",
            placeholder="E.g., What was our Q4 revenue?",
            height=100,
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            submit = st.form_submit_button("Send 📤", use_container_width=True)
        
        with col2:
            include_sources = st.checkbox("Include sources", value=True)
    
    if submit and user_input:
        # Add user message to display
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        try:
            with st.spinner("Thinking..."):
                response = send_message(
                    message=user_input,
                    conversation_id=st.session_state.conversation_id,
                    include_sources=include_sources
                )
            
            # Update conversation ID
            st.session_state.conversation_id = response["conversation_id"]
            
            # Add assistant message
            assistant_message = {
                "role": "assistant",
                "content": response["message"],
                "timestamp": response.get("timestamp")
            }
            
            if response.get("sources"):
                assistant_message["sources"] = response["sources"]
            
            st.session_state.messages.append(assistant_message)
            
            st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    # Helper text
    if not st.session_state.messages:
        st.info("""
        💡 **Tips:**
        - Ask questions about your uploaded documents
        - The chatbot uses RAG to find relevant information
        - You can continue conversations to maintain context
        """)


def render_chat_metrics():
    """Render chat metrics in sidebar."""
    st.sidebar.markdown("### 📊 Chat Stats")
    
    total_messages = len(st.session_state.messages)
    user_messages = sum(1 for m in st.session_state.messages if m["role"] == "user")
    
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Messages", total_messages)
    col2.metric("Your Questions", user_messages)