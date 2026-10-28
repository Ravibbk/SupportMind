# SupportMind System Architecture

## 1. System Overview

SupportMind is architected as a modular, enterprise-ready AI copilot for e-commerce customer support. The system decouples request ingestion, security sanitization, intent classification, hybrid information retrieval, agentic tool execution, and quality auditing.

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT TIER                                       |
|  React 18 + Vite + Tailwind CSS + Framer Motion (Glassmorphic Dark/Light SaaS UI) |
+-----------------------------------------------------------------------------------+
                                         |  HTTP / SSE
                                         v
+-----------------------------------------------------------------------------------+
|                                 API GATEWAY                                       |
|  FastAPI (Async endpoints, Pydantic V2 validation, CORS, Rate Limiting)          |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                             SECURITY GUARDRAILS                                   |
|  - PII Masker (Regex + Token Redaction for email, phone, credit cards)            |
|  - Prompt Injection Defense (Pattern heuristics, Canary tokens, Delimiter isolation)|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                             AGENTIC ROUTER LAYER                                  |
|  - ML Ticket Classifier (TF-IDF + Logistic Regression / SVM)                      |
|  - Intent Detection LLM fallback                                                  |
+-----------------------------------------------------------------------------------+
             |                                |                              |
             v                                v                              v
+------------------------+  +------------------------+  +---------------------------+
|    KNOWLEDGE AGENT     |  |       DATA AGENT       |  |       ACTION AGENT        |
|  - Hybrid RAG Search   |  |  - Parameterized SQLite|  |  - Create Ticket          |
|  - Chunk Grounding     |  |  - Order Lookup        |  |  - Refund Request         |
|  - Citation Generator  |  |  - Shipping Timeline   |  |  [HUMAN APPROVAL GATE]    |
+------------------------+  +------------------------+  +---------------------------+
             |                                                               |
             +------------------------------->+<-----------------------------+
                                              |
                                              v
+-----------------------------------------------------------------------------------+
|                               CRITIC & AUDIT AGENT                                |
|  - Compares draft claims vs. retrieved chunk evidence                              |
|  - Verifies factual consistency and suppresses hallucinated claims                |
+-----------------------------------------------------------------------------------+
                                              |
                                              v
+-----------------------------------------------------------------------------------+
|                             EXECUTION TRACE RECORDER                              |
|  - Records step latencies, token consumption, retrieval scores to SQLite / Memory  |
+-----------------------------------------------------------------------------------+
```

## 2. RAG Pipeline Mechanics
1. **Document Loading**: Parses Markdown, TXT, and PDF policy docs.
2. **Chunking Strategies**:
   - Fixed-size sliding window with token/character overlap.
   - Heading-aware semantic chunking (splitting on Markdown headings `#`, `##`, `###`).
3. **Dense Vector Search**: Embeds chunks using FastEmbed (`BAAI/bge-small-en-v1.5`), indexed via FAISS (with vector dot-product / cosine similarity NumPy fallback).
4. **Sparse BM25 Search**: Native inverted index computing term frequencies and inverted document frequencies with Robertson BM25 saturation constants ($k_1=1.5, b=0.75$).
5. **Reciprocal Rank Fusion (RRF)**: Merges sparse and dense ranked lists:
   $$RRF_{score}(d) = \sum_{m \in M} \frac{1}{60 + rank_m(d)}$$
6. **Custom DSA Top-K**: Min-heap selection ($O(N \log K)$) ensuring bounded memory overhead.
7. **LRU Query Cache**: In-memory hash-map with doubly-linked list ($O(1)$ lookup and eviction) for frequent customer questions.

## 3. Human-in-the-Loop Safeguards
Actions with financial or state-altering consequences (e.g. issuing refunds or modifying high-priority escalation tickets) emit a `pending_approval` status. The API and UI pause execution until an authenticated human operator clicks "Approve" or "Reject".
