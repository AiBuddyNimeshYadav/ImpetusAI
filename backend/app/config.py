"""
Application configuration.

All settings are loaded from environment variables or .env file.
The LLM provider can be swapped from a SINGLE place here — just change
LLM_PROVIDER and LLM_MODEL to switch between Gemini, Ollama, Claude, or OpenAI.
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── App ──────────────────────────────────────────────────────────
    APP_NAME: str = "ImpetusAI Workplace Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ── Database ─────────────────────────────────────────────────────
    # Use absolute path for SQLite to prevent 'no such table' errors based on CWD
    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'impetusai.db'))}"

    # ── Auth ─────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-use-a-random-64-char-hex"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    # ── LLM Configuration (SINGLE SWAP POINT) ───────────────────────
    # Supported providers: "gemini", "ollama", "claude", "openai"
    # Change LLM_PROVIDER + LLM_MODEL to switch the entire system's LLM.
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini/gemini-2.0-flash"

    # API keys (set the one matching your LLM_PROVIDER)
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Ollama settings (used when LLM_PROVIDER = "ollama")
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # ── LLM Fallback (optional) ──────────────────────────────────────
    LLM_FALLBACK_PROVIDER: str = ""  # e.g. "claude"
    LLM_FALLBACK_MODEL: str = ""     # e.g. "claude-3-5-sonnet-20241022"

    # ── Embeddings ───────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── ChromaDB (Vector Store) ──────────────────────────────────────
    CHROMA_PERSIST_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "chroma_data"))

    # ── RAG Settings ─────────────────────────────────────────────────
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.3

    # ── Document Upload ────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # ── Admin Bootstrap ──────────────────────────────────────────────
    # Created automatically on first startup if no admin user exists
    ADMIN_EMAIL: str = "admin@impetus.com"
    ADMIN_PASSWORD: str = "ChangeMe123!"

    model_config = {
        "env_file": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env")),
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
