"""
RAG Module - Main Service
Orquesta todo el pipeline RAG.
"""

from typing import List, Dict, Any

from .interfaces import (
    RAGConfig,
    RAGQuery,
    RAGResult,
    RetrievedChunk,
    Evidence,
    IndexType,
)
from .query_expander import LegalQueryExpander
from .scorer import ChunkScorer
from .filter import NormativeFilter, QualityScoreFilter
from .grounding import ClaimGrounder
from .contradiction import ContradictionDetector
from .confidence import RAGConfidenceCalculator
from .protocols import InsufficientEvidenceProtocol
from .adapters.base import VectorStoreAdapter
from .adapters.chroma import ChromaDBAdapter, create_chroma_adapter


class RAGModule:
    """
    Motor RAG principal.

    Pipeline completo:
    1. Query Normalization
    2. Legal Intent Expansion
    3. Multi-index Search
    4. Chunk Scoring
    5. Normative Filtering
    6. Contradiction Check
    7. Confidence Calculation
    8. Grounding (opcional, para output)
    """

    def __init__(
        self,
        vector_store: VectorStoreAdapter | None = None,
        config: RAGConfig | None = None,
    ):
        self.config = config or RAGConfig()
        self.vector_store = vector_store

        # Componentes del pipeline
        self.query_expander = LegalQueryExpander()
        self.scorer = ChunkScorer(self.config)
        self.normative_filter = NormativeFilter()
        self.quality_filter = QualityScoreFilter()
        self.contradiction_detector = ContradictionDetector()
        self.confidence_calculator = RAGConfidenceCalculator(self.config)
        self.grounder = ClaimGrounder()
        self.insufficient_protocol = InsufficientEvidenceProtocol(
            self.config.confidence_threshold
        )

    async def retrieve_and_ground(
        self,
        query: str,
        organization_id: str | None = None,
        indices: List[IndexType] | None = None,
        top_k_initial: int | None = None,
        top_k_rerank: int | None = None,
        strictness: int | None = None,
    ) -> RAGResult:
        """
        Ejecuta el pipeline RAG completo.

        Args:
            query: Consulta del usuario
            organization_id: ID de la organización (para buscar en sus docs privados)
            indices: Índices donde buscar
            top_k_initial: Chunks iniciales a recuperar
            top_k_rerank: Chunks finales después de rerank
            strictness: Nivel de strictness (1-5)

        Returns:
            RAGResult con chunks, confidence, etc.
        """
        # Configurar parámetros
        config = RAGConfig(
            top_k_initial=top_k_initial or self.config.top_k_initial,
            top_k_rerank=top_k_rerank or self.config.top_k_rerank,
            strictness=strictness or self.config.strictness,
            confidence_threshold=self.config.confidence_threshold,
        )

        target_indices = indices or [
            IndexType.NORMATIVE_PRIMARY,
            IndexType.REGULATORY_SECONDARY,
        ]

        # Crear query object
        rag_query = RAGQuery(
            original_query=query,
            target_indices=target_indices,
            config=config,
        )

        # 1. Expandir query
        expanded_terms = self.query_expander.expand(query)
        rag_query.expanded_terms = expanded_terms

        # 2. Verificar vector store
        if not self.vector_store:
            return RAGResult(
                query=rag_query,
                confidence=0.0,
                processing_notes=["Vector store no configurado"],
            )

        # 3. Generar embedding de la query
        from app.ai.embeddings import embed_text
        query_embedding = await embed_text(query)

        # 4. Buscar en vector store (multi-tenant si hay organization_id)
        if isinstance(self.vector_store, ChromaDBAdapter):
            chunks = await self.vector_store.search_multi_tenant(
                query_embedding=query_embedding,
                organization_id=organization_id,
                index_types=target_indices,
                top_k=config.top_k_initial,
            )
        else:
            index_names = [idx.value for idx in target_indices]
            chunks = await self.vector_store.search(
                query_embedding=query_embedding,
                index_names=index_names,
                top_k=config.top_k_initial,
            )

        # 5. Si no hay chunks, retornar resultado vacío
        if not chunks:
            return RAGResult(
                query=rag_query,
                chunks=[],
                evidence=[],
                confidence=0.0,
                indices_searched=[idx.value for idx in target_indices],
                processing_notes=["No se encontraron documentos relevantes"],
            )

        # 6. Procesar chunks recuperados (scoring, filtrado, etc.)
        return await self.process_retrieved_chunks(chunks, rag_query)

    async def retrieve_for_project(
        self,
        query: str,
        organization_ids: List[str],
        top_k_initial: int | None = None,
        top_k_rerank: int | None = None,
    ) -> RAGResult:
        """
        Búsqueda RAG a nivel proyecto (multi-organización).

        Busca en:
        - normativa_peru (compartido)
        - org_{id} para cada organización del proyecto

        Args:
            query: Consulta de búsqueda
            organization_ids: Lista de IDs de organizaciones del proyecto (1-3)
            top_k_initial: Chunks iniciales
            top_k_rerank: Chunks finales

        Returns:
            RAGResult con chunks de todas las fuentes
        """
        config = RAGConfig(
            top_k_initial=top_k_initial or self.config.top_k_initial,
            top_k_rerank=top_k_rerank or self.config.top_k_rerank,
            strictness=self.config.strictness,
            confidence_threshold=self.config.confidence_threshold,
        )

        rag_query = RAGQuery(
            original_query=query,
            target_indices=[IndexType.NORMATIVE_PRIMARY],
            config=config,
        )

        # Expandir query
        expanded_terms = self.query_expander.expand(query)
        rag_query.expanded_terms = expanded_terms

        if not self.vector_store:
            return RAGResult(
                query=rag_query,
                confidence=0.0,
                processing_notes=["Vector store no configurado"],
            )

        # Generar embedding
        from app.ai.embeddings import embed_text
        query_embedding = await embed_text(query)

        # Buscar a nivel proyecto
        if isinstance(self.vector_store, ChromaDBAdapter):
            chunks = await self.vector_store.search_project(
                query_embedding=query_embedding,
                organization_ids=organization_ids,
                top_k=config.top_k_initial,
            )
        else:
            # Fallback: buscar solo en normativa
            chunks = await self.vector_store.search(
                query_embedding=query_embedding,
                index_names=["normative_primary"],
                top_k=config.top_k_initial,
            )

        if not chunks:
            return RAGResult(
                query=rag_query,
                chunks=[],
                evidence=[],
                confidence=0.0,
                processing_notes=[f"No se encontraron documentos para proyecto con {len(organization_ids)} org(s)"],
            )

        return await self.process_retrieved_chunks(chunks, rag_query)

    async def process_retrieved_chunks(
        self,
        chunks: List[RetrievedChunk],
        query: RAGQuery,
    ) -> RAGResult:
        """
        Procesa chunks ya recuperados (para testing o cuando se tiene
        el vector store implementado).
        """
        # 1. Scoring
        query_terms = [query.original_query] + query.expanded_terms
        ranked_chunks = self.scorer.rank_chunks(
            chunks,
            query_terms,
            query.config.jurisdiction_filter,
        )

        chunks_before_filter = len(ranked_chunks)

        # 2. Filtrado normativo
        filter_result = self.normative_filter.filter(
            ranked_chunks,
            query.config.jurisdiction_filter,
        )
        filtered_chunks = filter_result.accepted

        # 3. Filtrado por calidad
        quality_result = self.quality_filter.filter(filtered_chunks)
        quality_chunks = quality_result.accepted

        # 4. Eliminar duplicados
        unique_chunks = self.normative_filter.filter_duplicates(quality_chunks)

        # 5. Limitar a top_k_rerank
        final_chunks = unique_chunks[:query.config.top_k_rerank]

        # 6. Detectar contradicciones
        contradiction_result = self.contradiction_detector.detect(final_chunks)

        # 7. Calcular confidence
        confidence_result = self.confidence_calculator.calculate(
            final_chunks,
            query_terms,
            contradiction_result.has_contradictions,
        )

        # Ajustar confidence por contradicciones
        final_confidence = confidence_result.total
        if contradiction_result.has_contradictions:
            final_confidence -= contradiction_result.confidence_penalty
            final_confidence = max(0.0, final_confidence)

        # 8. Construir resultado
        return RAGResult(
            query=query,
            chunks=final_chunks,
            evidence=[],  # Se llena después con grounding
            confidence=final_confidence,
            has_contradictions=contradiction_result.has_contradictions,
            contradicting_chunks=[
                c.model_dump() for c in contradiction_result.contradictions
            ],
            indices_searched=[idx.value for idx in query.target_indices],
            chunks_before_filter=chunks_before_filter,
            chunks_after_filter=len(final_chunks),
            processing_notes=[
                f"Expanded terms: {len(query.expanded_terms)}",
                f"Filtered: {filter_result.rejected_count} chunks",
                f"Quality filtered: {quality_result.rejected_count} chunks",
                f"Confidence: {confidence_result.total:.2f}",
            ],
        )

    async def ground_response(
        self,
        claims: List[str],
        rag_result: RAGResult,
    ) -> RAGResult:
        """
        Aplica grounding a las claims de una respuesta.
        Actualiza el RAGResult con la evidencia.
        """
        grounding_result = self.grounder.ground_claims(
            claims,
            rag_result.chunks,
        )

        # Construir lista de evidencia
        evidence = self.grounder.build_evidence_list(
            grounding_result.grounded_claims,
            rag_result.chunks,
        )

        # Actualizar resultado
        rag_result.evidence = evidence
        rag_result.grounded_claims = [
            c.model_dump() for c in grounding_result.grounded_claims
        ]
        rag_result.ungrounded_claims = [
            c.claim_text for c in grounding_result.ungrounded_claims
        ]

        # Ajustar confidence si hay claims no grounded
        if grounding_result.ungrounded_claims:
            penalty = len(grounding_result.ungrounded_claims) * 0.05
            rag_result.confidence = max(0.0, rag_result.confidence - penalty)

        return rag_result

    def check_evidence_sufficient(self, rag_result: RAGResult) -> bool:
        """Verifica si la evidencia es suficiente para responder"""
        return rag_result.is_sufficient()

    def should_escalate(self, rag_result: RAGResult) -> bool:
        """Determina si se debe escalar a asesor humano"""
        return rag_result.requires_escalation()


