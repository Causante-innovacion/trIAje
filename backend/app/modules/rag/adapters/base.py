"""
RAG Adapters - Base Interface
Interfaz abstracta que deben implementar todos los vector store adapters.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class IndexType(str, Enum):
    """Tipos de índice según spec"""
    NORMATIVE_PRIMARY = "normative_primary"
    REGULATORY_SECONDARY = "regulatory_secondary"
    GUIDANCE_DOCS = "guidance_docs"
    AUTHORITY_FAQ = "authority_faq"
    CASE_INTERPRETATION = "case_interpretation"


# Índices requeridos según spec
REQUIRED_INDICES = [
    IndexType.NORMATIVE_PRIMARY,
    IndexType.REGULATORY_SECONDARY,
    IndexType.GUIDANCE_DOCS,
    IndexType.AUTHORITY_FAQ,
]


class ChunkMetadata(BaseModel):
    """
    Metadata obligatoria para cada chunk.
    Cada chunk indexado DEBE tener estos campos.
    """
    doc_id: str
    title: str
    source_type: IndexType
    authority_level: float = Field(ge=0.0, le=1.0)
    jurisdiction: str
    validity_date: str | None = None
    url: str | None = None
    anchor: str | None = None  # Artículo específico, e.g., "Art. 15"
    normative_weight: float = Field(default=1.0, ge=0.0, le=1.0)

    # Metadata adicional flexible
    extra: Dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """Chunk recuperado del vector store"""
    chunk_id: str
    content: str
    metadata: ChunkMetadata
    similarity_score: float = Field(ge=0.0, le=1.0)


class IndexConfig(BaseModel):
    """Configuración para un índice"""
    name: str
    index_type: IndexType
    dimension: int = 1536  # OpenAI ada-002 default
    metric: str = "cosine"  # cosine, euclidean, dot_product


class VectorStoreAdapter(ABC):
    """
    Interfaz abstracta para vector stores.

    IMPLEMENTAR con: pgvector, Pinecone, Qdrant, Weaviate, etc.

    Ejemplo de uso:
    ```python
    class PgVectorAdapter(VectorStoreAdapter):
        async def index_document(self, ...):
            # Implementación con pgvector
            pass
    ```
    """

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Inicializa la conexión y crea índices si no existen.

        Returns:
            True si la inicialización fue exitosa
        """
        pass

    @abstractmethod
    async def create_index(self, config: IndexConfig) -> bool:
        """
        Crea un nuevo índice/collection.

        Args:
            config: Configuración del índice

        Returns:
            True si se creó exitosamente
        """
        pass

    @abstractmethod
    async def index_document(
        self,
        doc_id: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: ChunkMetadata,
        index_name: str
    ) -> List[str]:
        """
        Indexa un documento (sus chunks) en el store.

        Args:
            doc_id: ID único del documento
            chunks: Lista de textos (chunks del documento)
            embeddings: Lista de embeddings correspondientes
            metadata: Metadata base (se replica para cada chunk)
            index_name: Nombre del índice donde guardar

        Returns:
            Lista de chunk_ids generados
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        index_names: List[str],
        top_k: int = 20,
        filters: Dict[str, Any] | None = None
    ) -> List[RetrievedChunk]:
        """
        Búsqueda por embedding con filtros.

        Args:
            query_embedding: Vector de la query
            index_names: Índices donde buscar (multi-index)
            top_k: Número de resultados
            filters: Filtros adicionales (jurisdiction, authority, etc.)

        Returns:
            Lista de chunks ordenados por similaridad
        """
        pass

    @abstractmethod
    async def delete_document(self, doc_id: str) -> bool:
        """
        Elimina todos los chunks de un documento.

        Args:
            doc_id: ID del documento a eliminar

        Returns:
            True si se eliminó exitosamente
        """
        pass

    @abstractmethod
    async def get_document_chunks(self, doc_id: str) -> List[RetrievedChunk]:
        """
        Obtiene todos los chunks de un documento.

        Args:
            doc_id: ID del documento

        Returns:
            Lista de chunks del documento
        """
        pass

    @abstractmethod
    async def list_indices(self) -> List[str]:
        """
        Lista los índices disponibles.

        Returns:
            Lista de nombres de índices
        """
        pass

    @abstractmethod
    async def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """
        Obtiene estadísticas de un índice.

        Returns:
            Dict con: total_chunks, total_documents, etc.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verifica que el vector store esté funcionando.

        Returns:
            True si está healthy
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Cierra conexiones y libera recursos.
        """
        pass
