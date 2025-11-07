"""
Utility functions for Streamlit UI components.
"""
import streamlit as st
from datetime import datetime
from typing import Optional
from pathlib import Path


# Role permissions configuration (replicated to avoid core.config dependency)
ROLE_PERMISSIONS = {
    "Finance": ["view_finance", "upload_finance", "chat"],
    "Marketing": ["view_marketing", "upload_marketing", "chat"],
    "HR": ["view_hr", "upload_hr", "chat"],
    "Engineering": ["view_engineering", "upload_engineering", "chat"],
    "C-Level": ["view_all", "upload_all", "chat", "analytics", "admin"],
    "Employee": ["chat", "view_public"]
}


def init_session_state():
    """Initialize session state variables with default values."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "user" not in st.session_state:
        st.session_state.user = None

    if "token" not in st.session_state:
        st.session_state.token = None

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []


def restore_session_from_cookies():
    """
    Restore authentication session from cookies if available.
    Call this AFTER set_page_config() and init_session_state().
    """
    try:
        # Only restore if not already authenticated
        if not st.session_state.get("authenticated"):
            from streamlit_app.components.session_storage import load_session
            session_data = load_session()
            if session_data:
                st.session_state.authenticated = True
                st.session_state.token = session_data["token"]
                st.session_state.user = session_data["user"]
                st.session_state.persist_session = True
    except:
        # Silently fail if cookies not ready
        pass


def check_authentication() -> bool:
    """
    Check if user is authenticated.
    Redirects to login if not.
    
    Returns:
        True if authenticated, False otherwise
    """
    init_session_state()
    
    if not st.session_state.authenticated:
        st.warning("⚠️ Please login to access this page")
        st.stop()
        return False
    
    return True


def logout():
    """Logout user and clear session state and cookies."""
    # Clear session state
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None
    st.session_state.conversation_id = None
    st.session_state.messages = []
    st.session_state.persist_session = False

    # Clear cookies
    try:
        from streamlit_app.components.session_storage import clear_session
        clear_session()
    except:
        pass  # Silently fail if cookies not available

    st.success("✅ Logged out successfully!")
    st.rerun()


def format_datetime(dt: str) -> str:
    """
    Format datetime string for display.
    
    Args:
        dt: ISO format datetime string
        
    Returns:
        Formatted datetime string
    """
    try:
        parsed = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        return parsed.strftime("%b %d, %Y %I:%M %p")
    except:
        return dt


def format_file_size(size_bytes: int) -> str:
    """
    Format file size for display.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def show_success(message: str):
    """Show success message."""
    st.success(f"✅ {message}")


def show_error(message: str):
    """Show error message."""
    st.error(f"❌ {message}")


def show_info(message: str):
    """Show info message."""
    st.info(f"ℹ️ {message}")


def show_warning(message: str):
    """Show warning message."""
    st.warning(f"⚠️ {message}")


def get_role_badge(role: str) -> str:
    """
    Get badge HTML for role.
    
    Args:
        role: User role
        
    Returns:
        HTML badge string
    """
    colors = {
        "Finance": "#10B981",
        "Marketing": "#F59E0B",
        "HR": "#8B5CF6",
        "Engineering": "#3B82F6",
        "C-Level": "#EF4444",
        "Employee": "#6B7280"
    }
    
    color = colors.get(role, "#6B7280")
    
    return f"""
    <span style="
        background-color: {color}; 
        color: white; 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-size: 12px;
        font-weight: bold;
    ">
        {role}
    </span>
    """


def render_source_card(source: dict):
    """
    Render a source document card (without expander to avoid nesting).

    Args:
        source: Source document dictionary
    """
    # Render as a simple card instead of expander
    st.markdown(f"""
    <div style="background: #F3F4F6; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 3px solid #3B82F6;">
        <div style="font-weight: bold; color: #1F2937; margin-bottom: 4px;">
            📄 {source['document_name']} ({source['department']})
        </div>
        <div style="font-size: 12px; color: #6B7280; margin-bottom: 8px;">
            Relevance: {source['relevance_score']:.3f}
        </div>
        <div style="font-size: 13px; color: #374151; background: white; padding: 8px; border-radius: 4px; max-height: 100px; overflow-y: auto;">
            {source['content'][:300] + "..." if len(source['content']) > 300 else source['content']}
        </div>
    </div>
    """, unsafe_allow_html=True)


def load_custom_css():
    """Load custom CSS from file."""
    css_file = Path(__file__).parent.parent / "styles" / "main.css"
    
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def apply_custom_css():
    """Apply custom CSS styling."""
    # Hide sidebar completely on auth pages FIRST (before loading other CSS)
    if not st.session_state.get("authenticated", False):
        st.markdown("""
        <style>
        /* Aggressively hide sidebar on authentication pages - prevent flash */
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > *,
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        button[kind="header"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
        }
        /* Center content when sidebar is hidden */
        .main > div {
            max-width: 100% !important;
            padding-top: 2rem;
        }
        /* Hide sidebar toggle button */
        button[kind="header"][aria-label*="sidebar"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Load CSS from file after hiding sidebar
    load_custom_css()

    if st.session_state.get("authenticated", False):
        # Additional inline CSS for authenticated users
        st.markdown("""
        <style>
        .main > div {
            padding-top: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)