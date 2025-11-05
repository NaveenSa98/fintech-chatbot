"""
Test script for Phase 3: RAG & LLM Integration.
Tests the complete chatbot functionality.

Usage:
    python test_chat.py
"""
import requests
import json
from typing import Optional


BASE_URL = "http://localhost:8000/api/v1"


def login(email: str, password: str) -> Optional[str]:
    """Login and get token."""
    print(f"\n🔐 Logging in as {email}...")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.json()}")
        return None


def check_chat_health(token: str):
    """Check if chat system is healthy."""
    print("\n🏥 Checking chat system health...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/chat/health",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat system status: {data['status']}")
        print(f"🤖 LLM available: {data['llm_available']}")
        print(f"💾 Vector store available: {data['vector_store_available']}")
        print(f"📦 Model: {data['llm_model']}")
        return True
    else:
        print(f"❌ Health check failed: {response.json()}")
        return False


def send_message(token: str, message: str, conversation_id: Optional[int] = None):
    """Send a message to the chatbot."""
    print(f"\n💬 User: {message}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "message": message,
        "conversation_id": conversation_id,
        "include_sources": True
    }
    
    response = requests.post(
        f"{BASE_URL}/chat/",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n🤖 Assistant: {data['message']}")
        print(f"\n📊 Metadata:")
        print(f"   Conversation ID: {data['conversation_id']}")
        print(f"   Confidence: {data.get('confidence', 'N/A')}")
        print(f"   Tokens used: {data.get('tokens_used', 'N/A')}")
        
        if data.get('sources'):
            print(f"\n📚 Sources ({len(data['sources'])}):")
            for i, source in enumerate(data['sources'][:3], 1):  # Show top 3
                print(f"   {i}. {source['document_name']} ({source['department']})")
                print(f"      Relevance: {source['relevance_score']:.3f}")
                print(f"      Preview: {source['content'][:100]}...")
        
        return data['conversation_id']
    else:
        print(f"❌ Error: {response.json()}")
        return None


def list_conversations(token: str):
    """List all conversations."""
    print("\n📋 Listing conversations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/chat/conversations",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['total']} conversation(s)\n")
        
        for conv in data['conversations']:
            print(f"   ID: {conv['id']}")
            print(f"   Title: {conv['title']}")
            print(f"   Messages: {conv['message_count']}")
            print(f"   Created: {conv['created_at']}")
            print()
        
        return data['conversations']
    else:
        print(f"❌ Error: {response.json()}")
        return []


def get_conversation(token: str, conversation_id: int):
    """Get full conversation with messages."""
    print(f"\n📖 Getting conversation {conversation_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/chat/conversations/{conversation_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Conversation: {data['title']}")
        print(f"   Messages: {len(data['messages'])}\n")
        
        for msg in data['messages']:
            role = "👤 User" if msg['role'] == 'user' else "🤖 Assistant"
            print(f"{role}: {msg['message'][:100]}...")
        
        return data
    else:
        print(f"❌ Error: {response.json()}")
        return None


def run_interactive_chat(token: str):
    """Run interactive chat session."""
    print("\n" + "=" * 60)
    print("🎯 Interactive Chat Session")
    print("=" * 60)
    print("Type your questions. Type 'quit' to exit.\n")
    
    conversation_id = None
    
    while True:
        try:
            message = input("\n💬 You: ").strip()
            
            if not message:
                continue
            
            if message.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            conversation_id = send_message(token, message, conversation_id)
            
        except KeyboardInterrupt:
            print("\n👋 Chat session ended")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 FinSolve RBAC Chatbot - Phase 3 Test Suite")
    print("=" * 60)
    
    # Configuration
    EMAIL = "finance@finsolve.com"
    PASSWORD = "test123456"
    
    print("\n⚠️  Prerequisites:")
    print("1. Server is running (python main.py)")
    print("2. User account created with above credentials")
    print("3. Documents uploaded to Finance department")
    print("4. GROQ_API_KEY set in .env file")
    
    input("\nPress Enter to continue...")
    
    # Test 1: Login
    token = login(EMAIL, PASSWORD)
    if not token:
        print("\n❌ Cannot proceed without token")
        return
    
    # Test 2: Health check
    if not check_chat_health(token):
        print("\n❌ Chat system not healthy. Check:")
        print("   - GROQ_API_KEY is set correctly")
        print("   - Internet connection is active")
        return
    
    # Test 3: Send some test messages
    print("\n" + "=" * 60)
    print("📝 Testing Sample Queries")
    print("=" * 60)
    
    sample_questions = [
        "What was our Q4 revenue?",
        "Tell me about our marketing campaigns",
        "What are the key financial metrics?"
    ]
    
    conversation_id = None
    for question in sample_questions:
        input("\nPress Enter to send next question...")
        conversation_id = send_message(token, question, conversation_id)
    
    # Test 4: List conversations
    input("\nPress Enter to list conversations...")
    conversations = list_conversations(token)
    
    # Test 5: Get conversation details
    if conversations:
        input("\nPress Enter to view first conversation...")
        get_conversation(token, conversations[0]['id'])
    
    # Test 6: Interactive mode
    print("\n" + "=" * 60)
    choice = input("\nWant to try interactive chat? (y/n): ").strip().lower()
    if choice == 'y':
        run_interactive_chat(token)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    
    print("\n💡 Next steps:")
    print("1. Try different types of questions")
    print("2. Test with users from different departments")
    print("3. Check conversation history persistence")
    print("4. Test follow-up questions in same conversation")


if __name__ == "__main__":
    main()