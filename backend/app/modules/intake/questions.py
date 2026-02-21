"""
Intake Module - Questions
Definición de todas las preguntas de la Ficha Legal Mínima y preguntas específicas por herramienta
"""

from .schemas import (
    InputType,
    QuestionBlock,
    QuestionDefinition,
    QuestionSet,
    ToolType,
    ValidOptions,
)


# =============================================================================
# FICHA LEGAL MÍNIMA V2 - Bloques de preguntas consolidados
# =============================================================================

BLOCK_IDENTITY = QuestionBlock(
    id="identity",
    name="Identificación y Naturaleza",
    description="¿Quién eres y qué haces con tus fondos?",
    icon="Fingerprint",
    order=1,
    questions=[
        QuestionDefinition(
            id="identity_v2",
            text="¿Cómo está organizada tu iniciativa y qué hacen con el dinero que generan?",
            input_type=InputType.ENUM,
            options=ValidOptions.IDENTITY_V2,
            help_text="- **Asociación/Fundación:** Sin fines de lucro.\n- **Empresa:** Con fines de lucro.\n- **Colectivo:** Sin personería jurídica.",
            block="identity",
            order=1,
        ),
        QuestionDefinition(
            id="org_purpose",
            text="¿Cuál describe mejor el objeto o fin principal de la organización?",
            input_type=InputType.ENUM,
            options=ValidOptions.ORG_PURPOSES,
            help_text="El entorno legal varía según el sector de impacto.",
            block="identity",
            order=2,
        ),
    ],
)

BLOCK_SUNAT = QuestionBlock(
    id="sunat",
    name="Situación Tributaria (SUNAT)",
    description="Estado formal ante la administración tributaria",
    icon="Gavel",
    order=2,
    questions=[
        QuestionDefinition(
            id="sunat_v2",
            text="¿Cómo es tu relación actual con la SUNAT?",
            input_type=InputType.ENUM,
            options=ValidOptions.SUNAT_V2,
            help_text="Define si tienes RUC activo, problemas fiscales o eres informal.",
            block="sunat",
            order=1,
        ),
    ],
)

BLOCK_FUNDS = QuestionBlock(
    id="funds",
    name="Fondos y Cooperación",
    description="Manejo de dinero del exterior",
    icon="Banknote",
    order=3,
    questions=[
        QuestionDefinition(
            id="funds_v2",
            text="¿Recibes dinero de fuentes fuera del Perú o de Cooperación Internacional?",
            input_type=InputType.ENUM,
            options=ValidOptions.FUNDS_V2,
            help_text="Determina la necesidad de registro en APCI y beneficios tributarios.",
            block="funds",
            order=1,
        ),
    ],
)

BLOCK_RESOURCES = QuestionBlock(
    id="resources",
    name="Recursos Humanos",
    description="Modalidades de vinculación del equipo",
    icon="Users",
    order=4,
    questions=[
        QuestionDefinition(
            id="hiring_v2",
            text="¿Bajo qué modalidades vinculas a las personas de tu equipo?",
            input_type=InputType.MULTI_SELECT,
            options=ValidOptions.HIRING_V2,
            help_text="Planilla, Locación, Voluntariado, Practicantes o Gestión de fundadores.",
            block="resources",
            order=1,
        ),
    ],
)

BLOCK_INTANGIBLES = QuestionBlock(
    id="intangibles",
    name="Activos e Intangibles",
    description="Uso de software, marcas y datos personales",
    icon="Lightbulb",
    order=5,
    questions=[
        QuestionDefinition(
            id="intangibles_v2",
            text="¿La organización utiliza o gestiona alguno de los siguientes?",
            input_type=InputType.MULTI_SELECT,
            options=ValidOptions.INTANGIBLES_V2,
            help_text="Software, Bases de datos (usuarios/beneficiarios) o Marcas/Logos.",
            block="intangibles",
            order=1,
        ),
    ],
)

BLOCK_URGENCY = QuestionBlock(
    id="urgency",
    name="Nivel de Urgencia",
    description="Prioridad de la consulta legal",
    icon="ClipboardList",
    order=6,
    questions=[
        QuestionDefinition(
            id="urgency_v2",
            text="¿Cuál es el nivel de urgencia o necesidad de tu consulta?",
            input_type=InputType.ENUM,
            options=ValidOptions.URGENCY_V2,
            help_text="Urgente disparará una derivación prioritaria a un especialista.",
            block="urgency",
            order=1,
        ),
    ],
)

# Lista de todos los bloques de la Ficha Legal Mínima V2
LEGAL_PROFILE_BLOCKS = [
    BLOCK_IDENTITY,
    BLOCK_SUNAT,
    BLOCK_FUNDS,
    BLOCK_RESOURCES,
    BLOCK_INTANGIBLES,
    BLOCK_URGENCY,
]


# =============================================================================
# PREGUNTAS ESPECÍFICAS POR HERRAMIENTA
# =============================================================================

