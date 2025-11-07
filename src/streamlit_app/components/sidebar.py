"""
Sidebar component - uses Streamlit's default navigation only.
"""
import streamlit as st


def render_sidebar():
    """
    Minimal sidebar - Streamlit handles navigation automatically.
    No custom elements, just default behavior.
    """
    # Only show sidebar if authenticated
    if not st.session_state.get("authenticated", False):
        return

    # Streamlit automatically shows navigation from pages/ folder
    # No need to add anything custom
    pass
