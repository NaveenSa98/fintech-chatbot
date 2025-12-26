# FinSolve RBAC Chatbot

An enterprise-grade AI-powered chatbot with Role-Based Access Control (RBAC) for fintech companies. Built with modern technologies combining a robust Python FastAPI backend with Retrieval-Augmented Generation (RAG) and a responsive TypeScript React frontend.

## 🎯 Overview

FinSolve is a sophisticated multi-phase chatbot system designed for financial institutions. It provides secure document management, intelligent information retrieval, and department-based access control. The system uses advanced AI techniques to answer user queries with accuracy and confidence scoring, while maintaining strict security protocols.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [RAG Pipeline](#-rag-pipeline)
- [Usage Examples](#-usage-examples)
- [Development](#-development)
- [Contributing](#-contributing)

## ✨ Features

### Phase 1: Authentication & Authorization (✅ Complete)
- **User Management**: Registration, login, and profile management
- **Role-Based Access Control**: 6 predefined roles with specific permissions
  - Finance
  - Marketing
  - HR
  - Engineering
  - Employee
  - C-Level
- **JWT Authentication**: Secure token-based authentication
- **Password Security**: Bcrypt hashing with salting
- **Department-Based Access**: Documents accessible only to authorized departments

### Phase 2: Document Processing & Vector Storage (✅ Complete)
- **Multi-Format Support**: PDF, DOCX, CSV, XLSX, Markdown files
- **Smart Document Conversion**: Automatic PDF/DOCX to Markdown conversion for LLM optimization
- **Intelligent Chunking**:
  - Configurable chunk size (1000 tokens)
  - Dynamic overlap (150-200 tokens)
  - Preserves semantic boundaries
- **Vector Embeddings**: Using sentence-transformers (BAAI/bge-base-en-v1.5 model)
- **Semantic Search**: ChromaDB for fast similarity search
- **Department Collections**: Organized vector stores per department
- **Asynchronous Processing**: Background processing with thread pooling (max 5 concurrent tasks)
- **Metadata Tracking**: File type, size, uploader, timestamps

### Phase 3: Chat Interface with RAG (✅ Complete)
- **Retrieval-Augmented Generation**: 5-step intelligent retrieval pipeline
- **Conversation Memory**: Up to 10 messages context retention
- **Query Augmentation**: 5 query variations for enhanced retrieval
- **Source Attribution**: Citations with confidence scores
- **Chain-of-Thought Prompting**: Advanced prompt engineering
- **Role-Based Filtering**: Automatic document access control in RAG
- **Interactive CLI Testing**: Built-in testing tool for debugging

## 🛠️ Tech Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | 0.109.0 |
| **ASGI Server** | Uvicorn | 0.27.0 |
| **Database** | PostgreSQL | Latest |
| **ORM** | SQLAlchemy | 2.0.25 |
| **Migrations** | Alembic | - |
| **Authentication** | JWT (python-jose) | Latest |
| **Password Hashing** | Bcrypt | Latest |
| **LLM Framework** | LangChain | 0.1.0 |
| **LLM Provider** | Groq API (llama-3.1-8b-instant) | Latest |
| **Vector Database** | ChromaDB | 0.4.22 |
| **Embeddings** | sentence-transformers | 2.3.1 |
| **Document Parsing** | pypdf, python-docx, openpyxl | Latest |
| **Format Conversion** | pymupdf4llm, markitdown | Latest |
| **Data Processing** | Pandas | 2.1.4 |
| **Validation** | Pydantic | 2.5.3 |
| **CLI Formatting** | Rich | 13.7.0 |
| **Token Counting** | Tiktoken | Latest |

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | React | 18.2.0 |
| **Build Tool** | Vite | 7.3.0 |
| **Language** | TypeScript | 5.2.2 |
| **Routing** | React Router DOM | 7.11.0 |
| **UI Components** | Chakra UI | 2.10.9 |
| **Animations** | Framer Motion | Latest |
| **HTTP Client** | Axios | 1.7.7 |
| **Linting** | ESLint | Latest |

### Infrastructure
- **Runtime**: Python 3.x
- **Environment Management**: .env configuration
- **Logging**: Python logging with dated file output
- **CORS**: Enabled for cross-origin requests
- **Version Control**: Git

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (React + TypeScript)               │
│                    [Vite + Chakra UI + Axios]                   │
│  ┌──────────┬──────────┬──────────┬──────────────────────────┐  │
│  │  Login   │  Chat    │Documents │ Profile & Settings       │  │
│  └──────────┴──────────┴──────────┴──────────────────────────┘  │
└─────────────────────┬──────────────────────────────────────────┘
                      │ HTTP/HTTPS with JWT
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI + Python)                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Authentication & Authorization                 │ │
│  │  [JWT Tokens, Bcrypt, Role-Based Access Control]           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌──────────────────┬──────────────────┬──────────────────────┐ │
│  │   Documents      │      Chat        │   Vector Store       │ │
│  │   Management     │      & RAG       │    Management        │ │
│  │                  │                  │                      │ │
│  │ • Upload        │ • Query Process  │ • ChromaDB           │ │
│  │ • Processing    │ • Conversation   │ • Embeddings         │ │
│  │ • Conversion    │ • Augmentation   │ • Retrieval          │ │
│  │ • Storage       │ • LLM Calls      │ • Similarity Search  │ │
│  └──────────────────┴──────────────────┴──────────────────────┘ │
│                          ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Data Layer & Storage                           │ │
│  │  ┌──────────────────┬──────────────────────────────────┐  │ │
│  │  │   PostgreSQL     │    ChromaDB Vector Store         │  │ │
│  │  │   Database       │    (Department Collections)      │  │ │
│  │  │                  │                                  │  │ │
│  │  │ • Users          │    • Finance Collection         │  │ │
│  │  │ • Documents      │    • Marketing Collection       │  │ │
│  │  │ • Conversations  │    • HR Collection              │  │ │
│  │  │ • Messages       │    • Engineering Collection     │  │ │
│  │  │                  │    • General Collection         │  │ │
│  │  └──────────────────┴──────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         External Services & APIs                           │ │
│  │  [Groq API - llama-3.1-8b-instant for LLM Generation]     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### RAG Pipeline Architecture

```
User Query
    ▼
┌─────────────────────────────────────┐
│  1. Query Contextualization         │
│  [Build standalone question using   │
│   chat history context]             │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  2. Query Augmentation              │
│  [Generate 5 query variations for   │
│   better retrieval coverage]        │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  3. Multi-Collection Retrieval      │
│  [Query all department collections] │
│  [Filter by similarity threshold]   │
│  [Return top-K documents]           │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  4. Prompt Engineering              │
│  [Format retrieved context into     │
│   Chain-of-Thought template]        │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  5. LLM Generation                  │
│  [Call Groq API with formatted      │
│   prompt using llama-3.1-8b]        │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  6. Post-Processing                 │
│  [Extract sources, calculate        │
│   confidence, format response]      │
└──────────────┬──────────────────────┘
               ▼
Response with Sources & Confidence Score
```

## 📁 Project Structure

```
RBAC-Chatbot/
├── fintech-chatbot/
│   ├── src/
│   │   ├── auth/                          # Authentication & Authorization
│   │   │   ├── models.py                 # User database model
│   │   │   ├── router.py                 # Auth endpoints
│   │   │   ├── schemas.py                # Pydantic validation
│   │   │   ├── service.py                # Business logic
│   │   │   └── utils.py                  # Helper functions
│   │   │
│   │   ├── chat/                          # Chat & RAG System
│   │   │   ├── models.py                 # Conversation models
│   │   │   ├── rag_chain.py              # RAG orchestration
│   │   │   ├── llm_manager.py            # LLM integration
│   │   │   ├── prompt_templates.py       # Prompt engineering
│   │   │   ├── query_augmentation.py     # Query enhancement
│   │   │   ├── router.py                 # Chat endpoints
│   │   │   ├── schemas.py                # Request/response schemas
│   │   │   └── service.py                # Business logic
│   │   │
│   │   ├── documents/                     # Document Management
│   │   │   ├── models.py                 # Document model
│   │   │   ├── processor.py              # Document processing
│   │   │   ├── converters.py             # Format conversion
│   │   │   ├── loaders.py                # Document loading
│   │   │   ├── router.py                 # Documents endpoints
│   │   │   ├── schemas.py                # Schemas
│   │   │   └── service.py                # Business logic
│   │   │
│   │   ├── vectorstore/                   # Vector Database
│   │   │   ├── chroma_store.py           # ChromaDB integration
│   │   │   ├── embeddings.py             # Embedding functions
│   │   │   └── retriever.py              # Document retrieval
│   │   │
│   │   ├── database/
│   │   │   └── connection.py             # SQLAlchemy setup
│   │   │
│   │   ├── core/
│   │   │   ├── config.py                 # App settings & permissions
│   │   │   ├── security.py               # JWT & hashing
│   │   │   ├── logging_config.py         # Logging setup
│   │   │   ├── exceptions.py             # Custom exceptions
│   │   │   └── view_chroma_db.py         # Vector DB inspection
│   │   │
│   │   └── utils/
│   │       ├── formatting.py             # Output formatting
│   │       └── validators.py             # Input validation
│   │
│   ├── frontend-vite/                     # React TypeScript Frontend
│   │   ├── src/
│   │   │   ├── pages/                    # Page components
│   │   │   │   ├── Login.tsx
│   │   │   │   ├── Chat.tsx
│   │   │   │   ├── Documents.tsx
│   │   │   │   └── Profile.tsx
│   │   │   ├── components/               # Reusable components
│   │   │   ├── services/                 # API client
│   │   │   ├── context/                  # Auth context
│   │   │   ├── hooks/                    # Custom hooks
│   │   │   └── types/                    # TypeScript interfaces
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── vite.config.ts
│   │
│   ├── data/                              # Data Storage
│   │   ├── uploads/                      # Uploaded documents
│   │   ├── chroma_db/                    # Vector database
│   │   ├── raw/                          # Raw documents
│   │   └── processed/                    # Processed documents
│   │
│   ├── logs/                              # Application logs
│   │
│   ├── tests/                             # Test suite
│   │   ├── test_api.py
│   │   ├── test_chat.py
│   │   └── test_documents.py
│   │
│   ├── main.py                            # FastAPI application entry point
│   ├── test_interactive_cli.py            # Interactive testing tool
│   ├── requirements.txt                   # Python dependencies
│   ├── .env.example                       # Environment template
│   ├── .gitignore                         # Git ignore rules
│   └── README.md                          # This file
│
└── .git/                                   # Git repository
```

## 💾 Installation & Setup

### Prerequisites

- **Python**: 3.9 or higher
- **Node.js**: 16 or higher
- **PostgreSQL**: 12 or higher
- **npm** or **yarn**: Package manager for frontend

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RBAC-Chatbot/fintech-chatbot
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   # Create PostgreSQL database
   createdb fintech_chatbot

   # Run migrations (if using Alembic)
   alembic upgrade head
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend-vite
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure API endpoint** (update in `src/services/api.ts` if needed)
   ```typescript
   const API_BASE_URL = 'http://localhost:8000/api/v1';
   ```

## ⚙️ Configuration

### Backend Configuration (`.env`)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fintech_chatbot

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Groq API
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.1-8b-instant

# RAG Configuration
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=150

# File Upload
MAX_UPLOAD_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,docx,csv,xlsx,md

# Vector Database
VECTORSTORE_PATH=./data/chroma_db

# Application
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Conversation
MAX_CONVERSATION_HISTORY=10
MAX_CONCURRENT_DOCUMENT_PROCESSING=5
```

### Database Configuration

Update `DATABASE_URL` in `.env`:
```env
# PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/fintech_chatbot

# Alternative (with password in URL)
DATABASE_URL=postgres://user:password@localhost/fintech_chatbot
```

### Frontend Configuration

The frontend is configured to connect to the backend API. Update `frontend-vite/src/services/api.ts` if needed:

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
```

## 🚀 Running the Application

### Start Backend Server

From the `fintech-chatbot` directory:

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The backend will be available at: `http://localhost:8000`
- API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative docs (ReDoc): `http://localhost:8000/redoc`

### Start Frontend Server

From the `frontend-vite` directory:

```bash
# Development mode
npm run dev
# or
yarn dev
```

The frontend will be available at: `http://localhost:5173` (or port shown in terminal)

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=src
```

### Interactive CLI Testing

Test the RAG system directly:

```bash
python test_interactive_cli.py
```

Available commands:
- `/ask <query>` - Query the RAG system
- `/retrieve <query>` - Retrieve documents only
- `/role <role_name>` - Switch user role
- `/debug-on` or `/debug-off` - Enable/disable debug output
- `/history` - View conversation history
- `/exit` - Exit the CLI

## 📡 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "role": "Employee",
  "department": "General"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "Employee",
  "department": "General",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "Employee",
    "department": "General"
  }
}
```

#### Get Available Roles
```http
GET /api/v1/auth/roles
Authorization: Bearer <access_token>

Response: 200 OK
{
  "roles": ["Finance", "Marketing", "HR", "Engineering", "Employee", "C-Level"]
}
```

### Document Endpoints

#### Upload Document
```http
POST /api/v1/documents/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Parameters:
- file: <binary_file>
- description: "Optional document description"

Response: 201 Created
{
  "id": "uuid",
  "filename": "document.pdf",
  "file_size": 2048576,
  "file_type": "pdf",
  "department": "Finance",
  "is_processed": false,
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

#### List User's Documents
```http
GET /api/v1/documents/list
Authorization: Bearer <access_token>

Response: 200 OK
{
  "documents": [
    {
      "id": "uuid",
      "filename": "document.pdf",
      "file_size": 2048576,
      "file_type": "pdf",
      "department": "Finance",
      "is_processed": true,
      "chunk_count": 45,
      "uploaded_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Get Document Details
```http
GET /api/v1/documents/{document_id}
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": "uuid",
  "filename": "document.pdf",
  "file_size": 2048576,
  "file_type": "pdf",
  "department": "Finance",
  "is_processed": true,
  "chunk_count": 45,
  "description": "Financial report Q4 2024",
  "uploaded_by": "John Doe",
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

#### Delete Document
```http
DELETE /api/v1/documents/{document_id}
Authorization: Bearer <access_token>

Response: 204 No Content
```

### Chat Endpoints

#### Send Message (with RAG)
```http
POST /api/v1/chat/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "What are the financial highlights for Q4?",
  "conversation_id": "uuid" (optional, creates new if not provided)
}

Response: 200 OK
{
  "id": "uuid",
  "conversation_id": "uuid",
  "user_message": "What are the financial highlights for Q4?",
  "assistant_response": "Based on the documents, the Q4 financial highlights include...",
  "sources": [
    {
      "document_id": "uuid",
      "filename": "Q4_Report.pdf",
      "relevance_score": 0.92,
      "excerpt": "..."
    }
  ],
  "confidence_score": 0.87,
  "tokens_used": 245,
  "created_at": "2024-01-15T10:35:00Z"
}
```

#### List Conversations
```http
GET /api/v1/chat/conversations
Authorization: Bearer <access_token>

Response: 200 OK
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Financial Q4 2024",
      "message_count": 5,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:45:00Z"
    }
  ]
}
```

#### Get Conversation Details
```http
GET /api/v1/chat/conversations/{conversation_id}
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": "uuid",
  "title": "Financial Q4 2024",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "message": "What are Q4 highlights?",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "message": "Based on the documents...",
      "sources": [...],
      "confidence_score": 0.87,
      "created_at": "2024-01-15T10:35:00Z"
    }
  ]
}
```

### Health Check
```http
GET /api/v1/health

