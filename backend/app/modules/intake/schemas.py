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
    """Opciones válidas para cada campo del intake V2"""

    # Bloque 1: Identidad
    IDENTITY_V2 = [
        "Organización formal (Asociación o Fundación): Sin fines de lucro; el dinero se reinvierte en el objeto social.",
        "Empresa (SAC, SA, SRL, EIRL): Con fines de lucro; el objetivo es generar utilidades para los socios.",
        "Colectivo o Grupo: Iniciativa no formalizada (sin personería jurídica ante SUNARP)."
    ]

    ORG_PURPOSES = [
        "Educativo",
        "Cultural",
        "Ambiental",
        "Asistencial / Social",
        "Tecnológico / Innovación",
        "Otro"
    ]

    # Bloque 2: SUNAT
    SUNAT_V2 = [
        "Tengo RUC y está al día: Emito comprobantes y mis declaraciones están vigentes.",
        "Tengo RUC, pero está pausado o con problemas: Estado 'Suspendido', 'Baja de Oficio' o figura como 'No Habido'.",
        "No tengo RUC: Somos un colectivo o aún no iniciamos trámites ante impuestos.",
        "No estoy seguro: Existe un número de RUC pero desconozco la situación legal actual."
    ]

    # Bloque 3: Fondos y Cooperación
    FUNDS_V2 = [
        "No recibo fondos externos (Solo recibo dinero de ingresos propios o locales).",
        "Sí, y estamos registrados ante APCI (Vigente).",
        "Sí, pero no tenemos registro ante APCI o está vencido."
    ]

    # Bloque 4: RRHH
    HIRING_V2 = [
        "Personal en Planilla (Contrato de trabajo).",
        "Locación de Servicios (Recibos por Honorarios).",
        "Voluntariado (Bajo la Ley de Voluntariado).",
        "Practicantes (Modalidades formativas).",
        "Solo gestión de fundadores (Sin pagos externos)."
    ]

    # Bloque 5: Intangibles
    INTANGIBLES_V2 = [
        "Software propio o desarrollado por terceros.",
        "Bases de datos de usuarios o beneficiarios.",
        "Marcas, logotipos o símbolos distintivos.",
        "Ninguno de los anteriores."
    ]

    # Bloque 6: Urgencia
    URGENCY_V2 = [
        "Urgente: Tengo un plazo que vence pronto o recibí una notificación/demanda formal.",
        "Medio: Es para planeamiento, prevención o proyectos que recién van a empezar.",
        "Informativa: Solo estoy explorando el sistema o quiero aprender sobre el tema."
    ]

    # Tool-specific: Evaluación (se mantienen o ajustan si es necesario)
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
    identity_v2: str | None = None
    org_purpose: str | None = None
    org_purpose_other: str | None = None


class SunatData(BaseModel):
    """Bloque 2: Situación Tributaria (SUNAT)"""
    sunat_v2: str | None = None


class FundsData(BaseModel):
    """Bloque 3: Fondos y Cooperación"""
    funds_v2: str | None = None


class HumanResourcesData(BaseModel):
    """Bloque 4: Recursos Humanos"""
    hiring_v2: list[str] = Field(default_factory=list)


class IntangiblesData(BaseModel):
    """Bloque 5: Activos e Intangibles"""
    intangibles_v2: list[str] = Field(default_factory=list)


class UrgencyData(BaseModel):
    """Bloque 6: Nivel de Urgencia"""
    urgency_v2: str | None = None


class LegalProfile(BaseModel):
    """Ficha Legal Mínima completa V2"""
    identity: IdentityData = Field(default_factory=IdentityData)
    sunat: SunatData = Field(default_factory=SunatData)
    funds: FundsData = Field(default_factory=FundsData)
    human_resources: HumanResourcesData = Field(default_factory=HumanResourcesData)
    intangibles: IntangiblesData = Field(default_factory=IntangiblesData)
    urgency: UrgencyData = Field(default_factory=UrgencyData)


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


# =============================================================================
# MULTI-ORGANIZACIÓN - Soporte para proyectos con 1-3 organizaciones
# =============================================================================

class OrganizationRole(str, Enum):
    """Roles posibles de una organización en el proyecto"""
    MAIN_EXECUTOR = "Ejecutor principal"
    CO_EXECUTOR = "Co-ejecutor"
    FUNDER = "Financiador"
    PARTNER = "Aliado estratégico"
    BENEFICIARY = "Beneficiario"


class OrganizationProfile(BaseModel):
    """Perfil completo de una organización (Ficha Legal + metadata)"""
    id: str
    name: str
    role: OrganizationRole | str = OrganizationRole.MAIN_EXECUTOR
    legal_profile: LegalProfile


class ProjectInfo(BaseModel):
    """Información del proyecto"""
    id: str | None = None
    name: str | None = None
    description: str | None = None


class ProjectIntakeRequest(BaseModel):
    """
    Request para intake de proyecto con múltiples organizaciones.
    Soporta de 1 a 3 organizaciones por proyecto.
    """
    tool: ToolType
    project: ProjectInfo | None = None
    organizations: list[OrganizationProfile] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Lista de organizaciones (1-3)"
    )
    tool_specific: ToolSpecificData

    # Metadata
    session_id: str | None = None


class OrganizationRiskAssessment(BaseModel):
    """Evaluación de riesgo para una organización específica"""
    organization_id: str
    organization_name: str
    risk_level: RiskLevel = RiskLevel.LOW
    signals: list[RiskSignal] = Field(default_factory=list)


class ProjectRiskAssessment(BaseModel):
    """Evaluación de riesgo agregada del proyecto"""
    overall_risk_level: RiskLevel = RiskLevel.LOW
    derivation_color: DerivationColor = DerivationColor.GREEN
    derivation_required: bool = False

    # Riesgos por organización
    organization_risks: list[OrganizationRiskAssessment] = Field(default_factory=list)

    # Riesgos compartidos/interacción
    shared_signals: list[RiskSignal] = Field(default_factory=list)
    shared_reasons: list[str] = Field(default_factory=list)

    # Intenciones detectadas
    detected_intentions: list[str] = Field(default_factory=list)


class NormalizedProjectIntake(BaseModel):
    """Datos normalizados del proyecto para procesamiento por IA"""
    tool: ToolType

    # Info del proyecto
    project: ProjectInfo | None = None

    # Organizaciones con sus fichas legales
    organizations: list[OrganizationProfile]

    # Datos específicos de herramienta
    tool_specific: ToolSpecificData

    # Evaluación de riesgo agregada
    risk_assessment: ProjectRiskAssessment

    # Metadata
    session_id: str | None = None
    intake_timestamp: datetime = Field(default_factory=datetime.utcnow)
    intake_version: str = "2.0"
    jurisdiction: str = "PE"
    total_organizations: int = 1


class ProjectValidationError(BaseModel):
    """Error de validación para proyecto multi-organización"""
    organization_id: str | None = None  # None si es error del proyecto
    organization_name: str | None = None
    field: str
    message: str
    block: str | None = None


class ProjectValidationResponse(BaseModel):
    """Response de validación para proyecto multi-organización"""
    valid: bool
    errors: list[ProjectValidationError] = Field(default_factory=list)
    warnings: list[ValidationWarning] = Field(default_factory=list)
    risk_assessment: ProjectRiskAssessment = Field(default_factory=ProjectRiskAssessment)

    # Datos normalizados si es válido (listos para enviar a IA)
    normalized_data: NormalizedProjectIntake | None = None
