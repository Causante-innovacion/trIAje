"""
Intake Module - Service
Recolección y normalización de datos estructurados
"""

from datetime import datetime
from typing import Any, Dict, List

from .schemas import (
    InputType,
    QuestionDefinition,
    QuestionSet,
    IntakeData,
    NormalizedIntake,
)


class IntakeModule:
    """
    Módulo de intake: recolecta datos estructurados sin ambigüedad.
    """

    def __init__(self):
        self._question_sets: Dict[int, QuestionSet] = {}
        self._load_question_sets()

    def _load_question_sets(self):
        """Carga los conjuntos de preguntas por herramienta"""
        # Tool 1: Evaluación de proyecto
        self._question_sets[1] = QuestionSet(
            tool_id=1,
            tool_name="Evaluar proyecto",
            questions=self._get_evaluation_questions(),
        )
        # Tool 2: Duda puntual
        self._question_sets[2] = QuestionSet(
            tool_id=2,
            tool_name="Duda puntual",
            questions=self._get_query_questions(),
        )
        # Tool 3: Preparar reunión con asesor
        self._question_sets[3] = QuestionSet(
            tool_id=3,
            tool_name="Preparar reunión con asesor",
            questions=self._get_advisor_prep_questions(),
        )
        # Tool 4: Ruta de cumplimiento
        self._question_sets[4] = QuestionSet(
            tool_id=4,
            tool_name="Ruta de cumplimiento",
            questions=self._get_compliance_questions(),
        )

    def _get_evaluation_questions(self) -> List[QuestionDefinition]:
        """Preguntas para evaluación de proyecto"""
        return [
            QuestionDefinition(
                id="org_type",
                text="¿Qué tipo de organización eres?",
                input_type=InputType.ENUM,
                options=[
                    "Asociación civil",
                    "ONG registrada",
                    "Colectivo sin personería",
                    "Colectivo estudiantil",
                    "Medio independiente",
                    "Otro",
                ],
                help_text="Selecciona el tipo que mejor describa tu organización",
            ),
            QuestionDefinition(
                id="has_legal_entity",
                text="¿Tienen personería jurídica?",
                input_type=InputType.BOOLEAN,
                help_text="Personería jurídica significa estar registrados formalmente (SUNARP, etc.)",
            ),
            QuestionDefinition(
                id="project_area",
                text="¿En qué área legal se enmarca tu proyecto?",
                input_type=InputType.MULTI_SELECT,
                options=[
                    "Tributario (SUNAT)",
                    "Cooperación internacional (APCI)",
                    "Laboral",
                    "Propiedad intelectual",
                    "Protección de datos",
                    "Contratos",
                    "Otro",
                ],
            ),
            QuestionDefinition(
                id="funding_source",
                text="¿Cuál es la principal fuente de financiamiento?",
                input_type=InputType.ENUM,
                options=[
                    "Donaciones nacionales",
                    "Donaciones internacionales",
                    "Venta de servicios",
                    "Grants/Subvenciones",
                    "Autofinanciamiento",
                    "Mixto",
                    "Sin financiamiento aún",
                ],
            ),
            QuestionDefinition(
                id="urgency",
                text="¿Qué tan urgente es resolver esto?",
                input_type=InputType.ENUM,
                options=[
                    "Inmediato (días)",
                    "Corto plazo (semanas)",
                    "Mediano plazo (meses)",
                    "Planificación futura",
                ],
            ),
        ]

    def _get_query_questions(self) -> List[QuestionDefinition]:
        """Preguntas para duda puntual"""
        return [
            QuestionDefinition(
                id="query_area",
                text="¿En qué área es tu consulta?",
                input_type=InputType.ENUM,
                options=[
                    "Tributario (SUNAT)",
                    "Cooperación internacional (APCI)",
                    "Laboral",
                    "Propiedad intelectual",
                    "Contratos",
                    "Formalización",
                    "Otro",
                ],
            ),
            QuestionDefinition(
                id="org_type",
                text="¿Qué tipo de organización eres?",
                input_type=InputType.ENUM,
                options=[
                    "Asociación civil",
                    "ONG registrada",
                    "Colectivo sin personería",
                    "Persona natural",
                    "Otro",
                ],
            ),
            QuestionDefinition(
                id="has_legal_entity",
                text="¿Tienen personería jurídica?",
                input_type=InputType.BOOLEAN,
            ),
        ]

    def _get_advisor_prep_questions(self) -> List[QuestionDefinition]:
        """Preguntas para preparar reunión con asesor"""
        return [
            QuestionDefinition(
                id="advisor_type",
                text="¿Con qué tipo de asesor te reunirás?",
                input_type=InputType.ENUM,
                options=[
                    "Abogado tributarista",
                    "Abogado laboralista",
                    "Abogado corporativo",
                    "Contador",
                    "Notario",
                    "No estoy seguro",
                ],
            ),
            QuestionDefinition(
                id="meeting_goal",
                text="¿Cuál es el objetivo principal de la reunión?",
                input_type=InputType.MULTI_SELECT,
                options=[
                    "Validar estructura legal",
                    "Resolver problema específico",
                    "Planificar formalización",
                    "Revisar contratos",
                    "Consulta tributaria",
                    "Otro",
                ],
            ),
            QuestionDefinition(
                id="org_type",
                text="¿Qué tipo de organización eres?",
                input_type=InputType.ENUM,
                options=[
                    "Asociación civil",
                    "ONG registrada",
                    "Colectivo sin personería",
                    "Persona natural",
                    "Otro",
                ],
            ),
        ]

    def _get_compliance_questions(self) -> List[QuestionDefinition]:
        """Preguntas para ruta de cumplimiento"""
        return [
            QuestionDefinition(
                id="compliance_goal",
                text="¿Qué quieres lograr?",
                input_type=InputType.ENUM,
                options=[
                    "Formalizar organización",
                    "Registrar en APCI",
                    "Cumplir obligaciones SUNAT",
                    "Regularizar situación laboral",
                    "Obtener permisos específicos",
                    "Otro",
                ],
            ),
            QuestionDefinition(
                id="current_status",
                text="¿Cuál es tu situación actual?",
                input_type=InputType.ENUM,
                options=[
                    "Sin ningún registro",
                    "Solo RUC",
                    "Personería jurídica básica",
                    "Parcialmente formalizado",
                    "Formalizado pero con brechas",
                ],
            ),
            QuestionDefinition(
                id="org_type",
                text="¿Qué tipo de organización eres o quieres ser?",
                input_type=InputType.ENUM,
                options=[
                    "Asociación civil",
                    "ONG",
                    "Fundación",
                    "Colectivo (sin formalizar)",
                    "Otro",
                ],
            ),
            QuestionDefinition(
                id="timeline",
                text="¿En qué plazo necesitas completar esto?",
                input_type=InputType.ENUM,
                options=[
                    "Lo antes posible",
                    "1-3 meses",
                    "3-6 meses",
                    "6-12 meses",
                    "Sin prisa específica",
                ],
            ),
        ]

    def render_question_set(self, tool_id: int) -> QuestionSet:
        """Retorna el conjunto de preguntas para una herramienta"""
        if tool_id not in self._question_sets:
            raise ValueError(f"Tool ID {tool_id} no válido. Use 1-4.")
        return self._question_sets[tool_id]

    def validate_required_fields(self, data: IntakeData) -> List[str]:
        """Valida que todos los campos requeridos estén presentes"""
        question_set = self._question_sets.get(data.tool_id)
        if not question_set:
            return [f"Tool ID {data.tool_id} no válido"]

        missing = []
        for question in question_set.questions:
            if question.required and question.id not in data.answers:
                missing.append(question.id)
            elif question.required and data.answers.get(question.id) in [None, "", "no_se"]:
                missing.append(question.id)

        return missing

    def enforce_selector_inputs(self, data: IntakeData) -> List[str]:
        """Verifica que las respuestas correspondan a opciones válidas"""
        errors = []
        question_set = self._question_sets.get(data.tool_id)
        if not question_set:
            return errors

        for question in question_set.questions:
            answer = data.answers.get(question.id)
            if answer is None:
                continue

            if question.input_type == InputType.ENUM:
                if question.options and answer not in question.options:
                    errors.append(f"{question.id}: valor '{answer}' no es una opción válida")

            elif question.input_type == InputType.MULTI_SELECT:
                if question.options and isinstance(answer, list):
                    for item in answer:
                        if item not in question.options:
                            errors.append(f"{question.id}: valor '{item}' no es una opción válida")

            elif question.input_type == InputType.BOOLEAN:
                if not isinstance(answer, bool):
                    errors.append(f"{question.id}: debe ser booleano")

            elif question.input_type == InputType.RANGE:
                if question.range_min is not None and answer < question.range_min:
                    errors.append(f"{question.id}: valor menor al mínimo permitido")
                if question.range_max is not None and answer > question.range_max:
                    errors.append(f"{question.id}: valor mayor al máximo permitido")

        return errors

    def normalize_answers(self, data: IntakeData) -> NormalizedIntake:
        """Normaliza las respuestas a un formato estándar"""
        answers = data.answers

        return NormalizedIntake(
            tool_id=data.tool_id,
            organization_type=answers.get("org_type"),
            has_legal_entity=answers.get("has_legal_entity"),
            registration_status=answers.get("current_status"),
            legal_area=answers.get("project_area") or answers.get("query_area"),
            legal_question=answers.get("legal_question"),
            urgency_level=answers.get("urgency") or answers.get("timeline"),
            funding_source=answers.get("funding_source"),
            jurisdiction="PE",  # Default Perú
            topic_risk=self._detect_topic_risk(answers),
            structure_risk=self._detect_structure_risk(answers),
            normalized_fields=answers,
            intake_timestamp=datetime.utcnow().isoformat(),
        )

    def _detect_topic_risk(self, answers: Dict[str, Any]) -> str:
        """Detecta nivel de riesgo por tema"""
        high_risk_areas = ["Tributario (SUNAT)", "Cooperación internacional (APCI)"]
        area = answers.get("project_area") or answers.get("query_area")

        if isinstance(area, list):
            if any(a in high_risk_areas for a in area):
                return "HIGH"
        elif area in high_risk_areas:
            return "HIGH"

        return "MEDIUM"

    def _detect_structure_risk(self, answers: Dict[str, Any]) -> str:
        """Detecta nivel de riesgo por estructura organizacional"""
        has_entity = answers.get("has_legal_entity")
        org_type = answers.get("org_type")

        if has_entity is False:
            return "HIGH"
        if org_type in ["Colectivo sin personería", "Colectivo estudiantil"]:
            return "HIGH"

        return "LOW"

    async def process(self, data: IntakeData) -> NormalizedIntake:
        """
        Procesa el intake completo:
        1. Valida campos requeridos
        2. Verifica inputs contra opciones válidas
        3. Normaliza respuestas
        """
        # Validar campos requeridos
        missing = self.validate_required_fields(data)
        if missing:
            raise ValueError(f"Campos requeridos faltantes: {missing}")

        # Verificar selector inputs
        errors = self.enforce_selector_inputs(data)
        if errors:
            raise ValueError(f"Errores de validación: {errors}")

        # Normalizar
        return self.normalize_answers(data)
