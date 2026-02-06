# RAG Adapters - Vector Store Implementations
"""
Adaptadores para diferentes vector stores.

Implementados:
- chroma.py (ChromaDB) - Multi-tenant con collections compartidas y privadas

Para implementar:
- pgvector_adapter.py  (PostgreSQL + pgvector)
- pinecone_adapter.py  (Pinecone managed)
- qdrant_adapter.py    (Qdrant open source)
- weaviate_adapter.py  (Weaviate)

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
from .chroma import ChromaDBAdapter, create_chroma_adapter

__all__ = [
    "VectorStoreAdapter",
    "ChunkMetadata",
    "RetrievedChunk",
    "IndexConfig",
    "IndexType",
    "REQUIRED_INDICES",
    "ChromaDBAdapter",
    "create_chroma_adapter",
]


def get_adapter(adapter_type: str = "chroma", **kwargs) -> VectorStoreAdapter:
    """
    Factory para obtener el adapter configurado.

    Args:
        adapter_type: Tipo de adapter ("chroma", "pgvector", "pinecone", "qdrant")
        **kwargs: Argumentos adicionales para el adapter

    Returns:
        Instancia del adapter

    Raises:
        NotImplementedError: Si el adapter no está implementado
    """
    if adapter_type == "chroma":
        return create_chroma_adapter(**kwargs)

    if adapter_type == "pgvector":
        raise NotImplementedError("PgVectorAdapter no implementado aún")

    if adapter_type == "pinecone":
        raise NotImplementedError("PineconeAdapter no implementado aún")

    if adapter_type == "qdrant":
        raise NotImplementedError("QdrantAdapter no implementado aún")

    raise ValueError(f"Adapter type '{adapter_type}' no reconocido")
