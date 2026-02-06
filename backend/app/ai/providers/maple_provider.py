"""
AI Providers - Maple AI Implementation
Provider para Maple AI (más seguro para datos sensibles)
"""

import json
from typing import Any

import httpx

from .base import AIProvider, AIResponse


class MapleAIProvider(AIProvider):
    """
    Provider para Maple AI.

    Maple AI es una alternativa más segura para datos sensibles legales.
    La API es similar a OpenAI pero con endpoints diferentes.

    Configuración requerida:
    - MAPLE_API_KEY: API key de Maple
    - MAPLE_API_URL: URL base de la API (default: https://api.maple.ai/v1)
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_url: str = "https://api.maple.ai/v1",
    ):
        from app.core.config import settings

        self.api_key = api_key or getattr(settings, "MAPLE_API_KEY", None)
        self.api_url = api_url
        self._client: httpx.AsyncClient | None = None

    @property
    def name(self) -> str:
        return "maple"

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    async def generate(
        self,
        prompt: str,
        model: str = "maple-gpt-4",
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AIResponse:
        """Genera respuesta usando Maple AI"""
        if not self.api_key:
            raise ValueError("MAPLE_API_KEY no configurado")

        client = await self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await client.post(
                "/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()

            return AIResponse(
                content=data["choices"][0]["message"]["content"],
                model=model,
                provider=self.name,
                usage={
                    "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": data.get("usage", {}).get("total_tokens", 0),
                },
                metadata={"response_id": data.get("id", "")},
            )
        except httpx.HTTPStatusError as e:
            raise Exception(f"Maple AI error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Error conectando con Maple AI: {str(e)}")

    async def generate_json(
        self,
        prompt: str,
        model: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Genera respuesta JSON estructurada"""
        # Agregar instrucción de formato JSON al prompt
        json_instruction = f"""
Responde SOLO con un JSON válido que siga este schema:
{json.dumps(schema, indent=2, ensure_ascii=False)}

No incluyas texto antes o después del JSON.
"""
        full_prompt = f"{prompt}\n\n{json_instruction}"

        response = await self.generate(
            prompt=full_prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=0.3,  # Más determinístico para JSON
        )

        # Parsear JSON de la respuesta
        try:
            content = response.content.strip()
            # Limpiar posibles delimitadores de código
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"Respuesta no es JSON válido: {e}")

    async def health_check(self) -> bool:
        """Verifica disponibilidad de Maple AI"""
        if not self.api_key:
            return False

        try:
            client = await self._get_client()
            response = await client.get("/models")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Cierra el cliente HTTP"""
        if self._client:
            await self._client.aclose()
            self._client = None
