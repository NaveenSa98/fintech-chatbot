"""
Document uploader component.
Reusable document upload interface.
"""
import streamlit as st
from streamlit_app.api.document_api import upload_document
from streamlit_app.components.utils import show_success, show_error
from core.config import ROLE_PERMISSIONS


def render_document_uploader(show_recent: bool = True):
    """
    Render document upload interface.
    
    Args:
        show_recent: Whether to show recently uploaded documents
    """
    st.markdown("### 📤 Upload Document")
    
    # Get accessible departments
    user_role = st.session_state.user['role']
    accessible_depts = ROLE_PERMISSIONS.get(user_role, {}).get("departments", [])
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt", "xlsx","csv"],
        help="Max size: 10MB"
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            department = st.selectbox("Department", accessible_depts)
        
        with col2:
            description = st.text_input("Description (optional)")
        
        if st.button("Upload", use_container_width=True):
            try:
                with st.spinner("Uploading..."):
                    file_bytes = uploaded_file.read()
                    
                    response = upload_document(
                        file_bytes=file_bytes,
                        filename=uploaded_file.name,
                        department=department,
                        description=description
                    )
                
                show_success(f"Uploaded '{uploaded_file.name}'!")
                st.info(f"Chunks: {response['chunks_count']}")
                
                if show_recent:
                    st.rerun()
            
            except Exception as e:
                show_error(str(e))