"""
AdaptiveLens AI - FAISS Vector Store
Manages FAISS index for document embeddings with persistent storage.
"""

import faiss
import numpy as np
import json
import os
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages FAISS vector storage for document embeddings."""
    
    _instance = None

    def __init__(self):
        self.persist_dir = settings.chroma_persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        
        self.index = None
        self.documents: list[str] = []
        self.metadatas: list[dict] = []
        self.doc_ids: list[str] = []
        self.dimension = 3072  # Gemini embedding dimension (models/gemini-embedding-001)
        
        self._load_or_create()

    @classmethod
    def get_instance(cls):
        """Singleton pattern for vector store."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_or_create(self):
        """Load existing index or create a new one."""
        index_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.json")
        
        if os.path.exists(index_path) and os.path.exists(meta_path):
            try:
                self.index = faiss.read_index(index_path)
                self.dimension = self.index.d  # Sync with actual index dimension
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.metadatas = data.get("metadatas", [])
                    self.doc_ids = data.get("doc_ids", [])
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.warning(f"Failed to load index: {e}. Creating new.")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine after normalization)
        self.documents = []
        self.metadatas = []
        self.doc_ids = []
        logger.info("Created new FAISS index")

    def _save(self):
        """Persist index and metadata to disk."""
        index_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.json")
        
        faiss.write_index(self.index, index_path)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "documents": self.documents,
                "metadatas": self.metadatas,
                "doc_ids": self.doc_ids
            }, f, ensure_ascii=False)
        
        logger.info(f"Saved FAISS index with {self.index.ntotal} vectors")

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        """L2 normalize vectors for cosine similarity."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        return vectors / norms

    def add_documents(self, ids: list[str], embeddings: list[list[float]], 
                      documents: list[str], metadatas: list[dict]):
        """Add document chunks to the index."""
        vectors = np.array(embeddings, dtype=np.float32)
        vectors = self._normalize(vectors)
        
        # Update dimension if needed
        if self.index.ntotal == 0 and vectors.shape[1] != self.dimension:
            self.dimension = vectors.shape[1]
            self.index = faiss.IndexFlatIP(self.dimension)
        
        self.index.add(vectors)
        self.doc_ids.extend(ids)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        
        self._save()
        logger.info(f"Added {len(ids)} chunks to FAISS index")

    def query(self, query_embedding: list[float], n_results: int = 5,
              document_ids: list[str] = None) -> dict:
        """Query the index for similar documents."""
        if self.index.ntotal == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        query_vec = np.array([query_embedding], dtype=np.float32)
        query_vec = self._normalize(query_vec)
        
        # Search more if we need to filter by document_ids
        search_k = min(n_results * 3 if document_ids else n_results, self.index.ntotal)
        
        distances, indices = self.index.search(query_vec, search_k)
        
        result_docs = []
        result_metas = []
        result_dists = []
        
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            
            # Filter by document_ids if specified
            if document_ids:
                meta = self.metadatas[idx]
                if meta.get("document_id") not in document_ids:
                    continue
            
            result_docs.append(self.documents[idx])
            result_metas.append(self.metadatas[idx])
            result_dists.append(float(1 - distances[0][i]))  # Convert to distance
            
            if len(result_docs) >= n_results:
                break
        
        return {
            "documents": [result_docs],
            "metadatas": [result_metas],
            "distances": [result_dists]
        }

    def delete_document(self, document_id: str):
        """Delete all chunks belonging to a document by rebuilding the index."""
        # Find indices to keep
        keep_indices = [
            i for i, meta in enumerate(self.metadatas)
            if meta.get("document_id") != document_id
        ]
        
        if len(keep_indices) == len(self.metadatas):
            return  # Nothing to delete
        
        if not keep_indices:
            # Delete everything
            self._create_new_index()
            self._save()
            return
        
        # Reconstruct vectors for kept indices
        kept_vectors = np.zeros((len(keep_indices), self.dimension), dtype=np.float32)
        for new_idx, old_idx in enumerate(keep_indices):
            kept_vectors[new_idx] = self.index.reconstruct(old_idx)
        
        # Rebuild
        self.documents = [self.documents[i] for i in keep_indices]
        self.metadatas = [self.metadatas[i] for i in keep_indices]
        self.doc_ids = [self.doc_ids[i] for i in keep_indices]
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(kept_vectors)
        
        self._save()
        logger.info(f"Deleted document {document_id}, {len(keep_indices)} chunks remaining")

    def get_document_count(self) -> int:
        """Get total number of vectors in the index."""
        return self.index.ntotal if self.index else 0


# Global accessor
def get_vector_store() -> VectorStore:
    return VectorStore.get_instance()
