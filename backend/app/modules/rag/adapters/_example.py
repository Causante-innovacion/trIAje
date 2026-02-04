"""
RAG Adapters - Example In-Memory Implementation

⚠️  EJEMPLO SOLO PARA DESARROLLO Y TESTING
    NO USAR EN PRODUCCIÓN

Este adapter sirve como:
1. Referencia de implementación
2. Testing sin dependencias externas
3. Desarrollo local rápido

Para producción, implementar uno de:
- pgvector_adapter.py
- pinecone_adapter.py
- qdrant_adapter.py
"""

from typing import List, Dict, Any
from uuid import uuid4
import math

from .base import (
    VectorStoreAdapter,
    ChunkMetadata,
    RetrievedChunk,
    IndexConfig,
)


class InMemoryVectorAdapter(VectorStoreAdapter):
    """
    Adapter en memoria para desarrollo y testing.
    NO PERSISTENTE - los datos se pierden al reiniciar.
    """

    def __init__(self):
        # Estructura: {index_name: {chunk_id: (content, embedding, metadata)}}
        self._indices: Dict[str, Dict[str, tuple]] = {}
        self._initialized = False

    async def initialize(self) -> bool:
        """Inicializa el store en memoria"""
        self._initialized = True
        return True

    async def create_index(self, config: IndexConfig) -> bool:
        """Crea un nuevo índice"""
        if config.name not in self._indices:
            self._indices[config.name] = {}
        return True

    async def index_document(
        self,
        doc_id: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: ChunkMetadata,
        index_name: str
    ) -> List[str]:
        """Indexa chunks de un documento"""
        if index_name not in self._indices:
            self._indices[index_name] = {}

        chunk_ids = []
        for i, (content, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{doc_id}_chunk_{i}_{uuid4().hex[:8]}"

            # Crear metadata específica del chunk
            chunk_metadata = metadata.model_copy()

            self._indices[index_name][chunk_id] = (
                content,
                embedding,
                chunk_metadata,
            )
            chunk_ids.append(chunk_id)

        return chunk_ids

    async def search(
        self,
        query_embedding: List[float],
        index_names: List[str],
        top_k: int = 20,
        filters: Dict[str, Any] | None = None
    ) -> List[RetrievedChunk]:
        """Búsqueda por similaridad coseno"""
        results = []

        for index_name in index_names:
            if index_name not in self._indices:
                continue

            for chunk_id, (content, embedding, metadata) in self._indices[index_name].items():
                # Aplicar filtros
                if filters:
                    if not self._matches_filters(metadata, filters):
                        continue

                # Calcular similaridad coseno
                similarity = self._cosine_similarity(query_embedding, embedding)

                results.append(RetrievedChunk(
                    chunk_id=chunk_id,
                    content=content,
                    metadata=metadata,
                    similarity_score=similarity,
                ))

        # Ordenar por similaridad y limitar
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

    async def delete_document(self, doc_id: str) -> bool:
        """Elimina chunks de un documento"""
        deleted = False
        for index_name in self._indices:
            to_delete = [
                cid for cid in self._indices[index_name]
                if cid.startswith(doc_id)
            ]
            for cid in to_delete:
                del self._indices[index_name][cid]
                deleted = True
        return deleted

    async def get_document_chunks(self, doc_id: str) -> List[RetrievedChunk]:
        """Obtiene chunks de un documento"""
        chunks = []
        for index_name in self._indices:
            for chunk_id, (content, _, metadata) in self._indices[index_name].items():
                if metadata.doc_id == doc_id:
                    chunks.append(RetrievedChunk(
                        chunk_id=chunk_id,
                        content=content,
                        metadata=metadata,
                        similarity_score=1.0,
                    ))
        return chunks

    async def list_indices(self) -> List[str]:
        """Lista índices"""
        return list(self._indices.keys())

    async def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Estadísticas de un índice"""
        if index_name not in self._indices:
            return {"error": "Index not found"}

        chunks = self._indices[index_name]
        doc_ids = set()
        for _, (_, _, metadata) in chunks.items():
            doc_ids.add(metadata.doc_id)

        return {
            "total_chunks": len(chunks),
            "total_documents": len(doc_ids),
            "index_name": index_name,
        }

    async def health_check(self) -> bool:
        """Health check"""
        return self._initialized

    async def close(self) -> None:
        """Limpia recursos"""
        self._indices.clear()
        self._initialized = False

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calcula similaridad coseno entre dos vectores"""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _matches_filters(
        self,
        metadata: ChunkMetadata,
        filters: Dict[str, Any]
    ) -> bool:
        """Verifica si metadata cumple los filtros"""
        for key, value in filters.items():
            if hasattr(metadata, key):
                attr_value = getattr(metadata, key)
                if isinstance(value, list):
                    if attr_value not in value:
                        return False
                elif attr_value != value:
                    return False
        return True
