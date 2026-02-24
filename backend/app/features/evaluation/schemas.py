"""
Evaluation Feature - Schemas
Request/Response models para evaluación de proyectos multi-organización.
"""

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from app.modules.intake.schemas import (
    NormalizedProjectIntake,
    DerivationColor,
    RiskLevel,
)
from app.modules.legal_rules.schemas import (
    LegalIntention,
    GapSeverity,
)


# =============================================================================
# ENUMS
# =============================================================================

class ViabilityStatus(str, Enum):
    """Estado de viabilidad del proyecto"""
    VIABLE = "viable"
    VIABLE_WITH_CONDITIONS = "viable_with_conditions"
    NOT_VIABLE = "not_viable"
    REQUIRES_REVIEW = "requires_review"


class TrafficLight(str, Enum):
    """Semáforo de evaluación"""
    GREEN = "green"    # Viable, bajo riesgo
    YELLOW = "yellow"  # Viable con condiciones, riesgo medio
    RED = "red"        # No viable o requiere asesoría profesional


# =============================================================================
# REQUEST
# =============================================================================

class EvaluationRequest(BaseModel):
    """
    Request para evaluar un proyecto.
    Acepta el NormalizedProjectIntake completo.
    """
    intake: NormalizedProjectIntake = Field(
        ...,
        description="Datos normalizados del proyecto con 1-3 organizaciones"
    )

    # Opciones adicionales
    include_rag_justification: bool = Field(
        default=True,
        description="Si buscar justificación normativa vía RAG"
    )
    max_rag_queries: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Máximo de queries RAG para justificación"
    )


# =============================================================================
# RESPONSE - Componentes
# =============================================================================

class GapDetail(BaseModel):
    """Detalle de una brecha legal detectada"""
    id: str
    organization_id: str | None = None
    organization_name: str | None = None

    severity: GapSeverity
    intention: LegalIntention

    description: str
    impact: str
    recommendation: str

    # Justificación normativa (del RAG)
    legal_basis: list[str] = Field(default_factory=list)


class RequirementDetail(BaseModel):
    """Detalle de un requisito evaluado"""
    id: str
    name: str
    intention: LegalIntention
    status: str  # fulfilled, partial, not_fulfilled
    organization_id: str
    organization_name: str


class OrganizationEvaluation(BaseModel):
    """Evaluación de una organización específica"""
    organization_id: str
    organization_name: str
    role: str

    # Contadores
    requirements_fulfilled: int
    requirements_partial: int
    requirements_not_fulfilled: int

    # Gaps de esta org
    gaps: list[GapDetail]

    # Intenciones detectadas
    detected_intentions: list[LegalIntention]

    # Riesgo individual
    risk_level: RiskLevel


class RiskSummary(BaseModel):
    """Resumen de riesgo del proyecto"""
    overall_level: RiskLevel
    derivation_color: DerivationColor
    requires_professional_advice: bool
    professional_advice_reason: str | None = None

    # Factores de riesgo principales
    risk_factors: list[str] = Field(default_factory=list)


class EvidenceSource(BaseModel):
    """Fuente de evidencia normativa (del RAG)"""
    title: str
    authority_level: float
    url: str | None = None
    relevance: str  # Qué gap/requisito justifica


# =============================================================================
# RESPONSE - Principal
# =============================================================================

class EvaluationResponse(BaseModel):
    """
    Response completo de evaluación de proyecto.

    Estructura:
    1. Viabilidad general
    2. Semáforo (green/yellow/red)
    3. Evaluación por organización
    4. Gaps compartidos
    5. Riesgo agregado
    6. Próximos pasos
    7. Evidencia normativa
    8. Disclaimers
    """
    # Resultado principal
    viability: ViabilityStatus
    viability_explanation: str
    traffic_light: TrafficLight

    # Evaluación por organización
    organizations: list[OrganizationEvaluation] = Field(default_factory=list)

    # Gaps compartidos (interacción entre orgs)
    shared_gaps: list[GapDetail] = Field(default_factory=list)

    # Riesgo agregado
    risk_summary: RiskSummary

    # Contadores globales
    total_requirements: int = 0
    total_gaps: int = 0
    critical_gaps: int = 0

    # Intenciones del proyecto
    project_intentions: list[LegalIntention] = Field(default_factory=list)

    # Próximos pasos priorizados
    next_steps: list[str] = Field(default_factory=list)

    # Alternativas si no viable
    alternatives: list[str] = Field(default_factory=list)
    path_to_viability: str | None = None

    # Evidencia normativa (del RAG)
    evidence_sources: list[EvidenceSource] = Field(default_factory=list)

    # Metadatos
    confidence_level: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    # Sugerencia de paquete para asesor (cuando riesgo medio/alto o ambigüedad)
    suggest_adviser_package: bool = False
    adviser_package_reason: str | None = None

    # Disclaimers obligatorios
    disclaimers: list[str] = Field(default_factory=list)


# =============================================================================
# LEGACY - Para compatibilidad (deprecado)
# =============================================================================

class LegacyEvaluationRequest(BaseModel):
    """Request legacy - usar EvaluationRequest en su lugar"""
    organization_type: str
    has_legal_entity: bool
    project_areas: list[str]
    funding_source: str | None = None
    urgency: str | None = None
    project_description: str | None = None


class EvaluationQuestions(BaseModel):
    """Preguntas del intake para evaluación"""
    questions: list[dict[str, Any]]
    tool_id: int = 1
    tool_name: str = "Evaluar proyecto"
