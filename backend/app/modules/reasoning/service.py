"""
Reasoning Module - Service
Aplica lógica legal estructurada
"""

from typing import List, Dict, Any

from app.modules.intake.schemas import NormalizedIntake
from app.modules.rag.interfaces import RAGResult, RetrievedChunk
from .legal_logic import (
    LegalCondition,
    ConditionStatus,
    ApplicabilityMatrix,
    ApplicabilityRow,
    DecisionConstraint,
    ReasoningResult,
    Viability,
)
from .guards import ReasoningGuard


class ReasoningModule:
    """
    Módulo de razonamiento legal.
    Aplica lógica estructurada sobre evidencia recuperada.
    """

    def __init__(self):
        self.guard = ReasoningGuard()

    async def analyze(
        self,
        intake_data: NormalizedIntake,
        retrieved_evidence: List[RetrievedChunk],
        risk_level: str = "MEDIUM",
        rag_confidence: float = 0.5,
    ) -> ReasoningResult:
        """
        Ejecuta el análisis de razonamiento legal.

        Args:
            intake_data: Datos normalizados del intake
            retrieved_evidence: Chunks recuperados del RAG
            risk_level: Nivel de riesgo calculado
            rag_confidence: Confidence del RAG

        Returns:
            ReasoningResult con viabilidad, condiciones, etc.
        """
        # Crear RAG result para guards
        rag_result = RAGResult(
            query=None,  # type: ignore
            chunks=retrieved_evidence,
            confidence=rag_confidence,
        )

        # Verificar guards
        can_proceed, guard_message = self.guard.can_reason(rag_result, risk_level)

        if not can_proceed:
            return ReasoningResult(
                viability=Viability.INVIABLE_WITH_ALT,
                viability_explanation=guard_message or "No se puede proceder con el análisis",
                escalation_recommended=True,
                limitations=[guard_message] if guard_message else [],
            )

        # Determinar modo de razonamiento
        reasoning_mode = self.guard.get_reasoning_mode(rag_result, risk_level)

        # Analizar condiciones legales
        conditions = await self._analyze_conditions(
            intake_data, retrieved_evidence
        )

        # Construir matriz de aplicabilidad
        applicability = await self._build_applicability_matrix(
            intake_data, retrieved_evidence
        )

        # Identificar restricciones
        constraints = await self._identify_constraints(
            intake_data, conditions
        )

        # Determinar viabilidad
        viability, explanation, alternatives = self._determine_viability(
            conditions, constraints, intake_data
        )

        # Generar supuestos
        assumptions = self._generate_assumptions(intake_data, reasoning_mode)

        return ReasoningResult(
            viability=viability,
            viability_explanation=explanation,
            legal_conditions=conditions,
            applicability_matrix=applicability,
            decision_constraints=constraints,
            alternatives=alternatives,
            path_to_viability=self._generate_path_to_viability(
                viability, conditions, constraints
            ),
            assumptions=assumptions,
            limitations=self._generate_limitations(reasoning_mode),
            confidence_level=self._map_confidence_to_level(rag_confidence),
            requires_validation=reasoning_mode != "full",
            escalation_recommended=self.guard.should_add_disclaimer(
                rag_result, risk_level
            ),
        )

    async def _analyze_conditions(
        self,
        intake: NormalizedIntake,
        evidence: List[RetrievedChunk],
    ) -> List[LegalCondition]:
        """Analiza condiciones legales basadas en intake y evidencia"""
        conditions = []

        # Condición: Personería jurídica
        if intake.has_legal_entity is not None:
            conditions.append(LegalCondition(
                id="legal_entity",
                description="Contar con personería jurídica",
                status=ConditionStatus.SATISFIED if intake.has_legal_entity
                       else ConditionStatus.NOT_SATISFIED,
                requirements=[] if intake.has_legal_entity else [
                    "Constituir asociación civil ante notario",
                    "Inscribir en SUNARP",
                    "Obtener RUC",
                ],
            ))

        # Condición: Registro según área legal
        if intake.legal_area:
            areas = intake.legal_area if isinstance(intake.legal_area, list) else [intake.legal_area]

            if "Cooperación internacional (APCI)" in areas:
                conditions.append(LegalCondition(
                    id="apci_registration",
                    description="Registro en APCI para recibir cooperación internacional",
                    status=ConditionStatus.CONDITIONAL,
                    requirements=[
                        "Tener personería jurídica vigente",
                        "Estatutos que permitan recibir cooperación",
                        "Inscripción en registro de APCI",
                    ],
                    notes="Obligatorio para recibir fondos de cooperación internacional",
                ))

            if "Tributario (SUNAT)" in areas:
                conditions.append(LegalCondition(
                    id="sunat_compliance",
                    description="Cumplimiento de obligaciones tributarias",
                    status=ConditionStatus.CONDITIONAL,
                    requirements=[
                        "RUC activo y habido",
                        "Declaraciones al día",
                        "Libros contables según régimen",
                    ],
                ))

        return conditions

    async def _build_applicability_matrix(
        self,
        intake: NormalizedIntake,
        evidence: List[RetrievedChunk],
    ) -> ApplicabilityMatrix:
        """Construye matriz de aplicabilidad de normas"""
        rows = []

        # Determinar normas aplicables según tipo de organización
        if intake.organization_type in ["Asociación civil", "ONG registrada"]:
            rows.append(ApplicabilityRow(
                norm_id="cc_asociaciones",
                norm_name="Código Civil - Libro de Asociaciones",
                applies=True,
                reason="Aplica a todas las asociaciones civiles",
            ))

        if intake.funding_source in ["Donaciones internacionales", "Grants/Subvenciones"]:
            rows.append(ApplicabilityRow(
                norm_id="ley_apci",
                norm_name="Ley 27692 - Ley de APCI",
                applies=True,
                reason="Aplica por recibir recursos de cooperación internacional",
                conditions=["Requiere registro previo en APCI"],
            ))

        return ApplicabilityMatrix(rows=rows)

    async def _identify_constraints(
        self,
        intake: NormalizedIntake,
        conditions: List[LegalCondition],
    ) -> List[DecisionConstraint]:
        """Identifica restricciones para la decisión"""
        constraints = []

        # Revisar condiciones no satisfechas
        for condition in conditions:
            if condition.status == ConditionStatus.NOT_SATISFIED:
                constraints.append(DecisionConstraint(
                    constraint_type="blocking",
                    description=f"Requisito no cumplido: {condition.description}",
                    alternatives=condition.requirements,
                ))

        # Restricciones por estructura informal
        if intake.organization_type in ["Colectivo sin personería", "Colectivo estudiantil"]:
            constraints.append(DecisionConstraint(
                constraint_type="warning",
                description="Estructura informal limita opciones legales",
                alternatives=[
                    "Operar bajo paraguas de organización formal",
                    "Formalizar como asociación civil",
                    "Usar mecanismos de crowdfunding para financiamiento",
                ],
            ))

        return constraints

    def _determine_viability(
        self,
        conditions: List[LegalCondition],
        constraints: List[DecisionConstraint],
        intake: NormalizedIntake,
    ) -> tuple[Viability, str, List[str]]:
        """Determina viabilidad basada en condiciones y restricciones"""
        blocking_constraints = [
            c for c in constraints if c.constraint_type == "blocking"
        ]
        unsatisfied_conditions = [
            c for c in conditions if c.status == ConditionStatus.NOT_SATISFIED
        ]

        alternatives = []

        if not blocking_constraints and not unsatisfied_conditions:
            return (
                Viability.VIABLE,
                "El proyecto es viable en su forma actual según el análisis realizado.",
                [],
            )

        # Hay bloqueos - construir alternativas
        for constraint in blocking_constraints:
            alternatives.extend(constraint.alternatives)

        for condition in unsatisfied_conditions:
            alternatives.extend(condition.requirements)

        # Eliminar duplicados
        alternatives = list(dict.fromkeys(alternatives))

        explanation = (
            "El proyecto requiere ajustes para ser viable. "
            f"Se identificaron {len(blocking_constraints)} restricciones "
            f"y {len(unsatisfied_conditions)} requisitos pendientes."
        )

        return (Viability.INVIABLE_WITH_ALT, explanation, alternatives)

    def _generate_path_to_viability(
        self,
        viability: Viability,
        conditions: List[LegalCondition],
        constraints: List[DecisionConstraint],
    ) -> str | None:
        """Genera descripción del camino hacia la viabilidad"""
        if viability == Viability.VIABLE:
            return None

        steps = []

        # Priorizar condiciones no satisfechas
        for condition in conditions:
            if condition.status == ConditionStatus.NOT_SATISFIED:
                steps.extend(condition.requirements)

        if steps:
            return "Pasos recomendados: " + "; ".join(steps[:3])

        return "Consultar con un asesor legal para definir la ruta específica"

    def _generate_assumptions(
        self,
        intake: NormalizedIntake,
        reasoning_mode: str,
    ) -> List[str]:
        """Genera lista de supuestos del análisis"""
        assumptions = [
            "La información proporcionada es correcta y completa",
            f"Jurisdicción aplicable: {intake.jurisdiction}",
        ]

        if reasoning_mode == "conditional":
            assumptions.append(
                "El análisis está basado en evidencia parcial - validar con especialista"
            )

        return assumptions

    def _generate_limitations(self, reasoning_mode: str) -> List[str]:
        """Genera limitaciones del análisis"""
        limitations = [
            "Este análisis no constituye asesoría legal",
            "Las normas pueden haber sido modificadas recientemente",
        ]

        if reasoning_mode == "orientation":
            limitations.append(
                "Evidencia insuficiente - solo se proporciona orientación general"
            )

        return limitations

    def _map_confidence_to_level(self, confidence: float) -> str:
        """Mapea confidence numérico a nivel"""
        if confidence >= 0.8:
            return "HIGH"
        elif confidence >= 0.65:
            return "MEDIUM"
        else:
            return "LOW"
