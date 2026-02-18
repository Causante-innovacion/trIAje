"""
AI Providers - Base Interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator
from pydantic import BaseModel


class AIResponse(BaseModel):
    """Respuesta de un provider de IA"""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = {}
    metadata: Dict[str, Any] = {}


class AIProvider(ABC):
    """
    Interfaz abstracta para providers de IA.
    Implementar para: OpenAI, Anthropic, Google, etc.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del provider"""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AIResponse:
        """
        Genera una respuesta.

        Args:
            prompt: Prompt del usuario
            model: Modelo a usar
            system_prompt: Prompt de sistema
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens

        Returns:
            AIResponse con el contenido generado
        """
        pass

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        model: str,
        schema: Dict[str, Any],
        system_prompt: str | None = None,
    ) -> Dict[str, Any]:
        """
        Genera respuesta en formato JSON estructurado.

        Args:
            prompt: Prompt del usuario
            model: Modelo a usar
            schema: Schema JSON esperado
            system_prompt: Prompt de sistema

        Returns:
            Dict con la respuesta estructurada
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verifica que el provider esté disponible"""
        pass

    async def generate_stream(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1200,
    ) -> AsyncGenerator[str, None]:
        """
        Genera respuesta en streaming, yielding tokens uno a uno.
        Por defecto delega a generate() y emite el resultado completo.
        Override en providers que soporten streaming nativo.
        """
        response = await self.generate(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        yield response.content
