"""
Milestone Engine - Service
Construye rutas de cumplimiento paso a paso
"""

from typing import List, Dict
from app.modules.intake.schemas import NormalizedIntake
from app.modules.gap_engine.evaluator import GapAnalysisResult, Gap, GapStatus
from .dag_builder import (
    Milestone,
    MilestoneStatus,
    MilestoneType,
    MilestoneDAG,
    ExecutionPhase,
    ExecutionSequence,
    Document,
    Authority,
)


# Catálogo de milestones predefinidos
MILESTONES_CATALOG: Dict[str, Milestone] = {
    "elaborar_estatutos": Milestone(
        id="elaborar_estatutos",
        name="Elaborar estatutos",
        description="Redactar los estatutos de la asociación civil",
        milestone_type=MilestoneType.DOCUMENT,
        documents_required=[
            Document(name="Estatutos", description="Documento constitutivo"),
            Document(name="Acta de fundación", description="Acta de asamblea constitutiva"),
        ],
        steps=[
            "Definir objeto social y fines",
            "Establecer estructura organizativa",
            "Definir régimen de asociados",
            "Establecer patrimonio y régimen económico",
        ],
        phase="Formalización",
        order=1,
    ),
    "escritura_publica": Milestone(
        id="escritura_publica",
        name="Elevar a escritura pública",
        description="Formalizar estatutos ante notario",
        milestone_type=MilestoneType.PROCEDURE,
        prerequisites=["elaborar_estatutos"],
        authority=Authority(
            name="Notaría",
            full_name="Notaría Pública",
        ),
        documents_required=[
            Document(name="Estatutos aprobados"),
            Document(name="DNI de fundadores"),
            Document(name="Acta de fundación"),
        ],
        estimated_cost="S/ 300-500",
        phase="Formalización",
        order=2,
    ),
    "inscripcion_sunarp": Milestone(
        id="inscripcion_sunarp",
        name="Inscripción en SUNARP",
        description="Registrar la asociación en Registros Públicos",
        milestone_type=MilestoneType.REGISTRATION,
        prerequisites=["escritura_publica"],
        authority=Authority(
            name="SUNARP",
            full_name="Superintendencia Nacional de los Registros Públicos",
            website="https://www.sunarp.gob.pe",
        ),
        documents_required=[
            Document(name="Escritura pública"),
            Document(name="Formulario de inscripción"),
        ],
        estimated_duration="7-15 días hábiles",
        estimated_cost="S/ 50-100",
        phase="Formalización",
        order=3,
    ),
    "obtener_ruc": Milestone(
        id="obtener_ruc",
        name="Obtener RUC",
        description="Inscribirse en el Registro Único de Contribuyentes",
        milestone_type=MilestoneType.REGISTRATION,
        prerequisites=["inscripcion_sunarp"],
        authority=Authority(
            name="SUNAT",
            full_name="Superintendencia Nacional de Aduanas y de Administración Tributaria",
            website="https://www.sunat.gob.pe",
        ),
        documents_required=[
            Document(name="Partida registral"),
            Document(name="DNI del representante legal"),
            Document(name="Recibo de servicios del domicilio fiscal"),
        ],
        estimated_duration="1-3 días hábiles",
        steps=[
            "Acceder a SUNAT Virtual o acudir a centro de servicios",
            "Completar formulario de inscripción",
            "Presentar documentos requeridos",
            "Obtener ficha RUC y clave SOL",
        ],
        phase="Tributario",
        order=4,
    ),
    "registro_apci": Milestone(
        id="registro_apci",
        name="Registro en APCI",
        description="Inscribirse en el registro de APCI para recibir cooperación internacional",
        milestone_type=MilestoneType.REGISTRATION,
        prerequisites=["obtener_ruc"],
        authority=Authority(
            name="APCI",
            full_name="Agencia Peruana de Cooperación Internacional",
            website="https://www.apci.gob.pe",
        ),
        documents_required=[
            Document(name="Solicitud de inscripción"),
            Document(name="Estatutos vigentes"),
            Document(name="Partida registral actualizada"),
            Document(name="RUC activo"),
            Document(name="Plan de actividades"),
        ],
        estimated_duration="30-60 días hábiles",
        warnings=[
            "El proceso puede demorar si hay observaciones",
            "Mantener información actualizada ante APCI",
        ],
        phase="Cooperación Internacional",
        order=5,
    ),
}


