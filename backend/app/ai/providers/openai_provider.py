"""
AI Providers - OpenAI Implementation
"""

import json
from typing import Dict, Any, AsyncGenerator

from app.core.config import settings
from .base import AIProvider, AIResponse


class OpenAIProvider(AIProvider):
    """Provider para OpenAI"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self._client = None

    @property
    def name(self) -> str:
        return "openai"

    def _get_client(self):
        """Lazy initialization del cliente"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY no configurada")
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package no instalado")
        return self._client

    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AIResponse:
        """Genera respuesta con OpenAI"""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return AIResponse(
            content=response.choices[0].message.content or "",
            model=model,
            provider=self.name,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
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
        client = self._get_client()

        full_system = (system_prompt or "") + f"\n\nResponde SOLO con JSON válido según este schema:\n{json.dumps(schema)}"

        messages = [
            {"role": "system", "content": full_system},
            {"role": "user", "content": prompt},
        ]

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    async def health_check(self) -> bool:
        """Verifica disponibilidad"""
        try:
            client = self._get_client()
            # Simple test
            await client.models.list()
            return True
        except Exception:
            return False

    async def generate_stream(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1200,
    ) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming nativo de OpenAI, yield token a token."""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
