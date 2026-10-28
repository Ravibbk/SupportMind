"""Document chunking strategies: Fixed-Size with Overlap and Heading-Aware Semantic Chunking."""

import re
from dataclasses import dataclass, field
from typing import Any

from app.rag.loader import Document


@dataclass
class Chunk:
    """Represents a discrete text chunk indexed for RAG retrieval."""

    chunk_id: str
    text: str
    source: str
    section: str
    chunk_index: int
    metadata: dict[str, Any] = field(default_factory=dict)


def chunk_fixed_size(
    document: Document,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> list[Chunk]:
    """Strategy 1: Sliding-window chunking with configurable character size and overlap.

    Args:
        document: The ingested document to chunk.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between adjacent chunks.

    Returns:
        List of Chunks.
    """
    text = document.text
    if not text.strip():
        return []

    chunks: list[Chunk] = []
    start = 0
    text_len = len(text)
    chunk_idx = 0

    step = max(1, chunk_size - chunk_overlap)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunk_id = f"{document.source}_fixed_{chunk_idx}"
            chunks.append(Chunk(
                chunk_id=chunk_id,
                text=chunk_text,
                source=document.source,
                section="General",
                chunk_index=chunk_idx,
                metadata={
                    "strategy": "fixed_size",
                    "start_char": start,
                    "end_char": end,
                    **document.metadata
                }
            ))
            chunk_idx += 1

        if end == text_len:
            break
        start += step

    return chunks


def chunk_heading_aware(
    document: Document,
    max_chunk_size: int = 600,
    chunk_overlap: int = 50
) -> list[Chunk]:
    """Strategy 2: Semantic heading-aware chunking for Markdown documents.

    Splits document along Markdown headings (#, ##, ###), preserves the hierarchical
    section name, and subdivides oversized sections with sliding overlap.

    Args:
        document: The Markdown document to chunk.
        max_chunk_size: Upper limit before subdividing a large section.
        chunk_overlap: Overlap when subdividing long sections.

    Returns:
        List of Chunks with precise section metadata.
    """
    text = document.text
    if not text.strip():
        return []

    # Regex to capture Markdown headers: # Header, ## Header, ### Header
    header_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    matches = list(header_pattern.finditer(text))

    # If document has no headers, fallback to fixed-size chunking
    if not matches:
        return chunk_fixed_size(document, chunk_size=max_chunk_size, chunk_overlap=chunk_overlap)

    sections: list[dict[str, Any]] = []

    # Handle preamble before the first heading (if any)
    if matches[0].start() > 0:
        preamble = text[:matches[0].start()].strip()
        if preamble:
            sections.append({"section": "Overview", "text": preamble})

    # Extract text belonging to each heading
    for i, match in enumerate(matches):
        section_title = match.group(2).strip()
        content_start = match.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_body = text[content_start:content_end].strip()

        if section_body:
            sections.append({
                "section": section_title,
                "text": f"{section_title}\n\n{section_body}"
            })

    chunks: list[Chunk] = []
    chunk_idx = 0

    for sec in sections:
        sec_title = sec["section"]
        sec_text = sec["text"]

        if len(sec_text) <= max_chunk_size:
            chunk_id = f"{document.source}_sec_{chunk_idx}"
            chunks.append(Chunk(
                chunk_id=chunk_id,
                text=sec_text,
                source=document.source,
                section=sec_title,
                chunk_index=chunk_idx,
                metadata={"strategy": "heading_aware", **document.metadata}
            ))
            chunk_idx += 1
        else:
            # Subdivide large section with overlap
            sub_start = 0
            sub_step = max(1, max_chunk_size - chunk_overlap)
            while sub_start < len(sec_text):
                sub_end = min(sub_start + max_chunk_size, len(sec_text))
                sub_text = sec_text[sub_start:sub_end].strip()
                if sub_text:
                    chunk_id = f"{document.source}_sec_{chunk_idx}"
                    chunks.append(Chunk(
                        chunk_id=chunk_id,
                        text=sub_text,
                        source=document.source,
                        section=sec_title,
                        chunk_index=chunk_idx,
                        metadata={"strategy": "heading_aware_split", **document.metadata}
                    ))
                    chunk_idx += 1
                if sub_end == len(sec_text):
                    break
                sub_start += sub_step

    return chunks
