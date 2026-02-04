"""
Evaluation Feature - Router
Endpoints para evaluación de proyectos
"""

from fastapi import APIRouter, HTTPException
from .schemas import EvaluationRequest, EvaluationResponse, EvaluationQuestions
from .service import EvaluationService

router = APIRouter()
service = EvaluationService()


@router.get("/questions", response_model=EvaluationQuestions)
async def get_evaluation_questions():
    """
    Obtiene las preguntas del formulario de evaluación.

    Retorna el conjunto de preguntas que el usuario debe responder
    antes de ejecutar la evaluación.
    """
    return await service.get_questions()


@router.post("/", response_model=EvaluationResponse)
async def evaluate_project(request: EvaluationRequest):
    """
    Evalúa un proyecto.

    Analiza la viabilidad legal del proyecto, identifica riesgos,
    brechas regulatorias, y proporciona recomendaciones.

    Retorna:
    - Viabilidad (verde/amarillo)
    - Evaluación de riesgo
    - Brechas identificadas
    - Alternativas si aplica
    - Próximos pasos recomendados
    """
    try:
        return await service.evaluate(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en evaluación: {str(e)}")


@router.post("/civic-generator", response_model=EvaluationResponse)
async def evaluate_civic_generator_output(civic_output: dict):
    """
    Evalúa la salida del Generador Cívico.

    Endpoint especializado para procesar outputs del
    GPT Generador Cívico y evaluarlos legalmente.
    """
    try:
        return await service.evaluate_civic_output(civic_output)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en evaluación: {str(e)}")
