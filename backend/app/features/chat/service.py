"""
Chat Feature - Service (Orquestador principal)

Flujo:
1. Clasificar intención y semáforo
2. Según semáforo:
   - VERDE → RAG + respuesta con fuentes
   - AMARILLO → Pedir contexto mínimo
   - ROJO → Alerta + derivar a asesor
3. Detectar análisis de proyecto → sugerir subida de archivo
"""

import asyncio
import uuid
import json
import logging
from typing import List, Dict, Optional, AsyncGenerator

logger = logging.getLogger(__name__)

from app.ai.router import AIRouter
from app.modules.rag import get_rag_module

from .config import (
    Intention,
    Semaphore,
    INTENTIONS,
    GATILLOS,
    OUT_OF_SCOPE_MESSAGE,
    RED_DERIVATION_TEMPLATE,
    AMBER_CONTEXT_TEMPLATE,
    STANDARD_DISCLAIMERS,
    GREETING_PATTERNS,
    GREETING_MESSAGE,
    ADVISOR_PREP_ENDPOINT,
    PRE_CLARIFY_QUESTIONS,
    PRE_CLARIFY_SYSTEM_PROMPT,
    PRE_CLARIFY_INTRO_TEMPLATE,
)
from .schemas import (
    ChatRequest,
    ChatResponse,
    ChatClassification,
    LegalSource,
    SuggestedAction,
    ActionType,
)
from .classifier import (
    IntentionClassifier,
    SemaphoreClassifier,
    ProjectAnalysisDetector,
)


# =============================================================================
# FÁBRICA DE SYSTEM PROMPTS
# Centraliza las instrucciones comunes para todos los flujos de REASONING.
# =============================================================================

_BASE_RULES = (
    # Idioma y razonamiento
    "Siempre responde en español. "
    "CRÍTICO: Tu razonamiento interno (dentro de las etiquetas <think>) DEBE estar "
    "escrito enteramente en español. Nunca uses inglés, ni siquiera para razonar internamente. "
    # Acrónimos
    "Cuando menciones siglas o acrónimos, escríbelos siempre en su forma completa la primera vez "
    "que aparezcan en la respuesta (ejemplo: en lugar de 'SUNARP' escribe "
    "'Superintendencia Nacional de los Registros Públicos (SUNARP)'). "
    # Porcentajes y límites
    "Cada vez que cites un porcentaje, umbral numérico o límite legal (por ejemplo: '30 %', "
    "'50 UIT', '3 meses'), DEBES indicar inmediatamente su base legal: la ley, decreto o artículo "
    "concreto que lo establece. Nunca menciones un porcentaje sin su fundamento normativo. "
    # Lenguaje condicional
    "Usa lenguaje condicional cuando no tengas certeza: 'en principio', 'según el marco general', "
    "'se recomienda verificar con la normativa vigente'. "
    # Memoria contextual
    "Si el historial de conversación contiene información provista por el usuario (tipo de "
    "organización, estado del RUC, estatutos modificados, etc.), úsala en tu respuesta sin "
    "volver a pedirla. Mantén la continuidad del contexto durante toda la sesión. "
)

_STRUCTURE_RULES = (
    # Estructura estándar de respuesta
    "\n\nESTRUCTURA OBLIGATORIA DE TU RESPUESTA:\n"
    "1. **Resumen ejecutivo** (máximo 3 líneas): respuesta directa a la pregunta principal.\n"
    "2. **Desarrollo** (secciones numeradas o con encabezados ##): normativa aplicable, "
    "pasos o requisitos, consideraciones importantes.\n"
    "3. **⚠️ Consideraciones clave** (si aplica): riesgos, plazos críticos, excepciones.\n"
    "4. **📌 Próximo paso recomendado**: UNA acción concreta y específica que el usuario "
    "debe tomar inmediatamente (incluye el nombre del registro, trámite, plataforma o "
    "profesional; si hay costo o plazo aproximado, mencionarlo).\n\n"
    # Instrucciones de citas — el frontend las convierte en tooltips
    "SISTEMA DE CITAS (OBLIGATORIO cuando cites normativa):\n"
    "- Cuando hagas referencia a una ley, artículo o norma, añade un marcador de cita inline: [1], [2], etc.\n"
    "- NO escribas el nombre completo de la ley en el párrafo. Solo el marcador [N] al final de la frase.\n"
    "- Al FINAL de toda la respuesta, agrega un bloque con el encabezado exacto '## Referencias' "
    "y lista cada cita en el formato: [N] Descripción breve — Ley o decreto, Art. X.\n"
    "Ejemplo de cita inline: 'Las asociaciones deben inscribirse en registros públicos [1].'\n"
    "Ejemplo de bloque final:\n"
    "## Referencias\n"
    "[1] Inscripción de asociaciones — Código Civil, Art. 77 y ss., D.Leg. N.º 295.\n"
    "[2] Exoneración del Impuesto a la Renta — Ley del Impuesto a la Renta, Art. 19 inc. b), D.S. N.º 179-2004-EF.\n"
    "Si en una respuesta no citas ninguna norma específica, omite el bloque ## Referencias.\n"
)



def _build_system_prompt(mode: str) -> str:
    """
    Construye el system prompt según el modo de respuesta.

    Modos:
    - 'followup'    : Usuario ya dio contexto; respuesta específica y personalizada.
    - 'verde_rag'   : Respuesta VERDE con normativa RAG disponible.
    - 'verde_norag' : Respuesta VERDE sin normativa específica (orientación general).
    - 'amber_partial': Respuesta orientativa AMARILLO antes de recibir contexto completo.
    - 'amber_rag'   : Respuesta AMARILLO tras recibir contexto del usuario + RAG.
    """
    base = "Eres Justo, un asistente legal especializado en derecho peruano para organizaciones civiles. "

    if mode == "followup":
        core = (
            "El usuario ya te proporcionó información específica de su caso (en este mensaje o en "
            "turnos anteriores del historial). USA esa información para dar una respuesta "
            "ESPECÍFICA Y PERSONALIZADA — no orientación genérica. "
            "Cita los artículos normativos que aplican exactamente a su situación. "
            "Si el historial menciona detalles concretos (tipo de organización, estatutos, "
            "fechas, montos), recuérdalos y úsalos en tu respuesta sin pedirlos de nuevo. "
        )
    elif mode == "verde_rag":
        core = (
            "Responde SOLO con base en la normativa proporcionada en el contexto. "
            "Cita los artículos específicos con su número y nombre de ley. "
            "Si la información no está en el contexto normativo, indícalo claramente. "
            "No inventes normas ni artículos. "
            "Si detectas riesgo medio-alto o ambigüedad, recomienda asesoría profesional. "
        )
    elif mode == "verde_norag":
        core = (
            "Responde de forma orientativa; no se dispone de normativa específica en este momento. "
            "SIEMPRE usa lenguaje condicional. Nunca afirmes con certeza sin respaldo normativo. "
            "Si el caso parece de riesgo medio o alto, recomienda explícitamente asesoría profesional. "
        )
    elif mode == "amber_partial":
        core = (
            "El usuario tiene una situación específica pero faltan datos clave para orientarlo con precisión. "
            "Proporciona una orientación GENERAL usando lenguaje condicional. "
            "IMPORTANTE: incluye al final la sección '📋 **Supuestos que estoy aplicando:**' "
            "listando los supuestos que asumes. "
            "No des recomendaciones definitivas hasta confirmar los supuestos con el usuario. "
        )
    elif mode == "amber_rag":
        core = (
            "El usuario acaba de darte información adicional específica de su caso. "
            "Usa esa información junto con la normativa para dar una respuesta ESPECÍFICA y PERSONALIZADA. "
            "No des orientación genérica: enfócate en los detalles concretos del caso. "
            "Cita los artículos normativos aplicables. "
        )
    else:
        core = "Proporciona orientación legal clara y estructurada. "

    return base + core + _BASE_RULES + _STRUCTURE_RULES