Response: 200 OK
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,
  department VARCHAR(100),
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT valid_role CHECK (role IN ('Finance', 'Marketing', 'HR', 'Engineering', 'Employee', 'C-Level'))
);
```

### Documents Table
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  filename VARCHAR(255) NOT NULL,
  file_size INTEGER NOT NULL,
  file_type VARCHAR(20) NOT NULL,
  source_file_type VARCHAR(20),
  converted_from BOOLEAN DEFAULT false,
  department VARCHAR(100) NOT NULL,
  uploader_role VARCHAR(50) NOT NULL,
  is_processed BOOLEAN DEFAULT false,
  chunk_count INTEGER DEFAULT 0,
  uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Conversations Table
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chat Messages Table
```sql
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL,
  message TEXT NOT NULL,
  sources_used TEXT,
  confidence_score DECIMAL(3,2),
  tokens_used INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧠 RAG Pipeline Details

### Query Processing Steps

1. **Contextualization**: Takes the user's question and chat history to create a standalone question
2. **Augmentation**: Generates 5 variations of the query for comprehensive retrieval
3. **Retrieval**:
   - Searches across all department-specific vector collections
   - Applies cosine similarity matching
   - Filters by similarity threshold (0.7 default)
   - Returns top-K results (5 default)
4. **Ranking**: Sorts results by relevance score
5. **Prompt Building**: Formats context into Chain-of-Thought template
6. **Generation**: Sends to Groq API (llama-3.1-8b-instant)
7. **Post-Processing**: Extracts sources, calculates confidence, formats output

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `RAG_TOP_K` | 5 | Number of documents to retrieve |
| `RAG_SIMILARITY_THRESHOLD` | 0.7 | Minimum similarity score (0-1) |
| `RAG_CHUNK_SIZE` | 1000 | Tokens per chunk |
| `RAG_CHUNK_OVERLAP` | 150 | Overlap between chunks (tokens) |
| `MAX_CONVERSATION_HISTORY` | 10 | Messages to consider for context |

