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

    # Vector Store - ChromaDB
    VECTOR_STORE_TYPE: str = Field(default="chroma")  # chroma, pgvector, pinecone
    CHROMA_MODE: str = Field(default="local")  # local, server, memory
    CHROMA_PERSIST_DIR: str = Field(default="./chroma_data")
    CHROMA_HOST: str = Field(default="localhost")
    CHROMA_PORT: int = Field(default=8000)

    # AI Providers
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    MAPLE_API_KEY: str | None = None
    MAPLE_API_URL: str = Field(default="https://api.maple.ai/v1")

    # AI Provider preference (openai, maple, anthropic)
    AI_PROVIDER_PRIMARY: str = Field(default="openai")
    AI_PROVIDER_FALLBACK: str = Field(default="openai")

    # AI Models (configurables)
    MODEL_INTAKE: str = "gpt-4o-mini"      # Tareas simples, clasificación
    MODEL_REASONING: str = "gpt-4o"         # Análisis legal
    MODEL_CREATIVITY: str = "claude-sonnet-4-20250514"  # Redacción

    # Embeddings
    EMBEDDING_PROVIDER: str = Field(default="openai")  # openai, local
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")

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
