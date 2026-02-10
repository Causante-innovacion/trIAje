"""
Legal Rules - Schemas
Estructuras de datos para el motor de reglas legales.
"""

from enum import Enum
from pydantic import BaseModel, Field


class LegalIntention(str, Enum):
    """
    Intenciones legales del GPT Legal (10 intenciones + sub-categorías internas).
    Basado en el documento de diseño del Primer Entregable.
    """
    # === 10 INTENCIONES PRINCIPALES (documento de diseño) ===

    # 1. Formalización y registros (constitución, RUC, SUNARP)
    FORMALIZATION = "formalization"

    # 2. Evaluación de viabilidad del proyecto (requisitos mínimos)
    VIABILITY_EVALUATION = "viability_evaluation"

    # 3. Financiamiento y tributación (IGV, IR, exoneraciones)
    TAXATION = "taxation"

    # 4. Contratación de personal (modalidades laborales, voluntariado)
    HIRING = "hiring"

    # 5. Cooperación y donaciones internacionales (APCI, beneficios fiscales)
    INTERNATIONAL_COOPERATION = "international_cooperation"

    # 6. Propiedad intelectual y contratos (software, marcas, datos personales)
    INTELLECTUAL_PROPERTY = "intellectual_property"

    # 7. Preparación de reuniones y documentación (actas, estatutos, memorias)
    MEETINGS_DOCUMENTATION = "meetings_documentation"

    # 8. Riesgos y gestión preventiva (riesgos fiscales, laborales, contractuales)
    RISK_MANAGEMENT = "risk_management"

    # 9. Registro como entidad receptora de donaciones (SUNAT, certificados)
    DONATIONS = "donations"

    # 10. Casos grises (situaciones complejas que requieren abogado)
    GREY_CASES = "grey_cases"

    # === SUB-CATEGORÍAS INTERNAS (usadas por reglas de negocio) ===
    GOVERNANCE = "governance"
    DATA_PROTECTION = "data_protection"
    ACCOUNTING = "accounting"
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
