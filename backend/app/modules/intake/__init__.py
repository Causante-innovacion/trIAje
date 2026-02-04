# Intake Module
"""
Responsabilidad: recolectar datos estructurados sin ambigüedad.

Funciones:
- render_question_set()
- enforce_selector_inputs()
- trigger_contextual_help_icons()
- validate_required_fields()
- normalize_answers()

Entradas permitidas: boolean, enum, multi-select, range, role-selector
Nunca acepta: free_text crítico, null, no_se
"""

from .service import IntakeModule
from .schemas import (
    InputType,
    QuestionDefinition,
    IntakeData,
    NormalizedIntake,
)

__all__ = [
    "IntakeModule",
    "InputType",
    "QuestionDefinition",
    "IntakeData",
    "NormalizedIntake",
]
