# Validation Module
"""
Responsabilidad: validar consistencia de ficha legal mínima.

Checks:
- required_fields_complete
- cross-field consistency
- legal_trigger_presence
- risk_signals_present

Flags generados: validation_pass, validation_warning, validation_block
"""

from .service import ValidationModule
from .flags import ValidationFlag, ValidationResult

__all__ = [
    "ValidationModule",
    "ValidationFlag",
    "ValidationResult",
]
