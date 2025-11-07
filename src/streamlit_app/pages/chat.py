"""
Chat page - Main conversational interface.
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).resolve().parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.chat_interface import render_chat_interface, render_chat_metrics
from streamlit_app.components.utils import init_session_state, restore_session_from_cookies, check_authentication, apply_custom_css


# Page configuration
st.set_page_config(
    page_title="Chat - FinSolve",
    page_icon="💬",
    layout="wide"
)

# Initialize and restore session
init_session_state()
restore_session_from_cookies()

# Apply custom CSS
apply_custom_css()

# Check authentication
check_authentication()

# Render sidebar
render_sidebar()

# Render chat metrics in sidebar
render_chat_metrics()

# Main content
st.title("AI Chat Assistant")
st.markdown("Ask questions about your documents and get AI-powered responses with source citations.")

st.markdown("---")

# Render chat interface
render_chat_interface()