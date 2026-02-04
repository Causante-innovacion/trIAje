"""
Intake Module - Schemas
Tipos de entrada permitidos y estructuras de datos para la Ficha Legal Mínima
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS Y TIPOS BASE
# =============================================================================

class InputType(str, Enum):
    """Tipos de entrada permitidos según spec"""
    BOOLEAN = "boolean"
    ENUM = "enum"
    MULTI_SELECT = "multi_select"
    RANGE = "range"
    ROLE_SELECTOR = "role_selector"
    TEXT = "text"  # Solo para campos no críticos (ej: pregunta específica en Query)


class ToolType(str, Enum):
    """Tipos de herramientas disponibles"""
    EVALUATION = "evaluation"
    COMPLIANCE = "compliance"
    QUERY = "query"


class RiskLevel(str, Enum):
    """Niveles de riesgo"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DerivationColor(str, Enum):
    """Colores de derivación según documentación legal"""
    GREEN = "green"    # Respuesta estándar
    YELLOW = "yellow"  # Requiere prudencia, posible derivación
    RED = "red"        # Derivación inmediata a abogado


# =============================================================================
# OPCIONES VÁLIDAS (Constantes para validación)
# =============================================================================

class ValidOptions:
    """Opciones válidas para cada campo del intake"""

    # Identidad
    ORG_TYPES = [
        "Asociación",
        "Fundación",
        "ONG",
        "Empresa",
        "Colectivo / iniciativa no formalizada",
        "Otro"
    ]

    ORG_PURPOSES = [
        "Educativo",
        "Cultural",
        "Ambiental",
        "Asistencial / social",
        "Tecnológico / innovación",
        "Otro"
    ]

    # Formalización
    YES_NO_IN_PROGRESS = ["Sí", "No", "En trámite"]
    RUC_STATUS = ["Lo tengo", "No lo tengo", "En trámite"]
    SPECIAL_REGISTRIES = ["APCI", "Exonerada de Impuesto a la renta", "Ninguno"]

    # Cooperación Internacional
    APCI_STATUS = ["Registrado", "Necesita registro", "No aplica"]

    # Ingresos
    INCOME_SOURCES = [
        "Donaciones",
        "Venta de servicios o productos",
        "Fondos públicos",
        "Fondos privados",
        "Cooperación internacional",
        "Aún no recibe ingresos"
    ]

    # RRHH
    HIRING_MODALITIES = [
        "Planilla",
        "Locación de servicios",
        "Voluntariado",
        "Prácticas",
        "Ninguno"
    ]
    YES_NO_NA = ["Sí", "No", "No aplica"]

    # Contable
    ACCOUNTING_STATUS = ["Sí, completos", "Sí, parciales", "No", "En proceso"]
    AVAILABLE_DOCUMENTS = [
        "Estatuto o acta de constitución",
        "Libros de actas",
        "Estados financieros",
        "Memorias anuales",
        "Plan de uso de fondos",
        "Ninguno"
    ]

    # Intangibles
    INTANGIBLE_ASSETS = [
        "Software propio",
        "Software de terceros",
        "Bases de datos de usuarios",
        "Marca o símbolos distintivos",
        "Contenido con derechos de autor",
        "Ninguno"
    ]

    # Tool-specific: Evaluación
    EVALUATION_GOALS = [
        "Viabilidad legal del proyecto",
        "Identificación de riesgos",
        "Brechas regulatorias",
        "Análisis tributario",
        "Evaluación general"
    ]

    LEGAL_AREAS = [
        "Tributario",
        "Cooperación internacional (APCI)",
        "Laboral",
        "Propiedad intelectual",
        "Contratos",
        "Formalización",
        "Gobernanza"
    ]

    URGENCY_LEVELS = [
        "Inmediato (días)",
        "Corto plazo (semanas)",
        "Mediano plazo (meses)",
        "Solo planificación"
    ]

    # Tool-specific: Compliance
    COMPLIANCE_GOALS = [
        "Formalizar la organización",
        "Registrar en APCI",
        "Cumplir obligaciones SUNAT",
        "Regularizar situación laboral",
        "Obtener exoneración de IR",
        "Inscribirse como receptora de donaciones"
    ]

    TIMELINE_OPTIONS = [
        "Lo antes posible",
        "1-3 meses",
        "3-6 meses",
        "Sin prisa específica"
    ]

    # Tool-specific: Query
    QUERY_AREAS = [
        "Formalización y registros",
        "Tributación",
        "Contratación de personal",
        "Cooperación internacional",
        "Propiedad intelectual",
        "Donaciones",
        "Gobernanza",
        "Otro"
    ]


# =============================================================================
# DEFINICIÓN DE PREGUNTAS
# =============================================================================

class QuestionDefinition(BaseModel):
    """Definición de una pregunta del intake"""
    id: str
    text: str
    input_type: InputType
    required: bool = True
    options: list[str] | None = None
    range_min: int | None = None
    range_max: int | None = None
    help_text: str | None = None
    depends_on: dict[str, Any] | None = None  # {"field": "value"} para mostrar condicionalmente
    block: str | None = None  # Bloque al que pertenece
    order: int = 0  # Orden dentro del bloque


class QuestionBlock(BaseModel):
    """Bloque de preguntas relacionadas"""
    id: str
    name: str
    description: str | None = None
    icon: str | None = None
    order: int = 0
    questions: list[QuestionDefinition] = Field(default_factory=list)


class QuestionSet(BaseModel):
    """Conjunto completo de preguntas para intake"""
    tool: ToolType
    tool_name: str
    blocks: list[QuestionBlock]
    version: str = "1.0"
    total_questions: int = 0


