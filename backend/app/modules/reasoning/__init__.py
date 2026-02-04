# Reasoning Module
"""
Aplica lógica legal estructurada basada en:
- retrieved_norms
- intake_data
- risk_rules
- tool_logic

Produce:
- legal_conditions[]
- applicability_matrix
- decision_constraints

No puede operar si: rag_evidence == insufficient AND risk >= medium
"""

from .service import ReasoningModule
from .legal_logic import (
    LegalCondition,
    ApplicabilityMatrix,
    ReasoningResult,
)

__all__ = [
    "ReasoningModule",
    "LegalCondition",
    "ApplicabilityMatrix",
    "ReasoningResult",
]
