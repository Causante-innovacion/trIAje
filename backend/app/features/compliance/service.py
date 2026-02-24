"""
Compliance Feature - Service
Genera ruta de cumplimiento paso a paso basada en objetivo y estado actual.
"""

from .schemas import ComplianceRequest, ComplianceResponse, ComplianceQuestions, MilestoneResponse

# ---------------------------------------------------------------------------
# Mapeo: qué keywords en current_status indican que el milestone está hecho
# ---------------------------------------------------------------------------
COMPLETED_KEYWORDS: dict[str, list[str]] = {
    "elaborar_estatutos": ["estatuto", "estatutos", "acta constitutiva", "acta fundacional", "minuta"],
    "escritura_publica": ["escritura pública", "escritura publica", "notari", "elevado a escritura"],
    "inscripcion_sunarp": ["sunarp", "partida registral", "registros públicos", "inscrit", "inscripto", "registrado en sunarp"],
    "obtener_ruc": ["ruc", "número de ruc", "tengo ruc", "ruc activo", "ficha ruc"],
    "registro_apci": ["apci", "eniex", "ipreda", "registro apci", "registrado en apci"],
}

# ---------------------------------------------------------------------------
# Milestones seleccionados por objetivo principal
# ---------------------------------------------------------------------------
GOAL_MILESTONES: dict[str, list[str]] = {
    "formalizacion":  ["elaborar_estatutos", "escritura_publica", "inscripcion_sunarp", "obtener_ruc"],
    "tributario":     ["obtener_ruc"],
    "cooperacion":    ["elaborar_estatutos", "escritura_publica", "inscripcion_sunarp", "obtener_ruc", "registro_apci"],
    "general":        ["elaborar_estatutos", "escritura_publica", "inscripcion_sunarp", "obtener_ruc"],
}


