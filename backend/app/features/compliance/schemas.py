"""
Compliance Feature - Schemas
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ComplianceRequest(BaseModel):
    """Request para ruta de cumplimiento"""
    compliance_goal: str = Field(..., description="Objetivo de cumplimiento")
    current_status: str = Field(..., description="Estado actual")
    organization_type: str = Field(..., description="Tipo de organización")
    timeline: str | None = Field(None, description="Plazo deseado")


class MilestoneResponse(BaseModel):
    """Un milestone en la ruta"""
    id: str
    name: str
    description: str
    phase: str
    status: str
    order: int
    prerequisites: List[str]
    authority: str | None = None
    documents_required: List[str]
    estimated_duration: str | None = None
    estimated_cost: str | None = None
    steps: List[str]


class ComplianceResponse(BaseModel):
    """Response con ruta de cumplimiento"""
    # Resumen
    total_milestones: int
    completed_milestones: int
    progress_percentage: float

    # Fases
    phases: List[Dict[str, Any]]

    # Próximos pasos
    next_milestones: List[MilestoneResponse]
    blocked_milestones: List[MilestoneResponse]

    # Estimaciones
    estimated_total_duration: str | None

    # Brechas
    gaps_to_resolve: int
    critical_gaps: List[str]

    # Metadata
    disclaimers: List[str]


class ComplianceQuestions(BaseModel):
    """Preguntas del intake"""
    questions: List[Dict[str, Any]]
    tool_id: int = 4
    tool_name: str = "Ruta de cumplimiento"
