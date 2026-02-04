# Feature: Evaluation
"""
Modo 1: Evaluar proyecto/prototipo

Identifica riesgos, propone rutas legales, clasifica viabilidad.
Incluye salida del Generador Cívico si aplica.
"""

from .router import router
from .service import EvaluationService

__all__ = ["router", "EvaluationService"]
