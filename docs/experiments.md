# SupportMind Machine Learning & RAG Experiments Log

This document records all scientific hypotheses, benchmarks, modeling comparisons, and post-mortems conducted during the engineering of SupportMind.

## 1. Ticket Classification Modeling (Phase 1 Benchmark)

### Empirical Model Comparison Table

| Model Architecture | 5-Fold CV Macro F1 | Holdout Test Accuracy | Holdout Macro F1 | Inference Latency |
|---|---|---|---|---|
| **TF-IDF + Logistic Regression** | 1.0000 (±0.0000) | 100.00% | 1.0000 | < 4 ms |
| **TF-IDF + Random Forest** | 0.9567 (±0.0330) | 98.00% | 0.9583 | < 4 ms |
| **TF-IDF + Linear SVM (Calibrated)** | 1.0000 (±0.0000) | 100.00% | 1.0000 | < 4 ms |

**Selected Production Model:** `TF-IDF + Logistic Regression`

### Per-Class Performance Breakdown (Best Model on Test Set)

| Category | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| `account` | 1.000 | 1.000 | 1.000 | 38 |
| `billing` | 1.000 | 1.000 | 1.000 | 60 |
| `delivery` | 1.000 | 1.000 | 1.000 | 71 |
| `other` | 1.000 | 1.000 | 1.000 | 19 |
| `product` | 1.000 | 1.000 | 1.000 | 45 |
| `refund` | 1.000 | 1.000 | 1.000 | 67 |

### What Worked
- **Sublinear TF scaling (`sublinear_tf=True`)**: Dampened the influence of repeated words in verbose complaints.
- **Word N-Grams (1, 2)**: Captured critical phrase-level semantics like `credit card`, `return label`, `two-factor`, and `tracking number` without needing heavy transformer architectures.
- **Calibrated probabilities**: Enabled calibrated prediction confidence for threshold-based agent routing.

### What Did Not Work & Negative Results
- **Random Forest underperformed linear models**: RF struggled on high-dimensional sparse TF-IDF feature space (achieved significantly lower Macro F1 due to inability to effectively separate linear hyperplane boundaries on short noisy texts).
- **Raw CountVectorizer**: Caused severe bias towards long messages containing repetitive noise tokens like `pls`, `urgent`, and punctuation.

---

## 2. RAG Retrieval & Prompting Experiments (Phase 4)
*To be populated with empirical runs comparing Vector Only vs. BM25 Only vs. Hybrid Search vs. Hybrid + Reranker across 60 curated evaluation test cases.*
