"""
Gap Engine - Service
Detecta brechas regulatorias
"""

from typing import List, Dict, Any
from app.modules.intake.schemas import NormalizedIntake
from app.modules.reasoning.legal_logic import LegalCondition, ConditionStatus
from .evaluator import (
    GapStatus,
    GapPriority,
    Requirement,
    Gap,
    GapAnalysisResult,
)


# Catálogo de requisitos por área
REQUIREMENTS_CATALOG: Dict[str, List[Requirement]] = {
    "formalizacion_basica": [
        Requirement(
            id="ruc",
            name="Registro Único de Contribuyentes (RUC)",
            description="Número de identificación tributaria ante SUNAT",
            authority="SUNAT",
            legal_basis="D.L. 943",
        ),
        Requirement(
            id="personeria_juridica",
            name="Personería Jurídica",
            description="Inscripción como persona jurídica en SUNARP",
            authority="SUNARP",
            legal_basis="Código Civil Art. 77-98",
        ),
        Requirement(
            id="estatutos",
            name="Estatutos vigentes",
            description="Documento constitutivo con objeto social definido",
            authority="SUNARP",
        ),
    ],
    "cooperacion_internacional": [
        Requirement(
            id="registro_apci",
            name="Registro en APCI",
            description="Inscripción en el registro de APCI como ONGD, ENIEX o IPREDA",
            authority="APCI",
            legal_basis="Ley 27692",
            dependencies=["personeria_juridica", "estatutos"],
        ),
        Requirement(
            id="cuenta_interbancaria",
            name="Cuenta bancaria para cooperación",
            description="Cuenta en entidad financiera supervisada por SBS",
            authority="SBS/APCI",
            dependencies=["ruc"],
        ),
    ],
    "tributario": [
        Requirement(
            id="declaraciones_mensuales",
            name="Declaraciones tributarias al día",
            description="PDT mensuales presentados según régimen",
            authority="SUNAT",
            dependencies=["ruc"],
        ),
        Requirement(
            id="libros_contables",
            name="Libros contables",
            description="Libros según régimen tributario",
            authority="SUNAT",
            dependencies=["ruc"],
        ),
    ],
    "laboral": [
        Requirement(
            id="planilla_electronica",
            name="Planilla electrónica (PLAME)",
            description="Registro de trabajadores en PLAME",
            authority="SUNAT/MTPE",
            legal_basis="D.S. 018-2007-TR",
            dependencies=["ruc"],
        ),
        Requirement(
            id="essalud",
            name="Aportaciones a EsSalud",
            description="Pago de aportes de salud para trabajadores",
            authority="EsSalud",
            dependencies=["planilla_electronica"],
        ),
    ],
}


