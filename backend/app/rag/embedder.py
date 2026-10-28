"""Embedding generator wrapping FastEmbed (BAAI/bge-small-en-v1.5) for CPU inference."""


import hashlib

import numpy as np
from fastembed import TextEmbedding

# Global cached embedding model instance
_EMBEDDER_INSTANCE: TextEmbedding | None = None
DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"


def get_embedder(model_name: str = DEFAULT_MODEL) -> TextEmbedding:
    """Singleton getter for FastEmbed TextEmbedding model with single-thread optimization."""
    global _EMBEDDER_INSTANCE
    if _EMBEDDER_INSTANCE is None:
        try:
            _EMBEDDER_INSTANCE = TextEmbedding(model_name=model_name, threads=1)
        except TypeError:
            _EMBEDDER_INSTANCE = TextEmbedding(model_name=model_name)
    return _EMBEDDER_INSTANCE


def _fallback_embed_texts(texts: list[str], dim: int = 384) -> np.ndarray:
    """Ultra-lightweight deterministic projection for memory-constrained environments (<1MB RAM)."""
    vectors = np.zeros((len(texts), dim), dtype=np.float32)
    for i, text in enumerate(texts):
        tokens = text.lower().split()
        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vectors[i, idx] += sign
    return vectors


def embed_texts(texts: list[str], model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """Generate normalized dense embeddings for a list of strings with graceful memory fallback."""
    if not texts:
        return np.empty((0, 384), dtype=np.float32)

    try:
        embedder = get_embedder(model_name)
        embeddings = list(embedder.embed(texts))
        arr = np.array(embeddings, dtype=np.float32)
    except Exception:
        arr = _fallback_embed_texts(texts)

    # Normalize vectors to unit length for cosine similarity via dot product
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return arr / norms


def embed_query(query: str, model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """Generate normalized 1D embedding for a single query string.

    Args:
        query: User question or search phrase.
        model_name: FastEmbed model identifier.

    Returns:
        1D numpy array of shape (embedding_dim,).
    """
    return embed_texts([query], model_name=model_name)[0]
