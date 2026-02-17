# RAG Adapters - Vector Store Implementations
"""
Adaptadores para diferentes vector stores.

Implementados:
- qdrant.py (Qdrant) - Multi-tenant con collections compartidas y privadas + Dashboard GUI
- chroma.py (ChromaDB) - Legacy (disponible como respaldo)

Cada adapter debe implementar la interfaz VectorStoreAdapter de base.py
"""

from .base import (
    VectorStoreAdapter,
    ChunkMetadata,
    RetrievedChunk,
    IndexConfig,
    IndexType,
    REQUIRED_INDICES,
)
from .qdrant import QdrantAdapter, create_qdrant_adapter

__all__ = [
    "VectorStoreAdapter",
    "ChunkMetadata",
    "RetrievedChunk",
    "IndexConfig",
    "IndexType",
    "REQUIRED_INDICES",
    "QdrantAdapter",
    "create_qdrant_adapter",
]


def get_adapter(adapter_type: str = "qdrant", **kwargs) -> VectorStoreAdapter:
    """
    Factory para obtener el adapter configurado.

    Args:
        adapter_type: Tipo de adapter ("qdrant", "chroma", "pgvector")
        **kwargs: Argumentos adicionales para el adapter

    Returns:
        Instancia del adapter

    Raises:
        NotImplementedError: Si el adapter no está implementado
    """
    if adapter_type == "qdrant":
        return create_qdrant_adapter(**kwargs)

    if adapter_type == "chroma":
        from .chroma import create_chroma_adapter
        return create_chroma_adapter(**kwargs)

    if adapter_type == "pgvector":
        raise NotImplementedError("PgVectorAdapter no implementado aún")

    if adapter_type == "pinecone":
        raise NotImplementedError("PineconeAdapter no implementado aún")

    raise ValueError(f"Adapter type '{adapter_type}' no reconocido")
