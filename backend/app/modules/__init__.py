# GPT Legal - Sub-módulos canónicos
"""
Módulos compartidos reutilizables entre herramientas (modos).

Cada herramienta es un pipeline orquestado:

Tool = OrchestratedToolPipeline {
    intake_module
    validation_module
    legal_rules (Legal Requirements Resolver)  ← NUEVO
    rag_module (para justificar con normativa)
    reasoning_module
    gap_engine (optional)
    milestone_engine (optional)
    risk_engine
    output_builder
    advisor_package_generator (conditional)
}

Flujo conceptual:
    Ficha Legal Mínima (JSON)
            ↓
    Project Context (tipo, fondos, alcance)
            ↓
    Legal Requirements Resolver (reglas de negocio)
            ↓
    Requirement Coverage Checker
            ↓
    Estado Legal del Proyecto
            ↓
    RAG (solo para justificar y explicar)
            ↓
    Output Builder
"""

from .intake import IntakeService, intake_service
from .validation import ValidationModule
from .rag import RAGModule
from .reasoning import ReasoningModule
from .gap_engine import GapEngine
from .milestone_engine import MilestoneEngine
from .risk_engine import RiskEngine
from .output_builder import OutputBuilder
from .advisor_package import AdvisorPackageGenerator
from .legal_rules import (
    LegalRequirementsResolver,
    resolve_requirements,
    LegalIntention,
    LegalRequirement,
    LegalGap,
    LegalRequirementsResult,
)

__all__ = [
    # Intake
    "IntakeService",
    "intake_service",
    # Validation
    "ValidationModule",
    # Legal Rules (NEW)
    "LegalRequirementsResolver",
    "resolve_requirements",
    "LegalIntention",
    "LegalRequirement",
    "LegalGap",
    "LegalRequirementsResult",
    # RAG
    "RAGModule",
    # Processing
    "ReasoningModule",
    "GapEngine",
    "MilestoneEngine",
    "RiskEngine",
    # Output
    "OutputBuilder",
    "AdvisorPackageGenerator",
]
