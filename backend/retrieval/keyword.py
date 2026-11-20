import json
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any
from backend.indexing.bm25_builder import BM25OkapiIndex

logger = logging.getLogger(__name__)

class KeywordRetriever:
    """Retrieves top documents using BM25 sparse keyword matching."""

    def __init__(self, bm25_path: Path, chunks_path: Path):
        self.bm25_path = Path(bm25_path)
        self.chunks_path = Path(chunks_path)
        self.bm25: BM25OkapiIndex = None
        self.chunks: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if not self.chunks_path.exists():
            logger.warning(f"Chunks file not found at {self.chunks_path}")
            return
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        if self.bm25_path.exists():
            self.bm25 = BM25OkapiIndex.load(self.bm25_path)
            logger.info(f"KeywordRetriever initialized with BM25 index.")
        else:
            logger.warning(f"BM25 index not found at {self.bm25_path}")

    def search(self, query: str, top_k: int = 15) -> List[Tuple[Dict[str, Any], float]]:
        """Searches BM25 and returns (chunk, score) list."""
        if not self.bm25 or not self.chunks:
            return []
        indices, scores = self.bm25.search(query, top_k=top_k)

        results = []
        for idx, score in zip(indices, scores):
            if 0 <= idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
        return results