class ChatService:

    """Servicio principal del chat. Orquesta clasificación, RAG y respuestas."""

    def __init__(self):
        self._ai_router = AIRouter()

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Procesa un mensaje del usuario y retorna la respuesta completa.
        """
        message = request.message.strip()
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Build history for LLM multi-turn memory
        history: list | None = [{
            "role": h.role, "content": h.content
        } for h in (request.history or [])] or None

        # 0. Pending AMARILLO context: user is answering a clarifying question.
        #    Skip the classifier and route directly to VERDE with the enriched query.
        pending_amber = (request.context or {}).get("pending_amber")
        if pending_amber:
            try:
                prior_intention = Intention(pending_amber.get("intention", ""))
            except ValueError:
                prior_intention = None
            if prior_intention and prior_intention != Intention.FUERA_DE_ALCANCE:
                original_query = pending_amber.get("original_query", message)
                enriched_message = (
                    f"{original_query}\n\n"
                    f"Información adicional proporcionada por el usuario: {message}"
                )
                classification = ChatClassification(
                    intention=prior_intention,
                    intention_name=INTENTIONS[prior_intention].name,
                    semaphore=Semaphore.VERDE,
                    confidence=0.95,
                    gatillos_detected=[],
                    requires_context=[],
                )
                return await self._handle_green(enriched_message, classification, conversation_id, history=history, amber_followup=True)

        # 1. Detectar saludos simples
        if self._is_greeting(message):
            return self._build_greeting_response(conversation_id)

        # 2. Detectar si quiere analizar un proyecto
        #    Si el mensaje ya trae un archivo adjunto (📎), saltar el detector
        #    para que el flujo normal clasifique y analice el contenido.
        has_file_attached = "📎" in message
        if not has_file_attached and ProjectAnalysisDetector.is_project_analysis(message):
            return self._build_project_analysis_response(message, conversation_id)

        # 3. Clasificar intención (keywords + LLM fallback).
        # Cuando el LLM se invoca, su opinión sobre el semáforo viene gratis
        # en el mismo JSON — la capturamos para evitar una segunda llamada.
        intention, intention_confidence, _llm_semaphore_hint = await IntentionClassifier.classify(message)

        # 4. Antes de retornar fuera de alcance, verificar gatillos ROJO.
        #    Un mensaje como "nos llegó una denuncia en SUNAFIL" puede ser mal
        #    clasificado como fuera de alcance aunque contenga un trigger claro.
        #    detect_gatillos ya hace búsqueda cruzada por todas las intenciones.
        if intention == Intention.FUERA_DE_ALCANCE:
            early_gatillos = SemaphoreClassifier.detect_gatillos(message, intention)
            if early_gatillos:
                # Inferir la intención real buscando cuál gatillo disparó
                inferred_intention = Intention.FUERA_DE_ALCANCE
                for _intent, _gatillo_list in GATILLOS.items():
                    for _gtl in _gatillo_list:
                        if any(g in _gtl.trigger_phrases for g in early_gatillos):
                            inferred_intention = _intent
                            break
                    if inferred_intention != Intention.FUERA_DE_ALCANCE:
                        break
                # Si encontramos una intención real, redirigir al flujo ROJO
                if inferred_intention != Intention.FUERA_DE_ALCANCE:
                    intention = inferred_intention
                    intention_confidence = 0.7
                    semaphore = Semaphore.ROJO
                    gatillos = early_gatillos
                    context_needed: List[str] = []
                    classification = ChatClassification(
                        intention=intention,
                        intention_name=INTENTIONS[intention].name,
                        semaphore=semaphore,
                        confidence=intention_confidence,
                        gatillos_detected=gatillos,
                        requires_context=[],
                    )
                    return await self._handle_red(message, classification, conversation_id)
            return self._build_out_of_scope_response(conversation_id)

        # 5. Clasificar semáforo (reglas de palabras clave, síncrono)
        semaphore, gatillos, context_needed = SemaphoreClassifier.classify(
            message, intention
        )

        # Fallback LLM: cuando el semáforo es VERDE pero el mensaje describe un caso concreto,
        # usamos la opinión que el LLM ya emitió durante la clasificación de intención.
        # Si el LLM no fue invocado (keywords suficientes), solo entonces hacemos una llamada
        # adicional para el semáforo. Esto evita la segunda llamada en la mayoría de los casos.
        if semaphore == Semaphore.VERDE and SemaphoreClassifier._is_specific_case(message):
            if _llm_semaphore_hint is not None:
                _effective_sem = _llm_semaphore_hint
            else:
                _effective_sem = await SemaphoreClassifier._ask_llm_semaphore(message, intention)
            if _effective_sem == Semaphore.ROJO:
                semaphore = Semaphore.ROJO
                gatillos = []
                context_needed = []
            elif _effective_sem == Semaphore.AMARILLO:
                semaphore = Semaphore.AMARILLO
                context_needed = context_needed or [
                    "Describe el contexto específico de tu situación para orientarte mejor."
                ]

        # 6. Construir clasificación
        classification = ChatClassification(
            intention=intention,
            intention_name=INTENTIONS[intention].name,
            semaphore=semaphore,
            confidence=intention_confidence,
            gatillos_detected=gatillos,
            requires_context=context_needed,
        )

        # 7. Generar respuesta según semáforo
        if semaphore == Semaphore.ROJO:
            return await self._handle_red(message, classification, conversation_id)
        elif semaphore == Semaphore.AMARILLO:
            return await self._handle_amber(message, classification, context_needed, conversation_id, history=history)
        else:
            return await self._handle_green(message, classification, conversation_id, history=history)

    # =========================================================================
    # HANDLERS POR SEMÁFORO
    # =========================================================================

    async def stream_message(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """
        Versión streaming de process_message para consultas VERDE.
        Emite eventos SSE con el formato: data: {json}\n\n

        Eventos emitidos en orden:
          status      → etapa actual del procesamiento (para UI progresiva)
          classification → intención + semáforo detectados
          sources     → fuentes normativas encontradas en RAG
          token       → fragmento de texto del LLM (solo en VERDE)
          done        → señal de fin + actions + disclaimers
        """

        def sse(event: dict) -> str:
            return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        message = request.message.strip()
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # ── Saludo ──────────────────────────────────────────────────────────
        if self._is_greeting(message):
            resp = self._build_greeting_response(conversation_id)
            yield sse({"type": "done", "message": resp.message,
                       "classification": resp.classification.model_dump(),
                       "actions": [], "disclaimers": [],
                       "conversation_id": conversation_id})
            return

        # ── Análisis de proyecto ─────────────────────────────────────────────
        #    Si el mensaje ya trae un archivo adjunto (📎), saltar el detector
        #    para que el flujo normal clasifique y analice el contenido.
        has_file_attached = "📎" in message
        if not has_file_attached and ProjectAnalysisDetector.is_project_analysis(message):
            resp = self._build_project_analysis_response(message, conversation_id)
            yield sse({"type": "done", "message": resp.message,
                       "classification": resp.classification.model_dump(),
                       "actions": [a.model_dump() for a in resp.actions],
                       "disclaimers": resp.disclaimers,
                       "conversation_id": conversation_id})
            return
        # ── Pending AMARILLO: usuario responde pregunta de contexto ───────────────
        _amber_intention = None
        eff_message = message  # query usado para RAG y LLM (puede ser enriquecido)
        history: list | None = [{
            "role": h.role, "content": h.content
        } for h in (request.history or [])] or None
        pending_amber = (request.context or {}).get("pending_amber")
        if pending_amber:
            try:
                _pri = Intention(pending_amber.get("intention", ""))
                if _pri != Intention.FUERA_DE_ALCANCE:
                    _amber_intention = _pri
                    original_query = pending_amber.get("original_query", message)
                    eff_message = (
                        f"{original_query}\n\n"
                        f"Información adicional proporcionada por el usuario: {message}"
                    )
            except ValueError:
                pass
        # ── Clasificar intención ─────────────────────────────────────────────
        yield sse({"type": "status", "stage": "classifying",
                   "message": "Clasificando tu consulta..."})

        if _amber_intention:
            intention, intention_confidence, _llm_semaphore_hint = _amber_intention, 0.95, None
        else:
            intention, intention_confidence, _llm_semaphore_hint = await IntentionClassifier.classify(message)

        if intention == Intention.FUERA_DE_ALCANCE:
            # Antes de salir, verificar si hay gatillos ROJO en el mensaje.
            # Un mensaje como "nos llegó una denuncia en SUNAFIL" puede ser mal
            # clasificado como fuera de alcance aunque contenga un trigger claro.
            _early_gatillos = SemaphoreClassifier.detect_gatillos(message, intention)
            if _early_gatillos:
                _inferred = Intention.FUERA_DE_ALCANCE
                for _int, _glist in GATILLOS.items():
                    for _g in _glist:
                        if any(eg in _g.trigger_phrases for eg in _early_gatillos):
                            _inferred = _int
                            break
                    if _inferred != Intention.FUERA_DE_ALCANCE:
                        break
                if _inferred != Intention.FUERA_DE_ALCANCE:
                    intention = _inferred
                    intention_confidence = 0.7
                    _red_cls = ChatClassification(
                        intention=intention,
                        intention_name=INTENTIONS[intention].name,
                        semaphore=Semaphore.ROJO,
                        confidence=0.7,
                        gatillos_detected=_early_gatillos,
                        requires_context=[],
                    )
                    yield sse({"type": "classification", "data": _red_cls.model_dump()})
                    resp = await self._handle_red(message, _red_cls, conversation_id)
                    yield sse({"type": "done", "message": resp.message,
                               "classification": _red_cls.model_dump(),
                               "actions": [a.model_dump() for a in resp.actions],
                               "disclaimers": resp.disclaimers,
                               "conversation_id": conversation_id})
                    return
            classification = ChatClassification(
                intention=intention, intention_name="Fuera de Alcance",
                semaphore=Semaphore.VERDE, confidence=1.0,
                gatillos_detected=[], requires_context=[],
            )
            yield sse({"type": "done", "message": OUT_OF_SCOPE_MESSAGE,
                       "classification": classification.model_dump(),
                       "actions": [], "disclaimers": [],
                       "conversation_id": conversation_id})
            return

        # ── Semáforo ─────────────────────────────────────────────────────────
        if _amber_intention:
            semaphore, gatillos, context_needed = Semaphore.VERDE, [], []
        else:
            semaphore, gatillos, context_needed = SemaphoreClassifier.classify(message, intention)
            # Fallback LLM: si VERDE + caso concreto, usar el hint del LLM de intención
            # (ya viene gratis del mismo JSON) o solo entonces hacer una llamada adicional.
            if semaphore == Semaphore.VERDE and SemaphoreClassifier._is_specific_case(message):
                if _llm_semaphore_hint is not None:
                    _effective_sem = _llm_semaphore_hint
                else:
                    _effective_sem = await SemaphoreClassifier._ask_llm_semaphore(message, intention)
                if _effective_sem == Semaphore.ROJO:
                    semaphore = Semaphore.ROJO
                    gatillos = []
                    context_needed = []
                elif _effective_sem == Semaphore.AMARILLO:
                    semaphore = Semaphore.AMARILLO
                    context_needed = context_needed or [
                        "Describe el contexto específico de tu situación para orientarte mejor."
                    ]

        # ── Promover AMARILLO → VERDE si el historial ya tiene contexto previo ────
        # Si el clasificador dispara AMARILLO pero el usuario ya respondió ese tipo
        # de pregunta en un turno anterior, reutilizamos ese contexto y respondemos
        # directamente con una respuesta específica (evita el bucle de re-preguntar).
        _prior_amber_ctx: str | None = None
        if semaphore == Semaphore.AMARILLO and history:
            _prior_amber_ctx = self._find_prior_amber_answer(history)
            if _prior_amber_ctx:
                eff_message = (
                    f"{message}\n\n"
                    f"[Contexto que el usuario ya proporcionó anteriormente: {_prior_amber_ctx}]"
                )
                semaphore = Semaphore.VERDE
                gatillos = []
                context_needed = []

        classification = ChatClassification(
            intention=intention,
            intention_name=INTENTIONS[intention].name,
            semaphore=semaphore,
            confidence=intention_confidence,
            gatillos_detected=gatillos,
            requires_context=context_needed,
        )
        yield sse({"type": "classification", "data": classification.model_dump()})

        # ── ROJO: respuesta completa sin streaming ───────────────────────────
        if semaphore == Semaphore.ROJO:
            resp = await self._handle_red(message, classification, conversation_id)
            yield sse({"type": "done", "message": resp.message,
                       "classification": classification.model_dump(),
                       "actions": [a.model_dump() for a in resp.actions],
                       "disclaimers": resp.disclaimers,
                       "conversation_id": conversation_id})
            return

        # ── AMARILLO: respuesta parcial + contexto (streaming del partial) ───
        if semaphore == Semaphore.AMARILLO:
            yield sse({"type": "status", "stage": "searching",
                       "message": "Buscando normativa relevante..."})
            sources: List[LegalSource] = []
            rag_context = ""
            try:
                rag_module = get_rag_module()
                if rag_module:
                    rag_result = await rag_module.retrieve_and_ground(
                        query=eff_message, top_k_initial=6,
                        intention_filter=classification.intention.value,
                    )
                    if rag_result and rag_result.chunks:
                        rag_context = self._build_rag_context_from_chunks(rag_result)
                        sources = self._extract_sources_from_chunks(rag_result)
                        seen_docs_amber: set = set()
                        for chunk in rag_result.chunks:
                            title = chunk.metadata.title
                            if title and title not in seen_docs_amber:
                                seen_docs_amber.add(title)
                                yield sse({"type": "doc_scanning", "title": title})
                                await asyncio.sleep(0.06)
            except Exception:
                pass

            if sources:
                yield sse({"type": "sources", "data": [s.model_dump() for s in sources]})

            yield sse({"type": "status", "stage": "generating",
                       "message": "Preparando orientación..."})

            # Stream la respuesta parcial
            system_prompt = (
                "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
                "El usuario tiene una situación específica pero faltan datos clave para precisar la orientación. "
                "Proporciona orientación general sobre el marco normativo aplicable usando lenguaje condicional. "
                "IMPORTANTE: Al final de tu respuesta incluye una sección '📋 **Supuestos que estoy aplicando:**' "
                "donde listes explícitamente los supuestos que estás asumiendo sobre el caso del usuario. "
                "No des recomendaciones definitivas hasta que el usuario confirme esos supuestos. "
                "Responde en español, con estructura clara y concisa. "
                "CRÍTICO: Tu razonamiento interno (dentro de las etiquetas <think>) DEBE estar escrito enteramente en español. "
                "Nunca uses inglés, ni siquiera para razonar internamente. "
                "Cuando menciones siglas o acrónimos (por ejemplo: Registro Único de Contribuyentes, Registro Nacional de Grandes Contribuyentes, "
                "Agencia de Cooperación Internacional del Perú, Sistema de Administración Tributaria), "
                "escríbelos siempre en su forma completa la primera vez que aparezcan en la respuesta."
            )
            intention_config = INTENTIONS.get(classification.intention)
            if rag_context:
                prompt = (
                    f"Intención: {intention_config.name if intention_config else ''}\n"
                    f"Consulta: {eff_message}\n\nNormativa relevante:\n{rag_context}\n\n"
                    "Proporciona orientación general citando los artículos aplicables. "
                    "Señala qué aspectos dependen del caso concreto."
                )
            else:
                prompt = (
                    f"Área: {intention_config.name if intention_config else ''}\n"
                    f"Consulta: {eff_message}\n\n"
                    "Da orientación general sobre el marco normativo en Perú. "
                    "Señala qué información adicional cambiaría la respuesta."
                )

            questions_text = "\n".join(f"• {q}" for q in context_needed[:3])
            amber_suffix = (
                f"\n\n---\n\n🟡 **Para orientarte mejor sobre tu caso específico:**\n\n"
                f"{questions_text}\n\n"
                "Con esta información podré ajustar la orientación a tu situación concreta."
            )

            try:
                async for token in self._ai_router.reason_stream(
                    prompt=prompt, system_prompt=system_prompt, history=history
                ):
                    yield sse({"type": "token", "text": token})
            except Exception:
                fallback = await self._generate_amber_partial(message, classification, rag_context, history=history)
                yield sse({"type": "token", "text": fallback})

            yield sse({"type": "token", "text": amber_suffix})

            # Si el usuario pidió explícitamente preparar preguntas para un asesor,
            # o si el caso tiene alta complejidad (muchos datos faltantes), añadir la acción.
            amber_actions = [{"type": "provide_context", "label": "Añadir más contexto",
                              "description": "Responde las preguntas para recibir orientación más específica."}]
            if self._is_advisor_request(message) or len(context_needed) >= 3:
                amber_actions.append({
                    "type": "derive_to_advisor",
                    "label": "Preparar preguntas para el asesor",
                    "description": "Te ayudaré a organizar las preguntas clave para tu reunión con el especialista.",
                    "endpoint": ADVISOR_PREP_ENDPOINT,
                })

            yield sse({"type": "done",
                       "actions": amber_actions,
                       "disclaimers": STANDARD_DISCLAIMERS,
                       "conversation_id": conversation_id})
            return

        # ── PRE-CLARIFICACIÓN: preguntar antes de responder si falta contexto clave ──
        # Solo activa si: semáforo es VERDE, no hay follow-up ámbar, no hay historial
        # con contexto relevante, y la intención tiene preguntas configuradas.
        if (
            semaphore == Semaphore.VERDE
            and not _amber_intention
            and not _prior_amber_ctx
            and self._should_pre_clarify(eff_message, intention, history)
        ):
            pre_clarify_qs = PRE_CLARIFY_QUESTIONS.get(intention, [])
            if pre_clarify_qs:
                intent_cfg = INTENTIONS.get(intention)
                topic = intent_cfg.name if intent_cfg else "este tema"
                questions_text = "\n".join(
                    f"{i+1}. {q}" for i, q in enumerate(pre_clarify_qs[:2])
                )
                pre_clarify_msg = PRE_CLARIFY_INTRO_TEMPLATE.format(
                    topic=topic,
                    questions=questions_text,
                )
                yield sse({"type": "token", "text": pre_clarify_msg})
                yield sse({
                    "type": "done",
                    "actions": [],
                    "disclaimers": [],
                    "conversation_id": conversation_id,
                    "metadata": {"pre_clarify": True, "intention": intention.value},
                })
                return

        # ── VERDE: RAG + stream LLM ──────────────────────────────────────────
        yield sse({"type": "status", "stage": "searching",
                   "message": "Buscando normativa relevante..."})

        sources = []
        rag_context = ""
        try:
            rag_module = get_rag_module()
            if rag_module:
                rag_result = await rag_module.retrieve_and_ground(
                    query=eff_message, top_k_initial=10,
                    intention_filter=classification.intention.value,
                )
                if rag_result and rag_result.chunks:
                    rag_context = self._build_rag_context_from_chunks(rag_result)
                    sources = self._extract_sources_from_chunks(rag_result)
                    # Emitir progreso doc a doc para feedback visual en el frontend
                    seen_docs: set = set()
                    for chunk in rag_result.chunks:
                        title = chunk.metadata.title
                        if title and title not in seen_docs:
                            seen_docs.add(title)
                            yield sse({"type": "doc_scanning", "title": title})
                            await asyncio.sleep(0.06)
        except Exception:
            pass

        if sources:
            yield sse({"type": "sources", "data": [s.model_dump() for s in sources]})

        yield sse({"type": "status", "stage": "generating",
                   "message": "Generando respuesta..."})

        if _amber_intention or _prior_amber_ctx:
            # El usuario ya proporcionó contexto (ahora o en un turno anterior)
            # → respuesta específica y personalizada usando esa información
            system_prompt = _build_system_prompt("followup")
            prompt = (
                f"Intención legal: {INTENTIONS[intention].name}\n"
                f"Consulta con contexto del usuario:\n{eff_message}\n\n"
                + (f"Normativa relevante:\n{rag_context}\n\n" if rag_context else "")
                + "Estructura tu respuesta con: resumen ejecutivo (≤ 3 líneas), "
                "desarrollo con secciones numeradas, justificación explícita de cualquier "
                "porcentaje o umbral legal citado, y CTA concreto al final."
            )
        elif rag_context:
            system_prompt = _build_system_prompt("verde_rag")
            prompt = (
                f"Intención detectada: {INTENTIONS[intention].name}\n"
                f"Pregunta del usuario: {eff_message}\n\n"
                f"Contexto normativo relevante:\n{rag_context}\n\n"
                "Responde la pregunta citando los artículos específicos de la normativa. "
                "Estructura: resumen ejecutivo (≤ 3 líneas), desarrollo con secciones, CTA concreto al final."
            )
        else:
            intention_config = INTENTIONS.get(intention)
            system_prompt = _build_system_prompt("verde_norag")
            prompt = (
                f"El usuario consulta sobre: {intention_config.name if intention_config else ''}\n"
                f"Pregunta: {eff_message}\n\n"
                "Da una respuesta orientativa general. "
                "Incluye resumen ejecutivo, secciones, justificación de cualquier porcentaje o umbral, "
                "y un CTA claro al final con pasos prácticos."
            )

        try:
            async for token in self._ai_router.reason_stream(
                prompt=prompt, system_prompt=system_prompt, history=history
            ):
                yield sse({"type": "token", "text": token})
        except Exception as e:
            logger.error("[REASONING] reason_stream falló: %s: %s", type(e).__name__, e, exc_info=True)
            fallback = await self._generate_basic_response(
                eff_message, classification, history=history, amber_followup=bool(_amber_intention)
            )
            yield sse({"type": "token", "text": fallback})

        # Si el usuario pidió explícitamente preparar preguntas para un asesor,
        # añadir la acción aunque el semáforo sea VERDE.
        verde_actions = []
        if self._is_advisor_request(message):
            verde_actions.append({
                "type": "derive_to_advisor",
                "label": "Preparar preguntas para el asesor",
                "description": "Te ayudaré a organizar las preguntas clave para tu reunión con el especialista.",
                "endpoint": ADVISOR_PREP_ENDPOINT,
            })

        yield sse({"type": "done", "actions": verde_actions,
                   "disclaimers": STANDARD_DISCLAIMERS,
                   "conversation_id": conversation_id})

    # =========================================================================
    # HANDLERS POR SEMÁFORO
    # =========================================================================

    async def _handle_green(
        self,
        message: str,
        classification: ChatClassification,
        conversation_id: str,
        history: list | None = None,
        amber_followup: bool = False,
    ) -> ChatResponse:
        """Maneja consultas VERDE: busca en RAG + genera respuesta."""
        sources: List[LegalSource] = []
        response_text = ""

        # Intentar buscar en RAG
        try:
            rag_module = get_rag_module()
            if rag_module:
                rag_result = await rag_module.retrieve_and_ground(
                    query=message,
                    top_k_initial=10,
                    intention_filter=classification.intention.value,
                )

                if rag_result and rag_result.chunks:
                    # Construir contexto RAG desde los chunks
                    rag_context = self._build_rag_context_from_chunks(rag_result)
                    sources = self._extract_sources_from_chunks(rag_result)

                    # Generar respuesta con LLM + contexto RAG
                    response_text = await self._generate_rag_response(
                        message, classification, rag_context, history=history, amber_followup=amber_followup
                    )
        except Exception:
            pass

        # Si no hay RAG o falló, generar respuesta sin contexto
        if not response_text:
            response_text = await self._generate_basic_response(message, classification, history=history, amber_followup=amber_followup)

        return ChatResponse(
            message=response_text,
            classification=classification,
            sources=sources,
            actions=[],
            disclaimers=STANDARD_DISCLAIMERS,
            conversation_id=conversation_id,
        )

    async def _handle_amber(
        self,
        message: str,
        classification: ChatClassification,
        context_needed: List[str],
        conversation_id: str,
        history: list | None = None,
    ) -> ChatResponse:
        """Maneja consultas AMARILLO: genera orientación parcial con RAG + pide contexto para personalizar."""
        sources: List[LegalSource] = []
        partial_answer = ""

        # 1. Intentar buscar en RAG para dar una respuesta base orientativa
        try:
            rag_module = get_rag_module()
            if rag_module:
                rag_result = await rag_module.retrieve_and_ground(
                    query=message,
                    top_k_initial=6,
                    intention_filter=classification.intention.value,
                )
                if rag_result and rag_result.chunks:
                    rag_context = self._build_rag_context_from_chunks(rag_result)
                    sources = self._extract_sources_from_chunks(rag_result)
                    partial_answer = await self._generate_amber_partial(
                        message, classification, rag_context, history=history
                    )
        except Exception:
            pass

        # 2. Si no hay RAG o falló, generar orientación base sin contexto documental
        if not partial_answer:
            partial_answer = await self._generate_amber_partial(message, classification, "", history=history)

        # 3. Combinar respuesta parcial + preguntas de contexto
        questions_text = "\n".join(f"• {q}" for q in context_needed[:3])
        response_text = AMBER_CONTEXT_TEMPLATE.format(
            partial_answer=partial_answer,
            questions=questions_text,
        )

        return ChatResponse(
            message=response_text,
            classification=classification,
            sources=sources,
            actions=[
                SuggestedAction(
                    type=ActionType.PROVIDE_CONTEXT,
                    label="Añadir más contexto",
                    description="Responde las preguntas para recibir orientación más específica a tu caso.",
                ),
            ],
            disclaimers=STANDARD_DISCLAIMERS,
            conversation_id=conversation_id,
        )

    async def _generate_amber_partial(
        self,
        message: str,
        classification: ChatClassification,
        rag_context: str,
        history: list | None = None,
    ) -> str:
        """Genera respuesta orientativa parcial para AMARILLO, con o sin contexto RAG."""
        intention_config = INTENTIONS.get(classification.intention)

        system_prompt = _build_system_prompt("amber_partial")

        if rag_context:
            prompt = (
                f"Intención detectada: {intention_config.name if intention_config else classification.intention_name}\n"
                f"Consulta del usuario: {message}\n\n"
                f"Normativa relevante:\n{rag_context}\n\n"
                "Proporciona una orientación general sobre este tema basada en la normativa. "
                "Cita los artículos aplicables y señala qué aspectos dependen del caso concreto."
            )
        else:
            prompt = (
                f"El usuario consulta sobre: {intention_config.name if intention_config else classification.intention_name}\n"
                f"Descripción del área: {intention_config.description if intention_config else ''}\n"
                f"Consulta: {message}\n\n"
                "Da una orientación general sobre el marco normativo aplicable en Perú. "
                "Señala qué información adicional cambiaría o precisaría la respuesta."
            )

        try:
            response = await self._ai_router.reason(
                prompt=prompt,
                system_prompt=system_prompt,
                history=history,
            )
            return response.content
        except Exception:
            if intention_config:
                return (
                    f"Tu consulta está relacionada con **{intention_config.name}**. "
                    f"{intention_config.description} "
                    f"Para orientarte con mayor precisión, necesito algunos datos adicionales."
                )
            return "Para orientarte con mayor precisión sobre tu situación, necesito algunos datos adicionales."

    async def _handle_red(
        self,
        message: str,
        classification: ChatClassification,
        conversation_id: str,
    ) -> ChatResponse:
        """Maneja consultas ROJO: alerta + derivar a asesor."""
        # Buscar la razón de derivación del primer gatillo detectado
        derivation_reason = self._get_derivation_reason(
            classification.intention,
            classification.gatillos_detected,
        )

        response_text = RED_DERIVATION_TEMPLATE.format(reason=derivation_reason)

        return ChatResponse(
            message=response_text,
            classification=classification,
            sources=[],
            actions=[
                SuggestedAction(
                    type=ActionType.DERIVE_TO_ADVISOR,
                    label="Preparar documentación para asesor",
                    description="Te ayudaré a organizar toda la información necesaria para tu reunión con el abogado.",
                    endpoint=ADVISOR_PREP_ENDPOINT,
                ),
            ],
            disclaimers=[
                "Esta situación requiere asesoría legal profesional.",
                "El sistema NO puede brindar orientación sobre este caso.",
                "Consulta con un abogado especializado lo antes posible.",
            ],
            conversation_id=conversation_id,
        )

    # =========================================================================
    # RESPUESTAS ESPECIALES
    # =========================================================================

    @staticmethod
    def _find_prior_amber_answer(history: list) -> str | None:
        """
        Escanea el historial reciente buscando un exchange AMARILLO previo:
        el asistente hizo una pregunta de contexto (marcador 🟡) y el usuario respondió.
        Retorna la respuesta del usuario si la encuentra, None si no.
        """
        for i, msg in enumerate(history):
            if msg.get("role") == "assistant" and "\U0001f7e1" in msg.get("content", ""):
                # Hay un mensaje siguiente del usuario = su respuesta de contexto
                if i + 1 < len(history) and history[i + 1].get("role") == "user":
                    return history[i + 1]["content"]
        return None

    @staticmethod
    def _is_advisor_request(message: str) -> bool:
        """Detecta si el usuario pide explícitamente preparar preguntas para un asesor/especialista."""
        import unicodedata
        msg = message.lower().strip()
        nfkd = unicodedata.normalize("NFKD", msg)
        msg_norm = "".join(c for c in nfkd if not unicodedata.combining(c))

        # Palabras clave que indican que el usuario quiere prepararse para hablar con un asesor/especialista
        ADVISOR_WORDS = [
            "asesor", "abogado", "especialista", "notario", "consultor",
        ]
        PREP_WORDS = [
            "preguntas", "consulta", "preparar", "preparo", "prepararme",
            "preparacion", "reunion", "visita", "entrevista", "cita",
            "que le digo", "que le pregunto", "que pregunto", "como presento",
            "set de preguntas", "lista de preguntas", "documentos para",
            "documentacion para", "paquete para",
        ]
        has_advisor = any(w in msg_norm for w in ADVISOR_WORDS)
        has_prep = any(w in msg_norm for w in PREP_WORDS)
        return has_advisor and has_prep

    @staticmethod
    def _is_greeting(message: str) -> bool:
        """Detecta si el mensaje es un saludo simple."""
        import unicodedata
        msg = message.lower().strip()
        # Quitar acentos para matching robusto
        nfkd = unicodedata.normalize("NFKD", msg)
        msg_norm = "".join(c for c in nfkd if not unicodedata.combining(c))
        # Quitar signos de puntuación
        msg_clean = msg_norm.strip("!?.,;: ")
        for pattern in GREETING_PATTERNS:
            pattern_norm = unicodedata.normalize("NFKD", pattern.lower())
            pattern_norm = "".join(c for c in pattern_norm if not unicodedata.combining(c))
            if msg_clean == pattern_norm or msg_clean == pattern_norm + "!":
                return True
        return False

    def _build_greeting_response(self, conversation_id: str) -> ChatResponse:
        """Respuesta amigable para saludos."""
        return ChatResponse(
            message=GREETING_MESSAGE,
            classification=ChatClassification(
                intention=Intention.FUERA_DE_ALCANCE,
                intention_name="Saludo",
                semaphore=Semaphore.VERDE,
                confidence=1.0,
                gatillos_detected=[],
                requires_context=[],
            ),
            sources=[],
            actions=[],
            disclaimers=[],
            conversation_id=conversation_id,
        )

    @staticmethod
    def _should_pre_clarify(message: str, intention: Intention, history: list | None) -> bool:
        """
        Determina si se debe activar el flujo de pre-clarificación para una consulta VERDE.

        Condiciones para activar:
        1. La intención tiene preguntas configuradas en PRE_CLARIFY_QUESTIONS.
        2. El mensaje es una pregunta informativa general (no tiene indicadores de caso específico).
        3. El historial no contiene ya respuestas a las preguntas de pre-clarificación
           (es decir, el usuario ya respondió en turnos anteriores → no volver a preguntar).

        Esto evita preguntar de nuevo si el usuario ya dio contexto en la misma sesión.
        """
        # Si no hay preguntas configuradas para esta intención, no activar
        if intention not in PRE_CLARIFY_QUESTIONS:
            return False

        # Si el usuario ya tiene historial largo (> 2 turnos), asumimos que el
        # contexto ya está establecido — no interrumpir con preguntas nuevas.
        if history and len(history) > 2:
            return False

        # Si el mensaje tiene indicadores de caso específico (posesivos, verbos en 1ª persona,
        # palabras de problema), el sistema de semáforo ya lo maneja → no duplicar.
        from .classifier import SemaphoreClassifier
        if SemaphoreClassifier._is_specific_case(message):
            return False

        # Solo activar para preguntas informativas generales
        return SemaphoreClassifier._is_informative_question(message)

    def _build_out_of_scope_response(self, conversation_id: str) -> ChatResponse:
        """Respuesta para consultas fuera del ámbito legal."""
        return ChatResponse(
            message=OUT_OF_SCOPE_MESSAGE,
            classification=ChatClassification(
                intention=Intention.FUERA_DE_ALCANCE,
                intention_name="Fuera de Alcance",
                semaphore=Semaphore.VERDE,
                confidence=1.0,
                gatillos_detected=[],
                requires_context=[],
            ),
            sources=[],
            actions=[],
            disclaimers=[],
            conversation_id=conversation_id,
        )

    def _build_project_analysis_response(
        self, message: str, conversation_id: str
    ) -> ChatResponse:
        """Respuesta sugerida para análisis de proyecto."""
        return ChatResponse(
            message=(
                "¡Excelente! Para analizar la viabilidad legal de tu proyecto necesito "
                "información detallada.\n\n"
                "Te recomiendo **subir un archivo** con la descripción de tu proyecto "
                "(puede ser un PDF, Word o texto). Esto me permitirá hacer una evaluación "
                "más precisa.\n\n"
                "Puedes adjuntar tu documento usando el botón 📎 en la barra de mensajes."
            ),
            classification=ChatClassification(
                intention=Intention.FORMALIZACION,
                intention_name="Análisis de Proyecto",
                semaphore=Semaphore.VERDE,
                confidence=0.9,
                gatillos_detected=[],
                requires_context=[],
            ),
            sources=[],
            actions=[
                SuggestedAction(
                    type=ActionType.UPLOAD_FILE,
                    label="Subir archivo del proyecto",
                    description="Sube un documento con la descripción de tu proyecto para análisis automático.",
                    endpoint="/api/v1/documents/upload",
                ),
            ],
            disclaimers=STANDARD_DISCLAIMERS,
            conversation_id=conversation_id,
        )

    # =========================================================================
    # ANÁLISIS DE VIABILIDAD LEGAL DE PROYECTO (con archivo adjunto)
    # =========================================================================

    @staticmethod
    def _get_project_analysis_system_prompt() -> str:
        """Prompt de sistema para análisis de viabilidad legal de proyecto."""
        return (
            "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
            "El usuario ha subido un documento con la descripción de su proyecto. "
            "Tu tarea es realizar un ANÁLISIS DE VIABILIDAD LEGAL completo del proyecto descrito en el documento. "
            "\n\nDebe cubrir las siguientes áreas:\n"
            "1. **Tipo de organización recomendada**: Evalúa si el proyecto debería operarse como asociación, "
            "ONG, fundación, cooperativa, empresa social, etc. según la legislación peruana.\n"
            "2. **Requisitos de formalización**: Pasos legales necesarios para constituir la organización "
            "(escritura pública, SUNARP, RUC, licencias, etc.).\n"
            "3. **Régimen tributario aplicable**: Beneficios fiscales, exoneraciones, obligaciones tributarias.\n"
            "4. **Marco normativo relevante**: Leyes, decretos y normas que regulan el tipo de actividad del proyecto.\n"
            "5. **Riesgos legales potenciales**: Identifica posibles riesgos o contingencias legales.\n"
            "6. **Recomendaciones**: Pasos a seguir para la viabilidad legal del proyecto.\n\n"
            "Cita los artículos normativos aplicables cuando sea posible. "
            "Responde en español, de forma clara, con estructura y encabezados. "
            "CRÍTICO: Tu razonamiento interno (dentro de las etiquetas <think>) DEBE estar escrito enteramente en español. "
            "Nunca uses inglés, ni siquiera para razonar internamente. "
            "Cuando menciones siglas o acrónimos, escríbelos siempre en su forma completa la primera vez que aparezcan en la respuesta. "
            "NO des respuestas genéricas; analiza el contenido específico del documento."
        )

    @staticmethod
    def _get_project_analysis_prompt(message: str, rag_context: str) -> str:
        """Construye el prompt para análisis de viabilidad legal."""
        if rag_context:
            return (
                f"El usuario ha subido un documento para análisis de viabilidad legal. "
                f"Contenido del documento y mensaje del usuario:\n\n{message}\n\n"
                f"Normativa relevante encontrada:\n{rag_context}\n\n"
                "Realiza un análisis de viabilidad legal completo del proyecto descrito, "
                "citando la normativa proporcionada donde aplique."
            )
        return (
            f"El usuario ha subido un documento para análisis de viabilidad legal. "
            f"Contenido del documento y mensaje del usuario:\n\n{message}\n\n"
            "Realiza un análisis de viabilidad legal completo del proyecto descrito. "
            "Indica qué normativa peruana aplica a cada aspecto del proyecto."
        )

    async def _handle_project_file_analysis(
        self,
        message: str,
        conversation_id: str,
        history: list | None = None,
    ) -> ChatResponse:
        """Analiza la viabilidad legal de un proyecto a partir de un archivo adjunto."""
        sources: List[LegalSource] = []
        rag_context = ""
        response_text = ""

        # Buscar normativa relevante con RAG
        try:
            rag_module = get_rag_module()
            if rag_module:
                rag_result = await rag_module.retrieve_and_ground(
                    query=message,
                    top_k_initial=10,
                    intention_filter=Intention.FORMALIZACION.value,
                )
                if rag_result and rag_result.chunks:
                    rag_context = self._build_rag_context_from_chunks(rag_result)
                    sources = self._extract_sources_from_chunks(rag_result)
        except Exception:
            pass

        # Generar análisis con LLM
        system_prompt = self._get_project_analysis_system_prompt()
        prompt = self._get_project_analysis_prompt(message, rag_context)

        try:
            response = await self._ai_router.reason(
                prompt=prompt,
                system_prompt=system_prompt,
                history=history,
            )
            response_text = response.content
        except Exception:
            response_text = (
                "No pude completar el análisis de viabilidad legal en este momento. "
                "Por favor, intenta de nuevo o describe tu proyecto directamente en el chat."
            )

        classification = ChatClassification(
            intention=Intention.FORMALIZACION,
            intention_name="Análisis de Proyecto",
            semaphore=Semaphore.VERDE,
            confidence=0.95,
            gatillos_detected=[],
            requires_context=[],
        )

        return ChatResponse(
            message=response_text,
            classification=classification,
            sources=sources,
            actions=[],
            disclaimers=STANDARD_DISCLAIMERS,
            conversation_id=conversation_id,
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_derivation_reason(
        self, intention: Intention, gatillos_detected: List[str]
    ) -> str:
        """Obtiene la razón de derivación del gatillo detectado."""
        gatillo_list = GATILLOS.get(intention, [])
        for gatillo in gatillo_list:
            for phrase in gatillo.trigger_phrases:
                if phrase in gatillos_detected:
                    return gatillo.derivation_reason

        # Buscar en todas las intenciones
        for intent, g_list in GATILLOS.items():
            for gatillo in g_list:
                for phrase in gatillo.trigger_phrases:
                    if phrase in gatillos_detected:
                        return gatillo.derivation_reason

        return "Se detectaron indicadores de riesgo legal que requieren atención profesional."

    def _build_rag_context_from_chunks(self, rag_result) -> str:
        """Construye el contexto RAG desde los chunks del RAGResult."""
        if not rag_result.chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(rag_result.chunks[:5], 1):
            source = chunk.metadata.title or "Fuente desconocida"
            article = f" ({chunk.metadata.anchor})" if chunk.metadata.anchor else ""
            context_parts.append(f"[Fuente {i}: {source}{article}]\n{chunk.content}")

        return "\n\n---\n\n".join(context_parts)

    def _extract_sources_from_chunks(self, rag_result) -> List[LegalSource]:
        """Extrae fuentes legales de los chunks del RAGResult."""
        sources: List[LegalSource] = []
        seen_titles: set = set()

        for chunk in rag_result.chunks[:5]:
            title = chunk.metadata.title
            if title and title not in seen_titles:
                seen_titles.add(title)
                sources.append(LegalSource(
                    title=title,
                    article=chunk.metadata.anchor,
                    authority=chunk.metadata.jurisdiction,
                    url=chunk.metadata.url,
                ))

        return sources

    async def _generate_rag_response(
        self,
        message: str,
        classification: ChatClassification,
        rag_context: str,
        history: list | None = None,
        amber_followup: bool = False,
    ) -> str:
        """Genera respuesta usando LLM con contexto RAG."""
        if amber_followup:
            system_prompt = _build_system_prompt("amber_rag")
            prompt = (
                f"Intención legal: {classification.intention_name}\n"
                f"Consulta con contexto adicional del usuario:\n{message}\n\n"
                f"Normativa relevante:\n{rag_context}\n\n"
                "Responde de forma específica y personalizada para este caso concreto, "
                "citando los artículos de la normativa aplicables a su situación."
            )
        else:
            system_prompt = _build_system_prompt("verde_rag")
            prompt = (
                f"Intención detectada: {classification.intention_name}\n"
                f"Pregunta del usuario: {message}\n\n"
                f"Contexto normativo relevante:\n{rag_context}\n\n"
                "Responde la pregunta citando los artículos específicos de la normativa."
            )

        try:
            response = await self._ai_router.reason(
                prompt=prompt,
                system_prompt=system_prompt,
                history=history,
            )
            return response.content
        except Exception:
            return await self._generate_basic_response(message, classification, history=history, amber_followup=amber_followup)

    async def _generate_basic_response(
        self,
        message: str,
        classification: ChatClassification,
        history: list | None = None,
        amber_followup: bool = False,
    ) -> str:
        """Genera una respuesta básica cuando no hay RAG disponible."""
        intention_config = INTENTIONS.get(classification.intention)
        if not intention_config:
            return "No tengo información suficiente para responder esta consulta."

        if amber_followup:
            system_prompt = _build_system_prompt("followup")
            prompt = (
                f"Área legal: {intention_config.name}\n"
                f"Consulta con contexto adicional del usuario: {message}\n\n"
                "Da una respuesta personalizada y específica para este caso concreto, "
                "incluyendo qué normativa aplicaría y cuáles son los pasos recomendados. "
                "Recuerda usar la estructura: resumen ejecutivo + desarrollo + CTA concreto al final."
            )
        else:
            system_prompt = _build_system_prompt("verde_norag")
            prompt = (
                f"El usuario consulta sobre: {intention_config.name}\n"
                f"Descripción del área: {intention_config.description}\n"
                f"Pregunta: {message}\n\n"
                "Da una respuesta orientativa general indicando qué información adicional precisaría la respuesta."
            )

        try:
            response = await self._ai_router.reason(
                prompt=prompt,
                system_prompt=system_prompt,
                history=history,
            )
            return response.content
        except Exception as e:
            logger.error("[REASONING] reason() falló: %s: %s", type(e).__name__, e, exc_info=True)
            return (
                f"Tu consulta está relacionada con **{intention_config.name}**. "
                f"En este momento no puedo procesar la solicitud completamente. "
                f"Te recomiendo consultar directamente la normativa aplicable o "
                f"un profesional especializado en esta área."
            )


# Singleton
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Obtiene la instancia del servicio de chat."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
