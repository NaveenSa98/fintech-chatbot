"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings, create_directories
from src.database.connection import init_db
from src.auth.router import router as auth_router
from src.core.logging_config import setup_logging, get_logger
import uvicorn
from src.documents.router import router as documents_router
from src.chat.router import router as chat_router

# Initialize logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Replaces deprecated @app.on_event decorators.
    """
    # Startup
    try:
        logger.info("Starting FinSolve RBAC Chatbot...")
        logger.info("Initializing database...")
        init_db()
        print("📁 Creating required directories...")
        create_directories()
        print("✅ Directories ready!")
        print("🔮 Initializing AI components...")
        print("   - Vector store: Ready (lazy loading)")
        print("   - Embeddings: Ready (lazy loading)")
        print("   - LLM: Will initialize on first use")
        print("✅ AI components ready!")

        print("=" * 60)
        print("🎉 FinSolve RBAC Chatbot is running!")
        print("📚 API Docs: http://localhost:8000/api/docs")
        print("=" * 60)
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise

    yield  # Application runs here

    # Shutdown
    print("👋 Shutting down FinSolve RBAC Chatbot...")

#Create FastAPI app instance
app = FastAPI(
    lifespan=lifespan,
    title = settings.APP_NAME,
    description = "Fintech Chatbot with Role-Based Access Control",
    version = settings.API_VERSION,
    docs_url = "/api/docs",
    redoc_url = "/api/redoc"
)

#Configure CORS
app.add_middleware (
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Welcome to FinSolve RBAC Chatbot API",
        "version": settings.API_VERSION,
        "docs": "/api/docs",
        "features": {
            "phase1": "✅ Authentication & Role Management",
            "phase2": "✅ Document Processing & Vector Storage",
            "phase3": "✅ Chat Interface with LLM Integration"
        },
        "endpoints": {
            "auth": f"/api/{settings.API_VERSION}/auth",
            "documents": f"/api/{settings.API_VERSION}/documents",
            "chat": f"/api/{settings.API_VERSION}/chat"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "llm_model": settings.LLM_MODEL 
    }

app.include_router(auth_router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(documents_router, prefix=f"/api/{settings.API_VERSION}") 
app.include_router(chat_router, prefix=f"/api/{settings.API_VERSION}")

if __name__ == "__main__":
   
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True 
    )

    