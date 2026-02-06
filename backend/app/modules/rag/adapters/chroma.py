"""
RAG Adapters - ChromaDB Implementation
Implementación del VectorStoreAdapter para ChromaDB con soporte multi-tenant.
"""

import uuid
from typing import Any

from .base import (
    VectorStoreAdapter,
    IndexConfig,
    ChunkMetadata,
    RetrievedChunk,
    IndexType,
)


class ChromaDBAdapter(VectorStoreAdapter):
    """
    Adapter de ChromaDB para GPT Legal.

    Arquitectura multi-tenant:
    - Collection 'normativa_peru': Corpus compartido de normativa legal
    - Collection 'org_{org_id}': Documentos privados de cada organización

    Uso:
    ```python
    adapter = ChromaDBAdapter(persist_directory="./chroma_data")
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
    SHARED_COLLECTION = "normativa_peru"

    def __init__(
        self,
        persist_directory: str | None = None,
        host: str | None = None,
        port: int | None = None,
    ):
        """
        Inicializa el adapter.

        Args:
            persist_directory: Ruta para persistencia local (desarrollo)
            host: Host del servidor ChromaDB (producción)
            port: Puerto del servidor ChromaDB (producción)
        """
        self.persist_directory = persist_directory
        self.host = host
        self.port = port
        self._client = None
        self._collections: dict[str, Any] = {}

    async def initialize(self) -> bool:
        """Inicializa conexión con ChromaDB"""
        try:
            import chromadb
            from chromadb.config import Settings

            if self.host and self.port:
                # Modo servidor (producción)
                self._client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                )
            elif self.persist_directory:
                # Modo persistente local (desarrollo)
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False),
                )
            else:
                # Modo en memoria (testing)
                self._client = chromadb.Client(
                    settings=Settings(anonymized_telemetry=False),
                )

            # Crear collection compartida si no existe
            await self._ensure_shared_collection()

            return True
        except Exception as e:
            print(f"Error inicializando ChromaDB: {e}")
            return False

    async def _ensure_shared_collection(self) -> None:
        """Asegura que la collection compartida existe"""
        try:
            self._collections[self.SHARED_COLLECTION] = self._client.get_or_create_collection(
                name=self.SHARED_COLLECTION,
                metadata={
                    "description": "Normativa legal peruana compartida",
                    "type": "shared",
                    "hnsw:space": "cosine",
                }
            )
        except Exception as e:
            print(f"Error creando collection compartida: {e}")

    async def _get_org_collection(self, organization_id: str) -> Any:
        """Obtiene o crea la collection de una organización"""
        collection_name = f"org_{organization_id}"

        if collection_name not in self._collections:
            self._collections[collection_name] = self._client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "description": f"Documentos privados de {organization_id}",
                    "type": "organization",
                    "organization_id": organization_id,
                    "hnsw:space": "cosine",
                }
            )

        return self._collections[collection_name]

    async def create_index(self, config: IndexConfig) -> bool:
        """Crea un índice/collection"""
        try:
            self._collections[config.name] = self._client.get_or_create_collection(
                name=config.name,
                metadata={
                    "index_type": config.index_type.value,
                    "dimension": config.dimension,
                    "hnsw:space": config.metric,
                }
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
            collection = self._collections.get(index_name)
            if not collection:
                collection = self._client.get_or_create_collection(name=index_name)
                self._collections[index_name] = collection

            chunk_ids = []
            metadatas = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}_{uuid.uuid4().hex[:8]}"
                chunk_ids.append(chunk_id)

                # Preparar metadata para ChromaDB (solo tipos básicos)
                meta = {
                    "doc_id": metadata.doc_id,
                    "title": metadata.title,
                    "source_type": metadata.source_type.value if isinstance(metadata.source_type, IndexType) else metadata.source_type,
                    "authority_level": metadata.authority_level,
                    "jurisdiction": metadata.jurisdiction,
                    "normative_weight": metadata.normative_weight,
                    "chunk_index": i,
                }
                if metadata.validity_date:
                    meta["validity_date"] = metadata.validity_date
                if metadata.url:
                    meta["url"] = metadata.url
                if metadata.anchor:
                    meta["anchor"] = metadata.anchor

                metadatas.append(meta)

            # Añadir a la collection
            collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
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
            collection = self._collections.get(index_name)
            if not collection:
                try:
                    collection = self._client.get_collection(name=index_name)
                    self._collections[index_name] = collection
                except Exception:
                    continue

            # Construir where clause para filtros
            where = None
            if filters:
                where = {}
                if "jurisdiction" in filters:
                    where["jurisdiction"] = filters["jurisdiction"]
                if "authority_level_min" in filters:
                    where["authority_level"] = {"$gte": filters["authority_level_min"]}

            try:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where if where else None,
                    include=["documents", "metadatas", "distances"],
                )

                # Convertir resultados a RetrievedChunk
                if results and results["ids"] and results["ids"][0]:
                    for i, chunk_id in enumerate(results["ids"][0]):
                        metadata_dict = results["metadatas"][0][i]
                        distance = results["distances"][0][i] if results["distances"] else 0

                        # Convertir distancia a similaridad (cosine)
                        similarity = 1 - distance

                        chunk = RetrievedChunk(
                            chunk_id=chunk_id,
                            content=results["documents"][0][i],
                            metadata=ChunkMetadata(
                                doc_id=metadata_dict.get("doc_id", ""),
                                title=metadata_dict.get("title", ""),
                                source_type=metadata_dict.get("source_type", "normative_primary"),
                                authority_level=metadata_dict.get("authority_level", 0.5),
                                jurisdiction=metadata_dict.get("jurisdiction", "PE"),
                                validity_date=metadata_dict.get("validity_date"),
                                url=metadata_dict.get("url"),
                                anchor=metadata_dict.get("anchor"),
                                normative_weight=metadata_dict.get("normative_weight", 1.0),
                            ),
                            similarity_score=max(0, min(1, similarity)),
                        )
                        all_results.append(chunk)
            except Exception as e:
                print(f"Error buscando en {index_name}: {e}")

        # Ordenar por similaridad
        all_results.sort(key=lambda x: x.similarity_score, reverse=True)

        return all_results[:top_k]

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

        Args:
            query_embedding: Vector de la query
            organization_id: ID de la org (para buscar en sus docs privados)
            index_types: Tipos de índice a buscar (opcional)
            top_k: Número de resultados
            filters: Filtros adicionales

        Returns:
            Lista de chunks ordenados por similaridad
        """
        index_names = [self.SHARED_COLLECTION]

        if organization_id:
            org_collection_name = f"org_{organization_id}"
            # Verificar si la org tiene collection
            await self._get_org_collection(organization_id)
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

        Esto es para proyectos multi-organización (1-3 orgs).

        Args:
            query_embedding: Vector de la query
            organization_ids: Lista de IDs de organizaciones del proyecto
            top_k: Número de resultados
            filters: Filtros adicionales

        Returns:
            Lista de chunks ordenados por similaridad
        """
        index_names = [self.SHARED_COLLECTION]

        for org_id in organization_ids:
            org_collection_name = f"org_{org_id}"
            # Asegurar que la collection existe
            await self._get_org_collection(org_id)
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
            for collection in self._collections.values():
                try:
                    # Buscar chunks del documento
                    results = collection.get(
                        where={"doc_id": doc_id},
                        include=["metadatas"],
                    )
                    if results["ids"]:
                        collection.delete(ids=results["ids"])
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
        for collection in self._collections.values():
            try:
                results = collection.get(
                    where={"doc_id": doc_id},
                    include=["documents", "metadatas"],
                )
                if results["ids"]:
                    for i, chunk_id in enumerate(results["ids"]):
                        metadata_dict = results["metadatas"][i]
                        chunk = RetrievedChunk(
                            chunk_id=chunk_id,
                            content=results["documents"][i],
                            metadata=ChunkMetadata(
                                doc_id=metadata_dict.get("doc_id", ""),
                                title=metadata_dict.get("title", ""),
                                source_type=metadata_dict.get("source_type", "normative_primary"),
                                authority_level=metadata_dict.get("authority_level", 0.5),
                                jurisdiction=metadata_dict.get("jurisdiction", "PE"),
                            ),
                            similarity_score=1.0,  # No aplica para get
                        )
                        chunks.append(chunk)
            except Exception:
                pass
        return chunks

    async def list_indices(self) -> list[str]:
        """Lista las collections disponibles"""
        try:
            collections = self._client.list_collections()
            return [c.name for c in collections]
        except Exception as e:
            print(f"Error listando colecciones: {e}")
            return []

    async def get_index_stats(self, index_name: str) -> dict[str, Any]:
        """Obtiene estadísticas de una collection"""
        try:
            collection = self._collections.get(index_name)
            if not collection:
                collection = self._client.get_collection(name=index_name)

            count = collection.count()
            return {
                "name": index_name,
                "total_chunks": count,
                "metadata": collection.metadata,
            }
        except Exception as e:
            return {"error": str(e)}

    async def health_check(self) -> bool:
        """Verifica que ChromaDB esté funcionando"""
        try:
            self._client.heartbeat()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Cierra la conexión"""
        self._collections.clear()
        self._client = None


# Factory function para crear el adapter según configuración
def create_chroma_adapter(
    mode: str = "local",
    persist_directory: str = "./chroma_data",
    host: str = "localhost",
    port: int = 8000,
) -> ChromaDBAdapter:
    """
    Crea un ChromaDBAdapter según el modo.

    Args:
        mode: 'local' (persistente), 'server' (HTTP), 'memory' (testing)
        persist_directory: Ruta para modo local
        host: Host para modo servidor
        port: Puerto para modo servidor

    Returns:
        ChromaDBAdapter configurado
    """
    if mode == "server":
        return ChromaDBAdapter(host=host, port=port)
    elif mode == "local":
        return ChromaDBAdapter(persist_directory=persist_directory)
    else:  # memory
        return ChromaDBAdapter()
