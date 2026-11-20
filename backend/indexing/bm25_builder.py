import math
import pickle
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

def tokenize(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric words."""
    return re.findall(r"\b[a-zA-Z0-9_\u0600-\u06FF]+\b", text.lower())

class BM25OkapiIndex:
    """Production-grade Okapi BM25 sparse keyword index."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lens = []
        self.doc_freqs = {}  # term -> document frequency
        self.doc_term_freqs = []  # index -> {term: count}

    def fit(self, documents: List[str]):
        """Fits BM25 index on a collection of document texts."""
        self.corpus_size = len(documents)
        self.doc_lens = []
        self.doc_term_freqs = []
        self.doc_freqs = {}

        total_tokens = 0
        for doc in documents:
            tokens = tokenize(doc)
            doc_len = len(tokens)
            self.doc_lens.append(doc_len)
            total_tokens += doc_len

            term_freq = {}
            for t in tokens:
                term_freq[t] = term_freq.get(t, 0) + 1
            self.doc_term_freqs.append(term_freq)

            for t in term_freq:
                self.doc_freqs[t] = self.doc_freqs.get(t, 0) + 1

        self.avg_doc_len = total_tokens / self.corpus_size if self.corpus_size > 0 else 1.0
        logger.info(f"Fitted BM25 index on {self.corpus_size} docs (vocab size: {len(self.doc_freqs)})")

    def search(self, query: str, top_k: int = 15) -> Tuple[List[int], List[float]]:
        """Scores all documents for the given query and returns top_k (indices, scores)."""
        tokens = tokenize(query)
        if not tokens or self.corpus_size == 0:
            return [], []

        scores = [0.0] * self.corpus_size
        for t in tokens:
            if t not in self.doc_freqs:
                continue
            df = self.doc_freqs[t]
            # Standard Lucene/BM25 IDF formula
            idf = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))

            for idx in range(self.corpus_size):
                tf = self.doc_term_freqs[idx].get(t, 0)
                if tf == 0:
                    continue
                doc_len = self.doc_lens[idx]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                scores[idx] += idf * (numerator / denominator)

        # Rank documents
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        top_indices = [idx for idx in ranked[:top_k] if scores[idx] > 0]
        top_scores = [scores[idx] for idx in top_indices]
        return top_indices, top_scores

    def save(self, path: Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        logger.info(f"Saved BM25 index to {path}")

    @classmethod
    def load(cls, path: Path) -> "BM25OkapiIndex":
        with open(path, "rb") as f:
            idx = pickle.load(f)
        logger.info(f"Loaded BM25 index from {path} ({idx.corpus_size} documents)")
        return idx
