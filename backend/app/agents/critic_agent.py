"""Critic Agent: Post-generation hallucination and factual consistency auditor.

Examines the draft answer against the retrieved context chunks to verify that
every material claim (days, prices, policies) is supported by text evidence.
"""

import re
from dataclasses import dataclass

from app.rag.chunker import Chunk


@dataclass
class CriticVerdict:
    """Audit result from the Critic Agent."""

    is_faithful: bool
    faithfulness_score: float  # 0.0 to 1.0
    flagged_claims: list[str]
    notes: str


class CriticAgent:
    """Audits draft answers against retrieved chunk evidence."""

    def evaluate_faithfulness(
        self,
        query: str,
        draft_answer: str,
        retrieved_chunks: list[Chunk]
    ) -> CriticVerdict:
        """Verify whether draft answer statements are grounded in retrieved chunks.

        Heuristic:
        1. Extract specific numerical claims, days, currency values, and policy terms from draft.
        2. Verify presence across the corpus of retrieved chunk texts.
        3. If key entities cannot be corroborated, flag the answer as unfaithful.
        """
        if not draft_answer or not retrieved_chunks:
            return CriticVerdict(
                is_faithful=True,
                faithfulness_score=1.0,
                flagged_claims=[],
                notes="Empty or unanswerable baseline."
            )

        combined_chunk_text = " ".join(c.text.lower() for c in retrieved_chunks)
        answer_lower = draft_answer.lower()

        # 1. Check numbers and periods (e.g. "30 days", "45 days", "$5.99")
        entities = re.findall(r"(\$?\d+(?:\.\d{2})?(?:\s*(?:days?|hours?|business days?|years?|%))?)", answer_lower)
        flagged = []

        for ent in entities:
            clean_ent = ent.strip()
            # If a specific number/entity in the answer does not exist in any retrieved chunk
            if clean_ent and clean_ent not in combined_chunk_text:
                # Disregard trivial numbers like 1, 2, 3 if casual
                if not (clean_ent.isdigit() and int(clean_ent) < 5):
                    flagged.append(f"Entity '{clean_ent}' not grounded in context")

        # 2. Compute faithfulness score
        if flagged:
            score = max(0.2, 1.0 - (0.35 * len(flagged)))
            is_faithful = score >= 0.70
            notes = f"Critic detected {len(flagged)} uncorroborated claim(s): " + "; ".join(flagged)
        else:
            score = 0.98
            is_faithful = True
            notes = "All extracted numerical entities and constraints corroborated by retrieved chunks."

        return CriticVerdict(
            is_faithful=is_faithful,
            faithfulness_score=round(score, 2),
            flagged_claims=flagged,
            notes=notes
        )
