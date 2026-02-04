"""
Evaluation Feature - Schemas
Request/Response models para evaluación de proyectos
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    """Request para evaluar un proyecto"""
    # Datos de organización
    organization_type: str = Field(..., description="Tipo de organización")
    has_legal_entity: bool = Field(..., description="¿Tiene personería jurídica?")

    # Datos del proyecto
    project_areas: List[str] = Field(..., description="Áreas legales del proyecto")
    funding_source: str | None = Field(None, description="Fuente de financiamiento")
    urgency: str | None = Field(None, description="Nivel de urgencia")

    # Descripción opcional
    project_description: str | None = Field(None, description="Descripción del proyecto")

    # Datos del Generador Cívico (opcional)
    civic_generator_output: Dict[str, Any] | None = Field(
        None, description="Salida del Generador Cívico si aplica"
    )


class GapSummary(BaseModel):
    """Resumen de una brecha"""
    requirement: str
    status: str
    priority: str


class RiskSummary(BaseModel):
    """Resumen de riesgo"""
    level: str
    factors: List[str]


class EvaluationResponse(BaseModel):
    """Response de evaluación"""
    # Resultado principal
    viability: str = Field(..., description="viable o inviable_with_alternatives")
    viability_explanation: str

    # Semáforo
    traffic_light: str = Field(..., description="green o yellow")

    # Análisis
    risk_assessment: RiskSummary
    gaps_found: List[GapSummary]
    conditions_evaluated: List[Dict[str, Any]]

    # Alternativas si aplica
    alternatives: List[str] = []
    path_to_viability: str | None = None

    # Próximos pasos
    next_steps: List[str]
    escalation_recommended: bool

    # Evidencia y metadata
    evidence_sources: List[Dict[str, str]] = []
    confidence_level: str
    assumptions: List[str]
    limitations: List[str]

    # Disclaimers
    disclaimers: List[str]


class EvaluationQuestions(BaseModel):
    """Preguntas del intake para evaluación"""
    questions: List[Dict[str, Any]]
    tool_id: int = 1
    tool_name: str = "Evaluar proyecto"
