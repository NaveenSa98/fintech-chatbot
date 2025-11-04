"""
Test script for Phase 2: Document Processing & Vector Storage.
Run this after starting the server and creating a user.

Usage:
    python test_documents.py
"""
import requests
import json
from pathlib import Path


BASE_URL = "http://localhost:8000/api/v1"


def login(email: str, password: str) -> str:
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


def upload_document(token: str, file_path: str, department: str, description: str = None):
    """Upload a document."""
    print(f"\n📤 Uploading document: {file_path}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check if file exists
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        print("💡 Create a sample file first or use an existing document")
        return None
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {
            "department": department,
            "description": description
        }
        
        response = requests.post(
            f"{BASE_URL}/documents/upload",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code == 201 or response.status_code == 200:
        data = response.json()
        if response.status_code == 201:
            print(f"✅ Document uploaded successfully!")
        else:
            print(f"✅ Document already exists, using existing record!")
        print(f"📄 Document ID: {data['id']}")
        print(f"📊 Processing status: {data['is_processed']}")
        print(f"📝 Chunks created: {data['chunk_count']}")
        return data
    else:
        print(f"❌ Upload failed: {response.json()}")
        return None


def list_documents(token: str):
    """List all accessible documents."""
    print("\n📋 Listing documents...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/documents/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['total']} document(s)")
        
        for doc in data['documents']:
            print(f"\n  📄 {doc['original_filename']}")
            print(f"     ID: {doc['id']}")
            print(f"     Department: {doc['department']}")
            print(f"     Processed: {doc['is_processed']}")
            print(f"     Chunks: {doc['chunk_count']}")
        
        return data['documents']
    else:
        print(f"❌ Failed to list documents: {response.json()}")
        return []


def search_documents(token: str, query: str, top_k: int = 5):
    """Search documents."""
    print(f"\n🔍 Searching for: '{query}'")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/documents/search",
        headers=headers,
        json={"query": query, "top_k": top_k}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['total_results']} result(s)\n")
        
        for i, result in enumerate(data['results'], 1):
            print(f"Result {i}:")
            print(f"  📄 Content preview: {result['content'][:200]}...")
            print(f"  📊 Score: {result['score']:.4f}")
            print(f"  📁 Source: {result['metadata'].get('filename', 'Unknown')}")
            print(f"  🏢 Department: {result['metadata'].get('department', 'Unknown')}")
            print()
        
        return data
    else:
        print(f"❌ Search failed: {response.json()}")
        return None


def get_collection_stats(token: str):
    """Get collection statistics."""
    print("\n📊 Getting collection statistics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/documents/stats/collections",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Collection Statistics:\n")
        
        for stat in stats:
            print(f"  🏢 {stat['department']}: {stat['document_count']} documents")
        
        return stats
    else:
        print(f"❌ Failed to get stats: {response.json()}")
        return None


def get_sample_pdf_file():
    """Get path to an existing PDF file for testing."""
    print("\n📝 Looking for sample PDF file...")

    # Get project root (parent of tests directory)
    project_root = Path(__file__).parent.parent
    pdf_path = project_root / "data" / "uploads" / "6c5087a9-ecdd-406e-8bd2-81f038798166.pdf"

    if pdf_path.exists():
        print(f"✅ Found PDF file: {pdf_path}")
        return str(pdf_path)
    else:
        print(f"❌ PDF file not found: {pdf_path}")
        print("💡 Please ensure you have a PDF file in the data/uploads folder")

        # Try to list available files
        uploads_dir = project_root / "data" / "uploads"
        if uploads_dir.exists():
            files = list(uploads_dir.glob("*.pdf"))
            if files:
                print(f"\n📁 Available PDF files in uploads folder:")
                for f in files:
                    print(f"   - {f.name}")
                print(f"\n💡 Update the pdf_path in get_sample_pdf_file() to use one of these files")
        return None


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 FinSolve RBAC Chatbot - Phase 2 Test Suite")
    print("=" * 60)
    
    # Configuration
    EMAIL = "johndoe@finsolve.com"
    PASSWORD = "johndoe123"
    
    print("\n⚠️  Make sure you have:")
    print("1. Started the server (python main.py)")
    print("2. Created a user with the credentials above")
    
    input("\nPress Enter to continue...")
    
    # Test 1: Login
    token = login(EMAIL, PASSWORD)
    if not token:
        print("\n❌ Cannot proceed without token")
        print("💡 First register a user:")
        print(f"   Email: {EMAIL}")
        print(f"   Password: {PASSWORD}")
        print("   Role: Finance")
        return
    
    # Test 2: Get sample PDF file
    sample_file = get_sample_pdf_file()

    if not sample_file:
        print("\n❌ No sample file available. Cannot proceed with tests.")
        return

    # Test 3: Upload document
    doc = upload_document(
        token=token,
        file_path=sample_file,
        department="Finance",
        description="Financial Report - PDF Document"
    )

    if not doc:
        print("\n❌ Document upload failed. Cannot proceed with search tests.")
        return
    
    # Test 4: List documents
    list_documents(token)
    
    # Test 5: Search documents
    print("\n" + "=" * 60)
    print("Testing Document Search")
    print("=" * 60)

    search_queries = [
        "financial report",
        "revenue",
        "performance metrics"
    ]

    for query in search_queries:
        search_documents(token, query, top_k=3)
        input("\nPress Enter for next search...")

    # Test 6: Collection stats (requires C-Level user)
    print("\n" + "=" * 60)
    print("Note: Collection stats require C-Level role")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

    print("\n💡 Next steps:")
    print("1. Try uploading different file types (DOCX, XLSX, CSV)")
    print("2. Create users with different roles to test access control")
    print("3. Upload department-specific documents")
    print("4. Test search with various queries")
    print("5. Update the PDF path in get_sample_pdf_file() if using a different file")


if __name__ == "__main__":
    main()