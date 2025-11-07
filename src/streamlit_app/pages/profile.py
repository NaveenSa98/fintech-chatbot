"""
Profile page - User profile and settings.
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).resolve().parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.utils import (
    init_session_state, restore_session_from_cookies, check_authentication,
    apply_custom_css, get_role_badge, format_datetime, ROLE_PERMISSIONS
)


# Page configuration
st.set_page_config(
    page_title="Profile - FinSolve",
    page_icon="👤",
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

# Main content
st.markdown('<h1 class="page-title">👤 User Profile</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Your account information and permissions</p>', unsafe_allow_html=True)

st.markdown("---")

# Profile information
user = st.session_state.user

# Profile header card
st.markdown(f"""
<div class="document-card-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
    <div style="display: flex; align-items: center; gap: 1.5rem;">
        <div style="font-size: 80px;">👤</div>
        <div>
            <h2 style="color: white; margin: 0; font-size: 2rem;">{user['full_name']}</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">{user['email']}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Account details in cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🎭</div>
        <div class="metric-content">
            <p class="metric-label">Role</p>
            <p class="metric-value" style="font-size: 1.2rem;">{user['role']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🏢</div>
        <div class="metric-content">
            <p class="metric-label">Department</p>
            <p class="metric-value" style="font-size: 1.2rem;">{user['department']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    status_icon = "✅" if user['is_active'] else "❌"
    status_text = "Active" if user['is_active'] else "Inactive"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{status_icon}</div>
        <div class="metric-content">
            <p class="metric-label">Status</p>
            <p class="metric-value" style="font-size: 1.2rem;">{status_text}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    verified_icon = "✅" if user.get('is_verified', True) else "⏳"
    verified_text = "Verified" if user.get('is_verified', True) else "Pending"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{verified_icon}</div>
        <div class="metric-content">
            <p class="metric-label">Verified</p>
            <p class="metric-value" style="font-size: 1.2rem;">{verified_text}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Role permissions
st.markdown('<h2 class="section-title">🔐 Your Permissions</h2>', unsafe_allow_html=True)

user_role = user['role']
role_info = ROLE_PERMISSIONS.get(user_role, {})

# Determine accessible departments
if user_role == "C-Level":
    accessible_depts = ["Finance", "Marketing", "HR", "Engineering", "General"]
    description = "Full access to all departments and analytics"
elif user_role == "Employee":
    accessible_depts = ["General"]
    description = "Access to general company documents and chat"
else:
    accessible_depts = [user['department']]
    description = f"Access to {user['department']} department documents and chat"

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("**Accessible Departments:**")
    for dept in accessible_depts:
        st.markdown(f"- ✅ {dept}")

with col2:
    st.markdown("**Description:**")
    st.info(description)

# Activity statistics
st.markdown("---")
st.markdown('<h2 class="section-title">📊 Your Activity</h2>', unsafe_allow_html=True)

try:
    from streamlit_app.api.chat_api import list_conversations
    from streamlit_app.api.document_api import list_documents

    with st.spinner("Loading statistics..."):
        conv_response = list_conversations()
        doc_response = list_documents()

    col1, col2, col3 = st.columns(3)

    conversations = conv_response.get("conversations", [])
    total_messages = sum(conv.get("message_count", 0) for conv in conversations)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💬</div>
            <div class="metric-content">
                <p class="metric-label">Conversations</p>
                <p class="metric-value">{conv_response.get("total", 0)}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📁</div>
            <div class="metric-content">
                <p class="metric-label">Documents</p>
                <p class="metric-value">{doc_response.get("total", 0)}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💭</div>
            <div class="metric-content">
                <p class="metric-label">Messages</p>
                <p class="metric-value">{total_messages}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.warning("⚠️ Unable to load activity statistics")

# Account information
st.markdown("---")
st.markdown('<h2 class="section-title">ℹ️ Account Information</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-content">
            <p class="metric-label">Account Created</p>
            <p style="font-size: 1rem; color: #666;">{format_datetime(user.get('created_at', 'N/A'))}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-content">
            <p class="metric-label">User ID</p>
            <p style="font-size: 1rem; color: #666; font-family: monospace;">{user['id']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Logout button
st.markdown("---")
if st.button("🚪 Logout", use_container_width=True, type="primary"):
    from streamlit_app.components.utils import logout
    logout()
