"""
Evaluation Feature - Service
Business logic para evaluación de proyectos
"""

from .schemas import EvaluationRequest, EvaluationResponse, EvaluationQuestions
from .pipeline import EvaluationPipeline
from app.modules.intake import IntakeModule


class EvaluationService:
    """
    Servicio para evaluación de proyectos.
    """

    def __init__(self):
        self.pipeline = EvaluationPipeline()
        self.intake = IntakeModule()

    async def get_questions(self) -> EvaluationQuestions:
        """
        Obtiene las preguntas del intake para evaluación.
        """
        question_set = self.intake.render_question_set(tool_id=1)

        return EvaluationQuestions(
            questions=[
                {
                    "id": q.id,
                    "text": q.text,
                    "type": q.input_type.value,
                    "required": q.required,
                    "options": q.options,
                    "help_text": q.help_text,
                }
                for q in question_set.questions
            ],
            tool_id=1,
            tool_name="Evaluar proyecto",
        )

    async def evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        """
        Ejecuta la evaluación de un proyecto.
        """
        return await self.pipeline.execute(request)

    async def evaluate_civic_output(
        self,
        civic_generator_output: dict,
        additional_context: dict | None = None,
    ) -> EvaluationResponse:
        """
        Evalúa la salida del Generador Cívico.
        """
        # Extraer datos del output del generador cívico
        request = EvaluationRequest(
            organization_type=civic_generator_output.get("organization_type", "Otro"),
            has_legal_entity=civic_generator_output.get("has_legal_entity", False),
            project_areas=civic_generator_output.get("areas", ["Otro"]),
            funding_source=civic_generator_output.get("funding_source"),
            urgency=civic_generator_output.get("urgency"),
            project_description=civic_generator_output.get("description"),
            civic_generator_output=civic_generator_output,
        )

        return await self.pipeline.execute(request)
