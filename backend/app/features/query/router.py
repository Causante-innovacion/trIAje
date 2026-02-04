"""
Query Feature - Router
"""

from fastapi import APIRouter, HTTPException
from .schemas import QueryRequest, QueryResponse, QueryQuestions
from .service import QueryService

router = APIRouter()
service = QueryService()


@router.get("/questions", response_model=QueryQuestions)
async def get_query_questions():
    """Obtiene preguntas del formulario de consulta"""
    return await service.get_questions()


@router.post("/", response_model=QueryResponse)
async def answer_query(request: QueryRequest):
    """
    Responde una consulta legal puntual.

    Analiza la pregunta, busca evidencia relevante,
    y proporciona una respuesta con el nivel de confianza apropiado.
    """
    try:
        return await service.answer_query(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
