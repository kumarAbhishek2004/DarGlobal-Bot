import json
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any
from backend.indexing.embeddings import EmbeddingEngine
from backend.indexing.faiss_builder import FaissIndexManager

logger = logging.getLogger(__name__)

class SemanticRetriever:
    """Retrieves top documents using dense vector similarity (FAISS / Cosine)."""

    def __init__(self, indices_dir: Path, chunks_path: Path, embed_engine: EmbeddingEngine = None):
        self.indices_dir = Path(indices_dir)
        self.chunks_path = Path(chunks_path)
        self.embed_engine = embed_engine or EmbeddingEngine()
        self.faiss_mgr = FaissIndexManager(self.indices_dir)
        self.chunks: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if not self.chunks_path.exists():
            logger.warning(f"Chunks file not found at {self.chunks_path}")
            return
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        self.faiss_mgr.load()
        logger.info(f"SemanticRetriever initialized with {len(self.chunks)} chunks.")

    def search(self, query: str, top_k: int = 15) -> List[Tuple[Dict[str, Any], float]]:
        """Encodes query and returns (chunk, score) list."""
        if not self.chunks:
            return []
        q_vec = self.embed_engine.encode_query(query)
        indices, scores = self.faiss_mgr.search(q_vec, top_k=top_k)

        results = []
        for idx, score in zip(indices, scores):
            if 0 <= idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
        return results
