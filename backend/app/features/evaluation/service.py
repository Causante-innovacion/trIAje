"""
Evaluation Feature - Service
Business logic para evaluación de proyectos multi-organización.
"""

from app.modules.intake.schemas import (
    NormalizedProjectIntake,
    ToolType,
)
from app.modules.intake.questions import get_question_set

from .schemas import EvaluationRequest, EvaluationResponse, EvaluationQuestions
from .pipeline import EvaluationPipeline, get_evaluation_pipeline


class EvaluationService:
    """
    Servicio para evaluación de proyectos.
    """

    def __init__(self):
        self.pipeline = get_evaluation_pipeline()

    async def get_questions(self) -> EvaluationQuestions:
        """
        Obtiene las preguntas del intake para evaluación.
        """
        question_set = get_question_set(ToolType.EVALUATION)

        questions = []
        for block in question_set.blocks:
            for q in block.questions:
                questions.append({
                    "id": q.id,
                    "text": q.text,
                    "type": q.input_type.value,
                    "required": q.required,
                    "options": q.options,
                    "help_text": q.help_text,
                    "block": block.id,
                    "block_name": block.name,
                })

        return EvaluationQuestions(
            questions=questions,
            tool_id=1,
            tool_name="Evaluar proyecto",
        )

    async def evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        """
        Ejecuta la evaluación de un proyecto.

        Args:
            request: EvaluationRequest con NormalizedProjectIntake

        Returns:
            EvaluationResponse con viabilidad, gaps, y semáforo
        """
        return await self.pipeline.execute(request)

    async def evaluate_intake(
        self,
        intake: NormalizedProjectIntake,
        include_rag: bool = True,
    ) -> EvaluationResponse:
        """
        Evalúa un intake normalizado directamente.

        Args:
            intake: NormalizedProjectIntake
            include_rag: Si buscar justificación RAG

        Returns:
            EvaluationResponse
        """
        request = EvaluationRequest(
            intake=intake,
            include_rag_justification=include_rag,
        )
        return await self.pipeline.execute(request)


# Instancia singleton
_service: EvaluationService | None = None


def get_evaluation_service() -> EvaluationService:
    """Obtiene el servicio de evaluación"""
    global _service
    if _service is None:
        _service = EvaluationService()
    return _service
