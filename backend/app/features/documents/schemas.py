"""
Documents Feature - Schemas
Modelos para gestión de documentos RAG.
"""

from enum import Enum
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Tipos de documentos soportados"""
    NORMATIVE = "normative"           # Leyes, decretos, resoluciones
    REGULATORY = "regulatory"          # Reglamentos, directivas
    GUIDANCE = "guidance"              # Guías, manuales
    FAQ = "faq"                        # Preguntas frecuentes
    CASE = "case"                      # Casos, jurisprudencia
    ORGANIZATION = "organization"      # Documentos privados de org


class DocumentUploadRequest(BaseModel):
    """Request para subir un documento"""
    title: str = Field(..., description="Título del documento")
    content: str = Field(..., description="Contenido del documento")
    document_type: DocumentType = Field(..., description="Tipo de documento")
    organization_id: str | None = Field(
        None,
        description="ID de la organización (solo para docs privados)"
    )

    # Metadata legal
    authority_level: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Nivel de autoridad (0-1, donde 1 es máxima)"
    )
    jurisdiction: str = Field(default="PE", description="Jurisdicción (PE=Perú)")
    validity_date: str | None = Field(None, description="Fecha de vigencia (YYYY-MM-DD)")
    url: str | None = Field(None, description="URL de referencia")

    # Chunking options
    chunk_size: int = Field(default=600, description="Tamaño máximo de chunk (tokens)")
    chunk_overlap: int = Field(default=120, description="Overlap entre chunks")


class DocumentUploadResponse(BaseModel):
    """Response de carga de documento"""
    doc_id: str
    title: str
    chunks_created: int
    collection: str
    message: str


class DocumentSearchRequest(BaseModel):
    """Request para búsqueda RAG"""
    query: str = Field(..., description="Consulta de búsqueda")
    organization_id: str | None = Field(
        None,
        description="ID de la organización (busca en sus docs privados + normativa)"
    )
    top_k: int = Field(default=10, ge=1, le=50, description="Número de resultados")
    include_normativa: bool = Field(default=True, description="Incluir normativa compartida")


class ChunkResult(BaseModel):
    """Un chunk recuperado"""
    chunk_id: str
    content: str
    title: str
    source_type: str
    similarity_score: float
    authority_level: float
    jurisdiction: str
    url: str | None = None


class DocumentSearchResponse(BaseModel):
    """Response de búsqueda"""
    query: str
    results: list[ChunkResult]
    total_found: int
    collections_searched: list[str]


class CollectionStats(BaseModel):
    """Estadísticas de una colección"""
    name: str
    total_chunks: int
    metadata: dict


class RAGStatusResponse(BaseModel):
    """Estado del sistema RAG"""
    healthy: bool
    chroma_mode: str
    collections: list[CollectionStats]
    total_documents: int
