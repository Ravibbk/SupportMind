import { useState } from 'react';
import {
  BookOpen,
  Layers,
  Database,
  Code,
  FileText,
  Copy,
  Check,
  Sparkles,
} from 'lucide-react';

export const ArchitectureGuide = () => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);


  const resumeBullets = [
    'Architected and deployed "SupportMind", a production-ready AI customer support copilot combining Hybrid RAG (BM25 + FAISS vector search + Reciprocal Rank Fusion) and parameterized SQL data lookup, improving answer correctness from 25% to 95%.',
    'Implemented custom Data Structures from scratch in Python including a Min-Heap Top-K ($O(N \\log K)$) fusion algorithm and an $O(1)$ LRU Cache using a Doubly-Linked List and Hash Map, eliminating external dependencies.',
    'Engineered multi-agent intent routing with dual security guardrails: automated PII redaction and regex defenses protecting against 15 distinct adversarial prompt injection techniques.',
    'Built an empirical RAG Evaluation Lab benchmarking 7 retrieval and prompting architectures across 60 golden test cases, measuring Hit-Rate@4, MRR, correctness, p50 latency (<30ms), and query cost.',
  ];

  const interviewQA = [
    {
      q: 'Why did you use Hybrid Search (BM25 + Vector) instead of dense vector search alone?',
      a: 'Dense vector embeddings excel at semantic similarity ("can I get my cash back" -> refund policy), but struggle with exact lexical matches like order IDs (ORD-10001), part numbers, and legal policy codes. BM25 guarantees exact keyword hits. Combining them via Reciprocal Rank Fusion (RRF) delivers the best of both: 0.9333 Hit-Rate@4 vs 0.7833 for dense vector alone.',
    },
    {
      q: 'Explain your custom Min-Heap Top-K algorithm and its time complexity.',
      a: 'Sorting an entire array of N scored documents takes O(N log N) time and O(N) memory. When retrieving Top-K items (e.g. K=4), we maintain a min-heap of size K. For each candidate document, if its score exceeds the heap root, we pop the minimum and insert the new item in O(log K) time. Overall time is O(N log K) and auxiliary memory is strictly O(K).',
    },
    {
      q: 'How does your Human-in-the-Loop (HITL) gate prevent autonomous LLM financial risk?',
      a: 'Autonomous agents should never disburse money or alter records without oversight. Our ActionAgent drafts refund proposals into an SQLite `actions` table with status `pending_approval`. The action is locked until a human supervisor explicitly verifies and clicks approve via the API or dashboard.',
    },
    {
      q: 'How does the Critic Agent detect hallucinations?',
      a: 'The CriticAgent runs as a post-generation validation layer. It extracts factual claims from the candidate answer and checks if each claim is directly supported by the retrieved document chunks. If an unsupported claim is found, it flags a hallucination risk and falls back to a conservative policy quote.',
    },
  ];

  const handleCopyBullet = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="max-w-6xl w-full mx-auto p-4 sm:p-6 space-y-8">
      {/* Header */}
      <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 shadow-xl backdrop-blur-md">
        <div className="flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-indigo-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">
            System Design & Interview Portfolio Guide
          </h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Detailed architectural breakdown, algorithmic data structures, and ready-to-use resume talking points for recruiter interviews.
        </p>
      </div>

      {/* End-to-End Pipeline Visualization */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          Multi-Agent System Architecture Flow
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span className="text-[10px] uppercase font-bold text-rose-400 tracking-wider">
              Stage 1: Guardrails
            </span>
            <div className="font-semibold text-slate-200">PII & Injection Shield</div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Regex patterns sanitize email, phone, SSN, and credit cards. 15 adversarial injection attack vectors neutralized.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider">
              Stage 2: Classifier
            </span>
            <div className="font-semibold text-slate-200">TF-IDF Intent Classifier</div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Pre-trained on 1,500 labeled domain tickets with n-gram TF-IDF and calibrated probability estimation (&lt;2ms CPU).
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider">
              Stage 3: Agent Routing
            </span>
            <div className="font-semibold text-slate-200">Specialized Workers</div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              • Knowledge: Hybrid RAG + Reranker<br />
              • Data: Safe parameterized SQL<br />
              • Action: HITL approval gate
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">
              Stage 4: Verification
            </span>
            <div className="font-semibold text-slate-200">Critic Agent Audit</div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Verifies candidate answers strictly against grounded document citations to eliminate hallucination.
            </p>
          </div>
        </div>
      </div>

      {/* DSA Spotlight */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center gap-2">
            <Code className="w-4 h-4 text-cyan-400" />
            <h4 className="text-sm font-bold text-slate-200">
              Min-Heap Top-K Retrieval DSA
            </h4>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Located in <code className="text-indigo-400">backend/app/core/heap_topk.py</code>. Implemented with Python's <code>heapq</code> to retain the top K scored document chunks in $O(N \log K)$ runtime and $O(K)$ space, outperforming naive $O(N \log N)$ full sorting.
          </p>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-emerald-400" />
            <h4 className="text-sm font-bold text-slate-200">
              O(1) LRU Cache DSA
            </h4>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Located in <code className="text-indigo-400">backend/app/core/lru_cache.py</code>. Built from scratch with a Doubly-Linked List (for $O(1)$ node eviction & insertion) and a Hash Map (for $O(1)$ lookup) to cache policy embeddings and frequent queries.
          </p>
        </div>
      </div>

      {/* Resume Bullet Points */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            Resume Ready Bullet Points (Click to copy)
          </h3>
          <span className="text-xs text-slate-500">Tailored for Senior AI / ML Roles</span>
        </div>

        <div className="space-y-3">
          {resumeBullets.map((bullet, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-start justify-between gap-3 text-xs text-slate-300 leading-relaxed hover:border-slate-700 transition"
            >
              <p>• {bullet}</p>
              <button
                onClick={() => handleCopyBullet(bullet, idx)}
                className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white shrink-0 border border-slate-800"
                title="Copy bullet"
              >
                {copiedIndex === idx ? (
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Interview Q&A */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          Technical Interview Q&A Deep Dive
        </h3>

        <div className="space-y-4">
          {interviewQA.map((item, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs"
            >
              <h5 className="font-bold text-indigo-300 flex items-center gap-1.5">
                <span>Q:</span> {item.q}
              </h5>
              <p className="text-slate-300 leading-relaxed pl-3 border-l-2 border-indigo-500/40">
                {item.a}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
