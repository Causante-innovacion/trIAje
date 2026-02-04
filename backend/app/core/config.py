"""
Configuration settings using Pydantic Settings
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Project
    PROJECT_NAME: str = "GPT Legal"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])

    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./gpt_legal.db")

    # Vector Store (abstracto - configurar según implementación)
    VECTOR_STORE_TYPE: str = Field(default="none")  # none, pgvector, pinecone, qdrant
    VECTOR_STORE_URL: str | None = None
    VECTOR_STORE_API_KEY: str | None = None

    # AI Providers
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # AI Models (configurables)
    MODEL_INTAKE: str = "gpt-4o-mini"      # Tareas simples, clasificación
    MODEL_REASONING: str = "gpt-4o"         # Análisis legal
    MODEL_CREATIVITY: str = "claude-sonnet-4-20250514"  # Redacción

    # RAG Parameters (según spec)
    RAG_TOP_K_INITIAL: int = 20
    RAG_TOP_K_RERANK: int = 8
    RAG_MAX_CHUNK_TOKENS: int = 600
    RAG_CHUNK_OVERLAP: int = 120
    RAG_STRICTNESS: int = 3
    RAG_CONFIDENCE_THRESHOLD: float = 0.65

    # Scoring weights (según spec)
    SCORE_SEMANTIC_SIMILARITY: float = 0.35
    SCORE_AUTHORITY_WEIGHT: float = 0.25
    SCORE_RECENCY_WEIGHT: float = 0.15
    SCORE_JURISDICTION_MATCH: float = 0.15
    SCORE_LEGAL_TERM_DENSITY: float = 0.10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
