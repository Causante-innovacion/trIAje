"""
RAG Adapters - Qdrant Implementation
Implementación del VectorStoreAdapter para Qdrant con soporte multi-tenant.
"""

import uuid
from typing import Any, List, Dict

from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

from .base import (
    VectorStoreAdapter,
    IndexConfig,
    ChunkMetadata,
    RetrievedChunk,
    IndexType,
)


class QdrantAdapter(VectorStoreAdapter):
    """
    Adapter de Qdrant para GPT Legal.

    Arquitectura multi-tenant:
    - Collection 'leyes_peru': Corpus compartido de normativa legal
    - Collection 'org_{org_id}': Documentos privados de cada organización

    Dashboard: http://localhost:6333/dashboard

    Uso:
    ```python
    adapter = QdrantAdapter(host="localhost", port=6333)
    await adapter.initialize()

    # Buscar en normativa compartida + docs de la org
    results = await adapter.search_multi_tenant(
        query_embedding=[...],
        organization_id="org_123",
        top_k=10
    )
    ```
    """

    # Nombre de la collection compartida
    SHARED_COLLECTION = "legal_documents"

    # Dimensión por defecto de los embeddings
    DEFAULT_DIMENSION = 768  # paraphrase-multilingual-mpnet-base-v2

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        api_key: str | None = None,
        url: str | None = None,
        dimension: int = DEFAULT_DIMENSION,
    ):
        """
        Inicializa el adapter.

        Args:
            host: Host del servidor Qdrant
            port: Puerto del servidor Qdrant (REST API)
            api_key: API key para autenticación (opcional)
            url: URL completa (alternativa a host:port)
            dimension: Dimensión de los embeddings
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.url = url
        self.dimension = dimension
        self._client: QdrantClient | None = None

    async def initialize(self) -> bool:
        """Inicializa conexión con Qdrant"""
        try:
            if self.url:
                self._client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key,
                    timeout=30,
                )
            else:
                self._client = QdrantClient(
                    host=self.host,
                    port=self.port,
                    api_key=self.api_key,
                    timeout=30,
                )

            # Verificar conectividad
            self._client.get_collections()

            # Crear collection compartida si no existe
            await self._ensure_shared_collection()

            return True
        except Exception as e:
            print(f"Error inicializando Qdrant: {e}")
            return False

    async def _ensure_shared_collection(self) -> None:
        """Asegura que la collection compartida existe"""
        try:
            self._client.get_collection(self.SHARED_COLLECTION)
        except (UnexpectedResponse, Exception):
            try:
                self._client.create_collection(
                    collection_name=self.SHARED_COLLECTION,
                    vectors_config=models.VectorParams(
                        size=self.dimension,
                        distance=models.Distance.COSINE,
                    ),
                )
                print(f"Collection '{self.SHARED_COLLECTION}' creada")
            except Exception as e:
                print(f"Error creando collection compartida: {e}")

    async def _ensure_collection(self, name: str) -> None:
        """Asegura que una collection existe"""
        try:
            self._client.get_collection(name)
        except (UnexpectedResponse, Exception):
            try:
                self._client.create_collection(
                    collection_name=name,
                    vectors_config=models.VectorParams(
                        size=self.dimension,
                        distance=models.Distance.COSINE,
                    ),
                )
            except Exception as e:
                print(f"Error creando collection '{name}': {e}")

    async def create_index(self, config: IndexConfig) -> bool:
        """Crea un índice/collection"""
        try:
            await self._ensure_collection(config.name)

            # Crear payload index para filtrado eficiente
            self._client.create_payload_index(
                collection_name=config.name,
                field_name="intention",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )

            return True
        except Exception as e:
            print(f"Error creando índice {config.name}: {e}")
            return False

    async def index_document(
        self,
        doc_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: ChunkMetadata,
        index_name: str,
    ) -> list[str]:
        """Indexa un documento en una collection"""
        try:
            await self._ensure_collection(index_name)

            points = []
            chunk_ids = []

            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{doc_id}_chunk_{i}_{uuid.uuid4().hex[:8]}"
                chunk_ids.append(chunk_id)

                # Construir payload (metadatos consultables)
                payload = {
                    "doc_id": metadata.doc_id,
                    "title": metadata.title,
                    "source_type": (
                        metadata.source_type.value
                        if isinstance(metadata.source_type, IndexType)
                        else metadata.source_type
                    ),
                    "authority_level": metadata.authority_level,
                    "jurisdiction": metadata.jurisdiction,
                    "normative_weight": metadata.normative_weight,
                    "chunk_index": i,
                    "content": chunk_text,
                    "source": metadata.title, # Alias para compatibilidad con script RAG
                }

                # Campos opcionales
                if metadata.validity_date:
                    payload["validity_date"] = metadata.validity_date
                if metadata.url:
                    payload["url"] = metadata.url
                if metadata.anchor:
                    payload["anchor"] = metadata.anchor
                
                # Mapear intention -> intenciones para compatibilidad con script RAG
                if metadata.intention:
                    payload["intention"] = metadata.intention
                    payload["intenciones"] = metadata.intention

                points.append(
                    models.PointStruct(
                        id=uuid.uuid4().hex,
                        vector=embedding,
                        payload={**payload, "chunk_id": chunk_id},
                    )
                )

            # Upsert en batch
            self._client.upsert(
                collection_name=index_name,
                points=points,
            )

            return chunk_ids
        except Exception as e:
            print(f"Error indexando documento {doc_id}: {e}")
            return []

    async def search(
        self,
        query_embedding: list[float],
        index_names: list[str],
        top_k: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:
        """Búsqueda en múltiples collections"""
        all_results: list[RetrievedChunk] = []

        for index_name in index_names:
            try:
                # Verificar que la collection existe
                try:
                    self._client.get_collection(index_name)
                except Exception:
                    continue

                # Construir filtros Qdrant
                qdrant_filter = self._build_filter(filters)

                results = self._client.query_points(
                    collection_name=index_name,
                    query=query_embedding,
                    query_filter=qdrant_filter,
                    limit=top_k,
                    with_payload=True,
                )

                # Convertir resultados a RetrievedChunk
                for point in results.points:
                    payload = point.payload or {}
                    similarity = point.score if point.score is not None else 0.0

                    chunk = RetrievedChunk(
                        chunk_id=payload.get("chunk_id", str(point.id)),
                        content=payload.get("content", ""),
                        metadata=ChunkMetadata(
                            doc_id=payload.get("doc_id", ""),
                            title=payload.get("title", ""),
                            source_type=payload.get(
                                "source_type", "normative_primary"
                            ),
                            authority_level=payload.get("authority_level", 0.5),
                            jurisdiction=payload.get("jurisdiction", "PE"),
                            validity_date=payload.get("validity_date"),
                            url=payload.get("url"),
                            anchor=payload.get("anchor"),
                            normative_weight=payload.get("normative_weight", 1.0),
                            intention=payload.get("intention"),
                        ),
                        similarity_score=max(0, min(1, similarity)),
                    )
                    all_results.append(chunk)
            except Exception as e:
                print(f"Error buscando en {index_name}: {e}")

        # Ordenar por similaridad
        all_results.sort(key=lambda x: x.similarity_score, reverse=True)

        return all_results[:top_k]

    def _build_filter(
        self, filters: dict[str, Any] | None
    ) -> models.Filter | None:
        """Convierte filtros genéricos a filtros Qdrant"""
        if not filters:
            return None

        conditions = []

        if "jurisdiction" in filters:
            conditions.append(
                models.FieldCondition(
                    key="jurisdiction",
                    match=models.MatchValue(value=filters["jurisdiction"]),
                )
            )

        if "authority_level_min" in filters:
            conditions.append(
                models.FieldCondition(
                    key="authority_level",
                    range=models.Range(gte=filters["authority_level_min"]),
                )
            )

        if "intention" in filters:
            conditions.append(
                models.FieldCondition(
                    key="intenciones", # Cambiado de 'intention' a 'intenciones'
                    match=models.MatchValue(value=filters["intention"]),
                )
            )

        if not conditions:
            return None

        return models.Filter(must=conditions)

    async def search_multi_tenant(
        self,
        query_embedding: list[float],
        organization_id: str | None = None,
        index_types: list[IndexType] | None = None,
        top_k: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:
        """
        Búsqueda multi-tenant: combina normativa compartida + docs de la org.
        """
        index_names = [self.SHARED_COLLECTION]

        if organization_id:
            org_collection_name = f"org_{organization_id}"
            await self._ensure_collection(org_collection_name)
            index_names.append(org_collection_name)

        return await self.search(
            query_embedding=query_embedding,
            index_names=index_names,
            top_k=top_k,
            filters=filters,
        )

    async def search_project(
        self,
        query_embedding: list[float],
        organization_ids: list[str],
        top_k: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:
        """
        Búsqueda a nivel proyecto: normativa compartida + docs de TODAS las orgs.
        """
        index_names = [self.SHARED_COLLECTION]

        for org_id in organization_ids:
            org_collection_name = f"org_{org_id}"
            await self._ensure_collection(org_collection_name)
            index_names.append(org_collection_name)

        return await self.search(
            query_embedding=query_embedding,
            index_names=index_names,
            top_k=top_k,
            filters=filters,
        )

    async def delete_document(self, doc_id: str) -> bool:
        """Elimina todos los chunks de un documento"""
        try:
            deleted = False
            collections = self._client.get_collections().collections

            for collection in collections:
                try:
                    self._client.delete(
                        collection_name=collection.name,
                        points_selector=models.FilterSelector(
                            filter=models.Filter(
                                must=[
                                    models.FieldCondition(
                                        key="doc_id",
                                        match=models.MatchValue(value=doc_id),
                                    )
                                ]
                            )
                        ),
                    )
                    deleted = True
                except Exception:
                    pass
            return deleted
        except Exception as e:
            print(f"Error eliminando documento {doc_id}: {e}")
            return False

    async def get_document_chunks(self, doc_id: str) -> list[RetrievedChunk]:
        """Obtiene todos los chunks de un documento"""
        chunks = []
        try:
            collections = self._client.get_collections().collections

            for collection in collections:
                try:
                    results, _ = self._client.scroll(
                        collection_name=collection.name,
                        scroll_filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="doc_id",
                                    match=models.MatchValue(value=doc_id),
                                )
                            ]
                        ),
                        with_payload=True,
                        limit=1000,
                    )

                    for point in results:
                        payload = point.payload or {}
                        chunk = RetrievedChunk(
                            chunk_id=payload.get("chunk_id", str(point.id)),
                            content=payload.get("content", ""),
                            metadata=ChunkMetadata(
                                doc_id=payload.get("doc_id", ""),
                                title=payload.get("title", ""),
                                source_type=payload.get(
                                    "source_type", "normative_primary"
                                ),
                                authority_level=payload.get("authority_level", 0.5),
                                jurisdiction=payload.get("jurisdiction", "PE"),
                            ),
                            similarity_score=1.0,
                        )
                        chunks.append(chunk)
                except Exception:
                    pass
        except Exception:
            pass
        return chunks

    async def list_indices(self) -> list[str]:
        """Lista las collections disponibles"""
        try:
            collections = self._client.get_collections().collections
            return [c.name for c in collections]
        except Exception as e:
            print(f"Error listando colecciones: {e}")
            return []

    async def get_index_stats(self, index_name: str) -> dict[str, Any]:
        """Obtiene estadísticas de una collection"""
        try:
            info = self._client.get_collection(index_name)
            return {
                "name": index_name,
                "total_chunks": info.points_count or 0,
                "metadata": {
                    "vectors_count": info.vectors_count,
                    "status": info.status.value if info.status else "unknown",
                    "dimension": (
                        info.config.params.vectors.size
                        if hasattr(info.config.params.vectors, "size")
                        else self.dimension
                    ),
                },
            }
        except Exception as e:
            return {"error": str(e)}

    async def health_check(self) -> bool:
        """Verifica que Qdrant esté funcionando"""
        try:
            self._client.get_collections()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Cierra la conexión"""
        if self._client:
            self._client.close()
        self._client = None


# Factory function
def create_qdrant_adapter(
    host: str = "localhost",
    port: int = 6333,
    api_key: str | None = None,
    url: str | None = None,
    dimension: int = QdrantAdapter.DEFAULT_DIMENSION,
) -> QdrantAdapter:
    """
    Crea un QdrantAdapter.

    Args:
        host: Host del servidor Qdrant
        port: Puerto REST del servidor
        api_key: API key (opcional)
        url: URL completa (alternativa a host:port)
        dimension: Dimensión de los embeddings

    Returns:
        QdrantAdapter configurado
    """
    return QdrantAdapter(
        host=host,
        port=port,
        api_key=api_key,
        url=url,
        dimension=dimension,
    )