# =============================================================================
# Factory y instancia global
# =============================================================================

_rag_module: RAGModule | None = None


async def initialize_rag() -> RAGModule:
    """
    Inicializa el módulo RAG con ChromaDB.
    Debe llamarse al inicio de la aplicación.
    """
    global _rag_module

    from app.core.config import settings

    # Crear adapter de ChromaDB según configuración
    adapter = create_chroma_adapter(
        mode=settings.CHROMA_MODE,
        persist_directory=settings.CHROMA_PERSIST_DIR,
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
        token=settings.CHROMA_TOKEN,
    )

    # Inicializar ChromaDB
    await adapter.initialize()

    # Crear configuración RAG desde settings
    config = RAGConfig(
        top_k_initial=settings.RAG_TOP_K_INITIAL,
        top_k_rerank=settings.RAG_TOP_K_RERANK,
        strictness=settings.RAG_STRICTNESS,
        confidence_threshold=settings.RAG_CONFIDENCE_THRESHOLD,
    )

    # Crear módulo RAG
    _rag_module = RAGModule(vector_store=adapter, config=config)

    return _rag_module


def get_rag_module() -> RAGModule:
    """Obtiene la instancia del módulo RAG"""
    if _rag_module is None:
        raise RuntimeError(
            "RAG module not initialized. Call initialize_rag() first."
        )
    return _rag_module


async def shutdown_rag() -> None:
    """Cierra conexiones del módulo RAG"""
    global _rag_module
    if _rag_module and _rag_module.vector_store:
        await _rag_module.vector_store.close()
    _rag_module = None
