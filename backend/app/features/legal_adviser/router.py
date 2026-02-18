"""
Legal Adviser Feature - Router
Endpoint para generar paquete de asesor legal.
"""

from fastapi import APIRouter, HTTPException

from app.modules.intake.schemas import NormalizedProjectIntake

from .schemas import LegalAdviserResponse
from .service import get_legal_adviser_service

router = APIRouter()


@router.post("/intake", response_model=LegalAdviserResponse)
async def generate_adviser_package(intake: NormalizedProjectIntake):
    """
    Genera paquete de preparación para reunión con asesor legal.

    Recibe un NormalizedProjectIntake y retorna:
    - Perfil de la organización
    - Estado legal (SUNARP, RUC, APCI)
    - Tópicos críticos (alta prioridad)
    - Preguntas para el abogado
    - Documentos requeridos
    - Decisiones internas pendientes

    Args:
        intake: NormalizedProjectIntake con 1-3 organizaciones

    Returns:
        LegalAdviserResponse completo
    """
    try:
        service = get_legal_adviser_service()
        return await service.generate_from_intake(intake)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando paquete de asesor: {str(e)}")
