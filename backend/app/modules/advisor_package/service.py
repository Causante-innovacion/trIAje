"""
Advisor Package Generator - Service
Genera paquete de preparación para reunión con asesor
"""

from typing import List
from app.modules.intake.schemas import NormalizedIntake
from app.modules.reasoning.legal_logic import ReasoningResult
from app.modules.risk_engine.levels import RiskAssessment
from app.modules.gap_engine.evaluator import GapAnalysisResult, GapStatus

from .structurer import (
    AdvisorPackage,
    AdvisorType,
    ExportFormat,
    CaseStructure,
    LegalIssue,
    OpenQuestion,
    DocumentRequest,
)


class AdvisorPackageGenerator:
    """
    Genera paquetes de preparación para reuniones con asesores.
    """

    # Mapeo de áreas legales a tipos de asesor
    AREA_TO_ADVISOR: dict[str, AdvisorType] = {
        "Tributario (SUNAT)": AdvisorType.TRIBUTARISTA,
        "Laboral": AdvisorType.LABORALISTA,
        "Cooperación internacional (APCI)": AdvisorType.CORPORATIVO,
        "Contratos": AdvisorType.CORPORATIVO,
        "Formalización": AdvisorType.NOTARIO,
        "Propiedad intelectual": AdvisorType.CORPORATIVO,
    }

    async def generate(
        self,
        case: NormalizedIntake,
        analysis: ReasoningResult | None = None,
        risk: RiskAssessment | None = None,
        gaps: GapAnalysisResult | None = None,
        format: str = "json",
    ) -> AdvisorPackage:
        """
        Genera paquete completo para asesor.

        Args:
            case: Datos del caso (intake)
            analysis: Resultado del análisis de reasoning
            risk: Evaluación de riesgo
            gaps: Análisis de brechas
            format: Formato de exportación

        Returns:
            AdvisorPackage listo para usar
        """
        # 1. Determinar tipo de asesor recomendado
        advisor_type, advisor_reason = self._determine_advisor_type(case)

        # 2. Estructurar el caso
        case_structure = self._structure_case(case, analysis, risk, gaps)

        # 3. Identificar issues legales
        legal_issues = self._identify_issues(case, analysis, gaps)

        # 4. Generar preguntas abiertas
        open_questions = self._generate_questions(case, analysis, legal_issues)

        # 5. Listar documentos necesarios
        docs_to_bring, docs_to_prepare = self._list_documents(case, gaps)

        # 6. Generar resumen ejecutivo
        executive_summary = self._generate_executive_summary(
            case, analysis, risk, gaps
        )

        # 7. Definir objetivos de la reunión
        meeting_objectives = self._define_meeting_objectives(
            case, legal_issues
        )

        # 8. Construir paquete
        package = AdvisorPackage(
            format=ExportFormat(format),
            recommended_advisor_type=advisor_type,
            advisor_type_reason=advisor_reason,
            case_structure=case_structure,
            legal_issues=legal_issues,
            issues_by_severity=self._group_issues_by_severity(legal_issues),
            open_questions=open_questions,
            priority_questions=[q.question for q in open_questions if q.priority == "high"],
            documents_to_bring=docs_to_bring,
            documents_to_prepare=docs_to_prepare,
            executive_summary=executive_summary,
            meeting_objectives=meeting_objectives,
            gpt_legal_analysis_notes=self._generate_analysis_notes(analysis),
            limitations=[
                "Este paquete fue generado por GPT Legal y no constituye asesoría legal",
                "Verificar información con documentación oficial",
                "El asesor puede requerir información adicional",
            ],
        )

        return package

    def _determine_advisor_type(
        self,
        case: NormalizedIntake
    ) -> tuple[AdvisorType, str]:
        """Determina el tipo de asesor recomendado"""
        legal_area = case.legal_area

        if isinstance(legal_area, str):
            areas = [legal_area]
        elif isinstance(legal_area, list):
            areas = legal_area
        else:
            return (AdvisorType.GENERAL, "No se identificó área legal específica")

        # Buscar match
        for area in areas:
            if area in self.AREA_TO_ADVISOR:
                advisor = self.AREA_TO_ADVISOR[area]
                return (advisor, f"Recomendado por área: {area}")

        return (AdvisorType.GENERAL, "Asesoría legal general recomendada")

    def _structure_case(
        self,
        case: NormalizedIntake,
        analysis: ReasoningResult | None,
        risk: RiskAssessment | None,
        gaps: GapAnalysisResult | None,
    ) -> CaseStructure:
        """Estructura la información del caso"""
        return CaseStructure(
            organization_type=case.organization_type,
            has_legal_entity=case.has_legal_entity,
            main_concern=case.legal_question,
            preliminary_assessment=analysis.viability_explanation if analysis else None,
            identified_risks=[
                f.description for f in (risk.factors if risk else [])
                if f.level.value == "HIGH"
            ],
            identified_gaps=[
                g.requirement_name for g in (gaps.gaps if gaps else [])
                if g.status == GapStatus.MISSING
            ],
            viability_status=analysis.viability.value if analysis else None,
            alternatives_considered=analysis.alternatives if analysis else [],
        )

    def _identify_issues(
        self,
        case: NormalizedIntake,
        analysis: ReasoningResult | None,
        gaps: GapAnalysisResult | None,
    ) -> List[LegalIssue]:
        """Identifica issues legales para discutir"""
        issues = []

        # Issues desde condiciones legales
        if analysis:
            for condition in analysis.legal_conditions:
                if condition.status.value != "satisfied":
                    issues.append(LegalIssue(
                        id=condition.id,
                        title=condition.description,
                        description=f"Condición: {condition.status.value}",
                        severity="important" if condition.requirements else "informative",
                        area=case.legal_area if isinstance(case.legal_area, str) else "General",
                        questions_for_advisor=[
                            f"¿Cómo cumplir con: {condition.description}?",
                        ],
                    ))

        # Issues desde brechas
        if gaps:
            for gap in gaps.gaps:
                if gap.status in [GapStatus.MISSING, GapStatus.BLOCKED]:
                    issues.append(LegalIssue(
                        id=gap.requirement_id,
                        title=gap.requirement_name,
                        description=gap.description,
                        severity="critical" if gap.priority.value == "critical" else "important",
                        area=gap.authority,
                        questions_for_advisor=[
                            f"¿Cuál es el proceso para obtener {gap.requirement_name}?",
                            f"¿Qué documentos se necesitan para {gap.requirement_name}?",
                        ],
                    ))

        return issues

    def _generate_questions(
        self,
        case: NormalizedIntake,
        analysis: ReasoningResult | None,
        issues: List[LegalIssue],
    ) -> List[OpenQuestion]:
        """Genera preguntas abiertas para el asesor"""
        questions = []

        # Pregunta general sobre viabilidad
        if analysis and analysis.viability.value != "viable":
            questions.append(OpenQuestion(
                question="¿Qué pasos específicos recomienda para hacer viable este proyecto?",
                priority="high",
            ))

        # Preguntas desde issues
        for issue in issues[:5]:  # Limitar a 5 issues
            for q in issue.questions_for_advisor[:2]:
                questions.append(OpenQuestion(
                    question=q,
                    related_issue_id=issue.id,
                    priority="high" if issue.severity == "critical" else "normal",
                ))

        # Preguntas estándar
        standard_questions = [
            OpenQuestion(
                question="¿Hay riesgos que no hemos identificado?",
                priority="normal",
            ),
            OpenQuestion(
                question="¿Cuál es el cronograma realista para regularizar la situación?",
                priority="normal",
            ),
        ]

        questions.extend(standard_questions)

        return questions[:10]  # Máximo 10 preguntas

    def _list_documents(
        self,
        case: NormalizedIntake,
        gaps: GapAnalysisResult | None,
    ) -> tuple[List[DocumentRequest], List[DocumentRequest]]:
        """Lista documentos a traer y preparar"""
        to_bring = []
        to_prepare = []

        # Documentos básicos a traer
        if case.has_legal_entity:
            to_bring.extend([
                DocumentRequest(name="Partida registral actualizada", required=True),
                DocumentRequest(name="Estatutos vigentes", required=True),
                DocumentRequest(name="Ficha RUC", required=True),
            ])
        else:
            to_prepare.append(DocumentRequest(
                name="Acta de constitución (borrador)",
                required=False,
                purpose="Para discutir formalización",
            ))

        # Documentos según brechas
        if gaps:
            for gap in gaps.gaps:
                if gap.estimated_documents:
                    for doc_name in gap.estimated_documents:
                        to_prepare.append(DocumentRequest(
                            name=doc_name,
                            required=False,
                            purpose=f"Requerido para: {gap.requirement_name}",
                        ))

        return (to_bring, to_prepare)

    def _generate_executive_summary(
        self,
        case: NormalizedIntake,
        analysis: ReasoningResult | None,
        risk: RiskAssessment | None,
        gaps: GapAnalysisResult | None,
    ) -> str:
        """Genera resumen ejecutivo"""
        parts = []

        # Tipo de organización
        parts.append(f"Organización: {case.organization_type or 'No especificada'}")

        # Estado de personería
        if case.has_legal_entity is not None:
            status = "con" if case.has_legal_entity else "sin"
            parts.append(f"Estado: {status} personería jurídica")

        # Viabilidad
        if analysis:
            parts.append(f"Viabilidad preliminar: {analysis.viability.value}")

        # Riesgo
        if risk:
            parts.append(f"Nivel de riesgo: {risk.overall_level.value}")

        # Brechas
        if gaps:
            parts.append(f"Requisitos pendientes: {gaps.missing}")

        return ". ".join(parts) + "."

    def _define_meeting_objectives(
        self,
        case: NormalizedIntake,
        issues: List[LegalIssue],
    ) -> List[str]:
        """Define objetivos para la reunión"""
        objectives = []

        # Objetivo principal según estado
        if case.has_legal_entity is False:
            objectives.append("Definir estrategia de formalización")
        elif issues:
            objectives.append("Resolver issues legales identificados")
        else:
            objectives.append("Validar estructura legal actual")

        # Objetivos según issues
        critical_issues = [i for i in issues if i.severity == "critical"]
        if critical_issues:
            objectives.append(f"Atender {len(critical_issues)} issues críticos")

        # Objetivos estándar
        objectives.append("Definir próximos pasos y cronograma")
        objectives.append("Identificar costos estimados")

        return objectives[:5]

    def _group_issues_by_severity(
        self,
        issues: List[LegalIssue]
    ) -> dict[str, List[str]]:
        """Agrupa issues por severidad"""
        grouped: dict[str, List[str]] = {
            "critical": [],
            "important": [],
            "informative": [],
        }

        for issue in issues:
            if issue.severity in grouped:
                grouped[issue.severity].append(issue.title)

        return grouped

    def _generate_analysis_notes(
        self,
        analysis: ReasoningResult | None
    ) -> str:
        """Genera notas del análisis de GPT Legal"""
        if not analysis:
            return "No se realizó análisis previo."

        notes = []
        notes.append(f"Viabilidad: {analysis.viability.value}")
        notes.append(f"Confidence: {analysis.confidence_level}")

        if analysis.assumptions:
            notes.append(f"Supuestos: {', '.join(analysis.assumptions[:3])}")

        return " | ".join(notes)
