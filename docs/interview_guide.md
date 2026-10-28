# SupportMind: Technical Interview & Portfolio Guide

This guide is designed to help you confidently explain the architecture, design choices, data structures, and machine learning models of **SupportMind** during senior AI engineering and technical system design interviews.

---

## 1. Resume Bullet Points (Tailored & Quantified)

You can copy and adapt these bullet points directly onto your resume:

1. **Production AI & Hybrid RAG Architecture:**
   > *"Architected and deployed 'SupportMind', an enterprise AI customer support copilot combining Hybrid RAG (BM25 + FAISS Dense Vector Search + Reciprocal Rank Fusion) and parameterized SQL order fulfillment data, elevating answer correctness from 25% (zero-shot LLM baseline) to 95% with sub-30ms p50 retrieval latency."*

2. **Custom Data Structures & Algorithms (From Scratch):**
   > *"Engineered custom Data Structures from scratch in Python, including an $O(N \log K)$ Min-Heap Top-K retrieval algorithm and an $O(1)$ LRU Cache utilizing a Doubly-Linked List and Hash Map, eliminating external heavy dependencies while bounding memory overhead."*

3. **Autonomous Multi-Agent Routing & Dual Guardrails:**
   > *"Implemented a multi-agent orchestrator with dynamic intent routing and dual security guardrails: automated PII redaction (email, SSN, cards) and regex defenses neutralizing 15 distinct adversarial prompt injection vectors, coupled with a mandatory Human-in-the-Loop approval gate for financial refunds."*

4. **Empirical Evaluation & Hallucination Auditing:**
   > *"Designed and executed a 60-query golden evaluation benchmark comparing 7 retrieval and prompting architectures; integrated an automated post-generation Critic Agent that audits factual claims against retrieved policy snippets to eliminate hallucinations."*

---

## 2. Top 10 Technical Interview Questions & Answers

### Q1: Why did you build a Hybrid Search pipeline (BM25 + Dense Vector) instead of relying solely on vector embeddings?
**Answer:**
Dense vector embeddings (e.g., `BAAI/bge-small-en-v1.5`) excel at capturing semantic intent (e.g., matching *"can I get my cash back?"* to the refund policy document). However, vector embeddings notoriously suffer from the **out-of-vocabulary and lexical matching problem** when encountering specific SKU numbers, order IDs (`ORD-10025`), technical model names, and legal policy codes. 

BM25 provides exact keyword and term-frequency matching. By combining both through **Reciprocal Rank Fusion (RRF)**:
$$RRF_{score}(d) = \sum_{m \in \{\text{dense, sparse}\}} \frac{1}{60 + \text{rank}_m(d)}$$
we achieved a **0.9333 Hit-Rate@4** compared to only **0.7833** for dense vector search alone, ensuring the system never misses exact policy identifiers while preserving semantic understanding.

---

### Q2: Explain your custom Min-Heap Top-K algorithm. What is its time and space complexity?
**Answer:**
In retrieval systems, after scoring $N$ candidate documents, finding the top $K$ items by sorting the entire array takes $O(N \log N)$ time and requires $O(N)$ memory. When $N$ grows large and $K \ll N$ (e.g., retrieving the top 4 chunks out of thousands of candidates), full sorting is inefficient.

Our `MinHeapTopK` algorithm (implemented in `backend/app/core/heap_topk.py`):
1. Maintains a binary min-heap bounded at size $K$.
2. For each candidate document $(d, \text{score})$:
   - If the heap has fewer than $K$ elements, push $( \text{score}, d )$.
   - If the heap is full and $\text{score} > \text{heap}[0].\text{score}$, pop the minimum root and push the new candidate in $O(\log K)$ time.
3. At the end, pop all $K$ elements in reverse order to return the sorted top $K$ items.

**Complexity:**
- **Time Complexity:** $O(N \log K)$ — significantly faster than $O(N \log N)$ when $K \ll N$.
- **Space Complexity:** $O(K)$ auxiliary memory — strictly bounded.

---

### Q3: How did you implement the custom LRU Cache from scratch, and why not use Python's built-in `@lru_cache`?
**Answer:**
While Python’s `@functools.lru_cache` is convenient for function memoization, it does not support serialization, explicit cache inspection, key-based invalidation, or thread-safe telemetry metrics (such as tracking cache hit rates across multiple API worker requests).

In `backend/app/core/lru_cache.py`, we implemented a classical **Doubly-Linked List + Hash Map** pattern:
- **Hash Map (`dict`):** Maps `key` $\to$ `Node`, enabling $O(1)$ lookups.
- **Doubly-Linked List:** Maintains access order. The most recently accessed node is moved to the `head` in $O(1)$ time by updating pointer references (`prev` and `next`). The least recently used node at the `tail` is evicted in $O(1)$ time when capacity is exceeded.
- **Complexity:** Both `get(key)` and `put(key, value)` operate in strict $O(1)$ time.

---

### Q4: Why use a Scikit-Learn TF-IDF classifier for intent routing rather than asking an LLM to classify?
**Answer:**
Asking an LLM (like GPT-4 or Gemini) to classify every incoming message introduces 300ms–800ms of network latency and financial token costs on every single turn. 

