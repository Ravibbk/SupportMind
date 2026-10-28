# SupportMind Machine Learning & RAG Experiments Log

This document records all scientific hypotheses, benchmarks, modeling comparisons, and post-mortems conducted during the engineering of SupportMind.

---

## 1. Ticket Classification Modeling (Phase 1)
*To be populated with empirical evaluation results, confusion matrices, and precision/recall tradeoffs between Logistic Regression and Random Forest/SVM.*

### Hypotheses
1. N-gram TF-IDF representations (1-2 grams) combined with calibrated Logistic Regression will yield fast inference (<5ms) and superior F1 score compared to shallow tree ensembles on short, noisy customer messages.
2. Typos and informal punctuation in customer messages degrade high-dimensional token representations; subword features and text normalization will recover lost recall.

---

## 2. RAG Retrieval & Prompting Experiments (Phase 4)
*To be populated with empirical runs comparing Vector Only vs. BM25 Only vs. Hybrid Search vs. Hybrid + Reranker across 60 curated evaluation test cases.*

### Configurations Tested
- **Config A**: LLM Only (Zero-shot baseline, no retrieval)
- **Config B**: Dense Vector Search Only (FastEmbed BGE-small)
- **Config C**: Hybrid Search (Custom BM25 + FastEmbed via RRF)
- **Config D**: Hybrid Search + Cross-Encoder Reranker

### Key Metrics Tracked
- Retrieval Hit-Rate@K
- Mean Reciprocal Rank (MRR)
- Answer Correctness (LLM-as-a-judge score 1-5)
- Faithfulness / Hallucination Rate
- Refusal Accuracy (clean refusal on out-of-domain / unanswerable queries)
- Latency (p50, p95)
- Estimated Token Cost ($/1k requests)
