"""
Chat Feature - Interfaz principal del sistema GPT Legal.

Clasifica mensajes por intención (13 categorías) y semáforo (Verde/Amarillo/Rojo),
orquesta respuestas con RAG, y deriva automáticamente a asesor en casos ROJO.
"""

from .router import router
from .schemas import ChatRequest, ChatResponse, ChatClassification
from .classifier import IntentionClassifier, SemaphoreClassifier

__all__ = [
    "router",
    "ChatRequest",
    "ChatResponse",
    "ChatClassification",
    "IntentionClassifier",
    "SemaphoreClassifier",
]