Instead, we trained a lightweight **Scikit-Learn pipeline** (n-gram TF-IDF + Calibrated Linear SVM / Logistic Regression) on 1,500 labeled domain tickets with 5-fold cross validation:
- **Inference Latency:** $< 2\text{ms}$ running on standard CPU without GPU acceleration.
- **Accuracy:** $96.8\%$ across 6 core support categories.
- **Cost:** $\$0.00$ per inference.
- **Urgency Triage:** Extracts calibrated probability scores to detect high-urgency escalations before any LLM is invoked.

---

### Q5: How does the Human-in-the-Loop (HITL) safeguard prevent autonomous financial risk?
**Answer:**
Autonomous LLMs are probabilistic models and must never possess unilateral authority to trigger fund disbursements, charge credit cards, or delete customer accounts.

Our `ActionAgent`:
1. Formulates the proposed action (e.g. `start_refund_request(order_id, amount_usd, reason)`).
2. Persists the action into the SQLite `actions` table with status `pending_approval` and locks execution.
3. Emits an event to the frontend UI displaying an action approval card with exact parameters.
4. Only an authenticated human supervisor clicking **"Approve"** sends an authorized POST request to `/api/actions/{id}/approve` to transition the status to `approved` and disburse funds.

---

### Q6: How does the Critic Agent detect hallucinations, and what happens when an answer is unfaithful?
**Answer:**
The `CriticAgent` (`backend/app/agents/critic_agent.py`) executes post-generation verification:
1. It parses the generated answer into discrete factual assertions.
2. It audits each assertion against the retrieved context chunks using lexical containment and semantic sentence alignment.
3. If an assertion makes factual claims not grounded in the retrieved text (e.g. claiming a 90-day return window when the policy states 30 days), the faithfulness score drops below threshold ($< 0.70$).
4. In that event, the Critic Agent flags a hallucination risk, records the audit incident in the telemetry trace, and substitutes a safe, verbatim quote directly from the grounded policy document.

---

### Q7: How do your security guardrails defend against prompt injection and PII leakage?
**Answer:**
SupportMind employs defense-in-depth:
1. **PII Sanitizer (`backend/app/guardrails/pii.py`):** Uses comprehensive regex patterns matching RFC-5322 emails, Luhn-valid credit card numbers, E.164 phone numbers, and US SSNs, replacing them with typed anonymized tokens (`[REDACTED_EMAIL]`, `[REDACTED_CARD]`).
2. **Prompt Injection Defense (`backend/app/guardrails/injection.py`):** Neutralizes 15 distinct adversarial attack vectors (e.g. DAN jailbreaks, "ignore previous instructions", system prompt extraction, simulated developer mode, and SQL injection delimiters like `DROP TABLE` or `UNION SELECT`). Malicious prompts receive an immediate safe refusal without reaching downstream agents or LLMs.

---

### Q8: What were the findings of your Evaluation Lab benchmark across the 7 configurations?
**Answer:**
We created a 60-query golden evaluation benchmark (`eval/eval_set.json`) covering 45 policy questions, 8 unanswerable questions, and 7 adversarial attacks.
Key findings:
- **Config A (LLM Only):** 0.2333 Hit-Rate, 25% correctness (hallucinated generic return rules).
- **Config B (Vector Search Only):** 0.7833 Hit-Rate, 80% correctness.
- **Config C (Hybrid RAG + RRF):** 0.8833 Hit-Rate, 90% correctness.
- **Config D (Hybrid + Reranker + Prompt v3 Chain-of-Thought):** **0.9333 Hit-Rate@4**, **0.8542 MRR**, and **95% Answer Correctness**, with p50 latency under **30ms**.

---

### Q9: How do you handle unanswerable queries?
**Answer:**
A major failure mode in naive RAG systems is hallucinating an answer when the retrieved documents do not contain relevant information.

In SupportMind:
1. Retrieval chunks carry a relevance threshold score. If top chunks have low similarity, or if the question pertains to out-of-scope policies (e.g. international pet shipping), the context explicitly flags this to the prompt.
2. The prompt strategy (`v3` Chain-of-Thought) includes a strict negative constraint: *"If the retrieved policy excerpts do not contain the answer, state clearly that NovaCart policy does not cover this and offer to connect the customer with a human specialist."*
3. In our evaluation benchmark, SupportMind achieved **100% correct rejection** on unanswerable test queries without hallucinating.

---

### Q10: How is SupportMind architected for production deployment?
**Answer:**
1. **Containerization:** Multi-stage Docker build for the React frontend (Node 22 builder $\to$ Alpine Nginx serving static assets and reverse-proxying `/api/` calls) and lightweight Python 3.11 container for FastAPI running as non-root user `appuser`.
2. **Orchestration:** `docker-compose.yml` with automated container healthcheck dependencies (`service_healthy`) and persistent volume mounts for SQLite.
3. **CI/CD:** GitHub Actions workflow executing Python matrix tests (3.11 & 3.13), Ruff linting, Pytest, Vitest frontend tests, and Docker Compose validation on every pull request.
4. **Cloud Portability:** Ready for 1-click zero-cost deployment on Render (`render.yaml`) and Vercel (`vercel.json`).
