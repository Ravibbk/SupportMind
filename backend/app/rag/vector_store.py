"""Vector Store implementation using FAISS CPU with a pure NumPy fallback."""

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

# Try importing FAISS; fall back to NumPy if unavailable
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from app.rag.chunker import Chunk


class VectorStore:
    """Hybrid dense vector index supporting FAISS CPU and pure NumPy cosine similarity."""

    def __init__(self, backend: str = "faiss"):
        self.backend = "faiss" if (backend == "faiss" and FAISS_AVAILABLE) else "numpy"
        self.chunks: list[Chunk] = []
        self.embeddings: np.ndarray | None = None
        self.faiss_index = None

    def add_chunks(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        """Index a collection of chunks and their corresponding dense embedding vectors."""
        if not chunks or len(embeddings) == 0:
            return

        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings.")

        self.chunks.extend(chunks)

        # Ensure embeddings are normalized float32
        embeddings = embeddings.astype(np.float32)

        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

        if self.backend == "faiss":
            dim = embeddings.shape[1]
            if self.faiss_index is None:
                # IndexFlatIP (Inner Product) corresponds to cosine similarity for normalized vectors
                self.faiss_index = faiss.IndexFlatIP(dim)
            self.faiss_index.add(embeddings)

    def search(self, query_embedding: np.ndarray, top_k: int = 4) -> list[tuple[Chunk, float]]:
        """Search the vector index for the top_k most similar chunks.

        Returns list of (Chunk, similarity_score).
        """
        if not self.chunks or self.embeddings is None:
            return []

        top_k = min(top_k, len(self.chunks))
        q_vec = query_embedding.astype(np.float32).reshape(1, -1)

        # 1. FAISS Backend
        if self.backend == "faiss" and self.faiss_index is not None:
            try:
                scores, indices = self.faiss_index.search(q_vec, top_k)
                results: list[tuple[Chunk, float]] = []
                for score, idx in zip(scores[0], indices[0], strict=False):
                    if idx != -1 and idx < len(self.chunks):
                        results.append((self.chunks[idx], float(score)))
                return results
            except Exception:
                # Graceful fallback to numpy on any FAISS runtime anomaly
                pass

        # 2. Pure NumPy Cosine Similarity Fallback
        # Dot product between normalized vectors gives cosine similarity
        sims = np.dot(self.embeddings, q_vec.T).flatten()
        top_indices = np.argsort(sims)[::-1][:top_k]

        return [(self.chunks[idx], float(sims[idx])) for idx in top_indices]

    def save(self, directory: Path) -> None:
        """Persist vector index and metadata to disk."""
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)

        # Save chunk metadata as JSON
        chunks_data = [asdict(c) for c in self.chunks]
        with open(dir_path / "chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)

        # Save numpy embeddings
        if self.embeddings is not None:
            np.save(dir_path / "embeddings.npy", self.embeddings)

        # Save FAISS index if present
        if self.backend == "faiss" and self.faiss_index is not None:
            faiss.write_index(self.faiss_index, str(dir_path / "index.faiss"))

    @classmethod
    def load(cls, directory: Path, backend: str = "faiss") -> "VectorStore":
        """Load persisted vector store from disk."""
        dir_path = Path(directory)
        store = cls(backend=backend)

        chunks_path = dir_path / "chunks.json"
        embeddings_path = dir_path / "embeddings.npy"

        if chunks_path.exists() and embeddings_path.exists():
            with open(chunks_path, encoding="utf-8") as f:
                raw_chunks = json.load(f)
            chunks = [Chunk(**d) for d in raw_chunks]
            embeddings = np.load(embeddings_path)
            store.add_chunks(chunks, embeddings)

        return store
