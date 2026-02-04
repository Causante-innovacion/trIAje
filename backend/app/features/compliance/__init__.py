# Feature: Compliance
"""
Modo 4: Ruta de cumplimiento/formalización

Genera ruta paso a paso con milestones, dependencias,
autoridades y documentos.
"""

from .router import router
from .service import ComplianceService

__all__ = ["router", "ComplianceService"]
