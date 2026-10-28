"""Embedding generator wrapping FastEmbed (BAAI/bge-small-en-v1.5) for CPU inference."""


import numpy as np
from fastembed import TextEmbedding

# Global cached embedding model instance
_EMBEDDER_INSTANCE: TextEmbedding | None = None
DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"


def get_embedder(model_name: str = DEFAULT_MODEL) -> TextEmbedding:
    """Singleton getter for FastEmbed TextEmbedding model."""
    global _EMBEDDER_INSTANCE
    if _EMBEDDER_INSTANCE is None:
        _EMBEDDER_INSTANCE = TextEmbedding(model_name=model_name)
    return _EMBEDDER_INSTANCE


def embed_texts(texts: list[str], model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """Generate normalized dense embeddings for a list of strings.

    Args:
        texts: List of text passages or chunks.
        model_name: FastEmbed model identifier.

    Returns:
        2D numpy array of shape (len(texts), embedding_dim) with L2-normalized vectors.
    """
    if not texts:
        return np.empty((0, 384), dtype=np.float32)

    embedder = get_embedder(model_name)
    # embed returns a generator of numpy arrays
    embeddings = list(embedder.embed(texts))
    arr = np.array(embeddings, dtype=np.float32)

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
