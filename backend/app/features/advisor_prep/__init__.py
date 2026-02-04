# Feature: Advisor Prep
"""
Modo 3: Preparar reunión con asesor

Genera paquete estructurado para reunión con abogado/contador.
"""

from .router import router
from .service import AdvisorPrepService

__all__ = ["router", "AdvisorPrepService"]
