"""Document loaders supporting Markdown, Plain Text, and PDF formats."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pypdf


@dataclass
class Document:
    """Represents an ingested source document with metadata."""

    text: str
    source: str
    file_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


def load_file(file_path: Path) -> Document:
    """Load and parse an individual document based on its extension.

    Supports: .md, .txt, .pdf
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Source file not found at: {path}")

    suffix = path.suffix.lower()

    if suffix in (".md", ".txt"):
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        return Document(
            text=text,
            source=path.name,
            file_type=suffix.lstrip("."),
            metadata={"path": str(path), "size_bytes": path.stat().st_size}
        )

    elif suffix == ".pdf":
        reader = pypdf.PdfReader(str(path))
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            content = page.extract_text() or ""
            extracted_pages.append(content)
        full_text = "\n\n".join(extracted_pages)
        return Document(
            text=full_text,
            source=path.name,
            file_type="pdf",
            metadata={"path": str(path), "page_count": len(reader.pages)}
        )

    else:
        raise ValueError(f"Unsupported document format: {suffix}. Supported: .md, .txt, .pdf")


def load_directory(directory_path: Path) -> list[Document]:
    """Recursively load all supported documents (.md, .txt, .pdf) from a directory."""
    dir_path = Path(directory_path)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    docs: list[Document] = []
    for file_path in dir_path.glob("**/*"):
        if file_path.is_file() and file_path.suffix.lower() in (".md", ".txt", ".pdf"):
            docs.append(load_file(file_path))

    return docs
