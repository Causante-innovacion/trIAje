"""
Legal Rules - Schemas
Estructuras de datos para el motor de reglas legales.
"""

from enum import Enum
from pydantic import BaseModel, Field


class LegalIntention(str, Enum):
    """
    Intenciones legales detectadas según documentación.
    Cada intención representa un área legal que requiere atención.
    """
    # Estructura y formalización
    FORMALIZATION = "formalization"
    GOVERNANCE = "governance"

    # Financiero / Tributario
    TAXATION = "taxation"
    DONATIONS = "donations"

    # Cooperación Internacional
    INTERNATIONAL_COOPERATION = "international_cooperation"

    # Laboral
    HIRING = "hiring"

    # Propiedad Intelectual
    INTELLECTUAL_PROPERTY = "intellectual_property"

    # Datos
    DATA_PROTECTION = "data_protection"

    # Contabilidad
    ACCOUNTING = "accounting"

    # Evaluación general
    VIABILITY_EVALUATION = "viability_evaluation"
    COMPLIANCE_ROUTE = "compliance_route"


class RequirementStatus(str, Enum):
    """Estado de cumplimiento de un requisito"""
    FULFILLED = "fulfilled"           # Cumplido
    PARTIALLY_FULFILLED = "partial"   # Parcialmente cumplido
    NOT_FULFILLED = "not_fulfilled"   # No cumplido
    NOT_APPLICABLE = "not_applicable" # No aplica
    UNKNOWN = "unknown"               # No se puede determinar


class GapSeverity(str, Enum):
    """Severidad de una brecha legal"""
    CRITICAL = "critical"    # Bloquea operación, riesgo legal alto
    HIGH = "high"            # Debe resolverse pronto
    MEDIUM = "medium"        # Importante pero no urgente
    LOW = "low"              # Recomendación de mejora


class LegalRequirement(BaseModel):
    """Un requisito legal específico"""
    id: str
    name: str
    description: str
    intention: LegalIntention
    status: RequirementStatus = RequirementStatus.UNKNOWN

    # Normativa relacionada (para RAG)
    related_laws: list[str] = Field(default_factory=list)

    # Documentos/acciones requeridas
    required_documents: list[str] = Field(default_factory=list)
    required_registrations: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)

    # Razón del estado
    status_reason: str | None = None


class LegalGap(BaseModel):
    """Una brecha legal detectada"""
    id: str
    requirement_id: str
    organization_id: str | None = None
    organization_name: str | None = None

    severity: GapSeverity
    intention: LegalIntention

    description: str
    impact: str
    recommendation: str

    # Para buscar en RAG
    rag_query_hint: str | None = None

    # Campos fuente que revelaron la brecha
    source_fields: list[str] = Field(default_factory=list)


class OrganizationRequirements(BaseModel):
    """Requisitos y brechas de una organización"""
    organization_id: str
    organization_name: str

    # Requisitos que aplican
    requirements: list[LegalRequirement] = Field(default_factory=list)

    # Brechas detectadas
    gaps: list[LegalGap] = Field(default_factory=list)

    # Intenciones detectadas
    detected_intentions: list[LegalIntention] = Field(default_factory=list)

    # Contadores
    fulfilled_count: int = 0
    gap_count: int = 0
    critical_gaps: int = 0


class LegalRequirementsResult(BaseModel):
    """Resultado completo del análisis de requisitos legales"""
    # Por organización
    organizations: list[OrganizationRequirements] = Field(default_factory=list)

    # Brechas compartidas (entre organizaciones)
    shared_gaps: list[LegalGap] = Field(default_factory=list)

    # Intenciones detectadas a nivel proyecto
    project_intentions: list[LegalIntention] = Field(default_factory=list)

    # Resumen
    total_requirements: int = 0
    total_gaps: int = 0
    critical_gaps: int = 0

    # Recomendación general
    requires_professional_advice: bool = False
    professional_advice_reason: str | None = None
