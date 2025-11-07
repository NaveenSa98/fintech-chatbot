"""
Authentication UI components.
Beautiful login and registration forms with persistent session.
"""
import streamlit as st
import json
from streamlit_app.api.auth_api import login, register, get_all_roles
from streamlit_app.components.utils import show_error, show_success
from streamlit_app.components.session_storage import save_session, load_session


def save_session_to_storage(token: str, user: dict):
    """Save session data to cookies for persistence."""
    try:
        # Save to session state
        st.session_state.authenticated = True
        st.session_state.token = token
        st.session_state.user = user
        st.session_state.persist_session = True

        # Save to cookies for persistence across refreshes
        save_session(token, user)
    except Exception as e:
        st.warning(f"Could not persist session: {e}")


def load_session_from_storage():
    """Try to load session from cookies."""
    try:
        # Check if session is already loaded in session state
        if st.session_state.get("authenticated"):
            return True

        # Try to load from cookies
        session_data = load_session()
        if session_data:
            st.session_state.authenticated = True
            st.session_state.token = session_data["token"]
            st.session_state.user = session_data["user"]
            st.session_state.persist_session = True
            return True

        return False
    except Exception as e:
        # Silently fail if cookies aren't ready yet
        return False


def render_login_form():
    """Render modern login form."""
    st.markdown("""
    <div class="auth-form-container">
        <h2 class="auth-form-title">🔐 Welcome Back</h2>
        <p class="auth-form-subtitle">Login to access your documents</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            "Email Address",
            placeholder="user@finsolve.com",
            key="login_email"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        remember_me = st.checkbox("Remember me", value=True)

        submit = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")

        if submit:
            if not email or not password:
                show_error("Please fill in all fields")
                return

            try:
                with st.spinner("🔄 Logging in..."):
                    response = login(email, password)

                # Store authentication data
                if remember_me:
                    save_session_to_storage(response["access_token"], response["user"])
                else:
                    st.session_state.authenticated = True
                    st.session_state.token = response["access_token"]
                    st.session_state.user = response["user"]
                    st.session_state.persist_session = False

                show_success(f"Welcome back, {response['user']['full_name']}!")
                st.rerun()

            except Exception as e:
                show_error(f"Login failed: {str(e)}")

    # Switch to register
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Don't have an account? Register", use_container_width=True, key="switch_to_register"):
            st.session_state.show_register = True
            st.rerun()


def render_register_form():
    """Render modern registration form."""
    st.markdown("""
    <div class="auth-form-container">
        <h2 class="auth-form-title">📝 Create Account</h2>
        <p class="auth-form-subtitle">Join our platform today</p>
    </div>
    """, unsafe_allow_html=True)

    # Get available roles
    try:
        roles_response = get_all_roles()
        roles = [role["role"] for role in roles_response]
    except:
        roles = ["Finance", "Marketing", "HR", "Engineering", "Employee"]

    with st.form("register_form", clear_on_submit=False):
        full_name = st.text_input(
            "Full Name",
            placeholder="John Doe",
            key="register_name"
        )

        email = st.text_input(
            "Email Address",
            placeholder="john@finsolve.com",
            key="register_email"
        )

        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 8 characters",
                key="register_password"
            )
        with col2:
            password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter password",
                key="register_password_confirm"
            )

        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox("Role", roles, key="register_role")
        with col2:
            # Set default department based on role
            default_dept = "Administration" if role == "C-Level" else role
            department = st.text_input(
                "Department",
                value=default_dept,
                help="C-Level role automatically uses Administration department",
                key="register_department"
            )

        submit = st.form_submit_button("✨ Create Account", use_container_width=True, type="primary")

        if submit:
            # Force C-Level to use Administration department
            if role == "C-Level":
                department = "Administration"

            # Validation
            if not all([full_name, email, password, password_confirm, role, department]):
                show_error("Please fill in all fields")
                return

            if password != password_confirm:
                show_error("Passwords do not match")
                return

            if len(password) < 8:
                show_error("Password must be at least 8 characters")
                return

            try:
                with st.spinner("🔄 Creating account..."):
                    register(email, password, full_name, role, department)

                show_success("Account created successfully! Please login.")
                st.session_state.show_register = False
                st.rerun()

            except Exception as e:
                show_error(f"Registration failed: {str(e)}")

    # Switch to login
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Already have an account? Login", use_container_width=True, key="switch_to_login"):
            st.session_state.show_register = False
            st.rerun()


def render_auth_page():
    """
    Render complete authentication page.
    Shows login or register form based on state.
    """
    # Try to restore session
    if load_session_from_storage():
        st.rerun()

    # Initialize state
    if "show_register" not in st.session_state:
        st.session_state.show_register = False

    # Modern header
    st.markdown("""
    <div class="auth-header">
        <div class="auth-logo">
            <h1>FinTech Chatbot</h1>
        </div>
        <p class="auth-tagline">AI-Powered Document Assistant</p>
        <p class="auth-description">Secure document management with role-based access control</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Create centered form container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.session_state.show_register:
            render_register_form()
        else:
            render_login_form()

    # Features footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-features">
        <div class="feature-item">
            <span class="feature-icon">🤖</span>
            <span class="feature-text">RAG-Powered AI</span>
        </div>
        <div class="feature-item">
            <span class="feature-icon">📁</span>
            <span class="feature-text">Document Management</span>
        </div>
        <div class="feature-item">
            <span class="feature-icon">💬</span>
            <span class="feature-text">Chat History</span>
        </div>
        <div class="feature-item">
            <span class="feature-icon">🔒</span>
            <span class="feature-text">Secure Access</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
