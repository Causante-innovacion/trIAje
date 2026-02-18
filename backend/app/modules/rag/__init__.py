# RAG Module
"""
Motor RAG con grounding obligatorio + enforcement de evidencia.

Pipeline:
User Input → Query Normalization → Legal Intent Expansion
→ Retrieval Query Builder → Multi-index Search → Chunk Scoring
→ Normative Filtering → Contradiction Check → Grounded Context Pack
→ Reasoning Module → Citation Binding

Vector Store: Qdrant (dashboard: http://localhost:6333/dashboard)
"""

from .service import (
    RAGModule,
    initialize_rag,
    get_rag_module,
    shutdown_rag,
)
from .interfaces import (
    RAGConfig,
    RAGQuery,
    RAGResult,
    RetrievedChunk,
    ChunkMetadata,
    Evidence,
    IndexType,
)
from .confidence import RAGConfidenceCalculator
from .adapters.qdrant import QdrantAdapter, create_qdrant_adapter

__all__ = [
    # Service
    "RAGModule",
    "initialize_rag",
    "get_rag_module",
    "shutdown_rag",
    # Interfaces
    "RAGConfig",
    "RAGQuery",
    "RAGResult",
    "RetrievedChunk",
    "ChunkMetadata",
    "Evidence",
    "IndexType",
    # Confidence
    "RAGConfidenceCalculator",
    # Adapters
    "QdrantAdapter",
    "create_qdrant_adapter",
]
