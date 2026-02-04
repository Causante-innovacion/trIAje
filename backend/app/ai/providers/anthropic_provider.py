"""
AI Providers - Anthropic Implementation
"""

import json
from typing import Dict, Any

from app.core.config import settings
from .base import AIProvider, AIResponse


class AnthropicProvider(AIProvider):
    """Provider para Anthropic Claude"""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self._client = None

    @property
    def name(self) -> str:
        return "anthropic"

    def _get_client(self):
        """Lazy initialization del cliente"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY no configurada")
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package no instalado")
        return self._client

    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AIResponse:
        """Genera respuesta con Claude"""
        client = self._get_client()

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = await client.messages.create(**kwargs)

        return AIResponse(
            content=response.content[0].text if response.content else "",
            model=model,
            provider=self.name,
            usage={
                "input_tokens": response.usage.input_tokens if response.usage else 0,
                "output_tokens": response.usage.output_tokens if response.usage else 0,
            },
        )

    async def generate_json(
        self,
        prompt: str,
        model: str,
        schema: Dict[str, Any],
        system_prompt: str | None = None,
    ) -> Dict[str, Any]:
        """Genera respuesta JSON estructurada"""
        full_system = (system_prompt or "") + f"\n\nResponde SOLO con JSON válido según este schema:\n{json.dumps(schema)}"

        response = await self.generate(
            prompt=prompt,
            model=model,
            system_prompt=full_system,
            temperature=0.3,
        )

        # Extraer JSON del contenido
        content = response.content
        try:
            # Intentar parsear directamente
            return json.loads(content)
        except json.JSONDecodeError:
            # Buscar JSON en el contenido
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
            return {}

    async def health_check(self) -> bool:
        """Verifica disponibilidad"""
        try:
            self._get_client()
            return True
        except Exception:
            return False
