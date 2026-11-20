import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from .semantic import SemanticRetriever
from .keyword import KeywordRetriever
from .rrf import reciprocal_rank_fusion
from .reranker import CrossEncoderReranker
from backend.indexing.embeddings import EmbeddingEngine

logger = logging.getLogger(__name__)

class HybridRetriever:
    """Production Hybrid Retriever combining Dense FAISS + Sparse BM25 + RRF + Cross-Encoder Reranker."""

    def __init__(self, base_data_dir: Path, embed_engine: EmbeddingEngine = None):
        self.base_data_dir = Path(base_data_dir)
        self.indices_dir = self.base_data_dir / "indices"
        self.chunks_path = self.base_data_dir / "chunks" / "chunks.json"
        self.bm25_path = self.indices_dir / "bm25.pkl"

        self.embed_engine = embed_engine or EmbeddingEngine()
        self.semantic = SemanticRetriever(self.indices_dir, self.chunks_path, self.embed_engine)
        self.keyword = KeywordRetriever(self.bm25_path, self.chunks_path)
        self.reranker = CrossEncoderReranker()

    def retrieve(self, query: str, top_k: int = 4, candidate_k: int = 15) -> List[Dict[str, Any]]:
        """Executes full hybrid search pipeline:
        1. Dense retrieval (FAISS)
        2. Sparse retrieval (BM25)
        3. Reciprocal Rank Fusion (RRF)
        4. Cross-Encoder Reranker
        """
        logger.info(f"Hybrid retrieval for query: '{query}'")

        # 1. Semantic Search
        dense_results = self.semantic.search(query, top_k=candidate_k)
        # 2. Keyword Search
        sparse_results = self.keyword.search(query, top_k=candidate_k)

        # 3. Reciprocal Rank Fusion
        fused = reciprocal_rank_fusion(dense_results, sparse_results, k=60, top_k=candidate_k)
        candidate_chunks = [c for c, _ in fused]

        # 4. Cross-Encoder Reranker
        reranked = self.reranker.rerank(query, candidate_chunks, top_k=top_k)

        final_docs = []
        for rank, (chunk, score) in enumerate(reranked, start=1):
            doc = {
                "rank": rank,
                "relevance_score": round(float(score), 4),
                "title": chunk.get("title"),
                "source": chunk.get("source"),
                "brand": chunk.get("brand"),
                "city": chunk.get("city"),
                "district": chunk.get("district"),
                "country": chunk.get("country"),
                "property_type": chunk.get("property_type"),
                "price": chunk.get("price"),
                "bedrooms": chunk.get("bedrooms"),
                "area_sqm": chunk.get("area_sqm"),
                "handover_date": chunk.get("handover_date"),
                "url": chunk.get("url"),
                "text": chunk.get("text")
            }
            final_docs.append(doc)

        logger.info(f"Retrieved {len(final_docs)} reranked contexts.")
        return final_docs
