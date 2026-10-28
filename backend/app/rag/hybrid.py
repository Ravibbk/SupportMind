"""Hybrid Search using Reciprocal Rank Fusion (RRF) and custom Min-Heap Top-K selection."""


from app.core.heap_topk import top_k_heap
from app.rag.bm25 import BM25InvertedIndex
from app.rag.chunker import Chunk
from app.rag.embedder import embed_query
from app.rag.vector_store import VectorStore


def reciprocal_rank_fusion(
    ranked_lists: list[list[tuple[Chunk, float]]],
    k_rrf: int = 60,
    top_k: int = 4
) -> list[tuple[Chunk, float]]:
    """Merge multiple ranked lists using Reciprocal Rank Fusion (RRF).

    Formula:
        RRF_Score(doc) = SUM_{list in ranked_lists} ( 1.0 / (k_rrf + rank) )

    Args:
        ranked_lists: List of ranked lists, where each list contains (Chunk, original_score).
        k_rrf: Constant smoothing parameter (standard default is 60).
        top_k: Number of final results to extract using custom Min-Heap.

    Returns:
        List of (Chunk, rrf_score) tuples sorted in descending order of RRF score.
    """
    # Accumulator: chunk_id -> (Chunk, rrf_score)
    scores: dict[str, float] = {}
    chunk_map: dict[str, Chunk] = {}

    for ranked_list in ranked_lists:
        for rank, (chunk, _) in enumerate(ranked_list, start=1):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            # RRF score addition
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (k_rrf + rank))

    # Convert to list of (score, Chunk) pairs for custom Min-Heap Top-K selection
    candidates = [(score, chunk_map[cid]) for cid, score in scores.items()]

    # Use custom Min-Heap O(N log K) selection
    top_results = top_k_heap(candidates, k=top_k)

    # Return format: (Chunk, score)
    return [(chunk, score) for score, chunk in top_results]


class HybridRetriever:
    """Combines Dense Vector Search and Sparse BM25 Keyword Search."""

    def __init__(self, vector_store: VectorStore, bm25_index: BM25InvertedIndex):
        self.vector_store = vector_store
        self.bm25_index = bm25_index

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        candidate_multiplier: int = 3
    ) -> list[tuple[Chunk, float]]:
        """Perform hybrid retrieval by querying both engines and fusing with RRF.

        Args:
            query: User search query.
            top_k: Number of final top chunks to return.
            candidate_multiplier: Factor of candidate chunks to fetch from each retriever.

        Returns:
            List of (Chunk, rrf_score) sorted descending.
        """
        fetch_k = top_k * candidate_multiplier

        # 1. Dense Vector Retrieval
        q_vec = embed_query(query)
        dense_results = self.vector_store.search(q_vec, top_k=fetch_k)

        # 2. Sparse BM25 Retrieval
        bm25_results = self.bm25_index.search(query, top_k=fetch_k)

        # 3. Reciprocal Rank Fusion + Min-Heap Top-K
        return reciprocal_rank_fusion(
            ranked_lists=[dense_results, bm25_results],
            k_rrf=60,
            top_k=top_k
        )
