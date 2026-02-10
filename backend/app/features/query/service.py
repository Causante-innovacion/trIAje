"""
Query Feature - Service
(Placeholder - pendiente de implementacion completa)
"""

from .schemas import QueryRequest, QueryResponse, QueryQuestions


class QueryService:
    """Servicio para consultas puntuales (placeholder)"""

    def __init__(self):
        pass

    async def get_questions(self) -> QueryQuestions:
        """Obtiene preguntas del intake"""
        question_set = self.intake.render_question_set(tool_id=2)
        return QueryQuestions(
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

    async def answer_query(self, request: QueryRequest) -> QueryResponse:
        """Responde una consulta puntual"""
        # 1. Normalizar intake
        intake_data = IntakeData(
            tool_id=2,
            answers={
                "query_area": request.query_area,
                "org_type": request.organization_type,
                "has_legal_entity": request.has_legal_entity,
                "legal_question": request.question,
            },
        )
        normalized = await self.intake.process(intake_data)

        # 2. RAG
        rag_result = await self.rag.retrieve_and_ground(
            query=request.question,
        )

        # 3. Determinar tipo de respuesta según confidence
        if rag_result.confidence >= 0.8:
            answer_type = "direct"
        elif rag_result.confidence >= 0.65:
            answer_type = "conditional"
        else:
            answer_type = "orientation"

        # 4. Construir respuesta
        if answer_type == "orientation":
            answer = (
                "No tengo información suficiente para responder con seguridad. "
                "Te recomiendo consultar con un especialista en el tema."
            )
            escalation = True
        else:
            # En implementación real, aquí se llamaría al LLM con la evidencia
            answer = (
                f"Según la información disponible sobre {request.query_area}, "
                "se recomienda consultar la normativa específica aplicable."
            )
            escalation = rag_result.confidence < 0.8

        return QueryResponse(
            answer=answer,
            answer_type=answer_type,
            conditions=[],
            depends_on=[],
            sources=[
                {"title": e.title, "authority": e.authority, "anchor": e.anchor}
                for e in rag_result.evidence
            ],
            confidence_level="HIGH" if rag_result.confidence >= 0.8 else "MEDIUM" if rag_result.confidence >= 0.65 else "LOW",
            requires_validation=answer_type != "direct",
            related_topics=[],
            escalation_recommended=escalation,
            disclaimers=[
                "Esta respuesta no constituye asesoría legal",
                "Verificar información con normativa vigente",
            ],
        )
