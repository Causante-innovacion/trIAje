"""
RAG Module - Contradiction Detector
Detecta conflictos entre chunks recuperados.

Según spec, si dos chunks top tienen conflicto:
- contradiction_flag = true
- confidence ↓
- auto_escalation = true
- advisor_package_trigger = true
"""

from typing import List, Dict, Any, Tuple
from pydantic import BaseModel
from .interfaces import RetrievedChunk


class ContradictionPair(BaseModel):
    """Par de chunks contradictorios"""
    chunk_a_id: str
    chunk_a_content: str
    chunk_a_source: str

    chunk_b_id: str
    chunk_b_content: str
    chunk_b_source: str

    conflict_type: str  # "direct", "implicit", "temporal"
    description: str
    confidence: float


class ContradictionResult(BaseModel):
    """Resultado del análisis de contradicciones"""
    has_contradictions: bool
    contradictions: List[ContradictionPair]
    confidence_penalty: float  # Cuánto reducir el confidence
    requires_escalation: bool


class ContradictionDetector:
    """
    Detecta contradicciones entre chunks de evidencia.
    """

    # Patrones de contradicción conocidos
    CONTRADICTION_PATTERNS = [
        # (patrón_a, patrón_b, tipo, descripción)
        ("obligatorio", "opcional", "direct", "Conflicto sobre obligatoriedad"),
        ("prohibido", "permitido", "direct", "Conflicto sobre permisibilidad"),
        ("exento", "sujeto a", "direct", "Conflicto sobre exención"),
        ("no requiere", "requiere", "direct", "Conflicto sobre requisitos"),
        ("derogado", "vigente", "temporal", "Posible norma derogada"),
    ]

    def __init__(self, check_top_n: int = 5):
        """
        Args:
            check_top_n: Número de chunks top a verificar por contradicciones
        """
        self.check_top_n = check_top_n

    def detect(self, chunks: List[RetrievedChunk]) -> ContradictionResult:
        """
        Analiza los chunks top por contradicciones.
        """
        contradictions = []

        # Solo analizar los top N chunks
        top_chunks = chunks[:self.check_top_n]

        # Comparar pares de chunks
        for i, chunk_a in enumerate(top_chunks):
            for chunk_b in top_chunks[i + 1:]:
                contradiction = self._check_pair(chunk_a, chunk_b)
                if contradiction:
                    contradictions.append(contradiction)

        has_contradictions = len(contradictions) > 0

        # Calcular penalización de confidence
        penalty = self._calculate_penalty(contradictions)

        return ContradictionResult(
            has_contradictions=has_contradictions,
            contradictions=contradictions,
            confidence_penalty=penalty,
            requires_escalation=has_contradictions,
        )

    def _check_pair(
        self,
        chunk_a: RetrievedChunk,
        chunk_b: RetrievedChunk
    ) -> ContradictionPair | None:
        """
        Verifica si dos chunks tienen información contradictoria.
        """
        content_a = chunk_a.content.lower()
        content_b = chunk_b.content.lower()

        for pattern_a, pattern_b, conflict_type, description in self.CONTRADICTION_PATTERNS:
            # Verificar si hay contradicción
            if (pattern_a in content_a and pattern_b in content_b) or \
               (pattern_b in content_a and pattern_a in content_b):

                # Calcular confidence de la detección
                confidence = self._calculate_detection_confidence(
                    chunk_a, chunk_b, pattern_a, pattern_b
                )

                if confidence > 0.5:  # Threshold para reportar
                    return ContradictionPair(
                        chunk_a_id=chunk_a.chunk_id,
                        chunk_a_content=chunk_a.content[:200] + "...",
                        chunk_a_source=chunk_a.metadata.title,
                        chunk_b_id=chunk_b.chunk_id,
                        chunk_b_content=chunk_b.content[:200] + "...",
                        chunk_b_source=chunk_b.metadata.title,
                        conflict_type=conflict_type,
                        description=description,
                        confidence=confidence,
                    )

        # Verificar contradicción temporal (fechas)
        temporal = self._check_temporal_contradiction(chunk_a, chunk_b)
        if temporal:
            return temporal

        return None

    def _calculate_detection_confidence(
        self,
        chunk_a: RetrievedChunk,
        chunk_b: RetrievedChunk,
        pattern_a: str,
        pattern_b: str
    ) -> float:
        """
        Calcula qué tan seguro estamos de la contradicción.
        """
        # Factores que aumentan confidence:
        # 1. Ambos chunks tienen alta autoridad
        # 2. Ambos chunks hablan del mismo tema
        # 3. Los patrones están en contextos similares

        authority_factor = (
            chunk_a.metadata.authority_level +
            chunk_b.metadata.authority_level
        ) / 2

        # Si ambos son de alta autoridad, la contradicción es más seria
        return min(authority_factor, 0.9)

    def _check_temporal_contradiction(
        self,
        chunk_a: RetrievedChunk,
        chunk_b: RetrievedChunk
    ) -> ContradictionPair | None:
        """
        Verifica si hay contradicción por temporalidad (norma más nueva vs antigua).
        """
        date_a = chunk_a.metadata.validity_date
        date_b = chunk_b.metadata.validity_date

        if not date_a or not date_b:
            return None

        # Si hablan del mismo tema pero tienen fechas muy diferentes
        # y contenido diferente, podría haber una norma que deroga otra
        # Esta es una heurística simple - en producción usar NLP más sofisticado

        return None  # Por ahora no implementamos detección temporal automática

    def _calculate_penalty(self, contradictions: List[ContradictionPair]) -> float:
        """
        Calcula penalización de confidence basada en contradicciones.
        """
        if not contradictions:
            return 0.0

        # Penalización base por tener contradicciones
        base_penalty = 0.2

        # Penalización adicional por cada contradicción
        additional = len(contradictions) * 0.1

        # Penalización por contradicciones de alta confidence
        high_conf_penalty = sum(
            0.1 for c in contradictions if c.confidence > 0.7
        )

        return min(base_penalty + additional + high_conf_penalty, 0.5)