class GapEngine:
    """
    Motor de detección de brechas regulatorias.
    """

    def __init__(self):
        self.requirements_catalog = REQUIREMENTS_CATALOG

    async def evaluate(
        self,
        user_state: NormalizedIntake,
        legal_conditions: List[LegalCondition] | None = None,
    ) -> GapAnalysisResult:
        """
        Evalúa brechas entre estado actual y requisitos.

        Args:
            user_state: Estado actual del usuario (del intake)
            legal_conditions: Condiciones legales del reasoning

        Returns:
            GapAnalysisResult con brechas identificadas
        """
        # Determinar qué áreas aplican
        applicable_areas = self._determine_applicable_areas(user_state)

        # Obtener requisitos aplicables
        requirements = self._get_requirements_for_areas(applicable_areas)

        # Mapear estado del usuario
        user_status_map = self._map_user_state(user_state, legal_conditions)

        # Evaluar cada requisito
        gaps = []
        satisfied_count = 0

        for req in requirements:
            gap = self._evaluate_requirement(req, user_status_map, requirements)
            gaps.append(gap)

            if gap.status == GapStatus.SATISFIED:
                satisfied_count += 1

        # Calcular estadísticas
        result = GapAnalysisResult(
            total_requirements=len(requirements),
            satisfied=satisfied_count,
            missing=len([g for g in gaps if g.status == GapStatus.MISSING]),
            conditional=len([g for g in gaps if g.status == GapStatus.CONDITIONAL]),
            blocked=len([g for g in gaps if g.status == GapStatus.BLOCKED]),
            gaps=gaps,
            critical_gaps=[g for g in gaps if g.priority == GapPriority.CRITICAL],
            next_actions=self._generate_next_actions(gaps),
            severity=self._calculate_severity(gaps),
        )

        return result

    def _determine_applicable_areas(
        self,
        user_state: NormalizedIntake
    ) -> List[str]:
        """Determina qué áreas de requisitos aplican"""
        areas = ["formalizacion_basica"]  # Siempre aplica

        legal_area = user_state.legal_area
        if isinstance(legal_area, str):
            legal_areas = [legal_area]
        elif isinstance(legal_area, list):
            legal_areas = legal_area
        else:
            legal_areas = []

        # Mapear áreas legales a catálogos
        if "Cooperación internacional (APCI)" in legal_areas:
            areas.append("cooperacion_internacional")

        if "Tributario (SUNAT)" in legal_areas:
            areas.append("tributario")

        if "Laboral" in legal_areas:
            areas.append("laboral")

        # Por fuente de financiamiento
        if user_state.funding_source in ["Donaciones internacionales", "Grants/Subvenciones"]:
            if "cooperacion_internacional" not in areas:
                areas.append("cooperacion_internacional")

        return areas

    def _get_requirements_for_areas(
        self,
        areas: List[str]
    ) -> List[Requirement]:
        """Obtiene requisitos de las áreas seleccionadas"""
        requirements = []
        seen_ids = set()

        for area in areas:
            area_reqs = self.requirements_catalog.get(area, [])
            for req in area_reqs:
                if req.id not in seen_ids:
                    requirements.append(req)
                    seen_ids.add(req.id)

        return requirements

    def _map_user_state(
        self,
        user_state: NormalizedIntake,
        legal_conditions: List[LegalCondition] | None,
    ) -> Dict[str, bool | None]:
        """Mapea estado del usuario a requisitos conocidos"""
        status_map: Dict[str, bool | None] = {}

        # Desde intake
        if user_state.has_legal_entity is not None:
            status_map["personeria_juridica"] = user_state.has_legal_entity
            status_map["estatutos"] = user_state.has_legal_entity  # Asumimos

        # Desde legal conditions
        if legal_conditions:
            for condition in legal_conditions:
                if condition.status == ConditionStatus.SATISFIED:
                    status_map[condition.id] = True
                elif condition.status == ConditionStatus.NOT_SATISFIED:
                    status_map[condition.id] = False

        return status_map

    def _evaluate_requirement(
        self,
        requirement: Requirement,
        user_status: Dict[str, bool | None],
        all_requirements: List[Requirement],
    ) -> Gap:
        """Evalúa un requisito específico"""
        # Verificar dependencias
        dependencies_status = self._check_dependencies(
            requirement.dependencies, user_status, all_requirements
        )

        if dependencies_status == "blocked":
            return Gap(
                requirement_id=requirement.id,
                requirement_name=requirement.name,
                status=GapStatus.BLOCKED,
                priority=GapPriority.HIGH,
                description=requirement.description,
                authority=requirement.authority,
                legal_basis=requirement.legal_basis,
                dependencies_pending=requirement.dependencies,
                notes="Requiere completar requisitos previos",
            )

        # Verificar estado del requisito
        status = user_status.get(requirement.id)

        if status is True:
            return Gap(
                requirement_id=requirement.id,
                requirement_name=requirement.name,
                status=GapStatus.SATISFIED,
                priority=GapPriority.LOW,
                description=requirement.description,
                authority=requirement.authority,
                legal_basis=requirement.legal_basis,
            )
        elif status is False:
            return Gap(
                requirement_id=requirement.id,
                requirement_name=requirement.name,
                status=GapStatus.MISSING,
                priority=self._determine_priority(requirement),
                description=requirement.description,
                authority=requirement.authority,
                legal_basis=requirement.legal_basis,
                steps_to_resolve=self._get_resolution_steps(requirement),
            )
        else:
            # Estado desconocido
            return Gap(
                requirement_id=requirement.id,
                requirement_name=requirement.name,
                status=GapStatus.CONDITIONAL,
                priority=GapPriority.MEDIUM,
                description=requirement.description,
                authority=requirement.authority,
                legal_basis=requirement.legal_basis,
                notes="Verificar si se cumple este requisito",
            )

    def _check_dependencies(
        self,
        dependencies: List[str],
        user_status: Dict[str, bool | None],
        all_requirements: List[Requirement],
    ) -> str:
        """Verifica si las dependencias están satisfechas"""
        if not dependencies:
            return "ok"

        for dep_id in dependencies:
            dep_status = user_status.get(dep_id)
            if dep_status is False:
                return "blocked"

        return "ok"

    def _determine_priority(self, requirement: Requirement) -> GapPriority:
        """Determina prioridad de un requisito faltante"""
        critical_reqs = ["ruc", "personeria_juridica", "registro_apci"]
        high_reqs = ["declaraciones_mensuales", "planilla_electronica"]

        if requirement.id in critical_reqs:
            return GapPriority.CRITICAL
        elif requirement.id in high_reqs:
            return GapPriority.HIGH
        else:
            return GapPriority.MEDIUM

    def _get_resolution_steps(self, requirement: Requirement) -> List[str]:
        """Obtiene pasos para resolver una brecha"""
        steps_map = {
            "ruc": [
                "Acceder a SUNAT Virtual",
                "Completar formulario de inscripción",
                "Obtener clave SOL",
            ],
            "personeria_juridica": [
                "Elaborar estatutos",
                "Elevar a escritura pública ante notario",
                "Inscribir en SUNARP",
            ],
            "registro_apci": [
                "Preparar documentación requerida",
                "Presentar solicitud en APCI",
                "Esperar evaluación y resolución",
            ],
        }
        return steps_map.get(requirement.id, ["Consultar con especialista"])

    def _generate_next_actions(self, gaps: List[Gap]) -> List[str]:
        """Genera lista de próximas acciones prioritarias"""
        actions = []

        # Priorizar por criticidad
        for priority in [GapPriority.CRITICAL, GapPriority.HIGH]:
            for gap in gaps:
                if gap.priority == priority and gap.status == GapStatus.MISSING:
                    if gap.steps_to_resolve:
                        actions.append(f"{gap.requirement_name}: {gap.steps_to_resolve[0]}")
                    else:
                        actions.append(f"Resolver: {gap.requirement_name}")

        return actions[:5]  # Top 5 acciones

    def _calculate_severity(self, gaps: List[Gap]) -> str:
        """Calcula severidad general de las brechas"""
        critical = len([g for g in gaps if g.priority == GapPriority.CRITICAL and g.status != GapStatus.SATISFIED])
        missing = len([g for g in gaps if g.status == GapStatus.MISSING])

        if critical > 0:
            return "HIGH"
        elif missing > 2:
            return "MEDIUM"
        else:
            return "LOW"
