"""
Evaluation Feature - Router
Endpoints para evaluación de proyectos multi-organización.
"""

from fastapi import APIRouter, HTTPException

from app.modules.intake.schemas import NormalizedProjectIntake

from .schemas import EvaluationRequest, EvaluationResponse, EvaluationQuestions
from .service import get_evaluation_service

router = APIRouter()


@router.get("/questions", response_model=EvaluationQuestions)
async def get_evaluation_questions():
    """
    Obtiene las preguntas del formulario de evaluación.

    Retorna el conjunto de preguntas que el usuario debe responder
    antes de ejecutar la evaluación, organizadas por bloques.
    """
    service = get_evaluation_service()
    return await service.get_questions()


@router.post("/", response_model=EvaluationResponse)
async def evaluate_project(request: EvaluationRequest):
    """
    Evalúa un proyecto con múltiples organizaciones.

    Recibe un NormalizedProjectIntake (1-3 organizaciones) y retorna:
    - Viabilidad (viable/viable_with_conditions/not_viable/requires_review)
    - Semáforo (green/yellow/red)
    - Evaluación por organización con gaps detectados
    - Gaps compartidos entre organizaciones
    - Resumen de riesgo agregado
    - Próximos pasos priorizados
    - Evidencia normativa (si RAG está habilitado)
    - Disclaimers obligatorios

    Args:
        request: EvaluationRequest con intake y opciones

    Returns:
        EvaluationResponse completo
    """
    try:
        service = get_evaluation_service()
        return await service.evaluate(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en evaluación: {str(e)}")


@router.post("/intake", response_model=EvaluationResponse)
async def evaluate_intake_directly(
    intake: NormalizedProjectIntake,
    include_rag: bool = True,
):
    """
    Evalúa un intake normalizado directamente.

    Endpoint simplificado para cuando ya se tiene el NormalizedProjectIntake.

    Args:
        intake: NormalizedProjectIntake con 1-3 organizaciones
        include_rag: Si buscar justificación normativa vía RAG (default: True)

    Returns:
        EvaluationResponse completo
    """
    try:
        service = get_evaluation_service()
        return await service.evaluate_intake(intake, include_rag=include_rag)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en evaluación: {str(e)}")