BLOCK_EVALUATION_SPECIFIC = QuestionBlock(
    id="evaluation_specific",
    name="Detalles de evaluación",
    description="Información específica para la evaluación legal",
    icon="Search",
    order=9,
    questions=[
        QuestionDefinition(
            id="evaluation_goals",
            text="¿Qué aspectos desea evaluar?",
            input_type=InputType.MULTI_SELECT,
            options=ValidOptions.EVALUATION_GOALS,
            help_text="Seleccione los aspectos que le interesa evaluar de su organización.",
            block="evaluation_specific",
            order=1,
        ),
        QuestionDefinition(
            id="legal_areas",
            text="¿Qué áreas legales están involucradas o le preocupan?",
            input_type=InputType.MULTI_SELECT,
            options=ValidOptions.LEGAL_AREAS,
            help_text="Seleccione todas las áreas que considere relevantes.",
            block="evaluation_specific",
            order=2,
        ),
        QuestionDefinition(
            id="urgency",
            text="¿Cuál es la urgencia de esta evaluación?",
            input_type=InputType.ENUM,
            options=ValidOptions.URGENCY_V2,
            help_text="Esto nos ayuda a priorizar las recomendaciones.",
            block="evaluation_specific",
            order=3,
        ),
    ],
)

BLOCK_COMPLIANCE_SPECIFIC = QuestionBlock(
    id="compliance_specific",
    name="Objetivos de cumplimiento",
    description="Información específica para la ruta de cumplimiento",
    icon="CheckSquare",
    order=9,
    questions=[
        QuestionDefinition(
            id="compliance_goal",
            text="¿Cuál es el objetivo principal que desea lograr?",
            input_type=InputType.ENUM,
            options=ValidOptions.COMPLIANCE_GOALS,
            help_text="Seleccione el objetivo principal de cumplimiento.",
            block="compliance_specific",
            order=1,
        ),
        QuestionDefinition(
            id="timeline",
            text="¿En qué plazo desea completar este objetivo?",
            input_type=InputType.ENUM,
            options=ValidOptions.TIMELINE_OPTIONS,
            help_text="El plazo afecta la priorización de los pasos a seguir.",
            block="compliance_specific",
            order=2,
        ),
    ],
)

BLOCK_QUERY_SPECIFIC = QuestionBlock(
    id="query_specific",
    name="Consulta legal",
    description="Detalles de su consulta",
    icon="HelpCircle",
    order=9,
    questions=[
        QuestionDefinition(
            id="query_area",
            text="¿En qué área se enmarca su consulta?",
            input_type=InputType.ENUM,
            options=ValidOptions.QUERY_AREAS,
            help_text="Seleccione el área más relacionada con su consulta.",
            block="query_specific",
            order=1,
        ),
        QuestionDefinition(
            id="specific_question",
            text="¿Cuál es su consulta específica?",
            input_type=InputType.TEXT,
            required=True,
            help_text="Describa su consulta de forma clara y concisa. Incluya el contexto relevante.",
            block="query_specific",
            order=2,
        ),
    ],
)


# =============================================================================
# FUNCIONES PARA OBTENER CONJUNTOS DE PREGUNTAS
# =============================================================================

def get_legal_profile_blocks() -> list[QuestionBlock]:
    """Retorna los bloques de la Ficha Legal Mínima"""
    return LEGAL_PROFILE_BLOCKS.copy()


def get_tool_specific_block(tool: ToolType) -> QuestionBlock:
    """Retorna el bloque de preguntas específicas según la herramienta"""
    tool_blocks = {
        ToolType.EVALUATION: BLOCK_EVALUATION_SPECIFIC,
        ToolType.COMPLIANCE: BLOCK_COMPLIANCE_SPECIFIC,
        ToolType.QUERY: BLOCK_QUERY_SPECIFIC,
    }
    return tool_blocks[tool]


def get_question_set(tool: ToolType) -> QuestionSet:
    """
    Retorna el conjunto completo de preguntas para una herramienta.
    Incluye Ficha Legal Mínima + preguntas específicas de la herramienta.
    """
    tool_names = {
        ToolType.EVALUATION: "Evaluación Legal",
        ToolType.COMPLIANCE: "Ruta de Cumplimiento",
        ToolType.QUERY: "Consulta Legal",
    }

    blocks = get_legal_profile_blocks()
    blocks.append(get_tool_specific_block(tool))

    total_questions = sum(len(block.questions) for block in blocks)

    return QuestionSet(
        tool=tool,
        tool_name=tool_names[tool],
        blocks=blocks,
        version="2.0",
        total_questions=total_questions,
    )


def get_all_question_ids() -> list[str]:
    """Retorna todos los IDs de preguntas disponibles"""
    ids = []
    for block in LEGAL_PROFILE_BLOCKS:
        for question in block.questions:
            ids.append(question.id)
    for block in [BLOCK_EVALUATION_SPECIFIC, BLOCK_COMPLIANCE_SPECIFIC, BLOCK_QUERY_SPECIFIC]:
        for question in block.questions:
            ids.append(question.id)
    return ids


def get_question_by_id(question_id: str) -> QuestionDefinition | None:
    """Busca una pregunta por su ID"""
    all_blocks = LEGAL_PROFILE_BLOCKS + [
        BLOCK_EVALUATION_SPECIFIC,
        BLOCK_COMPLIANCE_SPECIFIC,
        BLOCK_QUERY_SPECIFIC,
    ]
    for block in all_blocks:
        for question in block.questions:
            if question.id == question_id:
                return question
    return None


def count_questions_by_tool(tool: ToolType) -> dict[str, int]:
    """Cuenta las preguntas por bloque para una herramienta"""
    question_set = get_question_set(tool)
    return {
        block.id: len(block.questions)
        for block in question_set.blocks
    }
