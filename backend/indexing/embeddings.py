import os
import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    """Handles text embeddings with sentence-transformers (BGE) and a zero-dependency fallback."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Attempting to import sentence_transformers...")
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer: {self.model_name} (this may download weights on first run)...")
            self.model = SentenceTransformer(self.model_name)
            logger.info("SentenceTransformer loaded successfully!")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({e}). Using deterministic hash-dense vectorizer fallback.")
            self.model = None

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encodes a list of texts into L2-normalized dense float32 vectors."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False, batch_size=32)
                return np.asarray(embeddings, dtype=np.float32)
            except Exception as e:
                logger.warning(f"Embedding encoding failed with model ({e}); falling back to hash vectorizer.")

        # Fallback: 384-dimensional deterministic feature hashing vectorizer with L2 normalization
        dim = 384
        vectors = np.zeros((len(texts), dim), dtype=np.float32)
        for i, text in enumerate(texts):
            tokens = text.lower().split()
            if not tokens:
                continue
            for token in tokens:
                h = abs(hash(token)) % dim
                vectors[i, h] += 1.0
            norm = np.linalg.norm(vectors[i])
            if norm > 0:
                vectors[i] /= norm

        return vectors

    def encode_query(self, query: str) -> np.ndarray:
        """Encodes a single query string into a normalized 1D vector."""
        vec = self.encode([query])
        return vec[0]
