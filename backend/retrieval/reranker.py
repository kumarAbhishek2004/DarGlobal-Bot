import os
import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    """Fast, memory-safe Reranker combining exact token affinity, brand boost, and optional CrossEncoder."""

    def __init__(self, model_name: str = None):
        # Only load heavy transformer reranker if explicitly requested in environment
        self.model_name = model_name or os.getenv("RERANKER_MODEL", "")
        self.model = None
        if self.model_name:
            self._load_model()
        else:
            logger.info("Using fast, zero-latency cross-scoring reranker (avoids 1GB model download and memory spikes).")

    def _load_model(self):
        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading CrossEncoder: {self.model_name}...")
            self.model = CrossEncoder(self.model_name, max_length=512)
            logger.info("CrossEncoder loaded successfully!")
        except Exception as e:
            logger.info(f"CrossEncoder model not loaded ({e}). Using optimized lexical-semantic cross-scoring.")
            self.model = None

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        """Scores candidate chunks against the query and returns top_k."""
        if not candidates:
            return []

        if self.model is not None:
            try:
                pairs = [[query, c["text"]] for c in candidates]
                scores = self.model.predict(pairs)
                ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
                return [(chunk, float(score)) for chunk, score in ranked[:top_k]]
            except Exception as e:
                logger.warning(f"CrossEncoder inference failed ({e}); falling back to lexical-semantic scorer.")

        # High-precision lexical & entity cross-scoring
        q_tokens = [t.lower() for t in query.split() if len(t) > 2]
        scored = []
        for c in candidates:
            text_lower = c.get("text", "").lower()
            title_lower = c.get("title", "").lower()
            brand_lower = c.get("brand", "").lower()
            city_lower = c.get("city", "").lower()
            country_lower = c.get("country", "").lower()

            score = 0.0
            for t in q_tokens:
                if t in title_lower:
                    score += 4.0  # Exact title match
                if t in brand_lower:
                    score += 3.5  # Brand match (Pagani, Missoni, Trump, Lamborghini)
                if t in city_lower or t in country_lower:
                    score += 2.5  # Geographic match
                if t in text_lower:
                    score += 1.0  # Document body match

            # Relevance boost for brand match
            if any(b in query.lower() for b in ["pagani", "missoni", "lamborghini", "trump", "w residences", "elie saab"]):
                if c.get("source") == "DarGlobal":
                    score += 2.0

            scored.append((c, score))

        ranked = sorted(scored, key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
