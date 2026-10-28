"""Regenerate policy_embeddings.npz using the zero-download hash embedder.

Run from the repo root:
    python scripts/regen_embeddings.py
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import numpy as np  # noqa: E402

from app.rag.chunker import chunk_heading_aware  # noqa: E402
from app.rag.embedder import embed_texts  # noqa: E402
from app.rag.loader import load_directory  # noqa: E402

DOCS_DIR = BACKEND_DIR / "data" / "policies"
OUT_FILE = BACKEND_DIR / "data" / "policy_embeddings.npz"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def main() -> None:
    raw_docs = load_directory(DOCS_DIR)
    all_chunks = []
    for doc in raw_docs:
        all_chunks.extend(chunk_heading_aware(doc, max_chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP))

    print(f"Loaded {len(all_chunks)} chunks from {len(raw_docs)} documents")
    texts = [c.text for c in all_chunks]
    embeddings = embed_texts(texts)
    np.savez_compressed(OUT_FILE, embeddings=embeddings)
    print(f"Saved {embeddings.shape} embeddings -> {OUT_FILE}")


if __name__ == "__main__":
    main()

