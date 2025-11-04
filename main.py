"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings, create_directories
from src.database.connection import init_db
from src.auth.router import router as auth_router
from src.core.logging_config import setup_logging, get_logger
import uvicorn
from src.documents.router import router as documents_router 

# Initialize logging
setup_logging()
logger = get_logger(__name__)

#Create FastAPI app instance
app = FastAPI(
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

#Event handlers
@app.on_event("startup")
async def startup_event():
    """
    Run when application starts.
    Initialize database tables.
    """
    try:
        logger.info("Starting FinSolve RBAC Chatbot...")
        logger.info("Initializing database...")
        init_db()
        print("📁 Creating required directories...")
        create_directories()
        print("✅ Directories ready!")
        print("🔮 Vector store will initialize on first use")
        print("✅ Startup complete!")
        logger.info("Application started successfully!")
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Run when application shuts down."""
    print("👋 Shutting down FinSolve RBAC Chatbot...")

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
            "phase2": "✅ Document Processing & Vector Storage"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME
    }

app.include_router(auth_router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(documents_router, prefix=f"/api/{settings.API_VERSION}") 

if __name__ == "__main__":
   
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True 
    )

    