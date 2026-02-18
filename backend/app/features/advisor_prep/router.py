"""
Advisor Prep Feature - Router
"""

from fastapi import APIRouter, HTTPException
from .schemas import AdvisorPrepFromChatRequest
from .service import get_advisor_prep_service

router = APIRouter()


@router.post("/from-chat")
async def prepare_from_chat(request: AdvisorPrepFromChatRequest):
    """
    Genera paquete de preparación para asesor a partir de la conversación del chat.

    Recibe el historial de conversación y usa el LLM para:
    - Extraer el contexto (organización, área legal, problemas detectados)
    - Generar preguntas específicas para el asesor
    - Listar documentos relevantes
    - Identificar temas críticos a tratar
    """
    try:
        service = get_advisor_prep_service()
        return await service.generate_from_chat(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando paquete: {str(e)}")
