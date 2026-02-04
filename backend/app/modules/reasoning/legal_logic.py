"""
Reasoning Module - Legal Logic
Estructuras para análisis legal
"""

from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel


class ConditionStatus(str, Enum):
    """Estado de una condición legal"""
    SATISFIED = "satisfied"
    NOT_SATISFIED = "not_satisfied"
    CONDITIONAL = "conditional"
    UNKNOWN = "unknown"


class Viability(str, Enum):
    """Viabilidad según spec"""
    VIABLE = "viable"              # 🟢 Viable en su forma actual
    INVIABLE_WITH_ALT = "inviable_with_alternatives"  # 🟡 Inviable + alternativas


class LegalCondition(BaseModel):
    """Una condición legal evaluada"""
    id: str
    description: str
    status: ConditionStatus
    source: str | None = None       # Documento/norma fuente
    anchor: str | None = None       # Artículo específico
    requirements: List[str] = []    # Requisitos para satisfacer
    notes: str | None = None


class ApplicabilityRow(BaseModel):
    """Fila de la matriz de aplicabilidad"""
    norm_id: str
    norm_name: str
    applies: bool
    reason: str
    conditions: List[str] = []


class ApplicabilityMatrix(BaseModel):
    """Matriz de aplicabilidad de normas"""
    rows: List[ApplicabilityRow] = []

    def get_applicable_norms(self) -> List[ApplicabilityRow]:
        return [r for r in self.rows if r.applies]

    def get_non_applicable_norms(self) -> List[ApplicabilityRow]:
        return [r for r in self.rows if not r.applies]


class DecisionConstraint(BaseModel):
    """Restricción para la toma de decisión"""
    constraint_type: str  # "blocking", "warning", "recommendation"
    description: str
    source: str | None = None
    alternatives: List[str] = []


class ReasoningResult(BaseModel):
    """Resultado del análisis de razonamiento"""
    viability: Viability
    viability_explanation: str

    legal_conditions: List[LegalCondition] = []
    applicability_matrix: ApplicabilityMatrix = ApplicabilityMatrix()
    decision_constraints: List[DecisionConstraint] = []

    # Alternativas si es inviable
    alternatives: List[str] = []
    path_to_viability: str | None = None

    # Supuestos y limitaciones
    assumptions: List[str] = []
    limitations: List[str] = []

    # Metadata
    confidence_level: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    requires_validation: bool = False
    escalation_recommended: bool = False
