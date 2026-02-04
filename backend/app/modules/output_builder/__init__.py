# Output Builder Module
"""
Genera schema de salida por herramienta.

Responsabilidades:
- schema_binding
- conditional_language_enforcement
- assumption_logging
- evidence_attachment
- uncertainty_flags
"""

from .service import OutputBuilder
from .schema_binder import ToolOutput, OutputSection

__all__ = [
    "OutputBuilder",
    "ToolOutput",
    "OutputSection",
]
