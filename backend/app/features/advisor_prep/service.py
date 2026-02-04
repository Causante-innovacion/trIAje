"""
Advisor Prep Feature - Service
"""

from app.modules.intake import IntakeModule
from app.modules.intake.schemas import IntakeData
from app.modules.validation import ValidationModule
from app.modules.reasoning import ReasoningModule
from app.modules.gap_engine import GapEngine
from app.modules.risk_engine import RiskEngine
from app.modules.advisor_package import AdvisorPackageGenerator

from .schemas import AdvisorPrepRequest, AdvisorPrepResponse, AdvisorPrepQuestions


class AdvisorPrepService:
    """Servicio para preparación de reunión con asesor"""

    def __init__(self):
        self.intake = IntakeModule()
        self.validation = ValidationModule()
        self.reasoning = ReasoningModule()
        self.gap = GapEngine()
        self.risk = RiskEngine()
        self.advisor_gen = AdvisorPackageGenerator()

    async def get_questions(self) -> AdvisorPrepQuestions:
        """Obtiene preguntas del intake"""
        question_set = self.intake.render_question_set(tool_id=3)
        return AdvisorPrepQuestions(
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
        )

    async def prepare_package(self, request: AdvisorPrepRequest) -> AdvisorPrepResponse:
        """Genera paquete para reunión con asesor"""
        # 1. Normalizar intake
        intake_data = IntakeData(
            tool_id=3,
            answers={
                "advisor_type": request.advisor_type,
                "meeting_goal": request.meeting_goals,
                "org_type": request.organization_type,
                "has_legal_entity": request.has_legal_entity,
            },
        )
        normalized = await self.intake.process(intake_data)

        # 2. Analizar
        risk = await self.risk.calculate(intake=normalized)
        gaps = await self.gap.evaluate(normalized)

        # 3. Generar paquete
        package = await self.advisor_gen.generate(
            case=normalized,
            risk=risk,
            gaps=gaps,
        )

        return AdvisorPrepResponse(
            recommended_advisor_type=package.recommended_advisor_type.value,
            advisor_type_reason=package.advisor_type_reason or "",
            executive_summary=package.executive_summary or "",
            meeting_objectives=package.meeting_objectives,
            legal_issues=[
                {
                    "id": i.id,
                    "title": i.title,
                    "severity": i.severity,
                    "area": i.area,
                }
                for i in package.legal_issues
            ],
            priority_issues=[i.title for i in package.legal_issues if i.severity == "critical"],
            questions_for_advisor=[q.question for q in package.open_questions],
            priority_questions=package.priority_questions,
            documents_to_bring=[d.name for d in package.documents_to_bring],
            documents_to_prepare=[d.name for d in package.documents_to_prepare],
            generated_at=package.generated_at,
            limitations=package.limitations,
        )
