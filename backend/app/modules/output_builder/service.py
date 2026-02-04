"""
Output Builder - Service
Construye outputs estructurados por herramienta
"""

from typing import List, Dict, Any

from app.modules.reasoning.legal_logic import ReasoningResult, Viability
from app.modules.rag.interfaces import Evidence, RAGResult
from app.modules.risk_engine.levels import RiskAssessment, RiskLevel
from app.modules.gap_engine.evaluator import GapAnalysisResult
from app.modules.validation.flags import ValidationResult, ValidationFlag

from .schema_binder import (
    ToolOutput,
    OutputType,
    OutputSection,
    EvidenceReference,
    Disclaimer,
    ViabilityIndicator,
    EvaluationOutput,
    QueryOutput,
)
from .language_enforcer import ConditionalLanguageEnforcer


class OutputBuilder:
    """
    Constructor de outputs estructurados.
    """

    def __init__(self):
        self.language_enforcer = ConditionalLanguageEnforcer()

    # Disclaimers estándar
    STANDARD_DISCLAIMERS = [
        Disclaimer(
            text="Este análisis no constituye asesoría legal profesional",
            type="legal",
            prominent=True,
        ),
        Disclaimer(
            text="Las normas pueden haber sido modificadas. Verificar vigencia",
            type="limitation",
            prominent=False,
        ),
        Disclaimer(
            text="Para decisiones importantes, consultar con un abogado especializado",
            type="recommendation",
            prominent=False,
        ),
    ]

    async def build(
        self,
        tool_id: int,
        reasoning: ReasoningResult | None = None,
        evidence: List[Evidence] | None = None,
        risk: RiskAssessment | None = None,
        gaps: GapAnalysisResult | None = None,
        assumptions: List[str] | None = None,
        conditional_language: bool = True,
        confidence: float = 0.5,
    ) -> ToolOutput:
        """
        Construye output completo para una herramienta.
        """
        # Determinar viabilidad
        viability = None
        if reasoning:
            viability = (
                ViabilityIndicator.VIABLE
                if reasoning.viability == Viability.VIABLE
                else ViabilityIndicator.INVIABLE_WITH_ALT
            )

        # Construir summary
        summary = self._build_summary(reasoning, risk, gaps)

        # Aplicar lenguaje condicional si aplica
        if conditional_language:
            summary = self.language_enforcer.enforce(summary, confidence)

        # Construir secciones
        sections = self._build_sections(reasoning, risk, gaps, confidence)

        # Convertir evidencia
        evidence_refs = self._convert_evidence(evidence) if evidence else []

        # Recopilar supuestos y limitaciones
        all_assumptions = assumptions or []
        if reasoning:
            all_assumptions.extend(reasoning.assumptions)

        all_limitations = []
        if reasoning:
            all_limitations.extend(reasoning.limitations)

        # Determinar si escalar
        escalation = self._should_escalate(reasoning, risk, confidence)

        # Construir output
        output = ToolOutput(
            output_type=self._get_output_type(tool_id),
            tool_id=tool_id,
            viability=viability,
            summary=summary,
            sections=sections,
            evidence=evidence_refs,
            grounding_ratio=self._calculate_grounding_ratio(evidence_refs),
            assumptions=all_assumptions,
            limitations=all_limitations,
            disclaimers=self.STANDARD_DISCLAIMERS.copy(),
            alternatives=reasoning.alternatives if reasoning else [],
            path_to_viability=reasoning.path_to_viability if reasoning else None,
            next_steps=self._generate_next_steps(reasoning, gaps),
            escalation_recommended=escalation,
            confidence_level=self._confidence_to_level(confidence),
        )

        return output

    def build_validation_error(
        self,
        validation_result: ValidationResult
    ) -> ToolOutput:
        """Construye output para error de validación"""
        summary = "No se puede completar el análisis debido a problemas de validación."

        sections = [
            OutputSection(
                title="Problemas encontrados",
                content="\n".join([
                    f"- {issue.message}" for issue in validation_result.issues
                ]),
                order=1,
            ),
        ]

        if validation_result.missing_fields:
            sections.append(OutputSection(
                title="Campos faltantes",
                content=", ".join(validation_result.missing_fields),
                order=2,
            ))

        return ToolOutput(
            output_type=OutputType.EVALUATION,
            tool_id=0,
            summary=summary,
            sections=sections,
            disclaimers=self.STANDARD_DISCLAIMERS,
            escalation_recommended=False,
        )

    def build_insufficient_evidence(
        self,
        rag_result: RAGResult | None = None,
        orientation_only: bool = True,
        advisor_recommendation: bool = True,
    ) -> ToolOutput:
        """Construye output para evidencia insuficiente"""
        summary = (
            "No tengo información suficiente para responder con seguridad. "
            "Te recomiendo consultar con un especialista."
        )

        sections = [
            OutputSection(
                title="Orientación general",
                content=(
                    "Aunque no puedo darte una respuesta definitiva, "
                    "te sugiero los siguientes pasos:"
                ),
                order=1,
                is_conditional=True,
            ),
        ]

        disclaimers = self.STANDARD_DISCLAIMERS.copy()
        disclaimers.insert(0, Disclaimer(
            text="Esta respuesta está limitada por falta de información suficiente",
            type="limitation",
            prominent=True,
        ))

        return ToolOutput(
            output_type=OutputType.QUERY_RESPONSE,
            tool_id=2,
            summary=summary,
            sections=sections,
            disclaimers=disclaimers,
            escalation_recommended=True,
            confidence_level="LOW",
            uncertainty_flags={
                "insufficient_evidence": True,
                "orientation_only": orientation_only,
            },
        )

    def build_contradiction_detected(
        self,
        rag_result: RAGResult,
        trigger_advisor_package: bool = True,
    ) -> ToolOutput:
        """Construye output cuando se detectan contradicciones"""
        summary = (
            "Se detectaron fuentes con información contradictoria. "
            "Se recomienda validación con un especialista."
        )

        sections = [
            OutputSection(
                title="Contradicciones detectadas",
                content="Las fuentes consultadas presentan información que podría ser contradictoria.",
                order=1,
            ),
            OutputSection(
                title="Recomendación",
                content=(
                    "Debido a la contradicción en las fuentes, se recomienda "
                    "consultar directamente con un abogado especializado."
                ),
                order=2,
            ),
        ]

        return ToolOutput(
            output_type=OutputType.EVALUATION,
            tool_id=0,
            summary=summary,
            sections=sections,
            disclaimers=self.STANDARD_DISCLAIMERS,
            escalation_recommended=True,
            confidence_level="LOW",
            uncertainty_flags={
                "contradictions_detected": True,
                "requires_specialist": True,
            },
        )

    def _build_summary(
        self,
        reasoning: ReasoningResult | None,
        risk: RiskAssessment | None,
        gaps: GapAnalysisResult | None,
    ) -> str:
        """Construye resumen del análisis"""
        parts = []

        if reasoning:
            parts.append(reasoning.viability_explanation)

        if risk and risk.overall_level == RiskLevel.HIGH:
            parts.append("Se identificaron factores de riesgo alto que requieren atención.")

        if gaps and gaps.missing > 0:
            parts.append(f"Se encontraron {gaps.missing} requisitos pendientes.")

        return " ".join(parts) if parts else "Análisis completado."

    def _build_sections(
        self,
        reasoning: ReasoningResult | None,
        risk: RiskAssessment | None,
        gaps: GapAnalysisResult | None,
        confidence: float,
    ) -> List[OutputSection]:
        """Construye secciones del output"""
        sections = []
        order = 1

        # Sección de condiciones legales
        if reasoning and reasoning.legal_conditions:
            content = "\n".join([
                f"- {c.description}: {c.status.value}"
                for c in reasoning.legal_conditions
            ])
            sections.append(OutputSection(
                title="Condiciones legales evaluadas",
                content=content,
                order=order,
            ))
            order += 1

        # Sección de brechas
        if gaps and gaps.missing > 0:
            content = "\n".join([
                f"- {g.requirement_name}"
                for g in gaps.gaps if g.status.value == "missing"
            ])
            sections.append(OutputSection(
                title="Requisitos pendientes",
                content=content,
                order=order,
            ))
            order += 1

        # Sección de riesgo
        if risk:
            content = f"Nivel de riesgo: {risk.overall_level.value}"
            if risk.high_risk_factors:
                content += "\nFactores de alto riesgo:\n" + "\n".join([
                    f"- {f}" for f in risk.high_risk_factors
                ])
            sections.append(OutputSection(
                title="Evaluación de riesgo",
                content=content,
                order=order,
            ))
            order += 1

        # Sección de alternativas
        if reasoning and reasoning.alternatives:
            content = "\n".join([f"- {alt}" for alt in reasoning.alternatives])
            sections.append(OutputSection(
                title="Alternativas para viabilidad",
                content=content,
                order=order,
                is_conditional=True,
            ))

        return sections

    def _convert_evidence(self, evidence: List[Evidence]) -> List[EvidenceReference]:
        """Convierte evidencia a referencias"""
        return [
            EvidenceReference(
                doc_id=e.doc_id,
                title=e.title,
                authority=e.authority,
                anchor=e.anchor,
                url=e.url,
            )
            for e in evidence
        ]

    def _calculate_grounding_ratio(self, evidence: List[EvidenceReference]) -> float:
        """Calcula ratio de grounding"""
        if not evidence:
            return 0.0
        # Simplificado: más evidencia = mejor ratio
        return min(len(evidence) / 5, 1.0)

    def _should_escalate(
        self,
        reasoning: ReasoningResult | None,
        risk: RiskAssessment | None,
        confidence: float,
    ) -> bool:
        """Determina si se debe recomendar escalamiento"""
        if confidence < 0.65:
            return True
        if risk and risk.overall_level == RiskLevel.HIGH:
            return True
        if reasoning and reasoning.escalation_recommended:
            return True
        return False

    def _generate_next_steps(
        self,
        reasoning: ReasoningResult | None,
        gaps: GapAnalysisResult | None,
    ) -> List[str]:
        """Genera lista de próximos pasos"""
        steps = []

        if gaps and gaps.next_actions:
            steps.extend(gaps.next_actions[:3])

        if reasoning and reasoning.alternatives:
            steps.append(f"Considerar: {reasoning.alternatives[0]}")

        if not steps:
            steps.append("Revisar los requisitos identificados")
            steps.append("Consultar con un especialista si hay dudas")

        return steps[:5]

    def _get_output_type(self, tool_id: int) -> OutputType:
        """Obtiene tipo de output según herramienta"""
        mapping = {
            1: OutputType.EVALUATION,
            2: OutputType.QUERY_RESPONSE,
            3: OutputType.ADVISOR_BRIEF,
            4: OutputType.COMPLIANCE_ROUTE,
        }
        return mapping.get(tool_id, OutputType.EVALUATION)

    def _confidence_to_level(self, confidence: float) -> str:
        """Convierte confidence a nivel"""
        if confidence >= 0.8:
            return "HIGH"
        elif confidence >= 0.65:
            return "MEDIUM"
        else:
            return "LOW"
