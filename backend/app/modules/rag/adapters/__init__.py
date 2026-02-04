# RAG Adapters - Vector Store Implementations
"""
Adaptadores para diferentes vector stores.

PARA IMPLEMENTAR:
Los compañeros deben crear uno de estos archivos según el vector store elegido:
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
    REQUIRED_INDICES,
)

__all__ = [
    "VectorStoreAdapter",
    "ChunkMetadata",
    "RetrievedChunk",
    "IndexConfig",
    "REQUIRED_INDICES",
]


def get_adapter(adapter_type: str = "none") -> VectorStoreAdapter:
    """
    Factory para obtener el adapter configurado.

    Args:
        adapter_type: Tipo de adapter ("pgvector", "pinecone", "qdrant", "none")

    Returns:
        Instancia del adapter

    Raises:
        NotImplementedError: Si el adapter no está implementado
    """
    if adapter_type == "none":
        raise NotImplementedError(
            "No hay vector store configurado. "
            "Implementa un adapter en app/modules/rag/adapters/"
        )

    if adapter_type == "pgvector":
        # from .pgvector_adapter import PgVectorAdapter
        # return PgVectorAdapter()
        raise NotImplementedError("PgVectorAdapter no implementado aún")

    if adapter_type == "pinecone":
        # from .pinecone_adapter import PineconeAdapter
        # return PineconeAdapter()
        raise NotImplementedError("PineconeAdapter no implementado aún")

    if adapter_type == "qdrant":
        # from .qdrant_adapter import QdrantAdapter
        # return QdrantAdapter()
        raise NotImplementedError("QdrantAdapter no implementado aún")

    raise ValueError(f"Adapter type '{adapter_type}' no reconocido")
