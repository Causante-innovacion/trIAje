"""
RAG Module - Normative Filter
Filtrado de chunks según criterios de calidad.

Según spec, se eliminan chunks si:
- no_authority
- no_date
- no_jurisdiction
- unverified_source
"""

from typing import List, Tuple
from .interfaces import RetrievedChunk, IndexType


class FilterResult:
    """Resultado del filtrado"""

    def __init__(self):
        self.accepted: List[RetrievedChunk] = []
        self.rejected: List[Tuple[RetrievedChunk, str]] = []  # (chunk, reason)

    @property
    def accepted_count(self) -> int:
        return len(self.accepted)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)

    def rejection_reasons(self) -> List[str]:
        """Lista de razones únicas de rechazo"""
        return list(set(reason for _, reason in self.rejected))


class NormativeFilter:
    """
    Filtra chunks que no cumplen criterios de calidad normativa.
    """

    # Tipos de fuente excluidos
    EXCLUDED_SOURCE_TYPES = [
        "blog",
        "articulo_opinion",
        "foro",
        "comentario",
    ]

    # Authority mínima requerida
    MIN_AUTHORITY_LEVEL = 0.3

    def __init__(
        self,
        require_authority: bool = True,
        require_date: bool = False,  # Flexible para FAQs
        require_jurisdiction: bool = True,
        min_authority: float = 0.3,
    ):
        self.require_authority = require_authority
        self.require_date = require_date
        self.require_jurisdiction = require_jurisdiction
        self.min_authority = min_authority

    def filter(
        self,
        chunks: List[RetrievedChunk],
        target_jurisdiction: str = "PE"
    ) -> FilterResult:
        """
        Filtra chunks según criterios de calidad.
        """
        result = FilterResult()

        for chunk in chunks:
            rejection_reason = self._check_chunk(chunk, target_jurisdiction)

            if rejection_reason:
                result.rejected.append((chunk, rejection_reason))
            else:
                result.accepted.append(chunk)

        return result

    def _check_chunk(
        self,
        chunk: RetrievedChunk,
        target_jurisdiction: str
    ) -> str | None:
        """
        Verifica si un chunk debe ser rechazado.
        Retorna la razón de rechazo o None si es aceptado.
        """
        metadata = chunk.metadata

        # Check: authority level
        if self.require_authority:
            if metadata.authority_level < self.min_authority:
                return "no_authority"

            # Check: excluded source types
            source_type = metadata.source_type.value.lower()
            if any(excluded in source_type for excluded in self.EXCLUDED_SOURCE_TYPES):
                return "unverified_source"

        # Check: date (flexible)
        if self.require_date:
            if not metadata.validity_date:
                return "no_date"

        # Check: jurisdiction
        if self.require_jurisdiction:
            if not metadata.jurisdiction:
                return "no_jurisdiction"

            # Verificar match de jurisdicción
            if metadata.jurisdiction not in [target_jurisdiction, "INTERNATIONAL", "GENERAL"]:
                return f"wrong_jurisdiction:{metadata.jurisdiction}"

        return None

    def filter_by_index(
        self,
        chunks: List[RetrievedChunk],
        allowed_indices: List[IndexType]
    ) -> FilterResult:
        """
        Filtra chunks por tipo de índice.
        """
        result = FilterResult()

        for chunk in chunks:
            if chunk.metadata.source_type in allowed_indices:
                result.accepted.append(chunk)
            else:
                result.rejected.append(
                    (chunk, f"index_not_allowed:{chunk.metadata.source_type.value}")
                )

        return result

    def filter_duplicates(
        self,
        chunks: List[RetrievedChunk],
        similarity_threshold: float = 0.95
    ) -> List[RetrievedChunk]:
        """
        Elimina chunks duplicados o muy similares.
        Mantiene el de mayor score.
        """
        if not chunks:
            return []

        # Ordenar por score descendente
        sorted_chunks = sorted(
            chunks, key=lambda c: c.composite_score, reverse=True
        )

        unique = []
        seen_content_hashes = set()

        for chunk in sorted_chunks:
            # Hash simple del contenido
            content_hash = hash(chunk.content[:200].lower().strip())

            if content_hash not in seen_content_hashes:
                unique.append(chunk)
                seen_content_hashes.add(content_hash)

        return unique


class QualityScoreFilter:
    """
    Filtra chunks basado en scores de calidad.
    """

    def __init__(
        self,
        min_similarity: float = 0.3,
        min_composite: float = 0.4,
    ):
        self.min_similarity = min_similarity
        self.min_composite = min_composite

    def filter(self, chunks: List[RetrievedChunk]) -> FilterResult:
        """
        Filtra por scores mínimos.
        """
        result = FilterResult()

        for chunk in chunks:
            if chunk.similarity_score < self.min_similarity:
                result.rejected.append((chunk, "low_similarity"))
            elif chunk.composite_score < self.min_composite:
                result.rejected.append((chunk, "low_composite_score"))
            else:
                result.accepted.append(chunk)

        return result
