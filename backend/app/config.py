"""SupportMind Application Configuration.

Loads environment variables with Pydantic Settings and validates defaults.
"""


import json
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings schema backed by environment variables."""

    # Project metadata
    PROJECT_NAME: str = "SupportMind"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] | str = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string, JSON array, or list."""
        if isinstance(v, str):
            v_trimmed = v.strip()
            if v_trimmed.startswith("[") and v_trimmed.endswith("]"):
                try:
                    parsed = json.loads(v_trimmed)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed if str(x).strip()]
                except Exception:
                    pass
            # Split comma separated or single origin (e.g. '*' or 'http://localhost:5173,http://localhost:3000')
            return [x.strip() for x in v.split(",") if x.strip()]
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        return ["*"]


    # LLM Settings
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.5-flash"

    PROMPT_VERSION: str = "v3"
    DEMO_MODE: bool = False

    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    TOP_K: int = 4
    USE_RERANKER: bool = False
    VECTOR_STORE_BACKEND: str = "faiss"  # 'faiss' or 'numpy'

    # Guardrails
    ENABLE_PII_MASKING: bool = True
    ENABLE_INJECTION_DEFENSE: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global settings singleton
settings = Settings()
