"""
AI Router — Capa de IA provider-agnóstica basada en LangChain.

Cada módulo puede usar un provider diferente (routing por módulo):
  1. PROVIDER_INTAKE / PROVIDER_REASONING / PROVIDER_CREATIVITY  → override por módulo.
  2. AI_PROVIDER_PRIMARY → fallback si no hay override.
  3. El nombre del modelo (claude-* → Anthropic auto-detect).

Agregar un nuevo provider = añadir un elif en `_build_llm()` y configurar
la API key / URL en config.py. El resto del código no cambia.

Módulos:
  INTAKE     → MODEL_INTAKE     (gpt-4o-mini por defecto, temp 0.3)  → OpenAI
  REASONING  → MODEL_REASONING  (deepseek-r1 vía Maple, temp 0.5)    → Maple
  CREATIVITY → MODEL_CREATIVITY (configurable, temp 0.7)
"""

import json
from typing import Dict, Any, List, AsyncGenerator

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

from app.core.config import settings
from .providers.base import AIResponse


# =============================================================================
# Helpers — resolución de provider por módulo
# =============================================================================

def _resolve_provider(module_override: str | None) -> str:
    """
    Resuelve qué provider usar para un módulo dado.

    Prioridad:
      1. Override explícito por módulo (PROVIDER_INTAKE, etc.)
      2. AI_PROVIDER_PRIMARY (fallback global)
    """
    if module_override:
        return module_override.lower()
    return settings.AI_PROVIDER_PRIMARY.lower()


# =============================================================================
# Factory — construye el LLM de LangChain correcto según provider y modelo
# =============================================================================

def _build_llm(model: str, temperature: float, provider: str = "openai") -> BaseChatModel:
    """
    Devuelve una instancia de BaseChatModel para el modelo dado.

    Args:
        model: Nombre del modelo (e.g. gpt-4o-mini, deepseek-r1)
        temperature: Temperatura de generación
        provider: Provider explícito ("openai", "maple", "anthropic")

    Reglas de selección:
      • provider == "anthropic" (o modelo claude-*) Y hay ANTHROPIC_API_KEY → Anthropic.
      • provider == "maple" Y hay MAPLE_API_KEY → Maple (OpenAI-compat).
      • Todo lo demás (o fallback cuando falta la key) → OpenAI.

    Para añadir un nuevo provider (ej. Google Gemini):
        elif provider == "google" and settings.GOOGLE_API_KEY:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=model, temperature=temperature,
                                          google_api_key=settings.GOOGLE_API_KEY)
    """
    from langchain_openai import ChatOpenAI

    provider = provider.lower()

    # Anthropic — por provider explícito o auto-detect por nombre de modelo
    if (provider == "anthropic" or "claude" in model.lower()) and settings.ANTHROPIC_API_KEY:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=settings.ANTHROPIC_API_KEY,  # type: ignore[arg-type]
        )

    # Maple (OpenAI-compatible) — endpoint propio, ideal para datos sensibles
    # IMPORTANTE: Maple Proxy solo soporta streaming, streaming=True es obligatorio.
    # Con streaming=True, ainvoke() sigue funcionando (acumula el stream internamente).
    if provider == "maple" and settings.MAPLE_API_KEY:
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.MAPLE_API_KEY,       # type: ignore[arg-type]
            base_url=settings.MAPLE_API_URL,
            streaming=True,
        )

    # Defecto: OpenAI.
    # Si el modelo era claude-* pero no hay Anthropic key, sustituimos por el
    # modelo de reasoning de OpenAI para no romper el arranque.
    effective_model = (
        settings.MODEL_REASONING
        if "claude" in model.lower()
        else model
    )
    return ChatOpenAI(
        model=effective_model,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY,          # type: ignore[arg-type]
    )


# =============================================================================
# Helpers
# =============================================================================

def _to_messages(
    prompt: str,
    system_prompt: str | None,
    history: list | None,
) -> List[BaseMessage]:
    """Construye la lista de mensajes LangChain para una llamada al LLM."""
    msgs: List[BaseMessage] = []
    if system_prompt:
        msgs.append(SystemMessage(content=system_prompt))
    for turn in (history or []):
        role = turn.get("role", "user")
        content = turn.get("content", "")
        msgs.append(HumanMessage(content=content) if role == "user" else AIMessage(content=content))
    msgs.append(HumanMessage(content=prompt))
    return msgs


def _parse_json(content: str) -> Dict[str, Any]:
    """Extrae un JSON del texto del LLM (maneja bloques markdown)."""
    content = content.strip()
    for prefix in ("```json", "```"):
        if content.startswith(prefix):
            content = content[len(prefix):]
            break
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(content[start:end])
            except json.JSONDecodeError:
                pass
    return {}


# =============================================================================
# Router
# =============================================================================

