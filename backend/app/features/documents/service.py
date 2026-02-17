"""
Documents Feature - Service
Lógica de negocio para gestión de documentos RAG.
"""

import uuid
import re
from typing import Any

from .schemas import (
    DocumentType,
    DocumentUploadRequest,
    DocumentUploadResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    ChunkResult,
    CollectionStats,
    RAGStatusResponse,
)
from app.modules.rag import get_rag_module, QdrantAdapter
from app.modules.rag.adapters.base import ChunkMetadata, IndexType
from app.ai.embeddings import embed_text, embed_texts


class DocumentService:
    """Servicio para gestión de documentos RAG"""

    # Mapeo de DocumentType a IndexType
    DOC_TYPE_TO_INDEX = {
        DocumentType.NORMATIVE: IndexType.NORMATIVE_PRIMARY,
        DocumentType.REGULATORY: IndexType.REGULATORY_SECONDARY,
        DocumentType.GUIDANCE: IndexType.GUIDANCE_DOCS,
        DocumentType.FAQ: IndexType.AUTHORITY_FAQ,
        DocumentType.CASE: IndexType.CASE_INTERPRETATION,
        DocumentType.ORGANIZATION: IndexType.NORMATIVE_PRIMARY,  # Se usa collection específica
    }

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 600,
        overlap: int = 120,
    ) -> list[str]:
        """
        Divide el texto en chunks semánticos.

        Estrategia:
        1. Intenta dividir por párrafos primero
        2. Si un párrafo es muy largo, divide por oraciones
        3. Respeta el overlap para mantener contexto
        """
        # Limpiar texto
        text = re.sub(r'\n{3,}', '\n\n', text.strip())

        # Dividir por párrafos
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""
        prev_chunk_end = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Estimar tokens (aproximación: 1 token ≈ 4 caracteres)
            estimated_tokens = len(current_chunk + para) // 4

            if estimated_tokens <= chunk_size:
                # Cabe en el chunk actual
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                # No cabe, guardar chunk actual y empezar nuevo
                if current_chunk:
                    chunks.append(current_chunk)
                    # Calcular overlap
                    overlap_chars = overlap * 4
                    prev_chunk_end = current_chunk[-overlap_chars:] if len(current_chunk) > overlap_chars else current_chunk

                # Si el párrafo es muy largo, dividir por oraciones
                if len(para) // 4 > chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_chunk = prev_chunk_end
                    for sent in sentences:
                        if len(current_chunk + sent) // 4 <= chunk_size:
                            current_chunk += " " + sent if current_chunk else sent
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = sent
                else:
                    current_chunk = prev_chunk_end + "\n\n" + para if prev_chunk_end else para

        # Agregar último chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    async def upload_document(
        self,
        request: DocumentUploadRequest,
    ) -> DocumentUploadResponse:
        """
        Procesa y sube un documento al sistema RAG.

        1. Genera chunks del documento
        2. Genera embeddings para cada chunk
        3. Indexa en Qdrant
        """
        rag = get_rag_module()

        if not isinstance(rag.vector_store, QdrantAdapter):
            raise RuntimeError("Vector store no es Qdrant")

        adapter: QdrantAdapter = rag.vector_store

        # Generar ID único para el documento
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"

        # Determinar colección destino
        if request.organization_id:
            collection_name = f"org_{request.organization_id}"
        else:
            collection_name = QdrantAdapter.SHARED_COLLECTION

        # Crear chunks
        chunks = self._chunk_text(
            request.content,
            chunk_size=request.chunk_size,
            overlap=request.chunk_overlap,
        )

        if not chunks:
            raise ValueError("El documento no generó ningún chunk")

        # Generar embeddings
        embeddings = await embed_texts(chunks)

        # Crear metadata
        metadata = ChunkMetadata(
            doc_id=doc_id,
            title=request.title,
            source_type=self.DOC_TYPE_TO_INDEX.get(
                request.document_type,
                IndexType.NORMATIVE_PRIMARY
            ),
            authority_level=request.authority_level,
            jurisdiction=request.jurisdiction,
            validity_date=request.validity_date,
            url=request.url,
            normative_weight=request.authority_level,
            intention=request.intention,
        )

        # Indexar en Qdrant
        chunk_ids = await adapter.index_document(
            doc_id=doc_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata,
            index_name=collection_name,
        )

        return DocumentUploadResponse(
            doc_id=doc_id,
            title=request.title,
            chunks_created=len(chunk_ids),
            collection=collection_name,
            message=f"Documento indexado exitosamente con {len(chunk_ids)} chunks",
        )

    async def search_documents(
        self,
        request: DocumentSearchRequest,
    ) -> DocumentSearchResponse:
        """
        Busca documentos usando RAG.
        """
        rag = get_rag_module()

        if not isinstance(rag.vector_store, QdrantAdapter):
            raise RuntimeError("Vector store no es Qdrant")

        adapter: QdrantAdapter = rag.vector_store

        # Generar embedding de la query
        query_embedding = await embed_text(request.query)

        # Determinar colecciones a buscar
        if request.organization_id:
            # Multi-tenant: normativa + docs de la org
            results = await adapter.search_multi_tenant(
                query_embedding=query_embedding,
                organization_id=request.organization_id if request.include_normativa else None,
                top_k=request.top_k,
            )
            collections_searched = [
                QdrantAdapter.SHARED_COLLECTION,
                f"org_{request.organization_id}"
            ]
        else:
            # Solo normativa compartida
            results = await adapter.search(
                query_embedding=query_embedding,
                index_names=[QdrantAdapter.SHARED_COLLECTION],
                top_k=request.top_k,
            )
            collections_searched = [QdrantAdapter.SHARED_COLLECTION]

        # Convertir a ChunkResult
        chunk_results = [
            ChunkResult(
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                title=chunk.metadata.title,
                source_type=chunk.metadata.source_type.value if isinstance(
                    chunk.metadata.source_type, IndexType
                ) else chunk.metadata.source_type,
                similarity_score=chunk.similarity_score,
                authority_level=chunk.metadata.authority_level,
                jurisdiction=chunk.metadata.jurisdiction,
                url=chunk.metadata.url,
            )
            for chunk in results
        ]

        return DocumentSearchResponse(
            query=request.query,
            results=chunk_results,
            total_found=len(chunk_results),
            collections_searched=collections_searched,
        )

    async def get_rag_status(self) -> RAGStatusResponse:
        """
        Obtiene el estado del sistema RAG.
        """
        from app.core.config import settings

        try:
            rag = get_rag_module()
        except RuntimeError:
            return RAGStatusResponse(
                healthy=False,
                vector_store_type=settings.VECTOR_STORE_TYPE,
                collections=[],
                total_documents=0,
            )

        if not isinstance(rag.vector_store, QdrantAdapter):
            return RAGStatusResponse(
                healthy=False,
                vector_store_type=settings.VECTOR_STORE_TYPE,
                collections=[],
                total_documents=0,
            )

        adapter: QdrantAdapter = rag.vector_store

        # Verificar salud
        healthy = await adapter.health_check()

        # Obtener colecciones
        collection_names = await adapter.list_indices()
        collections = []
        total_chunks = 0

        for name in collection_names:
            stats = await adapter.get_index_stats(name)
            if "error" not in stats:
                collections.append(CollectionStats(
                    name=stats["name"],
                    total_chunks=stats["total_chunks"],
                    metadata=stats.get("metadata", {}),
                ))
                total_chunks += stats["total_chunks"]

        return RAGStatusResponse(
            healthy=healthy,
            vector_store_type=settings.VECTOR_STORE_TYPE,
            collections=collections,
            total_documents=total_chunks,
        )

    async def delete_document(self, doc_id: str) -> bool:
        """Elimina un documento por su ID"""
        rag = get_rag_module()

        if not isinstance(rag.vector_store, QdrantAdapter):
            raise RuntimeError("Vector store no es Qdrant")

        return await rag.vector_store.delete_document(doc_id)


# Instancia global
document_service = DocumentService()
