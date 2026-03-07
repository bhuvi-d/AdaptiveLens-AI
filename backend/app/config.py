"""
AdaptiveLens AI - Configuration
Loads environment variables and defines application settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # API Keys
        self.google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
        
        # Storage
        self.chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./storage/chroma_db")
        self.pdf_storage_dir: str = os.getenv("PDF_STORAGE_DIR", "./storage/pdfs")
        
        # PDF Limits
        self.max_pdf_size_mb: int = int(os.getenv("MAX_PDF_SIZE_MB", "20"))
        self.max_pdf_pages: int = int(os.getenv("MAX_PDF_PAGES", "200"))
        
        # Chunking
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
        self.chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
        
        # Retrieval
        self.top_k_results: int = int(os.getenv("TOP_K_RESULTS", "5"))
        
        # LLM
        self.llm_model: str = os.getenv("LLM_MODEL", "models/gemini-flash-lite-latest")
        self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
        self.max_response_tokens: int = int(os.getenv("MAX_RESPONSE_TOKENS", "2000"))
        
        # CORS
        cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        self.cors_origins: list[str] = [o.strip() for o in cors_raw.split(",")]


settings = Settings()
