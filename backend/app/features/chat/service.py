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
from typing import List, Optional

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

        # 1. Detectar si quiere analizar un proyecto
        if ProjectAnalysisDetector.is_project_analysis(message):
            return self._build_project_analysis_response(message, conversation_id)

        # 2. Clasificar intención
        intention, intention_confidence = await IntentionClassifier.classify(message)

        # 3. Si es fuera de alcance, responder inmediatamente
        if intention == Intention.FUERA_DE_ALCANCE:
            return self._build_out_of_scope_response(conversation_id)

        # 4. Clasificar semáforo
        semaphore, gatillos, context_needed = SemaphoreClassifier.classify(
            message, intention
        )

        # 5. Construir clasificación
        classification = ChatClassification(
            intention=intention,
            intention_name=INTENTIONS[intention].name,
            semaphore=semaphore,
            confidence=intention_confidence,
            gatillos_detected=gatillos,
            requires_context=context_needed,
        )

        # 6. Generar respuesta según semáforo
        if semaphore == Semaphore.ROJO:
            return await self._handle_red(message, classification, conversation_id)
        elif semaphore == Semaphore.AMARILLO:
            return await self._handle_amber(message, classification, context_needed, conversation_id)
        else:
            return await self._handle_green(message, classification, conversation_id)

    # =========================================================================
    # HANDLERS POR SEMÁFORO
    # =========================================================================

    async def _handle_green(
        self,
        message: str,
        classification: ChatClassification,
        conversation_id: str,
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
                    top_k_initial=5,
                )

                if rag_result and rag_result.chunks:
                    # Construir contexto RAG desde los chunks
                    rag_context = self._build_rag_context_from_chunks(rag_result)
                    sources = self._extract_sources_from_chunks(rag_result)

                    # Generar respuesta con LLM + contexto RAG
                    response_text = await self._generate_rag_response(
                        message, classification, rag_context
                    )
        except Exception:
            pass

        # Si no hay RAG o falló, generar respuesta sin contexto
        if not response_text:
            response_text = await self._generate_basic_response(message, classification)

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
    ) -> ChatResponse:
        """Maneja consultas AMARILLO: pide contexto mínimo antes de responder."""
        questions_text = "\n".join(f"• {q}" for q in context_needed[:3])
        response_text = AMBER_CONTEXT_TEMPLATE.format(questions=questions_text)

        return ChatResponse(
            message=response_text,
            classification=classification,
            sources=[],
            actions=[
                SuggestedAction(
                    type=ActionType.PROVIDE_CONTEXT,
                    label="Proporcionar contexto",
                    description="Responde las preguntas anteriores para obtener orientación precisa.",
                ),
            ],
            disclaimers=STANDARD_DISCLAIMERS,
            conversation_id=conversation_id,
        )

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
    ) -> str:
        """Genera respuesta usando LLM con contexto RAG."""
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
            )
            return response.content
        except Exception:
            return await self._generate_basic_response(message, classification)

    async def _generate_basic_response(
        self,
        message: str,
        classification: ChatClassification,
    ) -> str:
        """Genera una respuesta básica cuando no hay RAG disponible."""
        intention_config = INTENTIONS.get(classification.intention)
        if not intention_config:
            return "No tengo información suficiente para responder esta consulta."

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
