
"""
Simple test script to verify API functionality.
Run this after starting the server.

Usage:
    python test_api.py
"""
import requests
import json


BASE_URL = "http://localhost:8000/api/v1"


def test_health_check():
    """Test if server is running."""
    print("🔍 Testing health check...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {response.json()}\n")
        return True
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def test_get_roles():
    """Test getting all roles."""
    print("🔍 Testing get all roles...")
    try:
        response = requests.get(f"{BASE_URL}/auth/roles")
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Available roles: {len(response.json())} roles")
        for role in response.json():
            print(f"   - {role['role']}: {role['description']}")
        print()
        return True
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def test_register_user():
    """Test user registration."""
    print("🔍 Testing user registration...")
    
    user_data = {
        "email": "test.user@finsolve.com",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "Finance",
        "department": "Finance Team"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data
        )
        
        if response.status_code == 201:
            print(f"✅ User registered successfully!")
            print(f"📄 User data: {json.dumps(response.json(), indent=2)}\n")
            return True
        elif response.status_code == 400:
            print(f"⚠️  User might already exist: {response.json()['detail']}\n")
            return True
        else:
            print(f"❌ Error: {response.json()}\n")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def test_login():
    """Test user login."""
    print("🔍 Testing user login...")
    
    credentials = {
        "email": "test.user@finsolve.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=credentials
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"🔑 Token (first 50 chars): {data['access_token'][:50]}...")
            print(f"👤 User: {data['user']['full_name']} ({data['user']['role']})\n")
            return data['access_token']
        else:
            print(f"❌ Login failed: {response.json()}\n")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return None


def test_get_current_user(token):
    """Test getting current user info with token."""
    print("🔍 Testing get current user...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Current user retrieved successfully!")
            print(f"📄 User data: {json.dumps(response.json(), indent=2)}\n")
            return True
        else:
            print(f"❌ Error: {response.json()}\n")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def test_logout(token):
    """Test logout."""
    print("🔍 Testing logout...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Logout successful!")
            print(f"📄 Response: {response.json()['message']}\n")
            return True
        else:
            print(f"❌ Error: {response.json()}\n")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 FinSolve RBAC Chatbot - API Test Suite")
    print("=" * 60 + "\n")
    
    # Test 1: Health check
    if not test_health_check():
        print("❌ Server is not running. Please start the server first.")
        return
    
    # Test 2: Get roles
    test_get_roles()
    
    # Test 3: Register user
    test_register_user()
    
    # Test 4: Login
    token = test_login()
    if not token:
        print("❌ Cannot proceed without token")
        return
    
    # Test 5: Get current user
    test_get_current_user(token)
    
    # Test 6: Logout
    test_logout(token)
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()