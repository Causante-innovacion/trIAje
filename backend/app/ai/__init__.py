# AI Layer
"""
Sistema de IA con Strategy Pattern para providers.

Módulos:
- INTAKE: Tareas simples (gpt-4o-mini)
- REASONING: Análisis lógico (gpt-4o)
- CREATIVITY: Contenido original (claude-sonnet)

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
