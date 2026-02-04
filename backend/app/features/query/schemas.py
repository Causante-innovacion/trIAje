"""
Query Feature - Schemas
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request para consulta puntual"""
    question: str = Field(..., min_length=10, description="Pregunta legal")
    query_area: str = Field(..., description="Área de la consulta")
    organization_type: str | None = Field(None, description="Tipo de organización")
    has_legal_entity: bool | None = Field(None, description="¿Tiene personería?")
    additional_context: str | None = Field(None, description="Contexto adicional")


class SourceReference(BaseModel):
    """Referencia a fuente"""
    title: str
    authority: str
    anchor: str | None = None


class QueryResponse(BaseModel):
    """Response de consulta"""
    # Respuesta principal
    answer: str
    answer_type: str  # "direct", "conditional", "orientation"

    # Condiciones si aplica
    conditions: List[str] = []
    depends_on: List[str] = []

    # Fuentes
    sources: List[SourceReference] = []

    # Metadata
    confidence_level: str
    requires_validation: bool

    # Recomendaciones
    related_topics: List[str] = []
    escalation_recommended: bool

    # Disclaimers
    disclaimers: List[str]


class QueryQuestions(BaseModel):
    """Preguntas del intake para consulta"""
    questions: List[Dict[str, Any]]
    tool_id: int = 2
    tool_name: str = "Duda puntual"
