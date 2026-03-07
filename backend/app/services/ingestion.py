"""
AdaptiveLens AI - Document Ingestion Service
Handles PDF upload, text extraction, semantic chunking, and embedding storage.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings
from app.services.embeddings import get_embeddings_service
from app.db.vector_store import get_vector_store

logger = logging.getLogger(__name__)

# Persistent document registry
REGISTRY_FILE = os.path.join(settings.chroma_persist_dir, "doc_registry.json")


def _load_registry() -> dict[str, dict]:
    """Load document registry from disk."""
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load registry: {e}")
    return {}


def _save_registry(registry: dict[str, dict]):
    """Save document registry to disk."""
    os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)


_document_registry: dict[str, dict] = _load_registry()


def get_document_registry():
    return _document_registry


class IngestionService:
    """Handles PDF processing, chunking, and vector storage."""

    def __init__(self):
        self.pdf_dir = settings.pdf_storage_dir
        os.makedirs(self.pdf_dir, exist_ok=True)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    async def process_pdf(self, file_content: bytes, filename: str) -> dict:
        """Process uploaded PDF: extract text, chunk, embed, store."""
        doc_id = str(uuid.uuid4())[:8]
        
        # Validate file size
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > settings.max_pdf_size_mb:
            raise ValueError(
                f"File size ({file_size_mb:.1f} MB) exceeds maximum "
                f"({settings.max_pdf_size_mb} MB)"
            )

        # Save PDF to disk
        file_path = os.path.join(self.pdf_dir, f"{doc_id}_{filename}")
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Extract text from PDF
        text_by_page = self._extract_text(file_path)
        
        if not text_by_page:
            os.remove(file_path)
            raise ValueError("Could not extract any text from the PDF. Ensure it is not a scanned/image-only PDF.")

        # Validate page count
        if len(text_by_page) > settings.max_pdf_pages:
            os.remove(file_path)
            raise ValueError(
                f"Page count ({len(text_by_page)}) exceeds maximum "
                f"({settings.max_pdf_pages})"
            )

        # Chunk the text with metadata
        chunks = self._chunk_text(text_by_page, doc_id, filename)
        
        if not chunks:
            os.remove(file_path)
            raise ValueError("No text chunks could be generated from the PDF.")

        # Generate embeddings
        embeddings_service = get_embeddings_service()
        chunk_texts = [c["text"] for c in chunks]
        embeddings = await embeddings_service.embed_documents(chunk_texts)

        # Store in FAISS
        vector_store = get_vector_store()
        vector_store.add_documents(
            ids=[c["id"] for c in chunks],
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=[c["metadata"] for c in chunks]
        )

        # Register document and persist
        doc_info = {
            "id": doc_id,
            "filename": filename,
            "file_path": file_path,
            "page_count": len(text_by_page),
            "chunk_count": len(chunks),
            "file_size_mb": round(file_size_mb, 2),
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
        _document_registry[doc_id] = doc_info
        _save_registry(_document_registry)

        logger.info(
            f"Processed '{filename}': {len(text_by_page)} pages, "
            f"{len(chunks)} chunks"
        )
        
        return doc_info

    def _extract_text(self, file_path: str) -> list[dict]:
        """Extract text from each page of the PDF."""
        text_by_page = []
        
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    text_by_page.append({
                        "page_number": i + 1,
                        "text": text.strip()
                    })
        
        return text_by_page

    def _chunk_text(self, text_by_page: list[dict], doc_id: str, 
                    filename: str) -> list[dict]:
        """Split text into semantic chunks with metadata."""
        chunks = []
        chunk_index = 0
        
        for page_data in text_by_page:
            page_num = page_data["page_number"]
            page_text = page_data["text"]
            
            # Detect section titles (lines that look like headers)
            section_title = self._detect_section_title(page_text)
            
            # Split page text into chunks
            page_chunks = self.text_splitter.split_text(page_text)
            
            for chunk_text in page_chunks:
                chunk_id = f"{doc_id}_chunk_{chunk_index}"
                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "metadata": {
                        "document_id": doc_id,
                        "document_name": filename,
                        "page_number": page_num,
                        "section_title": section_title or "",
                        "chunk_index": chunk_index
                    }
                })
                chunk_index += 1
        
        return chunks

    def _detect_section_title(self, text: str) -> Optional[str]:
        """Attempt to detect section title from the first line of text."""
        lines = text.strip().split("\n")
        if lines:
            first_line = lines[0].strip()
            # Heuristic: short lines that look like titles
            if (len(first_line) < 100 and 
                not first_line.endswith(".") and
                len(first_line.split()) <= 12):
                return first_line
        return None

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and its vectors."""
        if doc_id not in _document_registry:
            return False
        
        # Delete from FAISS
        vector_store = get_vector_store()
        vector_store.delete_document(doc_id)
        
        # Delete file
        doc_info = _document_registry[doc_id]
        if os.path.exists(doc_info["file_path"]):
            os.remove(doc_info["file_path"])
        
        # Remove from registry and persist
        del _document_registry[doc_id]
        _save_registry(_document_registry)
        
        logger.info(f"Deleted document {doc_id}")
        return True

    def get_all_documents(self) -> list[dict]:
        """Get all registered documents."""
        return list(_document_registry.values())

    def get_document(self, doc_id: str) -> Optional[dict]:
        """Get a specific document by ID."""
        return _document_registry.get(doc_id)


# Singleton
_ingestion_service = None

def get_ingestion_service() -> IngestionService:
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service
