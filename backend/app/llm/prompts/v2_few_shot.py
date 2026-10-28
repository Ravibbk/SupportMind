"""Prompt Version 2: Few-Shot In-Context Learning Prompt with Citations & Refusals."""


from app.rag.chunker import Chunk

V2_SYSTEM_INSTRUCTION = """You are SupportMind, NovaCart's AI support copilot.
Answer the customer's question strictly using the provided context chunks.
Study the few-shot examples below to understand how to cite exact snippets and when to refuse unanswerable questions.
"""

FEW_SHOT_EXAMPLES = """
### Example 1 (Successful grounded answer):
Context:
--- CHUNK 1 [Source: returns_refunds.md | Section: 1. 30-Day Standard Return Window] ---
We offer a 30-day return window for most items from the date of confirmed delivery. Items must be returned in their original condition, unwashed, unworn, with all original tags attached.

Question: What is the return window for clothing?
Output:
{
  "answer": "You can return most items within 30 days of confirmed delivery, provided they are unwashed, unworn, and have all original tags attached.",
  "citations": [
    {
      "source": "returns_refunds.md",
      "section": "1. 30-Day Standard Return Window",
      "snippet": "We offer a 30-day return window for most items from the date of confirmed delivery. Items must be returned in their original condition, unwashed, unworn, with all original tags attached."
    }
  ],
  "confidence": 0.98,
  "is_unanswerable": false
}

### Example 2 (Unanswerable query refusal):
Context:
--- CHUNK 1 [Source: shipping_delivery.md | Section: 1. Shipping Speeds & Rates] ---
Standard Ground takes 3-5 business days. Expedited 2-Day takes 2 business days.
Question: Can I pay with Bitcoin or cryptocurrency?
Output:
{
  "answer": "I do not have information in our company policy documents regarding cryptocurrency payments. Please check our payment terms or contact our billing team.",
  "citations": [],
  "confidence": 0.15,
  "is_unanswerable": true
}
"""


def format_v2_prompt(query: str, chunks: list[Chunk]) -> str:
    """Format Few-Shot prompt with demonstration examples and active context."""
    context_str = ""
    for i, c in enumerate(chunks, 1):
        context_str += f"\n--- CHUNK {i} [Source: {c.source} | Section: {c.section}] ---\n{c.text}\n"

    return f"""{FEW_SHOT_EXAMPLES}

### Actual Task:
Context Information:
{context_str}

Customer Question: {query}

Output valid JSON:
"""
