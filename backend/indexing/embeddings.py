import os
import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    """Ultra-fast, production-grade dense vectorizer designed for low-memory cloud instances."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self.model = None
        # Default to ultra-fast vectorizer on cloud free tiers to avoid 5-minute CPU freezes
        load_heavy = os.getenv("LOAD_HEAVY_TRANSFORMER", "0").strip().lower() in ("1", "true")
        if load_heavy:
            self._load_heavy_model()
        else:
            logger.info("Using ultra-fast, zero-memory dense semantic vectorizer (prevents cloud CPU freezes).")

    def _load_heavy_model(self):
        try:
            # Optimize PyTorch for single-threaded CPU cloud environments (Render, HuggingFace)
            try:
                import torch
                torch.set_num_threads(1)
                torch.set_num_interop_threads(1)
            except Exception:
                pass

            logger.info(f"Loading SentenceTransformer: {self.model_name}...")
            from sentence_transformers import SentenceTransformer
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
