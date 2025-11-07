"""
API Client for Streamlit frontend.
Handles all HTTP requests to the FastAPI backend.
"""
import requests
from typing import Dict, Any, Optional
import streamlit as st


class APIClient:
    """
    HTTP client for communicating with FastAPI backend.
    Manages authentication tokens and request/response handling.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the FastAPI backend
        """
        self.base_url = base_url
        self.timeout = 30  # Request timeout in seconds
    
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """
        Get request headers with optional authentication.
        
        Args:
            include_auth: Whether to include auth token
            
        Returns:
            Dictionary of headers
        """
        headers = {"Content-Type": "application/json"}
        
        if include_auth and "token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.token}"
        
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and errors.
        
        Args:
            response: HTTP response object
            
        Returns:
            Parsed JSON response
            
        Raises:
            Exception: If request failed
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = response.json().get("detail", str(e))
            raise Exception(f"API Error: {error_detail}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make GET request.
        
        Args:
            endpoint: API endpoint (e.g., "/documents")
            params: Query parameters
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=self.timeout
        )
        
        return self._handle_response(response)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        include_auth: bool = True
    ) -> Dict[str, Any]:
        """
        Make POST request.
        
        Args:
            endpoint: API endpoint
            data: Request body data
            files: Files to upload
            include_auth: Whether to include authentication
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        
        if files:
            # For file uploads, don't set Content-Type (let requests handle it)
            headers = {}
            if include_auth and "token" in st.session_state:
                headers["Authorization"] = f"Bearer {st.session_state.token}"
            
            response = requests.post(
                url,
                headers=headers,
                data=data,
                files=files,
                timeout=self.timeout
            )
        else:
            headers = self._get_headers(include_auth)
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
        
        return self._handle_response(response)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make DELETE request.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        response = requests.delete(
            url,
            headers=headers,
            timeout=self.timeout
        )
        
        return self._handle_response(response)
    
    def patch(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """
        Make PATCH request.
        
        Args:
            endpoint: API endpoint
            data: Request body data
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        response = requests.patch(
            url,
            headers=headers,
            json=data,
            timeout=self.timeout
        )
        
        return self._handle_response(response)


# Global client instance
def get_api_client() -> APIClient:
    """
    Get the global API client instance.
    
    Returns:
        APIClient instance
    """
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient()
    
    return st.session_state.api_client
    