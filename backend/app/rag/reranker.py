"""Lightweight Reranker module using FastEmbed TextCrossEncoder with graceful fallback."""

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
    """Reranker supporting cross-encoder inference and heuristic relevance scoring."""

    def __init__(self, enabled: bool = True, model_name: str = "BAAI/bge-reranker-base"):
        self.enabled = enabled
        self.model_name = model_name

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

        reranker = _get_reranker(self.model_name)

        if reranker is not None:
            try:
                # fastembed rerank yields scores
                scores = list(reranker.rerank(query, texts))
                scored_candidates = [(float(score), chunk) for score, chunk in zip(scores, candidates, strict=False)]
                top_results = top_k_heap(scored_candidates, k=top_k)
                return [(chunk, score) for score, chunk in top_results]
            except Exception:
                # Graceful fallback if cross-encoder fails to run
                pass

        # Heuristic term-overlap relevance fallback
        q_tokens = set(query.lower().split())
        scored_candidates = []
        for chunk, orig_score in chunks_with_scores:
            c_tokens = set(chunk.text.lower().split())
            overlap = len(q_tokens.intersection(c_tokens))
            bonus_score = orig_score + (0.1 * overlap)
            scored_candidates.append((bonus_score, chunk))

        top_results = top_k_heap(scored_candidates, k=top_k)
        return [(chunk, score) for score, chunk in top_results]
