"""
Analytics page - Admin dashboard (C-Level only).
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).resolve().parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.utils import init_session_state, restore_session_from_cookies, check_authentication, apply_custom_css
from streamlit_app.api.document_api import get_collection_stats
from streamlit_app.api.chat_api import list_conversations, check_chat_health
import plotly.graph_objects as go
import plotly.express as px


# Page configuration
st.set_page_config(
    page_title="Analytics - FinSolve",
    page_icon="📊",
    layout="wide"
)

# Initialize and restore session
init_session_state()
restore_session_from_cookies()

# Apply custom CSS
apply_custom_css()

# Check authentication
check_authentication()

# Check if user is C-Level
if st.session_state.user['role'] != "C-Level":
    st.error("⛔ Access Denied: This page is only accessible to C-Level users")
    st.stop()

# Render sidebar
render_sidebar()

# Main content
st.markdown('<h1 class="page-title">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Comprehensive overview of system usage and performance</p>', unsafe_allow_html=True)

st.markdown("---")

# Metrics row with loading
st.markdown("### 📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with st.spinner("Loading metrics..."):
    try:
        # Get collection stats with timeout handling
        stats = get_collection_stats()
        total_docs = sum(stat['document_count'] for stat in stats)
        active_collections = sum(1 for stat in stats if stat['document_count'] > 0)

        # Get conversations
        try:
            conv_response = list_conversations(limit=1000)
            total_conversations = conv_response.get("total", 0)
        except:
            total_conversations = "N/A"

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📚</div>
                <div class="metric-content">
                    <p class="metric-label">Total Documents</p>
                    <p class="metric-value">{total_docs}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">💬</div>
                <div class="metric-content">
                    <p class="metric-label">Conversations</p>
                    <p class="metric-value">{total_conversations}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🗂️</div>
                <div class="metric-content">
                    <p class="metric-label">Active Collections</p>
                    <p class="metric-value">{active_collections}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-icon">👥</div>
                <div class="metric-content">
                    <p class="metric-label">Active Users</p>
                    <p class="metric-value">-</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Failed to load metrics. Please ensure the backend API is running.")
        st.stop()

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📁 Documents by Department")

    try:
        stats = get_collection_stats()

        if stats and any(stat['document_count'] > 0 for stat in stats):
            departments = [stat['department'] for stat in stats]
            counts = [stat['document_count'] for stat in stats]

            fig = go.Figure(data=[
                go.Bar(
                    x=departments,
                    y=counts,
                    marker_color='#3B82F6',
                    marker_line_color='#2563EB',
                    marker_line_width=1.5
                )
            ])

            fig.update_layout(
                xaxis_title="Department",
                yaxis_title="Document Count",
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="sans-serif", size=12)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📭 No documents available yet")

    except Exception as e:
        st.warning("⚠️ Unable to load chart. Backend may be unavailable.")

with col2:
    st.markdown("### 🥧 Department Distribution")

    try:
        stats = get_collection_stats()

        departments = [stat['department'] for stat in stats if stat['document_count'] > 0]
        counts = [stat['document_count'] for stat in stats if stat['document_count'] > 0]

        if departments and counts:
            fig = go.Figure(data=[
                go.Pie(
                    labels=departments,
                    values=counts,
                    hole=0.4,
                    marker=dict(colors=px.colors.qualitative.Set3)
                )
            ])

            fig.update_layout(
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="sans-serif", size=12)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📭 No documents to display")

    except Exception as e:
        st.warning("⚠️ Unable to load chart. Backend may be unavailable.")

st.markdown("---")

# Collection details table - only show active collections
st.markdown("### 📊 Collection Statistics")

try:
    stats = get_collection_stats()

    if stats:
        # Create table data - only include collections with documents
        table_data = []
        for stat in stats:
            if stat['document_count'] > 0:  # Only add rows with documents
                table_data.append({
                    "Department": stat['department'],
                    "Collection": stat['collection_name'],
                    "Documents": stat['document_count'],
                    "Status": "✅ Active"
                })

        if table_data:
            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True,
                height=min(len(table_data) * 40 + 50, 300)  # Dynamic height based on rows
            )
        else:
            st.info("📭 No active collections with documents yet")
    else:
        st.info("No collection data available")

except Exception as e:
    st.warning("⚠️ Unable to load statistics table")

# System health
st.markdown("---")
st.markdown("### 🏥 System Health")

try:
    with st.spinner("Checking system health..."):
        health = check_chat_health()

        col1, col2, col3 = st.columns(3)

        with col1:
            status = health.get('status', 'unknown')
            status_icon = "🟢" if status == "healthy" else "🟡"
            st.markdown(f"""
            <div class="health-card-small">
                <p class="health-label-small">Overall Status</p>
                <p class="health-value-small">{status_icon} {status.upper()}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            llm_status = health.get('llm_available', False)
            llm_icon = "✅" if llm_status else "❌"
            st.markdown(f"""
            <div class="health-card-small">
                <p class="health-label-small">LLM Status</p>
                <p class="health-value-small">{llm_icon} {'Online' if llm_status else 'Offline'}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            vector_status = health.get('vector_store_available', False)
            vector_icon = "✅" if vector_status else "❌"
            st.markdown(f"""
            <div class="health-card-small">
                <p class="health-label-small">Vector Store</p>
                <p class="health-value-small">{vector_icon} {'Online' if vector_status else 'Offline'}</p>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error("⚠️ Health check unavailable. Please ensure the backend API is running.")
