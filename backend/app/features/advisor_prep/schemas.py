"""
Advisor Prep Feature - Schemas
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class AdvisorPrepRequest(BaseModel):
    """Request para preparar reunión con asesor"""
    advisor_type: str = Field(..., description="Tipo de asesor")
    meeting_goals: List[str] = Field(..., description="Objetivos de la reunión")
    organization_type: str = Field(..., description="Tipo de organización")
    has_legal_entity: bool | None = None
    main_concerns: str | None = Field(None, description="Preocupaciones principales")
    background: str | None = Field(None, description="Contexto del caso")


class AdvisorPrepResponse(BaseModel):
    """Response con paquete para asesor"""
    # Recomendación de asesor
    recommended_advisor_type: str
    advisor_type_reason: str

    # Resumen ejecutivo
    executive_summary: str
    meeting_objectives: List[str]

    # Issues identificados
    legal_issues: List[Dict[str, Any]]
    priority_issues: List[str]

    # Preguntas para el asesor
    questions_for_advisor: List[str]
    priority_questions: List[str]

    # Documentos
    documents_to_bring: List[str]
    documents_to_prepare: List[str]

    # Metadata
    generated_at: str
    limitations: List[str]


class AdvisorPrepQuestions(BaseModel):
    """Preguntas del intake"""
    questions: List[Dict[str, Any]]
    tool_id: int = 3
    tool_name: str = "Preparar reunión con asesor"
