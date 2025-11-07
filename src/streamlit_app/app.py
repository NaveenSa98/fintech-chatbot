"""
Main Streamlit application entry point.
This is the home page that users see first.
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).resolve().parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
from streamlit_app.components.auth import render_auth_page
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.utils import init_session_state, restore_session_from_cookies, apply_custom_css

# IMPORTANT: set_page_config MUST be the first Streamlit command
st.set_page_config(
    page_title="FinTech Chatbot",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
init_session_state()

# Restore session from cookies if available
restore_session_from_cookies()

# Apply custom CSS
apply_custom_css()


def main():
    """Main application logic."""
    
    # Check if user is authenticated
    if not st.session_state.authenticated:
        # Show authentication page
        render_auth_page()
    else:
        # Show sidebar
        render_sidebar()
        
        # Welcome page
        st.markdown("""
        <div class="welcome-header">
            <h1>Welcome to FinTech Chatbot!</h1>
            <p class="welcome-subtitle">Your AI-powered document assistant</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # User info section - improved UX
        st.markdown("""
        <div class="user-info-section">
            <div class="user-info-header">
                <span class="user-avatar">👤</span>
                <div class="user-details">
                    <h2 class="user-name">{}</h2>
                    <p class="user-email">{}</p>
                </div>
            </div>
        </div>
        """.format(
            st.session_state.user['full_name'],
            st.session_state.user['email']
        ), unsafe_allow_html=True)

        # User stats in compact cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-icon">🎭</div>
                <div class="stat-content">
                    <p class="stat-label">Role</p>
                    <p class="stat-value">{}</p>
                </div>
            </div>
            """.format(st.session_state.user['role']), unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-icon">🏢</div>
                <div class="stat-content">
                    <p class="stat-label">Department</p>
                    <p class="stat-value">{}</p>
                </div>
            </div>
            """.format(st.session_state.user['department']), unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="stat-card stat-active">
                <div class="stat-icon">✅</div>
                <div class="stat-content">
                    <p class="stat-label">Status</p>
                    <p class="stat-value">Active</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick actions
        st.markdown('<h2 class="section-title">🚀 Quick Actions</h2>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="quick-action-card">
                <div class="card-icon">💬</div>
                <h3>Start Chatting</h3>
                <p>Ask questions about your documents using AI</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Go to Chat", key="chat_btn", use_container_width=True):
                st.switch_page("pages/chat.py")

        with col2:
            st.markdown("""
            <div class="quick-action-card">
                <div class="card-icon">📁</div>
                <h3>Manage Documents</h3>
                <p>Upload and organize your company documents</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Go to Documents", key="docs_btn", use_container_width=True):
                st.switch_page("pages/documents.py")

        with col3:
            st.markdown("""
            <div class="quick-action-card">
                <div class="card-icon">👤</div>
                <h3>Your Profile</h3>
                <p>View your profile information</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Go to Profile", key="profile_btn", use_container_width=True):
                st.switch_page("pages/profile.py")


if __name__ == "__main__":
    main()