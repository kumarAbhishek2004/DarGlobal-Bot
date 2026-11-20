import json
import logging
from pathlib import Path
from backend.preprocessing.splitter import chunk_corpus
from backend.preprocessing.metadata import enrich_metadata
from backend.indexing.embeddings import EmbeddingEngine
from backend.indexing.faiss_builder import FaissIndexManager
from backend.indexing.bm25_builder import BM25OkapiIndex

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PROCESSED_PATH = BASE_DIR / "data" / "processed" / "corpus.json"
CHUNKS_DIR = BASE_DIR / "data" / "chunks"
INDICES_DIR = BASE_DIR / "data" / "indices"

def build_indices():
    """Builds both dense (FAISS) and sparse (BM25) search indices from the processed corpus."""
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    INDICES_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_PROCESSED_PATH.exists():
        raise FileNotFoundError(f"Processed corpus not found at {DATA_PROCESSED_PATH}. Run scraper first!")

    logger.info(f"Loading corpus from {DATA_PROCESSED_PATH}...")
    with open(DATA_PROCESSED_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)
    logger.info(f"Loaded {len(docs)} documents.")

    # 1. Chunk and enrich
    raw_chunks = chunk_corpus(docs)
    chunks = [enrich_metadata(c) for c in raw_chunks]
    chunks_path = CHUNKS_DIR / "chunks.json"
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    logger.info(f"Created and saved {len(chunks)} searchable chunks to {chunks_path}")

    # 2. Dense Index (FAISS)
    chunk_texts = [c["text"] for c in chunks]
    embed_engine = EmbeddingEngine()
    logger.info(f"Encoding {len(chunk_texts)} chunks into dense vectors...")
    vectors = embed_engine.encode(chunk_texts)
    
    faiss_mgr = FaissIndexManager(INDICES_DIR)
    faiss_mgr.build_and_save(vectors)

    # 3. Sparse Index (BM25)
    logger.info(f"Building BM25 sparse index...")
    bm25 = BM25OkapiIndex()
    bm25.fit(chunk_texts)
    bm25_path = INDICES_DIR / "bm25.pkl"
    bm25.save(bm25_path)

    logger.info("=" * 60)
    logger.info(f"SUCCESS: Dual-index build complete!")
    logger.info(f" - Documents indexed: {len(docs)}")
    logger.info(f" - Chunks created:    {len(chunks)}")
    logger.info(f" - FAISS/Dense vectors: {vectors.shape}")
    logger.info(f" - BM25 vocab size:   {len(bm25.doc_freqs)}")
    logger.info(f" - Output directory:  {INDICES_DIR}")
    logger.info("=" * 60)

if __name__ == "__main__":
    build_indices()
