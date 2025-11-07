"""
Documents page - Upload and manage documents.
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
    apply_custom_css, show_success, show_error, format_datetime, format_file_size,
    ROLE_PERMISSIONS
)
from streamlit_app.api.document_api import upload_document, list_documents, delete_document


# Page configuration
st.set_page_config(
    page_title="Documents - FinSolve",
    page_icon="📁",
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
st.markdown('<h1 class="page-title">📁 Document Management</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Upload, search, and manage your company documents</p>', unsafe_allow_html=True)

st.markdown("---")

# Get user role
user_role = st.session_state.user['role']
user_dept = st.session_state.user['department']

# Only C-Level can upload documents
if user_role == "C-Level":
    # Tabs for different sections
    tab1, tab2 = st.tabs(["📤 Upload Document", "📚 My Documents"])

    # Tab 1: Upload documents (C-Level only)
    with tab1:
        st.markdown("### Upload New Document")
        st.info("ℹ️ As a C-Level user, you can upload documents to any department.")

        # C-Level can upload to all departments
        accessible_depts = ["Finance", "Marketing", "HR", "Engineering", "General"]

        with st.form("upload_form"):
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["pdf", "docx", "csv", "xlsx"],
                help="Supported formats: PDF, DOCX, CSV, XLSX (Max 200MB)"
            )

            department = st.selectbox(
                "Department",
                options=accessible_depts,
                help="Select the department this document belongs to"
            )

            description = st.text_area(
                "Description (Optional)",
                placeholder="Brief description of the document...",
                height=100
            )

            submit = st.form_submit_button("📤 Upload Document", use_container_width=True, type="primary")

            if submit:
                if not uploaded_file:
                    show_error("Please select a file to upload")
                else:
                    # Check file size (200MB = 10 * 1024 * 1024 bytes)
                    max_size = 10 * 1024 * 1024
                    file_bytes = uploaded_file.read()

                    if len(file_bytes) > max_size:
                        show_error(f"File size exceeds 10MB limit. Your file is {format_file_size(len(file_bytes))}")
                    else:
                        try:
                            with st.spinner("📤 Uploading and processing document..."):
                                response = upload_document(
                                    file_bytes=file_bytes,
                                    filename=uploaded_file.name,
                                    department=department,
                                    description=description
                                )

                            show_success(f"Document '{uploaded_file.name}' uploaded successfully!")

                            is_processed = response.get('is_processed', False)
                            chunk_count = response.get('chunk_count', 0)

                            if is_processed and chunk_count > 0:
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.info(f"📊 Status: ✅ Processed")
                                with col2:
                                    st.info(f"🔢 Chunks created: {chunk_count}")
                            else:
                                st.info("⏳ Document uploaded. Processing will begin shortly. Chunks will be created after processing completes.")

                            st.balloons()

                        except Exception as e:
                            show_error(f"Upload failed: {str(e)}")

        # File requirements info
        st.markdown("""
        <div style="background: #F3F4F6; padding: 16px; border-radius: 8px; margin-top: 16px;">
            <p style="margin: 0; color: #6B7280; font-size: 14px;">
                📋 <strong>Limit:</strong> 10MB per file • <strong>Formats:</strong> PDF, DOCX, CSV, XLSX
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Tab 2: Document list
    with tab2:
        st.markdown("### Your Documents")

        try:
            # Load documents with loading state
            with st.spinner("Loading documents..."):
                response = list_documents(limit=100)
                documents = response.get("documents", [])

            if not documents:
                st.info("📭 No documents uploaded yet. Use the Upload tab to add documents.")
            else:
                # Add search filter
                search_term = st.text_input("🔍 Search documents", placeholder="Filter by filename or department...")

                # Filter documents
                filtered_docs = documents
                if search_term:
                    filtered_docs = [
                        doc for doc in documents
                        if search_term.lower() in doc.get('filename', '').lower()
                        or search_term.lower() in doc.get('original_filename', '').lower()
                        or search_term.lower() in doc.get('department', '').lower()
                        or search_term.lower() in doc.get('description', '').lower()
                    ]

                st.markdown(f"**Showing {len(filtered_docs)} of {len(documents)} document(s)**")
                st.markdown("<br>", unsafe_allow_html=True)

                # Display documents in improved cards
                for doc in filtered_docs:
                    st.markdown(f"""
                    <div class="document-card-header">
                        <div class="doc-icon">📄</div>
                        <div class="doc-title">{doc.get('original_filename', doc.get('filename', 'Unknown'))}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.markdown(f"**📁 Department:** {doc.get('department', 'N/A')}")
                        st.markdown(f"**📎 Type:** {doc.get('file_type', 'unknown').upper()}")
                        st.markdown(f"**📏 Size:** {format_file_size(doc.get('file_size', 0))}")

                    with col2:
                        st.markdown(f"**📅 Uploaded:** {format_datetime(doc.get('uploaded_at', 'N/A'))}")
                        if doc.get('description'):
                            st.markdown(f"**📝 Description:** {doc['description'][:50]}...")

                        # Processing status
                        if doc.get('is_processed', False):
                            st.success(f"✅ Processed | {doc.get('chunk_count', 0)} chunks")
                        else:
                            st.warning("⏳ Processing...")

                    with col3:
                        if st.button("🗑️ Delete", key=f"del_{doc['id']}", use_container_width=True):
                            if st.session_state.get(f"confirm_delete_{doc['id']}", False):
                                try:
                                    delete_document(doc['id'])
                                    show_success("Document deleted!")
                                    st.rerun()
                                except Exception as e:
                                    show_error(f"Delete failed: {str(e)}")
                            else:
                                st.session_state[f"confirm_delete_{doc['id']}"] = True
                                st.warning("⚠️ Click again to confirm")

                    st.markdown("---")

        except Exception as e:
            st.error("❌ Failed to load documents. Please ensure the backend API is running.")
            st.info("💡 Tip: Make sure the backend server is running on port 8000.")

else:
    # Non-C-Level users: Only show document list
    st.info("ℹ️ Only C-Level users can upload documents. You can view documents below.")
    st.markdown("---")

    st.markdown("### Your Documents")

    try:
        # Load documents with loading state
        with st.spinner("Loading documents..."):
            response = list_documents(limit=100)
            documents = response.get("documents", [])

        if not documents:
            st.info("📭 No documents available yet.")
        else:
            # Add search filter
            search_term = st.text_input("🔍 Search documents", placeholder="Filter by filename or department...")

            # Filter documents
            filtered_docs = documents
            if search_term:
                filtered_docs = [
                    doc for doc in documents
                    if search_term.lower() in doc.get('filename', '').lower()
                    or search_term.lower() in doc.get('original_filename', '').lower()
                    or search_term.lower() in doc.get('department', '').lower()
                    or search_term.lower() in doc.get('description', '').lower()
                ]

            st.markdown(f"**Showing {len(filtered_docs)} of {len(documents)} document(s)**")
            st.markdown("<br>", unsafe_allow_html=True)

            # Display documents in improved cards
            for doc in filtered_docs:
                st.markdown(f"""
                <div class="document-card-header">
                    <div class="doc-icon">📄</div>
                    <div class="doc-title">{doc.get('original_filename', doc.get('filename', 'Unknown'))}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([3, 2])

                with col1:
                    st.markdown(f"**📁 Department:** {doc.get('department', 'N/A')}")
                    st.markdown(f"**📎 Type:** {doc.get('file_type', 'unknown').upper()}")
                    st.markdown(f"**📏 Size:** {format_file_size(doc.get('file_size', 0))}")

                with col2:
                    st.markdown(f"**📅 Uploaded:** {format_datetime(doc.get('uploaded_at', 'N/A'))}")
                    if doc.get('description'):
                        st.markdown(f"**📝 Description:** {doc['description'][:50]}...")

                    # Processing status
                    if doc.get('is_processed', False):
                        st.success(f"✅ Processed | {doc.get('chunk_count', 0)} chunks")
                    else:
                        st.warning("⏳ Processing...")

                st.markdown("---")

    except Exception as e:
        st.error("❌ Failed to load documents. Please ensure the backend API is running.")
        st.info("💡 Tip: Make sure the backend server is running on port 8000.")

# Document statistics
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<h2 class="section-title">📊 Statistics</h2>', unsafe_allow_html=True)

try:
    with st.spinner("Loading statistics..."):
        response = list_documents()
        docs = response.get("documents", [])

    if docs:
        col1, col2, col3, col4 = st.columns(4)

        processed = sum(1 for doc in docs if doc.get('is_processed', False))
        total_size = sum(doc.get('file_size', 0) for doc in docs)
        total_chunks = sum(doc.get('chunk_count', 0) for doc in docs)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📚</div>
                <div class="metric-content">
                    <p class="metric-label">Total Documents</p>
                    <p class="metric-value">{len(docs)}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">✅</div>
                <div class="metric-content">
                    <p class="metric-label">Processed</p>
                    <p class="metric-value">{processed}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">💾</div>
                <div class="metric-content">
                    <p class="metric-label">Total Size</p>
                    <p class="metric-value">{format_file_size(total_size)}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🔢</div>
                <div class="metric-content">
                    <p class="metric-label">Total Chunks</p>
                    <p class="metric-value">{total_chunks}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 No documents available yet. Statistics will appear once documents are uploaded.")

except Exception as e:
    st.warning("⚠️ Unable to load statistics. Backend may be unavailable.")
