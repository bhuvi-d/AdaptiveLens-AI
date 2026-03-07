"""
AdaptiveLens AI - Embeddings Service
Handles embedding generation using Gemini Embeddings API.
"""

import logging
import asyncio
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """Generates embeddings using Gemini Embeddings API."""

    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model = settings.embedding_model
        logger.info(f"Gemini Embeddings service initialized with {self.model}")

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of text chunks."""
        embeddings = []
        
        # Process in batches of 100 to avoid rate limits
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            for text in batch:
                result = await asyncio.to_thread(
                    genai.embed_content,
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result["embedding"])
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings

    async def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query."""
        result = await asyncio.to_thread(
            genai.embed_content,
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return result["embedding"]


# Singleton
_embeddings_service = None

def get_embeddings_service() -> EmbeddingsService:
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service
