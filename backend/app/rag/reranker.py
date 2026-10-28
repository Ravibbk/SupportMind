"""Lightweight Reranker module using FastEmbed TextCrossEncoder with graceful fallback."""

import re
from typing import Any

from app.core.heap_topk import top_k_heap
from app.rag.chunker import Chunk

try:
    from fastembed.rerank.cross_encoder import TextCrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False

_RERANKER_MODEL: Any | None = None


def _get_reranker(model_name: str = "BAAI/bge-reranker-base"):
    global _RERANKER_MODEL
    if _RERANKER_MODEL is None and CROSS_ENCODER_AVAILABLE:
        try:
            _RERANKER_MODEL = TextCrossEncoder(model_name=model_name)
        except Exception:
            _RERANKER_MODEL = None
    return _RERANKER_MODEL


class Reranker:
    """Reranker supporting fast token-alignment relevance scoring and optional deep cross-encoders."""

    def __init__(self, enabled: bool = True, model_name: str = "BAAI/bge-reranker-base", use_deep_model: bool = False):
        self.enabled = enabled
        self.model_name = model_name
        self.use_deep_model = use_deep_model

    def rerank(
        self,
        query: str,
        chunks_with_scores: list[tuple[Chunk, float]],
        top_k: int = 4
    ) -> list[tuple[Chunk, float]]:
        """Rerank candidate chunks against the user query.

        Args:
            query: The user inquiry.
            chunks_with_scores: Initial candidate chunks from hybrid retrieval.
            top_k: Final number of chunks to return.

        Returns:
            List of (Chunk, reranked_score) sorted in descending order.
        """
        if not chunks_with_scores:
            return []

        # If reranking disabled, return top_k candidates directly
        if not self.enabled:
            return chunks_with_scores[:top_k]

        candidates = [chunk for chunk, _ in chunks_with_scores]
        texts = [c.text for c in candidates]

        if self.use_deep_model:
            reranker = _get_reranker(self.model_name)
            if reranker is not None:
                try:
                    scores = list(reranker.rerank(query, texts))
                    scored_candidates = [(float(score), chunk) for score, chunk in zip(scores, candidates, strict=False)]
                    top_results = top_k_heap(scored_candidates, k=top_k)
                    return [(chunk, score) for score, chunk in top_results]
                except Exception:
                    pass

        # Fast heuristic exact-term & proximity relevance reranking (0.1ms, 0 external downloads)
        q_tokens = set(re.findall(r"\b[a-zA-Z0-9_-]+\b", query.lower()))
        scored_candidates = []
        for chunk, orig_score in chunks_with_scores:
            c_text_lower = chunk.text.lower()
            c_tokens = set(re.findall(r"\b[a-zA-Z0-9_-]+\b", c_text_lower))
            overlap = len(q_tokens.intersection(c_tokens))

            # Bonus for matching title/section
            section_bonus = 0.5 if any(t in chunk.section.lower() for t in q_tokens) else 0.0
            relevance_score = orig_score + (0.15 * overlap) + section_bonus
            scored_candidates.append((relevance_score, chunk))

        top_results = top_k_heap(scored_candidates, k=top_k)
        return [(chunk, score) for score, chunk in top_results]
