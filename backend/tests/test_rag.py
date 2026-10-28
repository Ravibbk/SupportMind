"""Unit tests for the SupportMind RAG subsystem."""

from pathlib import Path

import numpy as np

from app.rag.bm25 import BM25InvertedIndex
from app.rag.chunker import Chunk, chunk_fixed_size, chunk_heading_aware
from app.rag.embedder import embed_query, embed_texts
from app.rag.hybrid import HybridRetriever
from app.rag.loader import Document, load_file
from app.rag.pipeline import RAGPipeline
from app.rag.vector_store import VectorStore

BASE_DIR = Path(__file__).resolve().parent.parent
POLICIES_DIR = BASE_DIR / "data" / "policies"


def test_document_loader():
    """Verify loading Markdown document preserves content and metadata."""
    doc_path = POLICIES_DIR / "returns_refunds.md"
    doc = load_file(doc_path)
    assert isinstance(doc, Document)
    assert doc.source == "returns_refunds.md"
    assert "30-day" in doc.text.lower()
    assert doc.file_type == "md"


def test_chunking_strategies():
    """Verify both fixed-size and heading-aware chunking output valid chunks."""
    doc_path = POLICIES_DIR / "shipping_delivery.md"
    doc = load_file(doc_path)

    # Strategy 1: Fixed size
    fixed_chunks = chunk_fixed_size(doc, chunk_size=300, chunk_overlap=30)
    assert len(fixed_chunks) > 1
    assert all(isinstance(c, Chunk) for c in fixed_chunks)

    # Strategy 2: Heading aware
    heading_chunks = chunk_heading_aware(doc, max_chunk_size=500, chunk_overlap=50)
    assert len(heading_chunks) > 1
    sections = [c.section for c in heading_chunks]
    assert any("shipping speeds" in s.lower() for s in sections)


def test_embedder_normalization():
    """Verify FastEmbed embeddings are unit-normalized float32 vectors."""
    texts = ["How do I track my order?", "Can I get a refund?"]
    embeddings = embed_texts(texts)
    assert embeddings.shape == (2, 384)
    assert embeddings.dtype == np.float32

    # L2 Norm of each embedding should be approximately 1.0
    norms = np.linalg.norm(embeddings, axis=1)
    np.testing.assert_allclose(norms, [1.0, 1.0], atol=1e-4)

    # Query embedding
    q_vec = embed_query("What is the return window?")
    assert q_vec.shape == (384,)


def test_bm25_inverted_index():
    """Verify custom BM25 index scores relevant keywords highest."""
    chunks = [
        Chunk(chunk_id="c1", text="NovaCart return window is 30 days for clothing and apparel.", source="returns.md", section="Returns", chunk_index=0),
        Chunk(chunk_id="c2", text="Standard ground shipping takes 3 to 5 business days by FedEx.", source="shipping.md", section="Shipping", chunk_index=1),
        Chunk(chunk_id="c3", text="Electronic items include a 1-year limited repair warranty.", source="warranty.md", section="Warranty", chunk_index=2),
    ]
    bm25 = BM25InvertedIndex()
    bm25.index_chunks(chunks)

    # Search for return keywords
    results = bm25.search("clothing return window", top_k=2)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert top_chunk.chunk_id == "c1"
    assert score > 0.0


def test_vector_store_faiss_and_numpy_fallback():
    """Verify vector search works on both FAISS and pure NumPy fallback."""
    chunks = [
        Chunk(chunk_id="c1", text="Return policy details 30 days.", source="returns.md", section="Ret", chunk_index=0),
        Chunk(chunk_id="c2", text="FedEx overnight shipping speeds.", source="shipping.md", section="Ship", chunk_index=1)
    ]
    texts = [c.text for c in chunks]
    embeddings = embed_texts(texts)

    # Test FAISS backend
    vs_faiss = VectorStore(backend="faiss")
    vs_faiss.add_chunks(chunks, embeddings)
    q_vec = embed_query("overnight shipping FedEx")
    res_faiss = vs_faiss.search(q_vec, top_k=1)
    assert len(res_faiss) == 1
    assert res_faiss[0][0].chunk_id == "c2"

    # Test NumPy Fallback backend
    vs_numpy = VectorStore(backend="numpy")
    vs_numpy.add_chunks(chunks, embeddings)
    res_numpy = vs_numpy.search(q_vec, top_k=1)
    assert len(res_numpy) == 1
    assert res_numpy[0][0].chunk_id == "c2"


def test_hybrid_search_rrf():
    """Verify Reciprocal Rank Fusion merges dense and sparse results."""
    chunks = [
        Chunk(chunk_id="c1", text="NovaCart 30-day return policy for items in original box.", source="ret.md", section="1", chunk_index=0),
        Chunk(chunk_id="c2", text="Shipping rates for Standard Ground and Overnight Express.", source="ship.md", section="2", chunk_index=1)
    ]
    embeddings = embed_texts([c.text for c in chunks])

    vs = VectorStore(backend="numpy")
    vs.add_chunks(chunks, embeddings)

    bm25 = BM25InvertedIndex()
    bm25.index_chunks(chunks)

    retriever = HybridRetriever(vs, bm25)
    fused_results = retriever.retrieve("What is the return window for items?", top_k=2)
    assert len(fused_results) == 2
    assert fused_results[0][0].chunk_id == "c1"


def test_rag_pipeline_end_to_end_with_citations():
    """Verify end-to-end RAG pipeline indexes documents and returns answers with citations."""
    pipeline = RAGPipeline(use_reranker=False, cache_capacity=10)
    indexed_count = pipeline.index_documents_from_directory(POLICIES_DIR)
    assert indexed_count > 0

    # Ask grounded policy question
    resp = pipeline.answer_query("What is the standard return window at NovaCart?", prompt_version="v3")
    assert resp.answer != ""
    assert resp.confidence > 0.5
    assert not resp.is_unanswerable
    assert len(resp.retrieved_chunks) > 0
    assert resp.from_cache is False

    # Second query should hit the LRU cache
    cached_resp = pipeline.answer_query("What is the standard return window at NovaCart?", prompt_version="v3")
    assert cached_resp.from_cache is True
    assert cached_resp.answer == resp.answer
