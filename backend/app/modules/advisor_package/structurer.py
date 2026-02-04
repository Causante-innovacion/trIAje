"""
Advisor Package - Structurer
Estructuras para paquete de asesor
"""

from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class AdvisorType(str, Enum):
    """Tipo de asesor recomendado"""
    TRIBUTARISTA = "abogado_tributarista"
    LABORALISTA = "abogado_laboralista"
    CORPORATIVO = "abogado_corporativo"
    CONTADOR = "contador"
    NOTARIO = "notario"
    GENERAL = "abogado_general"


class ExportFormat(str, Enum):
    """Formatos de exportación"""
    JSON = "json"
    PDF_READY = "pdf_ready"
    DOC_READY = "doc_ready"


class LegalIssue(BaseModel):
    """Issue legal identificado"""
    id: str
    title: str
    description: str
    severity: str  # "critical", "important", "informative"
    area: str  # Área legal
    questions_for_advisor: List[str] = []


class DocumentRequest(BaseModel):
    """Documento solicitado al usuario"""
    name: str
    description: str | None = None
    required: bool = True
    purpose: str | None = None


class OpenQuestion(BaseModel):
    """Pregunta abierta para el asesor"""
    question: str
    context: str | None = None
    priority: str = "normal"  # "high", "normal", "low"
    related_issue_id: str | None = None


class CaseStructure(BaseModel):
    """Estructura del caso para el asesor"""
    # Información básica
    organization_type: str | None = None
    organization_description: str | None = None
    has_legal_entity: bool | None = None

    # Contexto
    main_concern: str | None = None
    background: str | None = None
    timeline: str | None = None

    # Análisis previo
    preliminary_assessment: str | None = None
    identified_risks: List[str] = []
    identified_gaps: List[str] = []

    # Viabilidad
    viability_status: str | None = None
    alternatives_considered: List[str] = []


class AdvisorPackage(BaseModel):
    """Paquete completo para el asesor"""
    # Metadata
    generated_at: str = datetime.utcnow().isoformat()
    version: str = "1.0"
    format: ExportFormat = ExportFormat.JSON

    # Recomendación de asesor
    recommended_advisor_type: AdvisorType = AdvisorType.GENERAL
    advisor_type_reason: str | None = None

    # Estructura del caso
    case_structure: CaseStructure

    # Issues identificados
    legal_issues: List[LegalIssue] = []
    issues_by_severity: Dict[str, List[str]] = {}

    # Preguntas abiertas
    open_questions: List[OpenQuestion] = []
    priority_questions: List[str] = []

    # Documentos
    documents_to_bring: List[DocumentRequest] = []
    documents_to_prepare: List[DocumentRequest] = []

    # Brief ejecutivo
    executive_summary: str | None = None
    meeting_objectives: List[str] = []

    # Contexto adicional
    gpt_legal_analysis_notes: str | None = None
    limitations: List[str] = []

    def get_issues_by_area(self) -> Dict[str, List[LegalIssue]]:
        """Agrupa issues por área legal"""
        by_area: Dict[str, List[LegalIssue]] = {}
        for issue in self.legal_issues:
            if issue.area not in by_area:
                by_area[issue.area] = []
            by_area[issue.area].append(issue)
        return by_area
