"""Knowledge Agent: Executes hybrid RAG search across NovaCart policy documents."""

from pathlib import Path

from app.rag.pipeline import RAGPipeline, RAGResponse

BASE_DIR = Path(__file__).resolve().parent.parent.parent
POLICIES_DIR = BASE_DIR / "data" / "policies"


class KnowledgeAgent:
    """Agent answering customer policy questions using the hybrid RAG subsystem."""

    def __init__(self, pipeline: RAGPipeline | None = None):
        self.pipeline = pipeline or RAGPipeline()
        self._ensure_indexed()

    def _ensure_indexed(self) -> None:
        """Index policy documents on startup if the vector store is empty."""
        if not self.pipeline.indexed_chunks and POLICIES_DIR.exists():
            try:
                self.pipeline.index_documents_from_directory(POLICIES_DIR)
            except Exception:
                pass

    def handle_query(
        self,
        query: str,
        prompt_version: str = "v3",
        top_k: int = 4
    ) -> RAGResponse:
        """Run grounded policy search and return answer with citations."""
        return self.pipeline.answer_query(
            query=query,
            prompt_version=prompt_version,
            top_k=top_k
        )
