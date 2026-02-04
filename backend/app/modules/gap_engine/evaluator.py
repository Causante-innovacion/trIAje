"""
Gap Engine - Evaluator
Estructuras y lógica para evaluación de brechas
"""

from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel


class GapStatus(str, Enum):
    """Estado de una brecha según spec"""
    SATISFIED = "satisfied"       # Requisito cumplido
    MISSING = "missing"           # Requisito faltante
    CONDITIONAL = "conditional"   # Depende de condiciones
    BLOCKED = "blocked"           # Bloqueado por dependencia


class GapPriority(str, Enum):
    """Prioridad de resolver la brecha"""
    CRITICAL = "critical"     # Bloquea operación
    HIGH = "high"             # Importante resolver pronto
    MEDIUM = "medium"         # Resolver eventualmente
    LOW = "low"               # Nice to have


class Requirement(BaseModel):
    """Un requisito regulatorio"""
    id: str
    name: str
    description: str
    authority: str            # SUNAT, APCI, SUNARP, etc.
    legal_basis: str | None = None  # Ley o norma
    dependencies: List[str] = []     # IDs de requisitos previos


class Gap(BaseModel):
    """Una brecha identificada"""
    requirement_id: str
    requirement_name: str
    status: GapStatus
    priority: GapPriority

    # Detalles
    description: str
    authority: str
    legal_basis: str | None = None

    # Para resolver
    steps_to_resolve: List[str] = []
    estimated_documents: List[str] = []
    dependencies_pending: List[str] = []

    # Notas
    notes: str | None = None


class GapAnalysisResult(BaseModel):
    """Resultado del análisis de brechas"""
    total_requirements: int
    satisfied: int
    missing: int
    conditional: int
    blocked: int

    gaps: List[Gap] = []

    # Resumen
    critical_gaps: List[Gap] = []
    next_actions: List[str] = []

    # Metadata
    severity: str = "MEDIUM"  # HIGH, MEDIUM, LOW

    def get_gaps_by_status(self, status: GapStatus) -> List[Gap]:
        return [g for g in self.gaps if g.status == status]

    def get_gaps_by_priority(self, priority: GapPriority) -> List[Gap]:
        return [g for g in self.gaps if g.priority == priority]
