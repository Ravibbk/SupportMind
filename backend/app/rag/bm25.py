"""Custom BM25 Inverted Index Implementation from Scratch.

This module implements the Robertson-Spärck Jones Okapi BM25 scoring function
and an in-memory Inverted Index with zero external search dependencies.

Formulation:
Given a query Q with terms q_1, ..., q_n and document D:
    Score(D, Q) = SUM_{q_i in Q} IDF(q_i) * (f(q_i, D) * (k1 + 1)) / (f(q_i, D) + k1 * (1 - b + b * (|D| / avgdl)))

Where:
- f(q_i, D) is the term frequency of q_i in D.
- |D| is the document length (in tokens).
- avgdl is the average document length across the entire corpus.
- k1 = 1.5 (term frequency saturation parameter).
- b = 0.75 (document length normalization parameter).
- IDF(q_i) = ln(1 + (N - n(q_i) + 0.5) / (n(q_i) + 0.5))
"""

import math
import re
from collections import Counter

from app.rag.chunker import Chunk


def tokenize(text: str) -> list[str]:
    """Clean, lowercase, and tokenize text into alphanumeric word tokens."""
    return re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())


class BM25InvertedIndex:
    """In-memory inverted index and Robertson BM25 ranking engine."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: list[Chunk] = []
        # Inverted index structure: token -> {chunk_index: term_frequency}
        self.inverted_index: dict[str, dict[int, int]] = {}
        # Document lengths (token count per document)
        self.doc_lengths: list[int] = []
        self.avgdl: float = 0.0
        self.num_docs: int = 0

    def index_chunks(self, chunks: list[Chunk]) -> None:
        """Build the inverted index from a collection of text chunks."""
        self.chunks = list(chunks)
        self.num_docs = len(self.chunks)
        self.inverted_index.clear()
        self.doc_lengths = []

        if self.num_docs == 0:
            self.avgdl = 0.0
            return

        total_length = 0

        for doc_id, chunk in enumerate(self.chunks):
            tokens = tokenize(chunk.text)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_length += doc_len

            term_counts = Counter(tokens)
            for term, count in term_counts.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = {}
                self.inverted_index[term][doc_id] = count

        self.avgdl = total_length / self.num_docs if self.num_docs > 0 else 0.0

    def _idf(self, term: str) -> float:
        """Compute Robertson Inverse Document Frequency with smoothing."""
        doc_freq = len(self.inverted_index.get(term, {}))
        # Standard BM25 IDF formula with +1 smoothing to avoid negative weights
        return math.log(1.0 + (self.num_docs - doc_freq + 0.5) / (doc_freq + 0.5))

    def search(self, query: str, top_k: int = 4) -> list[tuple[Chunk, float]]:
        """Score all matching documents for the query terms and return top_k results.

        Returns:
            List of (Chunk, bm25_score) tuples sorted in descending order of score.
        """
        if self.num_docs == 0 or not query.strip():
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        # Candidate accumulator: doc_id -> accumulated BM25 score
        scores: dict[int, float] = {}

        for term in query_tokens:
            if term not in self.inverted_index:
                continue

            term_idf = self._idf(term)
            postings = self.inverted_index[term]

            for doc_id, tf in postings.items():
                doc_len = self.doc_lengths[doc_id]
                # BM25 term saturation calculation
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
                term_score = term_idf * (numerator / denominator)

                scores[doc_id] = scores.get(doc_id, 0.0) + term_score

        # Sort candidate documents descending by score
        ranked_doc_ids = sorted(scores.keys(), key=lambda d: scores[d], reverse=True)
        top_ids = ranked_doc_ids[:top_k]

        return [(self.chunks[doc_id], scores[doc_id]) for doc_id in top_ids]
