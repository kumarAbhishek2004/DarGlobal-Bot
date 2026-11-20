from typing import List, Tuple, Dict, Any

def reciprocal_rank_fusion(
    semantic_results: List[Tuple[Dict[str, Any], float]],
    keyword_results: List[Tuple[Dict[str, Any], float]],
    k: int = 60,
    top_k: int = 15
) -> List[Tuple[Dict[str, Any], float]]:
    """Combines semantic and keyword ranked lists using Reciprocal Rank Fusion (RRF)."""
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, Dict[str, Any]] = {}

    # 1. Process Semantic Ranks
    for rank, (chunk, _) in enumerate(semantic_results, start=1):
        cid = chunk["chunk_id"]
        chunk_map[cid] = chunk
        scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank))

    # 2. Process Keyword Ranks
    for rank, (chunk, _) in enumerate(keyword_results, start=1):
        cid = chunk["chunk_id"]
        chunk_map[cid] = chunk
        scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank))

    # Sort descending by combined RRF score
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    fused_results = [(chunk_map[cid], score) for cid, score in sorted_items[:top_k]]

    return fused_results
