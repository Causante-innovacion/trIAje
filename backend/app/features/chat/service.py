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

import uuid
import json
from typing import List, Dict, Optional, AsyncGenerator

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
        if ProjectAnalysisDetector.is_project_analysis(message):
            return self._build_project_analysis_response(message, conversation_id)

        # 3. Clasificar intención
        intention, intention_confidence = await IntentionClassifier.classify(message)

        # 4. Si es fuera de alcance, responder inmediatamente
        if intention == Intention.FUERA_DE_ALCANCE:
            return self._build_out_of_scope_response(conversation_id)

        # 5. Clasificar semáforo
        semaphore, gatillos, context_needed = SemaphoreClassifier.classify(
            message, intention
        )

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
        if ProjectAnalysisDetector.is_project_analysis(message):
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
            intention, intention_confidence = _amber_intention, 0.95
        else:
            intention, intention_confidence = await IntentionClassifier.classify(message)

        if intention == Intention.FUERA_DE_ALCANCE:
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
            except Exception:
                pass

            if sources:
                yield sse({"type": "sources", "data": [s.model_dump() for s in sources]})

            yield sse({"type": "status", "stage": "generating",
                       "message": "Preparando orientación..."})

            # Stream la respuesta parcial
            system_prompt = (
                "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
                "El usuario tiene una situación específica. Proporciona una orientación general sobre el "
                "marco normativo aplicable. Sé claro y útil, pero señala qué aspectos dependen del "
                "contexto concreto que aún no conoces. No des recomendaciones definitivas. "
                "Responde en español, con estructura clara y concisa."
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
            yield sse({"type": "done",
                       "actions": [{"type": "provide_context", "label": "Añadir más contexto",
                                    "description": "Responde las preguntas para recibir orientación más específica."}],
                       "disclaimers": STANDARD_DISCLAIMERS,
                       "conversation_id": conversation_id})
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
        except Exception:
            pass

        if sources:
            yield sse({"type": "sources", "data": [s.model_dump() for s in sources]})

        yield sse({"type": "status", "stage": "generating",
                   "message": "Generando respuesta..."})

        if _amber_intention or _prior_amber_ctx:
            # El usuario ya proporcionó contexto (ahora o en un turno anterior)
            # → respuesta específica y personalizada usando esa información
            system_prompt = (
                "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
                "El usuario te ha proporcionado información específica de su caso (ya sea ahora o en un turno anterior). "
                "Usa esa información junto con la normativa para dar una respuesta ESPECÍFICA y PERSONALIZADA. "
                "No des orientación genérica: enfócate en los detalles concretos del usuario. "
                "Cita los artículos normativos aplicables a su situación exacta. "
                "Responde en español, de forma clara y con estructura."
            )
            prompt = (
                f"Intención legal: {INTENTIONS[intention].name}\n"
                f"Consulta con contexto del usuario:\n{eff_message}\n\n"
                + (f"Normativa relevante:\n{rag_context}\n\n" if rag_context else "")
                + "Responde de forma específica y personalizada para este caso concreto, "
                "citando la normativa aplicable a su situación."
            )
        elif rag_context:
            system_prompt = (
                "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
                "Responde SOLO con base en la normativa proporcionada en el contexto. "
                "Cita los artículos específicos. "
                "Si la información no está en el contexto, indícalo claramente. "
                "No inventes normas ni artículos. "
                "Responde en español, de forma clara y con estructura."
            )
            prompt = (
                f"Intención detectada: {INTENTIONS[intention].name}\n"
                f"Pregunta del usuario: {eff_message}\n\n"
                f"Contexto normativo relevante:\n{rag_context}\n\n"
                "Responde la pregunta citando los artículos específicos de la normativa."
            )
        else:
            intention_config = INTENTIONS.get(intention)
            system_prompt = (
                "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
                "Responde de forma general y orientativa. "
                "SIEMPRE indica que el usuario debe verificar con la normativa vigente. "
                "Responde en español."
            )
            prompt = (
                f"El usuario consulta sobre: {intention_config.name if intention_config else ''}\n"
                f"Pregunta: {eff_message}\n\n"
                "Da una respuesta orientativa general indicando que debe consultar la normativa específica."
            )

        try:
            async for token in self._ai_router.reason_stream(
                prompt=prompt, system_prompt=system_prompt, history=history
            ):
                yield sse({"type": "token", "text": token})
        except Exception:
            fallback = await self._generate_basic_response(
                eff_message, classification, history=history, amber_followup=bool(_amber_intention)
            )
            yield sse({"type": "token", "text": fallback})

        yield sse({"type": "done", "actions": [],
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

        system_prompt = (
            "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
            "El usuario tiene una situación específica. Proporciona una orientación general sobre el "
            "marco normativo aplicable, explicando qué establece la ley peruana sobre este tema. "
            "Sé claro y útil, pero indica qué aspectos dependen del contexto concreto que aún no conoces. "
            "No des recomendaciones definitivas sin tener todos los datos. "
            "Responde en español, con estructura clara y concisa."
        )

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
                    endpoint="/api/v1/advisor-prep",
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
                "Alternativamente, puedes responder las preguntas del formulario de "
                "evaluación para que analice tu caso paso a paso.\n\n"
                "¿Cómo prefieres proceder?"
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
                SuggestedAction(
                    type=ActionType.PROVIDE_CONTEXT,
                    label="Llenar formulario de evaluación",
                    description="Responde preguntas guiadas para evaluar tu proyecto.",
                    endpoint="/api/v1/intake/questions?tool=evaluation",
                ),
            ],
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
            system_prompt = (
                "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
                "El usuario acaba de darte información adicional específica de su caso. "
                "Usa esa información junto con la normativa para dar una respuesta ESPECÍFICA y PERSONALIZADA. "
                "No des orientación genérica: enfócate en los detalles concretos del caso del usuario. "
                "Cita los artículos normativos aplicables a su situación exacta. "
                "Responde en español, de forma clara y con estructura."
            )
            prompt = (
                f"Intención legal: {classification.intention_name}\n"
                f"Consulta con contexto adicional del usuario:\n{message}\n\n"
                f"Normativa relevante:\n{rag_context}\n\n"
                "Responde de forma específica y personalizada para este caso concreto, "
                "citando los artículos de la normativa aplicables a su situación."
            )
        else:
            system_prompt = (
                "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
                "Responde SOLO con base en la normativa proporcionada en el contexto. "
                "Cita los artículos específicos. "
                "Si la información no está en el contexto, indícalo claramente. "
                "No inventes normas ni artículos. "
                "Responde en español, de forma clara y con estructura."
            )
            prompt = (
                f"Intención detectada: {classification.intention_name}\n"
                f"Pregunta del usuario: {message}\n\n"
                f"Contexto normativo relevante:\n{rag_context}\n\n"
                f"Responde la pregunta citando los artículos específicos de la normativa."
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
            system_prompt = (
                "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
                "El usuario acaba de darte información adicional específica de su caso. "
                "Usa esa información para dar una respuesta CONCRETA y PERSONALIZADA, no genérica. "
                "Enfócate en los detalles específicos que el usuario mencionó. "
                "Indica qué normativa peruana aplicaría a su situación concreta y los pasos recomendados. "
                "Responde en español, de forma clara."
            )
            prompt = (
                f"Área legal: {intention_config.name}\n"
                f"Consulta con contexto adicional del usuario: {message}\n\n"
                "Da una respuesta personalizada y específica para este caso concreto, "
                "indicando qué normativa aplicaría y cuáles son los pasos recomendados."
            )
        else:
            system_prompt = (
                "Eres un asistente legal especializado en derecho peruano para organizaciones civiles. "
                "Responde de forma general y orientativa. "
                "SIEMPRE indica que el usuario debe verificar con la normativa vigente. "
                "NO des respuestas categóricas ni afirmes con certeza. "
                "Responde en español."
            )
            prompt = (
                f"El usuario consulta sobre: {intention_config.name}\n"
                f"Descripción del área: {intention_config.description}\n"
                f"Pregunta: {message}\n\n"
                f"Da una respuesta orientativa general indicando que debe consultar la normativa específica."
            )

        try:
            response = await self._ai_router.reason(
                prompt=prompt,
                system_prompt=system_prompt,
                history=history,
            )
            return response.content
        except Exception:
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
