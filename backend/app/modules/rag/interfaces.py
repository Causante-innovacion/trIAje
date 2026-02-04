"""
RAG Module - Interfaces
Contratos y estructuras de datos para el motor RAG
"""

from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class IndexType(str, Enum):
    """Tipos de índice según spec"""
    NORMATIVE_PRIMARY = "normative_primary"         # Leyes, decretos supremos
    REGULATORY_SECONDARY = "regulatory_secondary"   # Reglamentos
    GUIDANCE_DOCS = "guidance_docs"                 # Guías oficiales
    AUTHORITY_FAQ = "authority_faq"                 # FAQs de autoridades
    CASE_INTERPRETATION = "case_interpretation"     # Opcional: jurisprudencia


class AuthorityLevel(float, Enum):
    """Peso de autoridad según spec"""
    LEY_DECRETO = 1.0
    REGLAMENTO = 0.9
    RESOLUCION = 0.8
    GUIA_OFICIAL = 0.7
    FAQ = 0.5
    BLOG = 0.0  # Excluido


class ChunkMetadata(BaseModel):
    """Metadata obligatoria para cada chunk según spec"""
    doc_id: str
    title: str
    source_type: IndexType
    authority_level: float = Field(ge=0.0, le=1.0)
    jurisdiction: str
    validity_date: str | None = None
    url: str | None = None
    anchor: str | None = None  # Artículo específico, e.g., "Art. 15"
    normative_weight: float = Field(default=1.0, ge=0.0, le=1.0)


class RetrievedChunk(BaseModel):
    """Chunk recuperado del vector store"""
    chunk_id: str
    content: str
    metadata: ChunkMetadata

    # Scores
    similarity_score: float = Field(ge=0.0, le=1.0)
    authority_score: float = Field(ge=0.0, le=1.0)
    recency_score: float = Field(ge=0.0, le=1.0)
    jurisdiction_score: float = Field(ge=0.0, le=1.0)
    term_density_score: float = Field(ge=0.0, le=1.0)
    composite_score: float = Field(ge=0.0, le=1.0)


class Evidence(BaseModel):
    """Evidencia para citation binding"""
    doc_id: str
    title: str
    authority: str
    url: str | None = None
    anchor: str | None = None
    retrieved_chunk_id: str
    relevance_score: float


class RAGConfig(BaseModel):
    """Configuración del motor RAG según spec"""
    top_k_initial: int = 20
    top_k_rerank: int = 8
    max_chunk_tokens: int = 600
    chunk_overlap: int = 120
    strictness: int = Field(default=3, ge=1, le=5)
    confidence_threshold: float = 0.65
    jurisdiction_filter: str = "PE"  # Perú por defecto

    # Weights para scoring compuesto
    weight_semantic: float = 0.35
    weight_authority: float = 0.25
    weight_recency: float = 0.15
    weight_jurisdiction: float = 0.15
    weight_term_density: float = 0.10


class RAGQuery(BaseModel):
    """Query para el motor RAG"""
    original_query: str
    expanded_terms: List[str] = []
    target_indices: List[IndexType] = [IndexType.NORMATIVE_PRIMARY, IndexType.REGULATORY_SECONDARY]
    jurisdiction: str = "PE"
    config: RAGConfig = Field(default_factory=RAGConfig)


class RAGResult(BaseModel):
    """Resultado del motor RAG"""
    query: RAGQuery
    chunks: List[RetrievedChunk] = []
    evidence: List[Evidence] = []

    # Scores y flags
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    has_contradictions: bool = False
    contradicting_chunks: List[Dict[str, Any]] = []

    # Grounding
    grounded_claims: List[Dict[str, Any]] = []
    ungrounded_claims: List[str] = []

    # Metadata
    indices_searched: List[str] = []
    chunks_before_filter: int = 0
    chunks_after_filter: int = 0
    processing_notes: List[str] = []

    def is_sufficient(self) -> bool:
        """Verifica si la evidencia es suficiente según threshold"""
        return self.confidence >= self.query.config.confidence_threshold

    def requires_escalation(self) -> bool:
        """Determina si requiere escalamiento humano"""
        return self.has_contradictions or not self.is_sufficient()
