"""
AdaptiveLens AI - Retrieval Service
Implements hybrid search (keyword + vector) with reranking.
"""

import logging
import numpy as np
from rank_bm25 import BM25Okapi
from app.config import settings
from app.services.embeddings import get_embeddings_service
from app.db.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class RetrievalService:
    """Hybrid retrieval with BM25 keyword search + vector similarity + reranking."""

    async def retrieve(self, query: str, document_ids: list[str] = None,
                       top_k: int = None) -> list[dict]:
        """
        Retrieve the most relevant chunks using hybrid search.
        
        1. Vector similarity search via ChromaDB
        2. BM25 keyword search
        3. Reciprocal Rank Fusion to combine results
        """
        if top_k is None:
            top_k = settings.top_k_results

        # Step 1: Vector search
        vector_results = await self._vector_search(query, document_ids, top_k * 2)
        
        # Step 2: BM25 keyword search
        keyword_results = self._keyword_search(query, vector_results, top_k * 2)
        
        # Step 3: Reciprocal Rank Fusion
        fused_results = self._reciprocal_rank_fusion(
            vector_results, keyword_results, top_k
        )
        
        logger.info(f"Retrieved {len(fused_results)} chunks for query: {query[:50]}...")
        return fused_results

    async def _vector_search(self, query: str, document_ids: list[str] = None,
                             n_results: int = 10) -> list[dict]:
        """Perform vector similarity search."""
        embeddings_service = get_embeddings_service()
        query_embedding = await embeddings_service.embed_query(query)
        
        vector_store = get_vector_store()

        results = vector_store.query(
            query_embedding=query_embedding,
            n_results=n_results,
            document_ids=document_ids
        )

        chunks = []
        if results and results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                chunks.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "relevance_score": 1 - results["distances"][0][i]
                })
        
        return chunks

    def _keyword_search(self, query: str, candidates: list[dict],
                        top_k: int = 10) -> list[dict]:
        """Perform BM25 keyword search over retrieved candidates."""
        if not candidates:
            return []

        # Tokenize documents
        tokenized_docs = [doc["text"].lower().split() for doc in candidates]
        tokenized_query = query.lower().split()

        bm25 = BM25Okapi(tokenized_docs)
        scores = bm25.get_scores(tokenized_query)

        # Attach BM25 scores
        scored_candidates = []
        for i, candidate in enumerate(candidates):
            scored_candidate = candidate.copy()
            scored_candidate["bm25_score"] = float(scores[i])
            scored_candidates.append(scored_candidate)

        # Sort by BM25 score
        scored_candidates.sort(key=lambda x: x["bm25_score"], reverse=True)
        return scored_candidates[:top_k]

    def _reciprocal_rank_fusion(self, vector_results: list[dict],
                                 keyword_results: list[dict],
                                 top_k: int, k: int = 60) -> list[dict]:
        """Combine vector and keyword results using Reciprocal Rank Fusion."""
        fusion_scores = {}
        doc_map = {}

        # Score from vector results
        for rank, doc in enumerate(vector_results):
            doc_key = doc["text"][:100]  # Use first 100 chars as key
            fusion_scores[doc_key] = fusion_scores.get(doc_key, 0) + 1 / (k + rank + 1)
            doc_map[doc_key] = doc

        # Score from keyword results
        for rank, doc in enumerate(keyword_results):
            doc_key = doc["text"][:100]
            fusion_scores[doc_key] = fusion_scores.get(doc_key, 0) + 1 / (k + rank + 1)
            doc_map[doc_key] = doc

        # Sort by fusion score
        sorted_keys = sorted(fusion_scores.keys(), 
                           key=lambda x: fusion_scores[x], reverse=True)

        results = []
        for key in sorted_keys[:top_k]:
            doc = doc_map[key]
            doc["fusion_score"] = fusion_scores[key]
            doc["relevance_score"] = fusion_scores[key]
            results.append(doc)

        return results


# Singleton
_retrieval_service = None

def get_retrieval_service() -> RetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
