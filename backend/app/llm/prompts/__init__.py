"""Prompt library selector supporting versioned prompts v1, v2, and v3."""

from app.llm.prompts.v1_zero_shot import V1_SYSTEM_INSTRUCTION, format_v1_prompt
from app.llm.prompts.v2_few_shot import V2_SYSTEM_INSTRUCTION, format_v2_prompt
from app.llm.prompts.v3_chain_of_thought import V3_SYSTEM_INSTRUCTION, format_v3_prompt
from app.rag.chunker import Chunk


def get_prompt_and_system(
    version: str,
    query: str,
    chunks: list[Chunk]
) -> tuple[str, str]:
    """Retrieve system instruction and formatted prompt for a requested version.

    Args:
        version: 'v1', 'v2', or 'v3'. Defaults to 'v3'.
        query: Customer inquiry.
        chunks: Retrieved context chunks.

    Returns:
        Tuple of (formatted_prompt_string, system_instruction_string).
    """
    v = (version or "v3").lower().strip()
    if v == "v1":
        return format_v1_prompt(query, chunks), V1_SYSTEM_INSTRUCTION
    elif v == "v2":
        return format_v2_prompt(query, chunks), V2_SYSTEM_INSTRUCTION
    else:  # v3 default
        return format_v3_prompt(query, chunks), V3_SYSTEM_INSTRUCTION
