"""
AdaptiveLens AI - Document Router
Handles PDF upload, listing, and deletion.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse, DocumentListResponse, DocumentInfo
from app.services.ingestion import get_ingestion_service
import logging
import json
import asyncio
from app.services.llm import get_llm_service
from app.db.vector_store import get_vector_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    try:
        content = await file.read()
        service = get_ingestion_service()
        result = await service.process_pdf(content, file.filename)
        
        return UploadResponse(
            id=result["id"],
            filename=result["filename"],
            page_count=result["page_count"],
            chunk_count=result["chunk_count"],
            message=f"Successfully processed '{result['filename']}': "
                    f"{result['page_count']} pages, {result['chunk_count']} chunks"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents."""
    service = get_ingestion_service()
    docs = service.get_all_documents()
    
    return DocumentListResponse(
        documents=[
            DocumentInfo(
                id=d["id"],
                filename=d["filename"],
                page_count=d["page_count"],
                chunk_count=d["chunk_count"],
                file_size_mb=d["file_size_mb"],
                uploaded_at=d["uploaded_at"]
            )
            for d in docs
        ],
        total=len(docs)
    )


@router.get("/suggestions")
async def get_document_suggestions():
    """Generate contextual suggestion questions based on uploaded documents."""
    try:
        service = get_ingestion_service()
        docs = service.get_all_documents()
        
        if not docs:
            return ["Explain quantum entanglement", "What is machine learning?", "How does DNA replication work?", "Explain the theory of relativity"]
            
        # Get titles for context
        doc_titles = [d['filename'] for d in docs[:5]]
        titles_str = ", ".join(doc_titles)
        
        llm_service = get_llm_service()
        prompt = f"""Based on these uploaded document titles, suggest 4 short, interesting research questions or topics a student might ask.
Titles: {titles_str}

Return EXACTLY a JSON list of 4 strings. No other text."""
        
        response = await llm_service.generate_content(prompt)
        try:
            # Simple cleanup for potential markdown
            text = response.text.strip() if response.text else ""
            if not text:
                return [f"Summarize {docs[0]['filename']}", "What are the key concepts?", "Explain the main findings", "How does this relate to other topics?"]
            
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"): text = text[4:]
            
            suggestions = json.loads(text.strip())
            if isinstance(suggestions, list):
                return suggestions[:4]
        except Exception as e:
            logger.warning(f"Failed to parse suggestions: {e}")
            
        return [f"Summarize {docs[0]['filename']}", "What are the key concepts?", "Explain the main findings", "How does this relate to other topics?"]
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        return ["Tell me more about my docs", "What are the core ideas?", "Summarize the content", "Give me an overview"]


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """Get details of a specific document."""
    service = get_ingestion_service()
    doc = service.get_document(doc_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentInfo(
        id=doc["id"],
        filename=doc["filename"],
        page_count=doc["page_count"],
        chunk_count=doc["chunk_count"],
        file_size_mb=doc["file_size_mb"],
        uploaded_at=doc["uploaded_at"]
    )


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its vectors."""
    service = get_ingestion_service()
    success = service.delete_document(doc_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": f"Document {doc_id} deleted successfully"}
