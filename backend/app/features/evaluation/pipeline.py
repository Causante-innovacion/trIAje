"""
Evaluation Feature - Pipeline
Orquesta los módulos para evaluación de proyectos
"""

from app.modules.intake import IntakeModule
from app.modules.intake.schemas import IntakeData, NormalizedIntake
from app.modules.validation import ValidationModule
from app.modules.rag import RAGModule
from app.modules.reasoning import ReasoningModule
from app.modules.gap_engine import GapEngine
from app.modules.risk_engine import RiskEngine
from app.modules.output_builder import OutputBuilder
from app.modules.advisor_package import AdvisorPackageGenerator

from .schemas import EvaluationRequest, EvaluationResponse


class EvaluationPipeline:
    """
    Pipeline para Modo 1: Evaluar proyecto.

    Módulos usados:
    - intake
    - validation
    - rag (cuando esté implementado)
    - reasoning
    - gap_engine
    - risk_engine
    - output_builder
    - advisor_package (condicional)
    """

    def __init__(self):
        self.intake = IntakeModule()
        self.validation = ValidationModule()
        self.rag = RAGModule()  # Sin vector store por ahora
        self.reasoning = ReasoningModule()
        self.gap = GapEngine()
        self.risk = RiskEngine()
        self.output = OutputBuilder()
        self.advisor = AdvisorPackageGenerator()

    async def execute(self, request: EvaluationRequest) -> EvaluationResponse:
        """
        Ejecuta el pipeline completo de evaluación.
        """
        # 1. Convertir request a IntakeData
        intake_data = IntakeData(
            tool_id=1,
            answers={
                "org_type": request.organization_type,
                "has_legal_entity": request.has_legal_entity,
                "project_area": request.project_areas,
                "funding_source": request.funding_source,
                "urgency": request.urgency,
            },
            metadata={
                "civic_generator_output": request.civic_generator_output,
            }
        )

        # 2. Normalizar intake
        normalized = await self.intake.process(intake_data)

        # 3. Validar
        validation_result = await self.validation.check(normalized)

        if validation_result.flag.value == "block":
            return self._build_validation_error_response(validation_result)

        # 4. RAG (placeholder - retorna evidencia vacía por ahora)
        rag_result = await self.rag.retrieve_and_ground(
            query=request.project_description or "evaluar proyecto",
            indices=None,
        )

        # 5. Calcular riesgo
        risk_assessment = await self.risk.calculate(intake=normalized)

        # 6. Evaluar brechas
        gap_result = await self.gap.evaluate(normalized)

        # 7. Razonamiento
        reasoning_result = await self.reasoning.analyze(
            intake_data=normalized,
            retrieved_evidence=rag_result.chunks,
            risk_level=risk_assessment.overall_level.value,
            rag_confidence=rag_result.confidence,
        )

        # 8. Construir output
        output = await self.output.build(
            tool_id=1,
            reasoning=reasoning_result,
            evidence=rag_result.evidence,
            risk=risk_assessment,
            gaps=gap_result,
            confidence=rag_result.confidence,
        )

        # 9. Generar advisor package si riesgo alto
        advisor_package = None
        if risk_assessment.overall_level.value == "HIGH" or output.escalation_recommended:
            advisor_package = await self.advisor.generate(
                case=normalized,
                analysis=reasoning_result,
                risk=risk_assessment,
                gaps=gap_result,
            )

        # 10. Construir response
        return self._build_response(
            output, reasoning_result, risk_assessment, gap_result, normalized
        )

    def _build_response(
        self,
        output,
        reasoning,
        risk,
        gaps,
        intake: NormalizedIntake,
    ) -> EvaluationResponse:
        """Construye el response final"""
        # Determinar semáforo
        traffic_light = "green" if output.viability and output.viability.value == "viable" else "yellow"

        return EvaluationResponse(
            viability=output.viability.value if output.viability else "inviable_with_alternatives",
            viability_explanation=output.summary,
            traffic_light=traffic_light,
            risk_assessment={
                "level": risk.overall_level.value,
                "factors": risk.high_risk_factors,
            },
            gaps_found=[
                {
                    "requirement": g.requirement_name,
                    "status": g.status.value,
                    "priority": g.priority.value,
                }
                for g in gaps.gaps if g.status.value != "satisfied"
            ],
            conditions_evaluated=[
                {
                    "id": c.id,
                    "description": c.description,
                    "status": c.status.value,
                }
                for c in reasoning.legal_conditions
            ],
            alternatives=output.alternatives,
            path_to_viability=output.path_to_viability,
            next_steps=output.next_steps,
            escalation_recommended=output.escalation_recommended,
            evidence_sources=[
                {"title": e.title, "authority": e.authority}
                for e in output.evidence
            ],
            confidence_level=output.confidence_level,
            assumptions=output.assumptions,
            limitations=output.limitations,
            disclaimers=[d.text for d in output.disclaimers],
        )

    def _build_validation_error_response(self, validation_result) -> EvaluationResponse:
        """Construye response para error de validación"""
        return EvaluationResponse(
            viability="inviable_with_alternatives",
            viability_explanation="No se puede completar la evaluación debido a datos incompletos o inconsistentes.",
            traffic_light="yellow",
            risk_assessment={"level": "MEDIUM", "factors": []},
            gaps_found=[],
            conditions_evaluated=[],
            next_steps=["Completar los datos faltantes", "Revisar inconsistencias"],
            escalation_recommended=False,
            confidence_level="LOW",
            assumptions=[],
            limitations=["Validación fallida"],
            disclaimers=["Este análisis no constituye asesoría legal"],
        )