# =============================================================================
# FICHA LEGAL MÍNIMA - Estructura de datos
# =============================================================================

class IdentityData(BaseModel):
    """Bloque 1: Identidad y naturaleza de la organización"""
    org_type: str | None = None
    org_type_other: str | None = None
    org_purpose: str | None = None
    org_purpose_other: str | None = None
    seeks_profits: bool | None = None


class FormalizationData(BaseModel):
    """Bloque 2: Nivel de formalización"""
    has_legal_status: str | None = None  # Sí/No/En trámite
    ruc_status: str | None = None  # Lo tengo/No lo tengo/En trámite
    special_registries: list[str] = Field(default_factory=list)


class IncomeData(BaseModel):
    """Bloque 3: Fuentes de ingreso y manejo de fondos"""
    handles_money: bool | None = None
    receives_foreign_funds: bool | None = None
    income_sources: list[str] = Field(default_factory=list)


class InternationalCooperationData(BaseModel):
    """Bloque 4: Cooperación internacional"""
    receives_international_cooperation: bool | None = None
    apci_status: str | None = None  # Registrado/Necesita registro/No aplica


class HumanResourcesData(BaseModel):
    """Bloque 5: Recursos humanos"""
    hiring_modalities: list[str] = Field(default_factory=list)
    contracts_valid: str | None = None  # Sí/No/No aplica


class AccountingData(BaseModel):
    """Bloque 6: Información contable y administrativa"""
    has_accounting_records: str | None = None  # Sí, completos/Sí, parciales/No/En proceso
    available_documents: list[str] = Field(default_factory=list)


class GovernanceData(BaseModel):
    """Bloque 7: Gobernanza y representación"""
    has_governance_bodies: bool | None = None
    has_legal_representative: str | None = None  # Sí/No/En trámite


class IntangiblesData(BaseModel):
    """Bloque 8: Uso de intangibles y datos"""
    intangible_assets: list[str] = Field(default_factory=list)


class LegalProfile(BaseModel):
    """Ficha Legal Mínima completa"""
    identity: IdentityData = Field(default_factory=IdentityData)
    formalization: FormalizationData = Field(default_factory=FormalizationData)
    income: IncomeData = Field(default_factory=IncomeData)
    international_cooperation: InternationalCooperationData = Field(
        default_factory=InternationalCooperationData
    )
    human_resources: HumanResourcesData = Field(default_factory=HumanResourcesData)
    accounting: AccountingData = Field(default_factory=AccountingData)
    governance: GovernanceData = Field(default_factory=GovernanceData)
    intangibles: IntangiblesData = Field(default_factory=IntangiblesData)


# =============================================================================
# PREGUNTAS ESPECÍFICAS POR HERRAMIENTA
# =============================================================================

class EvaluationSpecificData(BaseModel):
    """Preguntas específicas para Evaluación"""
    evaluation_goals: list[str] = Field(default_factory=list)
    legal_areas: list[str] = Field(default_factory=list)
    urgency: str | None = None


class ComplianceSpecificData(BaseModel):
    """Preguntas específicas para Compliance"""
    compliance_goal: str | None = None
    timeline: str | None = None


class QuerySpecificData(BaseModel):
    """Preguntas específicas para Query"""
    query_area: str | None = None
    specific_question: str | None = None  # Única excepción de free text


class ToolSpecificData(BaseModel):
    """Datos específicos de herramienta (union)"""
    evaluation: EvaluationSpecificData | None = None
    compliance: ComplianceSpecificData | None = None
    query: QuerySpecificData | None = None


# =============================================================================
# REQUEST / RESPONSE
# =============================================================================

class IntakeRequest(BaseModel):
    """Request completo del intake"""
    tool: ToolType
    legal_profile: LegalProfile
    tool_specific: ToolSpecificData

    # Metadata
    session_id: str | None = None
    organization_id: str | None = None


class ValidationError(BaseModel):
    """Error de validación"""
    field: str
    message: str
    block: str | None = None


class ValidationWarning(BaseModel):
    """Warning de validación (no bloquea)"""
    field: str
    message: str
    severity: Literal["low", "medium"] = "low"


class RiskSignal(BaseModel):
    """Señal de riesgo detectada"""
    signal_type: str
    description: str
    source_field: str | None = None


class RiskAssessment(BaseModel):
    """Evaluación de riesgo del intake"""
    derivation_required: bool = False
    derivation_color: DerivationColor = DerivationColor.GREEN
    risk_level: RiskLevel = RiskLevel.LOW
    signals: list[RiskSignal] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class IntakeValidationResponse(BaseModel):
    """Response de validación del intake"""
    valid: bool
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[ValidationWarning] = Field(default_factory=list)
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)

    # Datos normalizados si es válido
    normalized_data: "NormalizedIntake | None" = None


class NormalizedIntake(BaseModel):
    """Datos normalizados del intake para procesamiento"""
    tool: ToolType

    # Ficha Legal Mínima normalizada
    legal_profile: LegalProfile

    # Datos específicos de herramienta
    tool_specific: ToolSpecificData

    # Riesgos detectados
    risk_assessment: RiskAssessment

    # Intenciones detectadas (según documentación legal)
    detected_intentions: list[str] = Field(default_factory=list)

    # Metadata
    session_id: str | None = None
    organization_id: str | None = None
    intake_timestamp: datetime = Field(default_factory=datetime.utcnow)
    intake_version: str = "2.0"
    jurisdiction: str = "PE"  # Default: Perú


# Actualizar forward reference
IntakeValidationResponse.model_rebuild()
