"""RAG Pipeline Orchestrator for SupportMind.

Integrates:
- Document Loading & Heading-Aware Chunking
- FastEmbed Vector Embeddings + FAISS / NumPy Vector Store
- Scratch BM25 Inverted Index Keyword Retrieval
- Reciprocal Rank Fusion (RRF) with Custom Min-Heap Top-K
- FastEmbed Cross-Encoder Reranker
- Prompt Versioning (v1, v2, v3)
- Google Gemini LLM Generation with strict citation JSON schema
- O(1) LRU Query Caching
"""

import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.config import settings
from app.core.lru_cache import LRUCache
from app.llm.base import LLMProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.prompts import get_prompt_and_system
from app.rag.bm25 import BM25InvertedIndex
from app.rag.chunker import Chunk, chunk_heading_aware
from app.rag.embedder import embed_texts
from app.rag.hybrid import HybridRetriever
from app.rag.loader import load_directory
from app.rag.reranker import Reranker
from app.rag.vector_store import VectorStore


class Citation(BaseModel):
    """Source citation identifying document, section, and verified snippet."""

    source: str = Field(..., description="Source policy filename")
    section: str = Field(..., description="Document section heading")
    snippet: str = Field(..., description="Verbatim text quote from policy")


class RAGResponse(BaseModel):
    """Structured response from the SupportMind RAG pipeline."""

    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = 0.95
    is_unanswerable: bool = False
    thought: str | None = None
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list)
    latency_ms: float = 0.0
    prompt_version: str = "v3"
    from_cache: bool = False


class RAGPipeline:
    """Production RAG orchestrator for NovaCart customer policy support."""

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        use_reranker: bool | None = None,
        cache_capacity: int = 128
    ):
        self.vector_store = VectorStore(backend=settings.VECTOR_STORE_BACKEND)
        self.bm25_index = BM25InvertedIndex()
        self.hybrid_retriever = HybridRetriever(self.vector_store, self.bm25_index)
        self.reranker = Reranker(enabled=settings.USE_RERANKER if use_reranker is None else use_reranker)
        self.llm_provider = llm_provider or GeminiProvider()
        self.cache = LRUCache(capacity=cache_capacity)
        self.indexed_chunks: list[Chunk] = []

    def index_documents_from_directory(self, docs_dir: Path) -> int:
        """Load, chunk, embed, and index all policy documents in the directory."""
        raw_docs = load_directory(docs_dir)
        all_chunks: list[Chunk] = []

        for doc in raw_docs:
            doc_chunks = chunk_heading_aware(
                doc,
                max_chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            all_chunks.extend(doc_chunks)

        if not all_chunks:
            return 0

        self.indexed_chunks = all_chunks

        # 1. Index in BM25 Inverted Index
        self.bm25_index.index_chunks(all_chunks)

        # 2. Generate Dense Embeddings and Index in VectorStore
        texts = [c.text for c in all_chunks]
        embeddings = embed_texts(texts)
        self.vector_store.add_chunks(all_chunks, embeddings)

        # Clear query cache on re-indexing
        self.cache.clear()
        return len(all_chunks)

    def answer_query(
        self,
        query: str,
        prompt_version: str | None = None,
        top_k: int | None = None
    ) -> RAGResponse:
        """Process a customer question end-to-end through the RAG pipeline."""
        start_time = time.perf_counter()
        version = prompt_version or settings.PROMPT_VERSION
        k = top_k or settings.TOP_K

        # Check LRU Cache
        cache_key = f"{version}:{k}:{query.strip().lower()}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            cached_resp = RAGResponse(**cached)
            cached_resp.from_cache = True
            cached_resp.latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return cached_resp

        # 1. Hybrid Retrieval (Vector + BM25 via RRF)
        retrieved_with_scores = self.hybrid_retriever.retrieve(query, top_k=k * 2)

        # 2. Rerank candidates
        final_with_scores = self.reranker.rerank(query, retrieved_with_scores, top_k=k)
        selected_chunks = [chunk for chunk, _ in final_with_scores]

        # 3. Format Versioned Prompt
        prompt_text, system_instruction = get_prompt_and_system(version, query, selected_chunks)

        # 4. Invoke LLM for Structured Grounded JSON Generation
        llm_json = self.llm_provider.generate_json(
            prompt=prompt_text,
            system_instruction=system_instruction,
            temperature=0.1
        )

        total_latency = round((time.perf_counter() - start_time) * 1000, 2)

        # 5. Parse and Validate Citations
        citations = []
        for c in llm_json.get("citations", []):
            try:
                citations.append(Citation(**c))
            except Exception:
                pass

        serialized_chunks = [
            {"chunk_id": c.chunk_id, "source": c.source, "section": c.section, "text": c.text, "score": round(s, 4)}
            for c, s in final_with_scores
        ]

        response = RAGResponse(
            answer=llm_json.get("answer", "No answer could be formulated."),
            citations=citations,
            confidence=float(llm_json.get("confidence", 0.90)),
            is_unanswerable=bool(llm_json.get("is_unanswerable", False)),
            thought=llm_json.get("thought"),
            retrieved_chunks=serialized_chunks,
            latency_ms=total_latency,
            prompt_version=version,
            from_cache=False
        )

        # Store in LRU Cache
        self.cache.put(cache_key, response.model_dump())
        return response
