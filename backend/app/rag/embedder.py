"""Embedding generator for SupportMind — zero-download CPU-only implementation.

Strategy:
- At indexing time (startup), embeddings are loaded from the precomputed
  ``backend/data/policy_embeddings.npz`` (63 KB, committed to git).
  FastEmbed / ONNX model is NEVER downloaded on Render free tier.
- At query time, we use the same lightweight deterministic hash projection
  that was used to generate ``policy_embeddings.npz``, so vector similarity
  is internally consistent and retrieval works correctly in DEMO_MODE.
- If a real Gemini / OpenAI embedding API is configured in the future,
  this module is the single place to swap it in.
"""

import hashlib

import numpy as np

EMBEDDING_DIM = 384


def _hash_project(texts: list[str], dim: int = EMBEDDING_DIM) -> np.ndarray:
    """Deterministic TF-IDF-style hash projection.

    Each token is mapped to a dimension via MD5 hash with ±1 sign.  Vectors
    are L2-normalised so cosine similarity == dot product.  Memory: O(1) per
    token — no model weights downloaded or loaded.
    """
    vectors = np.zeros((len(texts), dim), dtype=np.float32)
    for i, text in enumerate(texts):
        tokens = text.lower().split()
        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vectors[i, idx] += sign
    # L2-normalise
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def embed_texts(texts: list[str], **_kwargs: object) -> np.ndarray:
    """Generate normalised dense embeddings for a list of strings.

    Uses the deterministic hash projection — zero network calls, zero disk
    downloads, < 1 MB RAM on the Render free tier.
    """
    if not texts:
        return np.empty((0, EMBEDDING_DIM), dtype=np.float32)
    return _hash_project(texts)


def embed_query(query: str, **_kwargs: object) -> np.ndarray:
    """Generate normalised 1-D embedding for a single query string.

    Returns:
        1-D numpy array of shape (EMBEDDING_DIM,).
    """
    return embed_texts([query])[0]