## 💡 Usage Examples

### Example 1: Upload a Document and Query It

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Save the access_token from response

# 2. Upload Document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/document.pdf" \
  -F "description=Q4 Financial Report"

# Save the document_id from response

# 3. Query the Document
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main financial highlights?"
  }'
```

### Example 2: Using the Interactive CLI

```bash
# Start the interactive CLI
python test_interactive_cli.py

# Switch to Finance role
/role Finance

# Query the system
/ask What were the Q4 financial results?

# Retrieve documents only
/retrieve financial performance

# View conversation history
/history

# Exit
/exit
```

### Example 3: Department-Based Access

```python
# Only users from Finance department can access Finance documents
# The system automatically filters documents based on:
# 1. User's role and its associated permissions
# 2. User's department
# 3. Document's department classification
```

## 🔧 Development

### Project Setup for Development

```bash
# Backend development with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend development with hot-reload
cd frontend-vite
npm run dev

# Run tests with watch mode
pytest tests/ --watch
```

### Key Development Patterns

**Error Handling**
```python
# Use custom exceptions
from src.core.exceptions import DocumentProcessingError

raise DocumentProcessingError("Failed to process document")
```

**Logging**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Processing document", extra={"doc_id": doc_id})
```

**Input Validation**
```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[str] = None
```

**Async Operations**
```python
# Document processing happens asynchronously
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)
future = executor.submit(process_document, file_path)
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_chat.py::test_rag_pipeline -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run integration tests
pytest tests/ -m integration
```

### Code Quality

```bash
# Format code
black src/ frontend-vite/src

# Lint
flake8 src/
eslint frontend-vite/src/

# Type checking
mypy src/
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** following code style guidelines
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Commit with clear messages** (`git commit -m 'Add amazing feature'`)
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request** with a clear description

### Development Workflow

1. Create a branch from `main`
2. Make changes and test locally
3. Ensure all tests pass
4. Submit PR with description of changes
5. Request review from maintainers
6. Address feedback and merge

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📞 Support & Contact

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team
- Check existing documentation

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- LLM powered by [Groq](https://groq.com/)
- Vector database [ChromaDB](https://www.trychroma.com/)
- Frontend with [React](https://react.dev/) and [Chakra UI](https://chakra-ui.com/)
- RAG implementation using [LangChain](https://langchain.com/)

---

**Last Updated**: January 2024
**Version**: 1.0.0
