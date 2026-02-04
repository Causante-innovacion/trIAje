"""
Advisor Prep Feature - Router
"""

from fastapi import APIRouter, HTTPException
from .schemas import AdvisorPrepRequest, AdvisorPrepResponse, AdvisorPrepQuestions
from .service import AdvisorPrepService

router = APIRouter()
service = AdvisorPrepService()


@router.get("/questions", response_model=AdvisorPrepQuestions)
async def get_advisor_prep_questions():
    """Obtiene preguntas del formulario"""
    return await service.get_questions()


@router.post("/", response_model=AdvisorPrepResponse)
async def prepare_advisor_package(request: AdvisorPrepRequest):
    """
    Genera paquete de preparación para reunión con asesor.

    Incluye:
    - Resumen ejecutivo del caso
    - Issues legales identificados
    - Preguntas prioritarias
    - Documentos a llevar
    """
    try:
        return await service.prepare_package(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
