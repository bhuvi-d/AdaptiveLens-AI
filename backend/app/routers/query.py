"""
AdaptiveLens AI - Query Router
Handles question-answering with adaptive complexity.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    QueryRequest, QueryResponse, SourceChunk, PrerequisiteTopic,
    COMPLEXITY_DESCRIPTIONS
)
from app.services.retrieval import get_retrieval_service
from app.services.llm import get_llm_service
from app.services.readability import get_readability_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/query", tags=["Query"])


@router.post("", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Ask a question and get an adaptive explanation.
    
    The explanation is generated at the specified complexity level (1-5)
    using retrieved document context.
    """
    try:
        # Step 1: Retrieve relevant chunks
        retrieval_service = get_retrieval_service()
        chunks = await retrieval_service.retrieve(
            query=request.question,
            document_ids=request.document_ids
        )

        if not chunks:
            raise HTTPException(
                status_code=404,
                detail="No relevant content found. Please upload documents first."
            )

        # Step 2: Generate explanation
        llm_service = get_llm_service()
        result = await llm_service.generate_explanation(
            question=request.question,
            context_chunks=chunks,
            complexity_level=request.complexity_level,
            detail_level=request.detail_level,
            chat_history=request.chat_history
        )

        # Step 3: Calculate readability
        readability_service = get_readability_service()
        readability_score = readability_service.calculate_flesch_score(
            result["explanation"]
        )
        readability_label = readability_service.get_readability_label(
            readability_score
        )

        # Step 4: Build response
        level_info = COMPLEXITY_DESCRIPTIONS.get(
            request.complexity_level, COMPLEXITY_DESCRIPTIONS[3]
        )

        sources = [
            SourceChunk(
                text=chunk["text"][:300] + "..." if len(chunk["text"]) > 300 else chunk["text"],
                page_number=chunk["metadata"].get("page_number"),
                section_title=chunk["metadata"].get("section_title"),
                document_id=chunk["metadata"].get("document_id", ""),
                document_name=chunk["metadata"].get("document_name", "Unknown"),
                relevance_score=round(chunk.get("relevance_score", 0), 3)
            )
            for chunk in chunks
        ]

        prerequisites = [
            PrerequisiteTopic(
                topic=p.get("topic", ""),
                description=p.get("description", "")
            )
            for p in result.get("prerequisites", [])[:3]
        ]

        return QueryResponse(
            explanation=result["explanation"],
            tldr=result.get("tldr", ""),
            complexity_level=request.complexity_level,
            complexity_name=level_info["name"],
            readability_score=readability_score,
            readability_label=readability_label,
            prerequisites=prerequisites,
            sources=sources
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/regenerate", response_model=QueryResponse)
async def regenerate_explanation(request: QueryRequest):
    """
    Regenerate an explanation at a different complexity level.
    Same as query but intended for slider changes.
    """
    return await query_documents(request)
