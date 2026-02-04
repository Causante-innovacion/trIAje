"""
RAG Module - Confidence Calculator
Calcula el RAG confidence score según spec:

confidence = coverage_score + authority_score + agreement_score + specificity_score

Usado para:
- traffic_light adjustment
- escalation trigger
- advisor package trigger
"""

from typing import List
from pydantic import BaseModel
from .interfaces import RetrievedChunk, RAGConfig


class ConfidenceBreakdown(BaseModel):
    """Desglose del score de confidence"""
    coverage_score: float      # Qué tan bien cubren los chunks la query
    authority_score: float     # Promedio de autoridad de los chunks
    agreement_score: float     # Qué tan consistentes son los chunks entre sí
    specificity_score: float   # Qué tan específicos son los chunks

    total: float
    threshold: float
    is_sufficient: bool


class RAGConfidenceCalculator:
    """
    Calcula el confidence score para resultados RAG.
    """

    # Pesos para cada componente
    WEIGHT_COVERAGE = 0.30
    WEIGHT_AUTHORITY = 0.30
    WEIGHT_AGREEMENT = 0.25
    WEIGHT_SPECIFICITY = 0.15

    def __init__(self, config: RAGConfig):
        self.config = config

    def calculate(
        self,
        chunks: List[RetrievedChunk],
        query_terms: List[str],
        has_contradictions: bool = False
    ) -> ConfidenceBreakdown:
        """
        Calcula el confidence score total.
        """
        if not chunks:
            return ConfidenceBreakdown(
                coverage_score=0.0,
                authority_score=0.0,
                agreement_score=0.0,
                specificity_score=0.0,
                total=0.0,
                threshold=self.config.confidence_threshold,
                is_sufficient=False,
            )

        coverage = self._calculate_coverage(chunks, query_terms)
        authority = self._calculate_authority(chunks)
        agreement = self._calculate_agreement(chunks, has_contradictions)
        specificity = self._calculate_specificity(chunks)

        total = (
            coverage * self.WEIGHT_COVERAGE +
            authority * self.WEIGHT_AUTHORITY +
            agreement * self.WEIGHT_AGREEMENT +
            specificity * self.WEIGHT_SPECIFICITY
        )

        return ConfidenceBreakdown(
            coverage_score=coverage,
            authority_score=authority,
            agreement_score=agreement,
            specificity_score=specificity,
            total=total,
            threshold=self.config.confidence_threshold,
            is_sufficient=total >= self.config.confidence_threshold,
        )

    def _calculate_coverage(
        self,
        chunks: List[RetrievedChunk],
        query_terms: List[str]
    ) -> float:
        """
        Calcula qué tan bien los chunks cubren los términos de la query.
        """
        if not query_terms:
            return 0.5  # Score neutro

        # Combinar contenido de todos los chunks
        all_content = " ".join(c.content.lower() for c in chunks)

        # Contar términos cubiertos
        covered = sum(
            1 for term in query_terms
            if term.lower() in all_content
        )

        return min(covered / len(query_terms), 1.0)

    def _calculate_authority(self, chunks: List[RetrievedChunk]) -> float:
        """
        Calcula el promedio ponderado de autoridad de los chunks.
        Los chunks con mayor similarity tienen más peso.
        """
        if not chunks:
            return 0.0

        weighted_sum = sum(
            c.metadata.authority_level * c.similarity_score
            for c in chunks
        )
        weight_total = sum(c.similarity_score for c in chunks)

        if weight_total == 0:
            return 0.0

        return weighted_sum / weight_total

    def _calculate_agreement(
        self,
        chunks: List[RetrievedChunk],
        has_contradictions: bool
    ) -> float:
        """
        Calcula qué tan consistentes son los chunks entre sí.
        Penaliza fuertemente si hay contradicciones.
        """
        if has_contradictions:
            return 0.3  # Penalización severa

        if len(chunks) < 2:
            return 0.7  # Score moderado con un solo chunk

        # Verificar que los chunks top tengan scores similares
        # Si hay mucha variación, puede indicar inconsistencia
        scores = [c.composite_score for c in chunks[:5]]

        if not scores:
            return 0.5

        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)

        # Menor varianza = mayor agreement
        agreement = max(0.0, 1.0 - (variance * 2))
        return agreement

    def _calculate_specificity(self, chunks: List[RetrievedChunk]) -> float:
        """
        Calcula qué tan específicos son los chunks (vs genéricos).
        Chunks con anchors específicos (Art. X) tienen mayor especificidad.
        """
        if not chunks:
            return 0.0

        # Contar chunks con anchor específico
        with_anchor = sum(
            1 for c in chunks
            if c.metadata.anchor is not None
        )

        # Contar chunks con alta autoridad
        high_authority = sum(
            1 for c in chunks
            if c.metadata.authority_level >= 0.8
        )

        anchor_ratio = with_anchor / len(chunks)
        authority_ratio = high_authority / len(chunks)

        return (anchor_ratio * 0.6 + authority_ratio * 0.4)

    def get_confidence_level(self, confidence: float) -> str:
        """
        Convierte score numérico a nivel descriptivo.
        """
        if confidence >= 0.8:
            return "HIGH"
        elif confidence >= self.config.confidence_threshold:
            return "MEDIUM"
        elif confidence >= 0.4:
            return "LOW"
        else:
            return "INSUFFICIENT"

    def should_escalate(self, confidence: float, has_contradictions: bool) -> bool:
        """
        Determina si se debe escalar a asesor humano.
        """
        if has_contradictions:
            return True
        if confidence < self.config.confidence_threshold:
            return True
        return False
