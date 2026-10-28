"""SupportMind Application Configuration.

Loads environment variables with Pydantic Settings and validates defaults.
"""


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
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

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
