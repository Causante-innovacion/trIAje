"""
Output Builder - Schema Binder
Estructuras de output por herramienta
"""

from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class OutputType(str, Enum):
    """Tipo de output"""
    EVALUATION = "evaluation"
    QUERY_RESPONSE = "query_response"
    ADVISOR_BRIEF = "advisor_brief"
    COMPLIANCE_ROUTE = "compliance_route"


class ViabilityIndicator(str, Enum):
    """Indicador de viabilidad según spec"""
    VIABLE = "viable"                      # 🟢
    INVIABLE_WITH_ALT = "inviable_with_alternatives"  # 🟡


class OutputSection(BaseModel):
    """Sección de un output"""
    title: str
    content: str
    order: int = 0
    is_conditional: bool = False  # True si usa lenguaje condicional


class EvidenceReference(BaseModel):
    """Referencia a evidencia"""
    doc_id: str
    title: str
    authority: str
    anchor: str | None = None
    url: str | None = None


class Disclaimer(BaseModel):
    """Disclaimer legal"""
    text: str
    type: str  # "legal", "limitation", "recommendation"
    prominent: bool = False  # Si debe mostrarse destacado


class ToolOutput(BaseModel):
    """Output completo de una herramienta"""
    output_type: OutputType
    tool_id: int

    # Resultado principal
    viability: ViabilityIndicator | None = None
    summary: str

    # Secciones de contenido
    sections: List[OutputSection] = []

    # Evidencia
    evidence: List[EvidenceReference] = []
    grounding_ratio: float = 0.0

    # Supuestos y limitaciones
    assumptions: List[str] = []
    limitations: List[str] = []

    # Disclaimers
    disclaimers: List[Disclaimer] = []

    # Flags de incertidumbre
    uncertainty_flags: Dict[str, bool] = {}

    # Alternativas (si aplica)
    alternatives: List[str] = []
    path_to_viability: str | None = None

    # Recomendaciones
    next_steps: List[str] = []
    escalation_recommended: bool = False

    # Metadata
    confidence_level: str = "MEDIUM"
    generated_at: str = datetime.utcnow().isoformat()
    version: str = "1.0"


class EvaluationOutput(ToolOutput):
    """Output específico para evaluación de proyecto"""
    output_type: OutputType = OutputType.EVALUATION

    # Campos específicos
    risk_level: str = "MEDIUM"
    gaps_found: int = 0
    critical_gaps: List[str] = []


class QueryOutput(ToolOutput):
    """Output específico para duda puntual"""
    output_type: OutputType = OutputType.QUERY_RESPONSE

    # Campos específicos
    direct_answer: str | None = None
    conditions: List[str] = []
    related_topics: List[str] = []


class AdvisorBriefOutput(ToolOutput):
    """Output específico para preparación de asesor"""
    output_type: OutputType = OutputType.ADVISOR_BRIEF

    # Campos específicos
    case_summary: str | None = None
    open_questions: List[str] = []
    documents_to_bring: List[str] = []
    advisor_type_recommended: str | None = None


class ComplianceRouteOutput(ToolOutput):
    """Output específico para ruta de cumplimiento"""
    output_type: OutputType = OutputType.COMPLIANCE_ROUTE

    # Campos específicos
    total_milestones: int = 0
    completed_milestones: int = 0
    progress_percentage: float = 0.0
    estimated_duration: str | None = None
