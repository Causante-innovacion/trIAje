"""
Evaluation Feature - Pipeline
Orquesta los módulos para evaluación de proyectos multi-organización.

Flujo:
    NormalizedProjectIntake (1-3 orgs)
            ↓
    LegalRequirementsResolver (reglas de negocio)
            ↓
    LegalRequirementsResult (gaps detectados)
            ↓
    RAG (justificar gaps con normativa) [opcional]
            ↓
    EvaluationResponse (viabilidad + semáforo)
"""

from app.modules.intake.schemas import (
    NormalizedProjectIntake,
    DerivationColor,
    RiskLevel,
)
from app.modules.legal_rules import (
    LegalRequirementsResolver,
    LegalRequirementsResult,
)
from app.modules.legal_rules.schemas import (
    RequirementStatus,
    GapSeverity,
)

from .schemas import (
    EvaluationRequest,
    EvaluationResponse,
    ViabilityStatus,
    TrafficLight,
    GapDetail,
    OrganizationEvaluation,
    RiskSummary,
    EvidenceSource,
)


class EvaluationPipeline:
    """
    Pipeline para evaluación de proyectos.

    Flujo simplificado:
    1. Resolver requisitos legales (reglas de negocio)
    2. Opcionalmente, buscar justificación RAG
    3. Construir response con viabilidad y semáforo
    """

    # Disclaimers obligatorios
    DISCLAIMERS = [
        "Esta información es orientativa y no constituye asesoría legal profesional.",
        "Se recomienda validar esta orientación con un abogado especializado antes de tomar decisiones.",
    ]

    def __init__(self):
        self.resolver = LegalRequirementsResolver()

    async def execute(self, request: EvaluationRequest) -> EvaluationResponse:
        """
        Ejecuta el pipeline de evaluación.
        """
        intake = request.intake

        # 1. Resolver requisitos legales
        requirements_result = self.resolver.resolve(intake)

        # 2. Opcionalmente, buscar justificación RAG
        evidence_sources = []
        if request.include_rag_justification:
            evidence_sources = await self._fetch_rag_justification(
                requirements_result,
                intake,
                max_queries=request.max_rag_queries,
            )

        # 3. Construir response
        return self._build_response(
            intake=intake,
            requirements_result=requirements_result,
            evidence_sources=evidence_sources,
        )

    async def _fetch_rag_justification(
        self,
        requirements_result: LegalRequirementsResult,
        intake: NormalizedProjectIntake,
        max_queries: int = 5,
    ) -> list[EvidenceSource]:
        """
        Busca justificación normativa para los gaps detectados.
        """
        evidence_sources = []

        try:
            from app.modules.rag import get_rag_module
            rag = get_rag_module()

            # Generar queries RAG
            rag_queries = self.resolver.get_rag_queries(requirements_result)

            # Limitar cantidad
            queries_to_run = rag_queries[:max_queries]

            # Obtener IDs de organizaciones
            org_ids = [org.id for org in intake.organizations]

            for query_info in queries_to_run:
                try:
                    result = await rag.retrieve_for_project(
                        query=query_info["query"],
                        organization_ids=org_ids,
                        top_k_initial=3,
                    )

                    # Agregar evidencia encontrada
                    for chunk in result.chunks[:2]:  # Top 2 por query
                        evidence_sources.append(EvidenceSource(
                            title=chunk.metadata.title,
                            authority_level=chunk.metadata.authority_level,
                            url=chunk.metadata.url,
                            relevance=f"Justifica: {query_info['gap_id']}",
                        ))
                except Exception:
                    # Si falla un query, continuar con los demás
                    pass

        except RuntimeError:
            # RAG no inicializado, continuar sin evidencia
            pass

        return evidence_sources

    def _build_response(
        self,
        intake: NormalizedProjectIntake,
        requirements_result: LegalRequirementsResult,
        evidence_sources: list[EvidenceSource],
    ) -> EvaluationResponse:
        """
        Construye el response de evaluación.
        """
        # Determinar viabilidad
        viability, viability_explanation = self._determine_viability(
            requirements_result
        )

        # Determinar semáforo
        traffic_light = self._determine_traffic_light(
            requirements_result,
            viability,
        )

        # Construir evaluación por organización
        org_evaluations = self._build_org_evaluations(requirements_result)

        # Construir gaps compartidos
        shared_gaps = [
            GapDetail(
                id=gap.id,
                organization_id=None,
                organization_name=None,
                severity=gap.severity,
                intention=gap.intention,
                description=gap.description,
                impact=gap.impact,
                recommendation=gap.recommendation,
            )
            for gap in requirements_result.shared_gaps
        ]

        # Construir resumen de riesgo
        risk_summary = self._build_risk_summary(requirements_result, traffic_light)

        # Generar próximos pasos
        next_steps = self._generate_next_steps(requirements_result)

        # Generar alternativas si no viable
        alternatives = []
        path_to_viability = None
        if viability == ViabilityStatus.NOT_VIABLE:
            alternatives, path_to_viability = self._generate_alternatives(
                requirements_result
            )

        # Disclaimers
        disclaimers = list(self.DISCLAIMERS)
        if requirements_result.requires_professional_advice:
            disclaimers.append(
                "IMPORTANTE: Este caso presenta complejidad que requiere "
                "atención de un profesional legal calificado."
            )

        # Determinar si se recomienda preparar paquete para asesor
        suggest_adviser_package = (
            requirements_result.requires_professional_advice
            or risk_summary.overall_level == RiskLevel.HIGH
            or (risk_summary.overall_level == RiskLevel.MEDIUM and confidence_level != "HIGH")
            or (confidence_level == "LOW" and requirements_result.total_gaps > 0)
        )
        adviser_package_reason: str | None = None
        if requirements_result.requires_professional_advice and requirements_result.professional_advice_reason:
            adviser_package_reason = requirements_result.professional_advice_reason
        elif suggest_adviser_package:
            adviser_package_reason = (
                "El nivel de riesgo y/o ambigüedad del caso justifica preparar preguntas "
                "específicas para un asesor legal antes de tomar decisiones."
            )

        return EvaluationResponse(
            viability=viability,
            viability_explanation=viability_explanation,
            traffic_light=traffic_light,
            organizations=org_evaluations,
            shared_gaps=shared_gaps,
            risk_summary=risk_summary,
            total_requirements=requirements_result.total_requirements,
            total_gaps=requirements_result.total_gaps,
            critical_gaps=requirements_result.critical_gaps,
            project_intentions=requirements_result.project_intentions,
            next_steps=next_steps,
            alternatives=alternatives,
            path_to_viability=path_to_viability,
            evidence_sources=evidence_sources,
            confidence_level=self._calculate_confidence(requirements_result, evidence_sources),
            assumptions=self._get_assumptions(),
            limitations=self._get_limitations(evidence_sources),
            suggest_adviser_package=suggest_adviser_package,
            adviser_package_reason=adviser_package_reason,
            disclaimers=disclaimers,
        )

    def _determine_viability(
        self,
        result: LegalRequirementsResult,
    ) -> tuple[ViabilityStatus, str]:
        """
        Determina el estado de viabilidad del proyecto.
        """
        if result.critical_gaps == 0 and result.total_gaps == 0:
            return (
                ViabilityStatus.VIABLE,
                "El proyecto cumple con los requisitos legales evaluados. "
                "No se detectaron brechas significativas."
            )

        if result.critical_gaps == 0 and result.total_gaps <= 3:
            return (
                ViabilityStatus.VIABLE_WITH_CONDITIONS,
                f"El proyecto es viable con {result.total_gaps} condiciones pendientes. "
                "Las brechas detectadas son subsanables."
            )

        if result.critical_gaps > 0 and result.critical_gaps <= 2:
            return (
                ViabilityStatus.VIABLE_WITH_CONDITIONS,
                f"El proyecto presenta {result.critical_gaps} brecha(s) crítica(s) "
                "que deben resolverse antes de continuar. "
                "Se recomienda atención prioritaria."
            )

        if result.critical_gaps > 2 or result.requires_professional_advice:
            return (
                ViabilityStatus.REQUIRES_REVIEW,
                f"El proyecto presenta {result.critical_gaps} brechas críticas. "
                "Se requiere revisión profesional antes de continuar."
            )

        return (
            ViabilityStatus.VIABLE_WITH_CONDITIONS,
            f"El proyecto presenta {result.total_gaps} brechas que deben atenderse."
        )

    def _determine_traffic_light(
        self,
        result: LegalRequirementsResult,
        viability: ViabilityStatus,
    ) -> TrafficLight:
        """
        Determina el semáforo de la evaluación.
        """
        if viability == ViabilityStatus.VIABLE:
            return TrafficLight.GREEN

        if viability == ViabilityStatus.NOT_VIABLE:
            return TrafficLight.RED

        if result.requires_professional_advice or result.critical_gaps > 2:
            return TrafficLight.RED

        if result.critical_gaps > 0:
            return TrafficLight.YELLOW

        return TrafficLight.YELLOW

    def _build_org_evaluations(
        self,
        result: LegalRequirementsResult,
    ) -> list[OrganizationEvaluation]:
        """
        Construye la evaluación detallada por organización.
        """
        org_evaluations = []

        for org_req in result.organizations:
            # Contar por status
            fulfilled = sum(
                1 for r in org_req.requirements
                if r.status == RequirementStatus.FULFILLED
            )
            partial = sum(
                1 for r in org_req.requirements
                if r.status == RequirementStatus.PARTIALLY_FULFILLED
            )
            not_fulfilled = sum(
                1 for r in org_req.requirements
                if r.status == RequirementStatus.NOT_FULFILLED
            )

            # Convertir gaps
            gaps = [
                GapDetail(
                    id=gap.id,
                    organization_id=gap.organization_id,
                    organization_name=gap.organization_name,
                    severity=gap.severity,
                    intention=gap.intention,
                    description=gap.description,
                    impact=gap.impact,
                    recommendation=gap.recommendation,
                )
                for gap in org_req.gaps
            ]

            # Determinar riesgo individual
            if org_req.critical_gaps > 0:
                risk_level = RiskLevel.HIGH
            elif org_req.gap_count > 2:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW

            org_evaluations.append(OrganizationEvaluation(
                organization_id=org_req.organization_id,
                organization_name=org_req.organization_name,
                role="",  # Se puede obtener del intake si es necesario
                requirements_fulfilled=fulfilled,
                requirements_partial=partial,
                requirements_not_fulfilled=not_fulfilled,
                gaps=gaps,
                detected_intentions=org_req.detected_intentions,
                risk_level=risk_level,
            ))

        return org_evaluations

    def _build_risk_summary(
        self,
        result: LegalRequirementsResult,
        traffic_light: TrafficLight,
    ) -> RiskSummary:
        """
        Construye el resumen de riesgo agregado.
        """
        # Determinar nivel general
        if result.critical_gaps > 2:
            overall_level = RiskLevel.HIGH
        elif result.critical_gaps > 0 or result.total_gaps > 5:
            overall_level = RiskLevel.MEDIUM
        else:
            overall_level = RiskLevel.LOW

        # Determinar color de derivación
        if traffic_light == TrafficLight.RED:
            derivation_color = DerivationColor.RED
        elif traffic_light == TrafficLight.YELLOW:
            derivation_color = DerivationColor.YELLOW
        else:
            derivation_color = DerivationColor.GREEN

        # Factores de riesgo
        risk_factors = []
        if result.critical_gaps > 0:
            risk_factors.append(f"{result.critical_gaps} brecha(s) crítica(s) detectada(s)")

        # Agregar factores de gaps críticos
        for org in result.organizations:
            for gap in org.gaps:
                if gap.severity == GapSeverity.CRITICAL:
                    risk_factors.append(gap.description[:100])

        for gap in result.shared_gaps:
            if gap.severity == GapSeverity.CRITICAL:
                risk_factors.append(f"[Compartido] {gap.description[:80]}")

        return RiskSummary(
            overall_level=overall_level,
            derivation_color=derivation_color,
            requires_professional_advice=result.requires_professional_advice,
            professional_advice_reason=result.professional_advice_reason,
            risk_factors=risk_factors[:5],  # Limitar a 5
        )

    def _generate_next_steps(
        self,
        result: LegalRequirementsResult,
    ) -> list[str]:
        """
        Genera los próximos pasos priorizados.
        """
        steps = []

        # Primero, gaps críticos
        for org in result.organizations:
            for gap in org.gaps:
                if gap.severity == GapSeverity.CRITICAL:
                    steps.append(f"[URGENTE] {gap.recommendation}")

        for gap in result.shared_gaps:
            if gap.severity == GapSeverity.CRITICAL:
                steps.append(f"[URGENTE] {gap.recommendation}")

        # Luego, gaps HIGH
        for org in result.organizations:
            for gap in org.gaps:
                if gap.severity == GapSeverity.HIGH:
                    steps.append(gap.recommendation)

        # Limitar y agregar paso final
        steps = steps[:7]

        if result.requires_professional_advice:
            steps.append("Agendar consulta con abogado especializado")

        return steps

    def _generate_alternatives(
        self,
        result: LegalRequirementsResult,
    ) -> tuple[list[str], str]:
        """
        Genera alternativas cuando el proyecto no es viable.
        """
        alternatives = []
        path = ""

        # Analizar gaps críticos para sugerir alternativas
        critical_gaps = []
        for org in result.organizations:
            critical_gaps.extend([g for g in org.gaps if g.severity == GapSeverity.CRITICAL])

        if any("personería" in g.description.lower() for g in critical_gaps):
            alternatives.append(
                "Formalizar la organización como asociación civil antes de continuar"
            )
            path = "Proceso de formalización (2-4 semanas típicamente)"

        if any("apci" in g.description.lower() for g in critical_gaps):
            alternatives.append(
                "Completar registro en APCI antes de recibir fondos internacionales"
            )
            if not path:
                path = "Registro APCI (30-60 días hábiles)"

        if not alternatives:
            alternatives.append("Resolver las brechas críticas identificadas")
            path = "Atender brechas en orden de prioridad"

        return alternatives, path

    def _calculate_confidence(
        self,
        result: LegalRequirementsResult,
        evidence: list[EvidenceSource],
    ) -> str:
        """
        Calcula el nivel de confianza de la evaluación.
        """
        if result.total_requirements == 0:
            return "LOW"

        fulfilled_ratio = sum(
            org.fulfilled_count for org in result.organizations
        ) / max(result.total_requirements, 1)

        if fulfilled_ratio > 0.8 and len(evidence) > 3:
            return "HIGH"
        elif fulfilled_ratio > 0.5 or len(evidence) > 1:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_assumptions(self) -> list[str]:
        """
        Retorna las asunciones de la evaluación.
        """
        return [
            "La información proporcionada es veraz y completa",
            "Las respuestas reflejan la situación actual de la organización",
            "La normativa aplicada es la vigente a la fecha de evaluación",
        ]

    def _get_limitations(self, evidence: list[EvidenceSource]) -> list[str]:
        """
        Retorna las limitaciones de la evaluación.
        """
        limitations = [
            "Esta evaluación se basa en información declarativa",
            "No reemplaza una auditoría legal completa",
        ]

        if not evidence:
            limitations.append(
                "No se pudo obtener justificación normativa del sistema RAG"
            )

        return limitations


# Instancia singleton
_pipeline: EvaluationPipeline | None = None


def get_evaluation_pipeline() -> EvaluationPipeline:
    """Obtiene el pipeline de evaluación"""
    global _pipeline
    if _pipeline is None:
        _pipeline = EvaluationPipeline()
    return _pipeline
