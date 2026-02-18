"""
Chat Feature - Router
Endpoints FastAPI para el sistema de chat.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from .schemas import (
    ChatRequest,
    ChatResponse,
    IntentionInfo,
    IntentionListResponse,
    GatilloInfo,
    GatilloListResponse,
)
from .config import INTENTIONS, GATILLOS, Intention
from .service import get_chat_service

router = APIRouter()


@router.post(
    "/message",
    response_model=ChatResponse,
    summary="Procesar mensaje de chat",
    description=(
        "Recibe un mensaje del usuario, clasifica la intención y el semáforo, "
        "y retorna la respuesta apropiada con fuentes y acciones sugeridas."
    ),
)
async def send_message(request: ChatRequest) -> ChatResponse:
    """
    Endpoint principal del chat.

    Flujo:
    1. Clasifica la intención del mensaje (13 categorías)
    2. Determina el semáforo (Verde/Amarillo/Rojo)
    3. Verde → Responde con normativa y fuentes
    4. Amarillo → Pide contexto mínimo
    5. Rojo → Alerta y deriva a asesor
    """
    try:
        service = get_chat_service()
        return await service.process_message(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando el mensaje: {str(e)}",
        )


@router.post(
    "/message/stream",
    summary="Procesar mensaje de chat (streaming SSE)",
    description=(
        "Versión streaming del endpoint de chat. Emite eventos SSE a medida que "
        "el sistema procesa la consulta: clasificación, búsqueda RAG y tokens LLM. "
        "El usuario ve la primera respuesta en ~1s en vez de esperar ~10s."
    ),
)
async def send_message_stream(request: ChatRequest) -> StreamingResponse:
    """
    Endpoint streaming. Emite eventos Server-Sent Events (SSE):
      - status: etapa actual (clasificando / buscando / generando)
      - classification: intención y semáforo detectados
      - sources: fuentes normativas encontradas
      - token: fragmento de texto del LLM
      - done: señal de fin con actions y disclaimers
    """
    try:
        service = get_chat_service()
        return StreamingResponse(
            service.stream_message(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",   # Desactiva buffering en Nginx
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error iniciando streaming: {str(e)}",
        )


@router.get(
    "/intentions",
    response_model=IntentionListResponse,
    summary="Listar intenciones disponibles",
    description="Retorna las 13 intenciones del sistema con sus descripciones y ejemplos.",
)
async def list_intentions() -> IntentionListResponse:
    """Lista todas las intenciones del sistema."""
    intentions = [
        IntentionInfo(
            id=config.id.value,
            name=config.name,
            description=config.description,
            example_questions=config.example_questions,
        )
        for config in INTENTIONS.values()
        if config.id != Intention.FUERA_DE_ALCANCE
    ]

    return IntentionListResponse(
        intentions=intentions,
        total=len(intentions),
    )


@router.get(
    "/gatillos",
    response_model=GatilloListResponse,
    summary="Listar gatillos ROJO",
    description="Retorna todos los gatillos (triggers) configurados que activan el semáforo ROJO.",
)
async def list_gatillos() -> GatilloListResponse:
    """Lista todos los gatillos configurados."""
    gatillos = []
    for intention, gatillo_list in GATILLOS.items():
        intention_name = INTENTIONS[intention].name
        for gatillo in gatillo_list:
            gatillos.append(GatilloInfo(
                intention=intention.value,
                intention_name=intention_name,
                trigger_phrases=gatillo.trigger_phrases,
                derivation_reason=gatillo.derivation_reason,
            ))

    return GatilloListResponse(
        gatillos=gatillos,
        total=len(gatillos),
    )
