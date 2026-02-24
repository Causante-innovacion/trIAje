"""
Compliance Feature - Router
"""

from fastapi import APIRouter, HTTPException
from .schemas import ComplianceRequest, ComplianceResponse, ComplianceQuestions
from .service import get_compliance_service

router = APIRouter()


@router.get("/questions", response_model=ComplianceQuestions)
async def get_compliance_questions():
    """Obtiene preguntas del formulario"""
    service = get_compliance_service()
    return await service.get_questions()


@router.post("/", response_model=ComplianceResponse)
async def generate_compliance_route(request: ComplianceRequest):
    """
    Genera ruta de cumplimiento paso a paso.

    Incluye:
    - Milestones ordenados por dependencia
    - Fases de ejecución
    - Documentos requeridos
    - Estimaciones de tiempo y costo
    """
    try:
        service = get_compliance_service()
        return await service.generate_route(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
