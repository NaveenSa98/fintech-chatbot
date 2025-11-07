"""
Session storage module for persisting authentication across page refreshes.
Uses browser cookies via extra_streamlit_components.
"""
import json
from typing import Optional, Dict, Any
import extra_streamlit_components as stx


# Initialize cookie manager with a unique key
def get_cookie_manager():
    """Get or create cookie manager instance."""
    return stx.CookieManager(key="cookie_manager")


def save_session(token: str, user: Dict[str, Any]) -> None:
    """
    Save authentication session to cookies.

    Args:
        token: JWT access token
        user: User data dictionary
    """
    cookie_manager = get_cookie_manager()

    # Store token and user separately for better management
    cookie_manager.set("auth_token", token, expires_at=None, key="set_auth_token")
    cookie_manager.set("user_data", json.dumps(user), expires_at=None, key="set_user_data")


def load_session() -> Optional[Dict[str, Any]]:
    """
    Load authentication session from cookies.

    Returns:
        Session data dictionary with 'token' and 'user' keys, or None
    """
    cookie_manager = get_cookie_manager()

    # Get cookies - this returns immediately with current values
    token = cookie_manager.get("auth_token")
    user_data_str = cookie_manager.get("user_data")

    if token and user_data_str:
        try:
            user = json.loads(user_data_str)
            return {
                "token": token,
                "user": user,
                "authenticated": True
            }
        except json.JSONDecodeError:
            return None

    return None


def clear_session() -> None:
    """Clear authentication session from cookies."""
    cookie_manager = get_cookie_manager()

    # Delete cookies
    cookie_manager.delete("auth_token", key="del_auth_token")
    cookie_manager.delete("user_data", key="del_user_data")
