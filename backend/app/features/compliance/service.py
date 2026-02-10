"""
Compliance Feature - Service
(Placeholder - pendiente de implementacion completa)
"""

from .schemas import ComplianceRequest, ComplianceResponse, ComplianceQuestions, MilestoneResponse


class ComplianceService:
    """Servicio para ruta de cumplimiento (placeholder)"""

    def __init__(self):
        pass

    async def get_questions(self) -> ComplianceQuestions:
        """Obtiene preguntas del intake"""
        question_set = self.intake.render_question_set(tool_id=4)
        return ComplianceQuestions(
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

    async def generate_route(self, request: ComplianceRequest) -> ComplianceResponse:
        """Genera ruta de cumplimiento"""
        # 1. Normalizar intake
        intake_data = IntakeData(
            tool_id=4,
            answers={
                "compliance_goal": request.compliance_goal,
                "current_status": request.current_status,
                "org_type": request.organization_type,
                "timeline": request.timeline,
            },
        )
        normalized = await self.intake.process(intake_data)

        # 2. Analizar brechas
        gaps = await self.gap.evaluate(normalized)

        # 3. Construir ruta
        route = await self.milestone.build_route(
            user_state=normalized,
            gap_analysis=gaps,
            target_goal=request.compliance_goal,
        )

        # 4. Convertir a response
        return ComplianceResponse(
            total_milestones=route.total_milestones,
            completed_milestones=route.completed_milestones,
            progress_percentage=route.get_progress_percentage(),
            phases=[
                {
                    "name": p.name,
                    "order": p.order,
                    "milestones": [m.id for m in p.milestones],
                }
                for p in route.phases
            ],
            next_milestones=[
                MilestoneResponse(
                    id=m.id,
                    name=m.name,
                    description=m.description,
                    phase=m.phase or "General",
                    status=m.status.value,
                    order=m.order,
                    prerequisites=m.prerequisites,
                    authority=m.authority.name if m.authority else None,
                    documents_required=[d.name for d in m.documents_required],
                    estimated_duration=m.estimated_duration,
                    estimated_cost=m.estimated_cost,
                    steps=m.steps,
                )
                for m in route.next_milestones
            ],
            blocked_milestones=[
                MilestoneResponse(
                    id=m.id,
                    name=m.name,
                    description=m.description,
                    phase=m.phase or "General",
                    status=m.status.value,
                    order=m.order,
                    prerequisites=m.prerequisites,
                    authority=m.authority.name if m.authority else None,
                    documents_required=[d.name for d in m.documents_required],
                    estimated_duration=m.estimated_duration,
                    estimated_cost=m.estimated_cost,
                    steps=m.steps,
                )
                for m in route.blocked_milestones
            ],
            estimated_total_duration=route.estimated_total_duration,
            gaps_to_resolve=gaps.missing,
            critical_gaps=[g.requirement_name for g in gaps.critical_gaps],
            disclaimers=[
                "Esta ruta es orientativa y puede variar según el caso",
                "Consultar con especialista para casos complejos",
            ],
        )