class AIRouter:
    """
    Router de IA basado en LangChain. Provider-agnóstico con routing por módulo.

    Cada método corresponde a un módulo funcional (INTAKE, REASONING, CREATIVITY).
    Cada módulo puede usar un provider diferente vía PROVIDER_INTAKE, etc.
    Los LLMs se construyen una sola vez al iniciar y se reutilizan.
    """

    def __init__(self):
        # Resolver provider por módulo (con fallback a AI_PROVIDER_PRIMARY)
        intake_provider = _resolve_provider(settings.PROVIDER_INTAKE)
        reason_provider = _resolve_provider(settings.PROVIDER_REASONING)
        create_provider = _resolve_provider(settings.PROVIDER_CREATIVITY)

        self._intake_llm: BaseChatModel = _build_llm(
            settings.MODEL_INTAKE, temperature=0.3, provider=intake_provider,
        )
        self._reason_llm: BaseChatModel = _build_llm(
            settings.MODEL_REASONING, temperature=0.5, provider=reason_provider,
        )
        self._create_llm: BaseChatModel = _build_llm(
            settings.MODEL_CREATIVITY, temperature=0.7, provider=create_provider,
        )

        # Guardar providers resueltos para metadata en responses
        self._intake_provider = intake_provider
        self._reason_provider = reason_provider
        self._create_provider = create_provider

    # ------------------------------------------------------------------
    # INTAKE — modelo ligero para clasificación y extracción
    # ------------------------------------------------------------------

    async def intake(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> AIResponse:
        """Clasificación e intake. Usa el modelo económico (gpt-4o-mini por defecto)."""
        msgs = _to_messages(prompt, system_prompt, None)
        result = await self._intake_llm.ainvoke(msgs)
        return AIResponse(
            content=str(result.content),
            model=settings.MODEL_INTAKE,
            provider=self._intake_provider,
        )

    # ------------------------------------------------------------------
    # REASONING — análisis legal con soporte de historial multi-turno
    # ------------------------------------------------------------------

    async def reason(
        self,
        prompt: str,
        system_prompt: str | None = None,
        history: List[Dict[str, str]] | None = None,
    ) -> AIResponse:
        """Análisis legal. Soporte de historial para memoria multi-turno."""
        msgs = _to_messages(prompt, system_prompt, history)
        result = await self._reason_llm.ainvoke(msgs)
        return AIResponse(
            content=str(result.content),
            model=settings.MODEL_REASONING,
            provider=self._reason_provider,
        )

    async def reason_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        history: List[Dict[str, str]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Análisis legal en streaming. Yield token a token vía LangChain .astream()."""
        msgs = _to_messages(prompt, system_prompt, history)
        async for chunk in self._reason_llm.astream(msgs):
            if chunk.content:
                yield str(chunk.content)

    # ------------------------------------------------------------------
    # CREATIVITY — redacción y generación de contenido
    # ------------------------------------------------------------------

    async def create(
        self,
        prompt: str,
        system_prompt: str | None = None,
        prefer_claude: bool = True,
    ) -> AIResponse:
        """
        Generación de contenido (redacción, documentos).
        Usa MODEL_CREATIVITY (claude-sonnet por defecto).
        Si falla, cae al modelo de reasoning.
        """
        msgs = _to_messages(prompt, system_prompt, None)
        try:
            result = await self._create_llm.ainvoke(msgs)
        except Exception:
            result = await self._reason_llm.ainvoke(msgs)
        return AIResponse(
            content=str(result.content),
            model=settings.MODEL_CREATIVITY,
            provider=self._create_provider,
        )

    # ------------------------------------------------------------------
    # JSON — salida estructurada para ambos módulos
    # ------------------------------------------------------------------

    async def intake_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: str | None = None,
    ) -> Dict[str, Any]:
        """INTAKE con respuesta JSON estructurada."""
        return await self._call_json(self._intake_llm, prompt, schema, system_prompt)

    async def reason_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: str | None = None,
    ) -> Dict[str, Any]:
        """REASONING con respuesta JSON estructurada."""
        return await self._call_json(self._reason_llm, prompt, schema, system_prompt)

    async def _call_json(
        self,
        llm: BaseChatModel,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: str | None,
    ) -> Dict[str, Any]:
        """
        Llama al LLM y parsea la respuesta como JSON.

        Intenta primero activar el modo JSON nativo del provider
        (response_format=json_object, disponible en OpenAI/Maple).
        Si el provider no lo soporta (Anthropic, etc.), cae al parsing por prompt.
        """
        json_instruction = (
            "\n\nResponde SOLO con JSON válido según este schema "
            "(sin texto antes ni después, sin bloques markdown):\n"
            + json.dumps(schema, ensure_ascii=False, indent=2)
        )
        json_system = (system_prompt or "") + json_instruction
        msgs = _to_messages(prompt, json_system, None)

        try:
            # Modo JSON nativo (OpenAI / Maple)
            llm_json = llm.bind(response_format={"type": "json_object"})
            result = await llm_json.ainvoke(msgs)
        except Exception:
            # Anthropic y otros providers sin response_format → parsing manual
            result = await llm.ainvoke(msgs)

        return _parse_json(str(result.content))

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    async def health_check(self) -> Dict[str, bool]:
        """Verifica que el provider principal responde."""
        provider = settings.AI_PROVIDER_PRIMARY
        try:
            await self._intake_llm.ainvoke([HumanMessage(content="ping")])
            return {provider: True}
        except Exception:
            return {provider: False}
