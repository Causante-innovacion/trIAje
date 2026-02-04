# Feature: Query
"""
Modo 2: Resolver duda puntual

Responde consultas legales específicas sin semáforo de viabilidad,
salvo condición especial.
"""

from .router import router
from .service import QueryService

__all__ = ["router", "QueryService"]
