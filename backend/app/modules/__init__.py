# GPT Legal - Sub-módulos canónicos
"""
Módulos compartidos reutilizables entre herramientas (modos).

Cada herramienta es un pipeline orquestado:

Tool = OrchestratedToolPipeline {
    intake_module
    validation_module
    rag_module
    reasoning_module
    gap_engine (optional)
    milestone_engine (optional)
    risk_engine
    output_builder
    advisor_package_generator (conditional)
}
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

__all__ = [
    "IntakeService",
    "intake_service",
    "ValidationModule",
    "RAGModule",
    "ReasoningModule",
    "GapEngine",
    "MilestoneEngine",
    "RiskEngine",
    "OutputBuilder",
    "AdvisorPackageGenerator",
]
