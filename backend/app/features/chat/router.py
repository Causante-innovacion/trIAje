"""
Chat Feature - Router
Endpoints FastAPI para el sistema de chat.
"""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
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


@router.post(
    "/upload",
    summary="Subir archivo para análisis en el chat",
    description=(
        "Acepta un PDF, DOCX o TXT, extrae su texto y retorna un preview que el frontend "
        "puede enviar como mensaje al chat para que trIAje lo analice."
    ),
)
async def upload_chat_file(
    file: UploadFile = File(...),
    tool: str = Form("general"),
):
    """
    Sube un archivo desde el chat.

    Flujo:
    1. Valida tipo y tamaño del archivo.
     2. Extrae texto (PDF via PyMuPDF, DOCX via python-docx, TXT via UTF-8).
    3. Retorna filename + content_preview (hasta 3000 chars) para que el frontend
         lo pueda re-enviar como mensaje a trIAje.
    """
    import io

    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }
    # Algunos browsers envían application/octet-stream; confiar también en la extensión
    filename = file.filename or "archivo"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if file.content_type not in allowed_types and ext not in ("pdf", "docx", "txt"):
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Solo se aceptan PDF, DOCX o TXT.",
        )

    content = await file.read()
    size_kb = round(len(content) / 1024, 1)

    max_size_kb = 10 * 1024  # 10 MB
    if size_kb > max_size_kb:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo excede el tamaño máximo de 10 MB.",
        )

    text_preview = ""
    try:
        if ext == "pdf":
            import fitz  # PyMuPDF
            doc = fitz.open(stream=content, filetype="pdf")
            pages_text = []
            for page in doc[:10]:  # máximo 10 páginas
                pages_text.append(page.get_text())
            doc.close()
            full_text = "\n".join(pages_text).strip()
            text_preview = full_text[:2000] + ("..." if len(full_text) > 2000 else "")
        elif ext == "docx":
            import docx as docx_lib
            doc = docx_lib.Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n".join(paragraphs).strip()
            text_preview = full_text[:2000] + ("..." if len(full_text) > 2000 else "")
        elif ext == "txt":
            full_text = content.decode("utf-8", errors="replace").strip()
            text_preview = full_text[:2000] + ("..." if len(full_text) > 2000 else "")
    except Exception:
        text_preview = ""

    return {
        "filename": filename,
        "size_kb": size_kb,
        "content_preview": text_preview,
        "message": f"Archivo '{filename}' cargado correctamente ({size_kb} KB).",
    }
