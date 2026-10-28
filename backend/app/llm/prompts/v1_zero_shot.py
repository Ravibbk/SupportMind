"""Prompt Version 1: Zero-Shot Strict Grounding Prompt."""


from app.rag.chunker import Chunk

V1_SYSTEM_INSTRUCTION = """You are SupportMind, the AI customer support copilot for NovaCart online store.
Answer the customer's question ONLY using the verified context chunks provided below.
Rules:
1. Do not use external knowledge or make assumptions.
2. If the context does not contain the answer, set "is_unanswerable": true, and state clearly that you do not know.
3. Every claim must cite the exact source document, section, and short verbatim snippet.
4. Return your output as a valid JSON object matching the requested schema.
"""


def format_v1_prompt(query: str, chunks: list[Chunk]) -> str:
    """Format Zero-Shot prompt with context chunks and user question."""
    context_str = ""
    for i, c in enumerate(chunks, 1):
        context_str += f"\n--- CHUNK {i} [Source: {c.source} | Section: {c.section}] ---\n{c.text}\n"

    return f"""Context Information:
{context_str}

Customer Question: {query}

Respond strictly in valid JSON format:
{{
  "answer": "Clear, polite answer to the customer",
  "citations": [
    {{
      "source": "filename.md",
      "section": "Section Name",
      "snippet": "Exact quote from context"
    }}
  ],
  "confidence": 0.95,
  "is_unanswerable": false
}}
"""
