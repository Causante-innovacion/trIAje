"""
Milestone Engine - DAG Builder
Estructuras para construcción de rutas
"""

from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel


class MilestoneStatus(str, Enum):
    """Estado de un milestone"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class MilestoneType(str, Enum):
    """Tipo de milestone"""
    DOCUMENT = "document"       # Preparar documento
    PROCEDURE = "procedure"     # Trámite ante autoridad
    REGISTRATION = "registration"  # Inscripción/registro
    PAYMENT = "payment"         # Pago de tasas
    VERIFICATION = "verification"  # Verificación/validación


class Document(BaseModel):
    """Documento requerido para un milestone"""
    name: str
    description: str | None = None
    template_available: bool = False
    required: bool = True


class Authority(BaseModel):
    """Autoridad relacionada con un milestone"""
    name: str
    full_name: str | None = None
    website: str | None = None
    contact: str | None = None


class Milestone(BaseModel):
    """Un hito en la ruta de cumplimiento"""
    id: str
    name: str
    description: str
    milestone_type: MilestoneType
    status: MilestoneStatus = MilestoneStatus.PENDING

    # Dependencias
    prerequisites: List[str] = []  # IDs de milestones previos

    # Autoridad
    authority: Authority | None = None

    # Documentos
    documents_required: List[Document] = []

    # Estimaciones
    estimated_duration: str | None = None  # "1-2 semanas"
    estimated_cost: str | None = None      # "S/ 50-100"

    # Instrucciones
    steps: List[str] = []
    tips: List[str] = []
    warnings: List[str] = []

    # Metadata
    order: int = 0
    phase: str | None = None  # "Formalización", "Registro", etc.


class MilestoneDAG(BaseModel):
    """Grafo dirigido acíclico de milestones"""
    milestones: List[Milestone]
    edges: Dict[str, List[str]]  # {from_id: [to_ids]}

    def get_roots(self) -> List[Milestone]:
        """Obtiene milestones sin prerrequisitos"""
        return [m for m in self.milestones if not m.prerequisites]

    def get_children(self, milestone_id: str) -> List[Milestone]:
        """Obtiene milestones que dependen del dado"""
        child_ids = self.edges.get(milestone_id, [])
        return [m for m in self.milestones if m.id in child_ids]

    def get_by_phase(self, phase: str) -> List[Milestone]:
        """Obtiene milestones de una fase"""
        return [m for m in self.milestones if m.phase == phase]


class ExecutionPhase(BaseModel):
    """Fase de ejecución"""
    name: str
    order: int
    milestones: List[Milestone]
    description: str | None = None


class ExecutionSequence(BaseModel):
    """Secuencia de ejecución ordenada"""
    phases: List[ExecutionPhase]
    total_milestones: int
    completed_milestones: int = 0

    # Estimaciones totales
    estimated_total_duration: str | None = None
    estimated_total_cost: str | None = None

    # Próximos pasos
    next_milestones: List[Milestone] = []
    blocked_milestones: List[Milestone] = []

    def get_progress_percentage(self) -> float:
        if self.total_milestones == 0:
            return 0.0
        return (self.completed_milestones / self.total_milestones) * 100
