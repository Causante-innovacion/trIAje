# AI Layer
"""
Sistema de IA con Strategy Pattern para providers.
Routing por módulo — cada módulo puede usar un provider diferente.

Módulos:
- INTAKE:     Tareas simples      (gpt-4o-mini vía OpenAI)
- REASONING:  Análisis legal      (deepseek-r1 vía Maple AI)
- CREATIVITY: Contenido original  (configurable)

Providers disponibles: openai, maple, anthropic

Embeddings:
- OpenAI: text-embedding-3-small
- Local: sentence-transformers
"""

from .router import AIRouter
from .embeddings import (
    EmbeddingService,
    EmbeddingProvider,
    EmbeddingServiceFactory,
    OpenAIEmbeddingService,
    LocalEmbeddingService,
    embed_text,
    embed_texts,
)
from .providers import (
    AIProvider,
    AIResponse,
    OpenAIProvider,
    AnthropicProvider,
    MapleAIProvider,
)

__all__ = [
    # Router
    "AIRouter",
    # Embeddings
    "EmbeddingService",
    "EmbeddingProvider",
    "EmbeddingServiceFactory",
    "OpenAIEmbeddingService",
    "LocalEmbeddingService",
    "embed_text",
    "embed_texts",
    # Providers
    "AIProvider",
    "AIResponse",
    "OpenAIProvider",
    "AnthropicProvider",
    "MapleAIProvider",
]
