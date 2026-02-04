"""
RAG Module - Grounding
Grounding obligatorio: cada afirmación debe mapearse a evidencia.

Regla dura según spec:
claim_allowed ONLY IF claim → grounded_in_chunk == true

Cada afirmación debe mapearse a:
- chunk_id
- doc_id
- authority
- article_anchor
"""

from typing import List, Dict, Any, Tuple
from pydantic import BaseModel
from .interfaces import RetrievedChunk, Evidence


class GroundedClaim(BaseModel):
    """Una afirmación con su evidencia de respaldo"""
    claim_text: str
    chunk_id: str
    doc_id: str
    authority: str
    anchor: str | None = None
    confidence: float
    is_grounded: bool = True


class UngroundedClaim(BaseModel):
    """Una afirmación sin evidencia suficiente"""
    claim_text: str
    reason: str
    attempted_chunks: List[str] = []


class GroundingResult(BaseModel):
    """Resultado del proceso de grounding"""
    grounded_claims: List[GroundedClaim]
    ungrounded_claims: List[UngroundedClaim]
    grounding_ratio: float  # grounded / total
    all_claims_grounded: bool


class ClaimGrounder:
    """
    Verifica que las afirmaciones estén respaldadas por evidencia.
    """

    def __init__(self, min_confidence: float = 0.6):
        self.min_confidence = min_confidence

    def ground_claims(
        self,
        claims: List[str],
        chunks: List[RetrievedChunk]
    ) -> GroundingResult:
        """
        Intenta mapear cada afirmación a un chunk de evidencia.

        Args:
            claims: Lista de afirmaciones a verificar
            chunks: Chunks recuperados del RAG

        Returns:
            GroundingResult con claims grounded y ungrounded
        """
        grounded = []
        ungrounded = []

        for claim in claims:
            result = self._find_grounding(claim, chunks)

            if result:
                grounded.append(result)
            else:
                ungrounded.append(UngroundedClaim(
                    claim_text=claim,
                    reason="No se encontró evidencia suficiente",
                    attempted_chunks=[c.chunk_id for c in chunks[:5]],
                ))

        total = len(claims) if claims else 1
        ratio = len(grounded) / total

        return GroundingResult(
            grounded_claims=grounded,
            ungrounded_claims=ungrounded,
            grounding_ratio=ratio,
            all_claims_grounded=len(ungrounded) == 0,
        )

    def _find_grounding(
        self,
        claim: str,
        chunks: List[RetrievedChunk]
    ) -> GroundedClaim | None:
        """
        Busca el mejor chunk que respalde una afirmación.
        """
        claim_lower = claim.lower()
        best_match: Tuple[RetrievedChunk | None, float] = (None, 0.0)

        for chunk in chunks:
            # Calcular relevancia del chunk para esta claim
            relevance = self._calculate_claim_chunk_relevance(
                claim_lower, chunk.content.lower()
            )

            # Ajustar por autoridad del chunk
            adjusted_relevance = relevance * chunk.metadata.authority_level

            if adjusted_relevance > best_match[1]:
                best_match = (chunk, adjusted_relevance)

        chunk, confidence = best_match

        if chunk and confidence >= self.min_confidence:
            return GroundedClaim(
                claim_text=claim,
                chunk_id=chunk.chunk_id,
                doc_id=chunk.metadata.doc_id,
                authority=f"{chunk.metadata.source_type.value} - {chunk.metadata.title}",
                anchor=chunk.metadata.anchor,
                confidence=confidence,
            )

        return None

    def _calculate_claim_chunk_relevance(
        self,
        claim: str,
        chunk_content: str
    ) -> float:
        """
        Calcula qué tan relevante es un chunk para una afirmación.
        Implementación simple basada en overlap de términos.
        """
        claim_words = set(claim.split())
        chunk_words = set(chunk_content.split())

        if not claim_words:
            return 0.0

        # Palabras comunes a ignorar
        stopwords = {
            "el", "la", "los", "las", "de", "del", "en", "a", "que",
            "y", "o", "un", "una", "es", "son", "para", "por", "con",
            "se", "su", "al", "lo", "como", "más", "pero", "sus",
        }

        claim_words = claim_words - stopwords
        chunk_words = chunk_words - stopwords

        if not claim_words:
            return 0.5  # Score neutro si solo había stopwords

        overlap = claim_words & chunk_words
        relevance = len(overlap) / len(claim_words)

        return min(relevance, 1.0)

    def build_evidence_list(
        self,
        grounded_claims: List[GroundedClaim],
        chunks: List[RetrievedChunk]
    ) -> List[Evidence]:
        """
        Construye la lista de evidencias para citation binding.
        """
        evidence_map: Dict[str, Evidence] = {}

        for claim in grounded_claims:
            # Encontrar el chunk correspondiente
            chunk = next(
                (c for c in chunks if c.chunk_id == claim.chunk_id),
                None
            )

            if chunk and claim.chunk_id not in evidence_map:
                evidence_map[claim.chunk_id] = Evidence(
                    doc_id=chunk.metadata.doc_id,
                    title=chunk.metadata.title,
                    authority=claim.authority,
                    url=chunk.metadata.url,
                    anchor=chunk.metadata.anchor,
                    retrieved_chunk_id=chunk.chunk_id,
                    relevance_score=claim.confidence,
                )

        return list(evidence_map.values())
