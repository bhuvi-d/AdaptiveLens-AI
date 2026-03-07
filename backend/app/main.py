"""
AdaptiveLens AI - Main Application
FastAPI entry point with all routers and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import documents, query, quiz
from app.db.vector_store import get_vector_store
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AdaptiveLens AI",
    description="RAG-based adaptive learning system that simplifies academic content "
                "with personalized complexity levels.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(quiz.router)


@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    # Ensure storage directories exist
    os.makedirs(settings.pdf_storage_dir, exist_ok=True)
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    
    # Initialize vector store
    vector_store = get_vector_store()
    doc_count = vector_store.get_document_count()
    
    logger.info("=" * 50)
    logger.info("🔬 AdaptiveLens AI Backend Started")
    logger.info(f"📊 Vectors in DB: {doc_count}")
    logger.info(f"📁 PDF Storage: {settings.pdf_storage_dir}")
    logger.info(f"🗄️  ChromaDB: {settings.chroma_persist_dir}")
    logger.info("=" * 50)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    vector_store = get_vector_store()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "documents_count": vector_store.get_document_count()
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AdaptiveLens AI",
        "version": "1.0.0",
        "description": "RAG-based adaptive learning system",
        "docs": "/docs"
    }
