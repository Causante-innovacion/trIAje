"""
RAG Module - Chunk Scorer
Scoring compuesto según spec:
score = semantic_similarity * 0.35 + authority_weight * 0.25
      + recency_weight * 0.15 + jurisdiction_match * 0.15
      + legal_term_density * 0.10
"""

from datetime import datetime
from typing import List
from .interfaces import RetrievedChunk, ChunkMetadata, RAGConfig


class ChunkScorer:
    """
    Calcula scores compuestos para chunks recuperados.
    """

    def __init__(self, config: RAGConfig):
        self.config = config

    def calculate_composite_score(
        self,
        chunk: RetrievedChunk,
        query_terms: List[str],
        target_jurisdiction: str = "PE"
    ) -> float:
        """
        Calcula el score compuesto para un chunk.
        """
        # Ya vienen del vector store
        semantic = chunk.similarity_score

        # Calcular otros scores
        authority = self._calculate_authority_score(chunk.metadata)
        recency = self._calculate_recency_score(chunk.metadata)
        jurisdiction = self._calculate_jurisdiction_score(
            chunk.metadata, target_jurisdiction
        )
        term_density = self._calculate_term_density(chunk.content, query_terms)

        # Score compuesto
        composite = (
            semantic * self.config.weight_semantic +
            authority * self.config.weight_authority +
            recency * self.config.weight_recency +
            jurisdiction * self.config.weight_jurisdiction +
            term_density * self.config.weight_term_density
        )

        # Actualizar chunk con scores
        chunk.authority_score = authority
        chunk.recency_score = recency
        chunk.jurisdiction_score = jurisdiction
        chunk.term_density_score = term_density
        chunk.composite_score = composite

        return composite

    def _calculate_authority_score(self, metadata: ChunkMetadata) -> float:
        """
        Score basado en nivel de autoridad de la fuente.
        """
        return metadata.authority_level

    def _calculate_recency_score(self, metadata: ChunkMetadata) -> float:
        """
        Score basado en qué tan reciente es el documento.
        Documentos más recientes tienen mayor peso.
        """
        if not metadata.validity_date:
            return 0.5  # Score neutro si no hay fecha

        try:
            doc_date = datetime.fromisoformat(metadata.validity_date)
            now = datetime.now()
            years_old = (now - doc_date).days / 365

            if years_old < 1:
                return 1.0
            elif years_old < 3:
                return 0.9
            elif years_old < 5:
                return 0.7
            elif years_old < 10:
                return 0.5
            else:
                return 0.3
        except (ValueError, TypeError):
            return 0.5

    def _calculate_jurisdiction_score(
        self,
        metadata: ChunkMetadata,
        target: str
    ) -> float:
        """
        Score basado en coincidencia de jurisdicción.
        """
        if metadata.jurisdiction == target:
            return 1.0
        elif metadata.jurisdiction == "INTERNATIONAL":
            return 0.7  # Documentos internacionales tienen aplicación parcial
        else:
            return 0.3

    def _calculate_term_density(
        self,
        content: str,
        query_terms: List[str]
    ) -> float:
        """
        Score basado en densidad de términos de la query en el contenido.
        """
        if not query_terms or not content:
            return 0.0

        content_lower = content.lower()
        total_words = len(content_lower.split())

        if total_words == 0:
            return 0.0

        matches = sum(
            1 for term in query_terms
            if term.lower() in content_lower
        )

        # Normalizar: más términos encontrados = mejor score
        density = min(matches / max(len(query_terms), 1), 1.0)
        return density

    def rank_chunks(
        self,
        chunks: List[RetrievedChunk],
        query_terms: List[str],
        target_jurisdiction: str = "PE",
        top_k: int | None = None
    ) -> List[RetrievedChunk]:
        """
        Calcula scores y ordena chunks por score compuesto.
        """
        for chunk in chunks:
            self.calculate_composite_score(chunk, query_terms, target_jurisdiction)

        # Ordenar por score compuesto descendente
        ranked = sorted(chunks, key=lambda c: c.composite_score, reverse=True)

        if top_k:
            return ranked[:top_k]
        return ranked


class AuthorityWeightResolver:
    """
    Resuelve el peso de autoridad según tipo de fuente.
    Según spec:
    - ley / decreto supremo = 1.0
    - reglamento = 0.9
    - resolución = 0.8
    - guía oficial = 0.7
    - FAQ = 0.5
    - blog = 0 (excluido)
    """

    WEIGHTS = {
        "ley": 1.0,
        "decreto_supremo": 1.0,
        "decreto_legislativo": 1.0,
        "reglamento": 0.9,
        "resolucion": 0.8,
        "resolucion_superintendencia": 0.8,
        "directiva": 0.75,
        "guia_oficial": 0.7,
        "manual": 0.7,
        "faq_oficial": 0.5,
        "comunicado": 0.4,
        "blog": 0.0,
        "articulo_opinion": 0.0,
    }

    @classmethod
    def get_weight(cls, source_type: str) -> float:
        """Obtiene el peso de autoridad para un tipo de fuente"""
        normalized = source_type.lower().replace(" ", "_")
        return cls.WEIGHTS.get(normalized, 0.5)

    @classmethod
    def is_excluded(cls, source_type: str) -> bool:
        """Determina si la fuente debe ser excluida"""
        return cls.get_weight(source_type) == 0.0
