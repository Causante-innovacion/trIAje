# RAG Module
"""
Motor RAG con grounding obligatorio + enforcement de evidencia.

Pipeline:
User Input → Query Normalization → Legal Intent Expansion
→ Retrieval Query Builder → Multi-index Search → Chunk Scoring
→ Normative Filtering → Contradiction Check → Grounded Context Pack
→ Reasoning Module → Citation Binding

Índices RAG (multi-index):
- index_normative_primary
- index_regulatory_secondary
- index_guidance_docs
- index_authority_FAQ
- index_case_interpretation (optional)
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
from .adapters.chroma import ChromaDBAdapter, create_chroma_adapter

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
    "ChromaDBAdapter",
    "create_chroma_adapter",
]
