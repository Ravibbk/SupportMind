"""Prompt Version 3: Chain-of-Thought (CoT) Prompt with Reasoning & Structured Output."""


from app.rag.chunker import Chunk

V3_SYSTEM_INSTRUCTION = """You are SupportMind, NovaCart's premier AI customer support copilot.
You rigorously examine company policies to formulate grounded, accurate customer answers.
Step-by-step reasoning procedure:
1. Examine the user's question and identify the core topic and policy entity.
2. Cross-reference the retrieved context chunks to check whether factual evidence exists.
3. Formulate a short reasoning step in the "thought" field before answering.
4. Extract the exact verbatim text snippet and document name for citations.
5. If the context does not contain direct answers, declare "is_unanswerable": true.
"""


def format_v3_prompt(query: str, chunks: list[Chunk]) -> str:
    """Format Chain-of-Thought prompt demanding a reasoning trace and strict citations."""
    context_str = ""
    for i, c in enumerate(chunks, 1):
        context_str += f"\n--- CHUNK {i} [Source: {c.source} | Section: {c.section}] ---\n{c.text}\n"

    return f"""Context Information:
{context_str}

Customer Question: {query}

Instructions:
First analyze the chunks in a "thought" field, then construct your concise answer and exact citations.

Respond strictly in valid JSON format:
{{
  "thought": "1-2 sentences of reasoning analyzing whether the chunks answer the question",
  "answer": "Polite, helpful, and concise answer directly addressing the customer",
  "citations": [
    {{
      "source": "filename.md",
      "section": "Exact section heading",
      "snippet": "Verbatim quote copied directly from the chunk text"
    }}
  ],
  "confidence": 0.95,
  "is_unanswerable": false
}}
"""
