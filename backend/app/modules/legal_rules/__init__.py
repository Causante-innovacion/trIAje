# Legal Rules Module
"""
Motor de reglas legales para GPT Legal.

Este módulo contiene la lógica de negocio que determina:
- Qué requisitos legales aplican según el perfil de la organización
- Qué brechas existen (gaps)
- Qué documentos son necesarios
- Qué registros son obligatorios

El RAG se usa DESPUÉS para justificar y explicar estas reglas con normativa.
"""

from .resolver import (
    LegalRequirementsResolver,
    resolve_requirements,
)
from .schemas import (
    LegalIntention,
    LegalRequirement,
    RequirementStatus,
    LegalGap,
    GapSeverity,
    LegalRequirementsResult,
)
from .rules import LEGAL_RULES

__all__ = [
    # Resolver
    "LegalRequirementsResolver",
    "resolve_requirements",
    # Schemas
    "LegalIntention",
    "LegalRequirement",
    "RequirementStatus",
    "LegalGap",
    "GapSeverity",
    "LegalRequirementsResult",
    # Rules
    "LEGAL_RULES",
]
