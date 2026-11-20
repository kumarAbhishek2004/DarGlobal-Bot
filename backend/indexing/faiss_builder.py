import os
import logging
import numpy as np
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class FaissIndexManager:
    """Manages dense vector indexing using FAISS IndexFlatIP with a NumPy fallback."""

    def __init__(self, index_dir: Path):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.faiss_path = self.index_dir / "faiss.index"
        self.npy_path = self.index_dir / "vectors.npy"
        self.index = None
        self.vectors = None

    def build_and_save(self, vectors: np.ndarray):
        """Builds and serializes the dense vector index."""
        self.vectors = np.ascontiguousarray(vectors, dtype=np.float32)
        # Always persist numpy vectors
        np.save(self.npy_path, self.vectors)
        logger.info(f"Saved dense vectors ({self.vectors.shape}) to {self.npy_path}")

        try:
            import faiss
            dim = self.vectors.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.index.add(self.vectors)
            faiss.write_index(self.index, str(self.faiss_path))
            logger.info(f"Built and saved FAISS index to {self.faiss_path}")
        except Exception as e:
            logger.warning(f"FAISS serialization skipped ({e}). Using NumPy dense index fallback.")

    def load(self) -> bool:
        """Loads index from disk."""
        if self.faiss_path.exists():
            try:
                import faiss
                self.index = faiss.read_index(str(self.faiss_path))
                logger.info(f"Loaded FAISS index from {self.faiss_path}")
                return True
            except Exception as e:
                logger.warning(f"Could not load FAISS ({e}); falling back to NumPy vectors.")

        if self.npy_path.exists():
            self.vectors = np.load(self.npy_path)
            logger.info(f"Loaded NumPy vectors from {self.npy_path} with shape {self.vectors.shape}")
            return True

        return False

    def search(self, query_vector: np.ndarray, top_k: int = 15):
        """Searches for the nearest neighbors. Returns (indices, scores)."""
        q = np.ascontiguousarray(query_vector, dtype=np.float32)
        if q.ndim == 1:
            q = np.expand_dims(q, axis=0)

        if self.index is not None:
            scores, indices = self.index.search(q, top_k)
            return indices[0], scores[0]

        if self.vectors is not None:
            # Cosine similarity on normalized vectors is dot product
            scores = np.dot(self.vectors, q[0])
            top_indices = np.argsort(scores)[::-1][:top_k]
            return top_indices, scores[top_indices]

        return np.array([]), np.array([])
