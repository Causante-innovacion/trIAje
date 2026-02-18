"""
AI Router - Selecciona provider según módulo

Módulos según spec:
- INTAKE: gpt-4o-mini (tareas simples, clasificación)
- REASONING: gpt-4o (análisis lógico)
- CREATIVITY: claude-sonnet (redacción)
"""

from typing import Dict, Any, List, AsyncGenerator
from app.core.config import settings
from .providers import AIProvider, AIResponse, OpenAIProvider, AnthropicProvider


class AIRouter:
    """
    Router que selecciona el provider y modelo según el tipo de tarea.
    """

    def __init__(self):
        self._providers: Dict[str, AIProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Inicializa los providers disponibles"""
        if settings.OPENAI_API_KEY:
            self._providers["openai"] = OpenAIProvider()

        if settings.ANTHROPIC_API_KEY:
            self._providers["anthropic"] = AnthropicProvider()

    def _get_provider(self, provider_name: str) -> AIProvider:
        """Obtiene un provider por nombre"""
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' no disponible")
        return self._providers[provider_name]

    async def intake(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> AIResponse:
        """
        Módulo INTAKE: tareas simples, clasificación, extracción.
        Usa modelo económico y rápido.
        """
        provider = self._get_provider("openai")
        return await provider.generate(
            prompt=prompt,
            model=settings.MODEL_INTAKE,  # gpt-4o-mini
            system_prompt=system_prompt,
            temperature=0.3,  # Más determinístico
            max_tokens=1000,
        )

    async def reason(
        self,
        prompt: str,
        system_prompt: str | None = None,
        history: List[Dict[str, str]] | None = None,
    ) -> AIResponse:
        """
        Módulo REASONING: análisis lógico, comparaciones, evaluación.
        Usa modelo con buena capacidad de razonamiento.
        """
        provider = self._get_provider("openai")
        return await provider.generate(
            prompt=prompt,
            model=settings.MODEL_REASONING,  # gpt-4o
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=1200,
            history=history,
        )

    async def reason_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        history: List[Dict[str, str]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        REASONING en streaming: emite tokens a medida que el LLM los genera.
        El usuario ve la primera palabra en ~1s en vez de esperar ~8s.
        """
        provider = self._get_provider("openai")
        async for token in provider.generate_stream(
            prompt=prompt,
            model=settings.MODEL_REASONING,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=1200,
            history=history,
        ):
            yield token

    async def create(
        self,
        prompt: str,
        system_prompt: str | None = None,
        prefer_claude: bool = True,
    ) -> AIResponse:
        """
        Módulo CREATIVITY: generación de contenido, redacción.
        Prefiere Claude para mejor redacción.
        """
        # Intentar Claude primero si está disponible y se prefiere
        if prefer_claude and "anthropic" in self._providers:
            provider = self._get_provider("anthropic")
            return await provider.generate(
                prompt=prompt,
                model=settings.MODEL_CREATIVITY,  # claude-sonnet
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=3000,
            )

        # Fallback a OpenAI
        provider = self._get_provider("openai")
        return await provider.generate(
            prompt=prompt,
            model=settings.MODEL_REASONING,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=3000,
        )

    async def intake_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: str | None = None,
    ) -> Dict[str, Any]:
        """INTAKE con respuesta JSON estructurada"""
        provider = self._get_provider("openai")
        return await provider.generate_json(
            prompt=prompt,
            model=settings.MODEL_INTAKE,
            schema=schema,
            system_prompt=system_prompt,
        )

    async def reason_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: str | None = None,
    ) -> Dict[str, Any]:
        """REASONING con respuesta JSON estructurada"""
        provider = self._get_provider("openai")
        return await provider.generate_json(
            prompt=prompt,
            model=settings.MODEL_REASONING,
            schema=schema,
            system_prompt=system_prompt,
        )

    async def health_check(self) -> Dict[str, bool]:
        """Verifica estado de todos los providers"""
        results = {}
        for name, provider in self._providers.items():
            results[name] = await provider.health_check()
        return results