class MilestoneEngine:
    """
    Motor de construcción de rutas de cumplimiento.
    """

    def __init__(self):
        self.catalog = MILESTONES_CATALOG

    async def build_route(
        self,
        user_state: NormalizedIntake,
        gap_analysis: GapAnalysisResult,
        target_goal: str | None = None,
    ) -> ExecutionSequence:
        """
        Construye la ruta de cumplimiento basada en brechas.

        Args:
            user_state: Estado actual del usuario
            gap_analysis: Resultado del análisis de brechas
            target_goal: Objetivo específico (opcional)

        Returns:
            ExecutionSequence con la ruta ordenada
        """
        # 1. Identificar milestones necesarios
        required_milestones = self._identify_required_milestones(
            gap_analysis, target_goal
        )

        # 2. Construir DAG
        dag = self._build_dag(required_milestones)

        # 3. Ordenar topológicamente
        ordered = self._topological_sort(dag)

        # 4. Agrupar en fases
        phases = self._group_into_phases(ordered)

        # 5. Marcar completados según estado actual
        self._mark_completed(phases, user_state, gap_analysis)

        # 6. Identificar próximos pasos
        next_milestones = self._identify_next_steps(phases)
        blocked = self._identify_blocked(phases)

        return ExecutionSequence(
            phases=phases,
            total_milestones=len(ordered),
            completed_milestones=sum(
                1 for m in ordered if m.status == MilestoneStatus.COMPLETED
            ),
            next_milestones=next_milestones,
            blocked_milestones=blocked,
            estimated_total_duration=self._estimate_total_duration(phases),
        )

    def _identify_required_milestones(
        self,
        gap_analysis: GapAnalysisResult,
        target_goal: str | None,
    ) -> List[Milestone]:
        """Identifica milestones necesarios según brechas"""
        required = []

        # Mapeo de gap IDs a milestone IDs
        gap_to_milestone = {
            "personeria_juridica": ["elaborar_estatutos", "escritura_publica", "inscripcion_sunarp"],
            "ruc": ["obtener_ruc"],
            "registro_apci": ["registro_apci"],
        }

        for gap in gap_analysis.gaps:
            if gap.status in [GapStatus.MISSING, GapStatus.BLOCKED]:
                milestone_ids = gap_to_milestone.get(gap.requirement_id, [])
                for m_id in milestone_ids:
                    if m_id in self.catalog:
                        milestone = self.catalog[m_id].model_copy()
                        if milestone not in required:
                            required.append(milestone)

        # Agregar dependencias
        required = self._add_dependencies(required)

        return required

    def _add_dependencies(self, milestones: List[Milestone]) -> List[Milestone]:
        """Agrega milestones de dependencias faltantes"""
        result = list(milestones)
        added_ids = {m.id for m in result}

        changed = True
        while changed:
            changed = False
            for milestone in list(result):
                for prereq_id in milestone.prerequisites:
                    if prereq_id not in added_ids and prereq_id in self.catalog:
                        result.append(self.catalog[prereq_id].model_copy())
                        added_ids.add(prereq_id)
                        changed = True

        return result

    def _build_dag(self, milestones: List[Milestone]) -> MilestoneDAG:
        """Construye el DAG de milestones"""
        edges: Dict[str, List[str]] = {}

        for milestone in milestones:
            for prereq_id in milestone.prerequisites:
                if prereq_id not in edges:
                    edges[prereq_id] = []
                edges[prereq_id].append(milestone.id)

        return MilestoneDAG(milestones=milestones, edges=edges)

    def _topological_sort(self, dag: MilestoneDAG) -> List[Milestone]:
        """Ordena milestones topológicamente"""
        # Calcular in-degree
        in_degree = {m.id: 0 for m in dag.milestones}
        for milestone in dag.milestones:
            for prereq in milestone.prerequisites:
                if prereq in in_degree:
                    in_degree[milestone.id] += 1

        # Cola con nodos sin dependencias
        queue = [m for m in dag.milestones if in_degree[m.id] == 0]
        result = []

        while queue:
            # Ordenar por order field
            queue.sort(key=lambda m: m.order)
            current = queue.pop(0)
            result.append(current)

            # Reducir in-degree de dependientes
            for child in dag.get_children(current.id):
                in_degree[child.id] -= 1
                if in_degree[child.id] == 0:
                    queue.append(child)

        return result

    def _group_into_phases(
        self,
        milestones: List[Milestone]
    ) -> List[ExecutionPhase]:
        """Agrupa milestones en fases"""
        phases_dict: Dict[str, List[Milestone]] = {}

        for milestone in milestones:
            phase = milestone.phase or "General"
            if phase not in phases_dict:
                phases_dict[phase] = []
            phases_dict[phase].append(milestone)

        # Ordenar fases
        phase_order = ["Formalización", "Tributario", "Cooperación Internacional", "General"]
        phases = []

        for i, phase_name in enumerate(phase_order):
            if phase_name in phases_dict:
                phases.append(ExecutionPhase(
                    name=phase_name,
                    order=i,
                    milestones=phases_dict[phase_name],
                ))

        return phases

    def _mark_completed(
        self,
        phases: List[ExecutionPhase],
        user_state: NormalizedIntake,
        gap_analysis: GapAnalysisResult,
    ):
        """Marca milestones completados según estado"""
        satisfied_gaps = {
            g.requirement_id for g in gap_analysis.gaps
            if g.status == GapStatus.SATISFIED
        }

        milestone_to_gap = {
            "inscripcion_sunarp": "personeria_juridica",
            "obtener_ruc": "ruc",
            "registro_apci": "registro_apci",
        }

        for phase in phases:
            for milestone in phase.milestones:
                gap_id = milestone_to_gap.get(milestone.id)
                if gap_id and gap_id in satisfied_gaps:
                    milestone.status = MilestoneStatus.COMPLETED

    def _identify_next_steps(
        self,
        phases: List[ExecutionPhase]
    ) -> List[Milestone]:
        """Identifica próximos milestones a ejecutar"""
        next_steps = []

        for phase in phases:
            for milestone in phase.milestones:
                if milestone.status == MilestoneStatus.PENDING:
                    # Verificar si prerrequisitos están completos
                    prereqs_done = all(
                        self._is_completed(prereq_id, phases)
                        for prereq_id in milestone.prerequisites
                    )
                    if prereqs_done:
                        next_steps.append(milestone)

        return next_steps[:3]  # Top 3 próximos

    def _identify_blocked(
        self,
        phases: List[ExecutionPhase]
    ) -> List[Milestone]:
        """Identifica milestones bloqueados"""
        blocked = []

        for phase in phases:
            for milestone in phase.milestones:
                if milestone.status == MilestoneStatus.PENDING:
                    prereqs_done = all(
                        self._is_completed(prereq_id, phases)
                        for prereq_id in milestone.prerequisites
                    )
                    if not prereqs_done and milestone.prerequisites:
                        milestone.status = MilestoneStatus.BLOCKED
                        blocked.append(milestone)

        return blocked

    def _is_completed(self, milestone_id: str, phases: List[ExecutionPhase]) -> bool:
        """Verifica si un milestone está completado"""
        for phase in phases:
            for m in phase.milestones:
                if m.id == milestone_id:
                    return m.status == MilestoneStatus.COMPLETED
        return False

    def _estimate_total_duration(self, phases: List[ExecutionPhase]) -> str:
        """Estima duración total aproximada"""
        # Estimación simple basada en número de milestones
        pending = sum(
            1 for phase in phases
            for m in phase.milestones
            if m.status != MilestoneStatus.COMPLETED
        )

        if pending <= 2:
            return "2-4 semanas"
        elif pending <= 5:
            return "1-2 meses"
        else:
            return "2-4 meses"
