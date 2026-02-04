# AI Layer
"""
Sistema de IA con Strategy Pattern para providers.

Módulos:
- INTAKE: Tareas simples (gpt-4o-mini)
- REASONING: Análisis lógico (gpt-4o)
- CREATIVITY: Contenido original (claude-sonnet)
"""

from .router import AIRouter

__all__ = ["AIRouter"]