class ComplianceService:
    """Servicio funcional para ruta de cumplimiento paso a paso."""

    DISCLAIMERS = [
        "Esta ruta es orientativa y no reemplaza asesoría legal profesional.",
        "Los plazos y costos son estimados; pueden variar según cada caso.",
        "Verifica los requisitos vigentes directamente con las entidades competentes (SUNARP, SUNAT, APCI).",
    ]

    async def get_questions(self) -> ComplianceQuestions:
        """Obtiene preguntas del intake para cumplimiento."""
        return ComplianceQuestions(
            questions=[
                {
                    "id": "org_type",
                    "text": "¿Qué tipo de organización es?",
                    "type": "select",
                    "required": True,
                    "options": ["Asociación civil", "Fundación", "ONG", "Colectivo informal", "Empresa", "Otro"],
                    "help_text": None,
                    "block": "org",
                    "block_name": "Organización",
                },
                {
                    "id": "compliance_goal",
                    "text": "¿Cuál es el objetivo principal de cumplimiento?",
                    "type": "select",
                    "required": True,
                    "options": [
                        "Formalizarme legalmente (SUNARP)",
                        "Obtener o regularizar RUC en SUNAT",
                        "Registrarme en APCI para cooperación internacional",
                        "Cumplimiento tributario general",
                        "Todo lo anterior",
                    ],
                    "help_text": None,
                    "block": "goal",
                    "block_name": "Objetivo",
                },
                {
                    "id": "current_status",
                    "text": "¿Qué pasos ya ha completado?",
                    "type": "text",
                    "required": False,
                    "options": None,
                    "help_text": "Describe tu estado actual, por ejemplo: 'Tenemos estatutos pero no RUC'",
                    "block": "status",
                    "block_name": "Estado actual",
                },
                {
                    "id": "timeline",
                    "text": "¿Tienes un plazo específico para completar el proceso?",
                    "type": "text",
                    "required": False,
                    "options": None,
                    "help_text": "Opcional: ej. '3 meses', 'antes de enero'",
                    "block": "timeline",
                    "block_name": "Plazo",
                },
            ],
            tool_id=4,
            tool_name="Ruta de cumplimiento",
        )

    async def generate_route(self, request: ComplianceRequest) -> ComplianceResponse:
        """Genera ruta de cumplimiento paso a paso."""
        from app.modules.milestone_engine.service import MILESTONES_CATALOG

        goal_key = self._detect_goal(request.compliance_goal)
        milestone_ids = GOAL_MILESTONES.get(goal_key, GOAL_MILESTONES["general"])
        current_status_lower = (request.current_status or "").lower()

        milestones: list[MilestoneResponse] = []
        for mid in milestone_ids:
            m = MILESTONES_CATALOG.get(mid)
            if not m:
                continue
            completed = self._is_completed(mid, current_status_lower)
            blocked = (
                not completed
                and self._is_blocked(mid, milestone_ids, current_status_lower)
            )
            status = "completed" if completed else ("blocked" if blocked else "pending")

            milestones.append(MilestoneResponse(
                id=m.id,
                name=m.name,
                description=m.description,
                phase=m.phase or "General",
                status=status,
                order=m.order,
                prerequisites=m.prerequisites,
                authority=m.authority.name if m.authority else None,
                documents_required=[d.name for d in m.documents_required],
                estimated_duration=m.estimated_duration,
                estimated_cost=m.estimated_cost,
                steps=m.steps,
            ))

        total = len(milestones)
        completed_count = sum(1 for m in milestones if m.status == "completed")
        progress = round((completed_count / total) * 100, 1) if total > 0 else 0.0

        # Build phases dict
        phases_dict: dict[str, list[str]] = {}
        for m in milestones:
            phases_dict.setdefault(m.phase, []).append(m.id)
        phases = [{"name": phase, "milestones": ids} for phase, ids in phases_dict.items()]

        next_milestones = [m for m in milestones if m.status == "pending"]
        blocked_milestones = [m for m in milestones if m.status == "blocked"]

        # Critical gaps and escalation
        critical_gaps: list[str] = []
        disclaimers = list(self.DISCLAIMERS)
        needs_professional = self._needs_professional_advice(request, milestones)

        for m in blocked_milestones:
            prereqs_str = ", ".join(m.prerequisites)
            critical_gaps.append(
                f"{m.name}: bloqueado — prerrequisitos pendientes: {prereqs_str}"
            )

        if needs_professional:
            critical_gaps.append(
                "Este proceso incluye pasos que pueden requerir asesoría legal especializada."
            )
            disclaimers.append(
                "IMPORTANTE: Este caso incluye requisitos de complejidad media-alta. "
                "Se recomienda consultar con un abogado especializado en organizaciones civiles "
                "antes de iniciar o continuar el proceso."
            )

        return ComplianceResponse(
            total_milestones=total,
            completed_milestones=completed_count,
            progress_percentage=progress,
            phases=phases,
            next_milestones=next_milestones,
            blocked_milestones=blocked_milestones,
            estimated_total_duration=self._estimate_duration(milestones),
            gaps_to_resolve=total - completed_count,
            critical_gaps=critical_gaps,
            disclaimers=disclaimers,
        )

    # ─── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _detect_goal(compliance_goal: str) -> str:
        g = compliance_goal.lower()
        if any(k in g for k in ["apci", "cooperaci", "internacional"]):
            return "cooperacion"
        if any(k in g for k in ["tributar", "sunat", "ruc", "impuesto"]):
            return "tributario"
        if any(k in g for k in ["formaliz", "sunarp", "personería", "personeria", "inscribi", "constituir"]):
            return "formalizacion"
        return "general"

    @staticmethod
    def _is_completed(milestone_id: str, current_status_lower: str) -> bool:
        keywords = COMPLETED_KEYWORDS.get(milestone_id, [])
        return any(kw in current_status_lower for kw in keywords)

    @staticmethod
    def _is_blocked(
        milestone_id: str,
        included_ids: list[str],
        current_status_lower: str,
    ) -> bool:
        """Un milestone está bloqueado si algún prerrequisito suyo está pendiente."""
        from app.modules.milestone_engine.service import MILESTONES_CATALOG
        m = MILESTONES_CATALOG.get(milestone_id)
        if not m:
            return False
        for prereq_id in m.prerequisites:
            if prereq_id in included_ids:
                prereq_done = any(
                    kw in current_status_lower
                    for kw in COMPLETED_KEYWORDS.get(prereq_id, [])
                )
                if not prereq_done:
                    return True
        return False

    @staticmethod
    def _needs_professional_advice(request: ComplianceRequest, milestones: list) -> bool:
        escalation_kws = ["apci", "cooperaci", "internacional", "fusi", "disoluci"]
        return (
            any(k in request.compliance_goal.lower() for k in escalation_kws)
            or len(milestones) >= 4
        )

    @staticmethod
    def _estimate_duration(milestones: list) -> str | None:
        pending = [m for m in milestones if m.status != "completed"]
        if not pending:
            return "Proceso completado"
        has_apci = any(m.id == "registro_apci" for m in pending)
        has_sunarp = any(m.id == "inscripcion_sunarp" for m in pending)
        if has_apci:
            return "3 - 6 meses"
        if has_sunarp:
            return "4 - 8 semanas"
        return "1 - 3 semanas"


# Singleton
_service: ComplianceService | None = None


def get_compliance_service() -> ComplianceService:
    global _service
    if _service is None:
        _service = ComplianceService()
    return _service

