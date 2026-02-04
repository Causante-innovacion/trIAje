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
# FICHA LEGAL MÍNIMA - Bloques de preguntas base (comunes a todas las herramientas)
# =============================================================================

BLOCK_IDENTITY = QuestionBlock(
    id="identity",
    name="Identidad y naturaleza",
    description="Información básica sobre la organización",
    icon="Fingerprint",
    order=1,
    questions=[
        QuestionDefinition(
            id="org_type",
            text="¿Con cuál de las siguientes opciones se identifica mejor?",
            input_type=InputType.ENUM,
            options=ValidOptions.ORG_TYPES,
            help_text="Seleccione el tipo de organización que mejor describe su situación actual.",
            block="identity",
            order=1,
        ),
        QuestionDefinition(
            id="org_purpose",
            text="¿Cuál describe mejor el objeto o fin principal de la organización?",
            input_type=InputType.ENUM,
            options=ValidOptions.ORG_PURPOSES,
            help_text="El objeto social determina muchas obligaciones legales y beneficios tributarios.",
            block="identity",
            order=2,
        ),
        QuestionDefinition(
            id="seeks_profits",
            text="¿La organización busca generar ganancias para repartir entre sus miembros?",
            input_type=InputType.BOOLEAN,
            help_text="Las organizaciones sin fines de lucro no distribuyen utilidades entre sus miembros.",
            block="identity",
            order=3,
        ),
    ],
)

BLOCK_FORMALIZATION = QuestionBlock(
    id="formalization",
    name="Nivel de formalización",
    description="Estado de inscripción y registros",
    icon="Gavel",
    order=2,
    questions=[
        QuestionDefinition(
            id="has_legal_status",
            text="¿La organización cuenta actualmente con personería jurídica vigente?",
            input_type=InputType.ENUM,
            options=ValidOptions.YES_NO_IN_PROGRESS,
            help_text="La personería jurídica se obtiene al inscribirse en Registros Públicos (SUNARP).",
            block="formalization",
            order=1,
        ),
        QuestionDefinition(
            id="ruc_status",
            text="¿Cuál es la situación del RUC?",
            input_type=InputType.ENUM,
            options=ValidOptions.RUC_STATUS,
            help_text="El RUC es necesario para emitir comprobantes y cumplir obligaciones tributarias.",
            block="formalization",
            order=2,
        ),
        QuestionDefinition(
            id="special_registries",
            text="¿La organización está inscrita en algún registro especial?",
            input_type=InputType.MULTI_SELECT,
            options=ValidOptions.SPECIAL_REGISTRIES,
            help_text="Estos registros otorgan beneficios específicos según el tipo de organización.",
            block="formalization",
            order=3,
        ),
    ],
)

BLOCK_INCOME = QuestionBlock(
    id="income",
    name="Fuentes de ingreso",
    description="Manejo de fondos y financiamiento",
    icon="Banknote",
    order=3,
    questions=[
        QuestionDefinition(
            id="handles_money",
            text="¿La organización maneja o manejará dinero?",
            input_type=InputType.BOOLEAN,
            help_text="Incluye donaciones, cuotas, pagos por servicios, etc.",
            block="income",
            order=1,
        ),
        QuestionDefinition(
            id="receives_foreign_funds",
            text="¿Recibe o planea recibir fondos desde fuera del Perú?",
            input_type=InputType.BOOLEAN,
            help_text="Fondos extranjeros pueden requerir registro en APCI y tienen tratamiento tributario especial.",
            block="income",
            order=2,
        ),
        QuestionDefinition(
            id="income_sources",
            text="¿De dónde provienen o provendrán los ingresos?",
            input_type=InputType.MULTI_SELECT,
            options=ValidOptions.INCOME_SOURCES,
            help_text="Seleccione todas las fuentes de ingreso que apliquen.",
            block="income",
            order=3,
        ),
    ],
)

BLOCK_INTERNATIONAL_COOPERATION = QuestionBlock(
    id="international_cooperation",
    name="Cooperación internacional",
    description="Registro y requisitos APCI",
    icon="Globe",
    order=4,
    questions=[
        QuestionDefinition(
            id="receives_international_cooperation",
            text="¿La organización recibe o planea recibir cooperación técnica internacional?",
            input_type=InputType.BOOLEAN,
            help_text="La cooperación técnica incluye asistencia, capacitación, transferencia de tecnología y donaciones de fuentes internacionales.",
            block="international_cooperation",
            order=1,
        ),
        QuestionDefinition(
            id="apci_status",
            text="¿Cuál es la situación respecto al registro en APCI?",
            input_type=InputType.ENUM,
            options=ValidOptions.APCI_STATUS,
            help_text="La APCI es la Agencia Peruana de Cooperación Internacional. El registro es obligatorio para recibir cooperación internacional.",
            depends_on={"receives_international_cooperation": True},
            block="international_cooperation",
            order=2,
        ),
    ],
)

BLOCK_HUMAN_RESOURCES = QuestionBlock(
    id="human_resources",
    name="Recursos humanos",
    description="Modalidades de contratación",
    icon="Users",
    order=5,
    questions=[
        QuestionDefinition(
            id="hiring_modalities",
            text="¿Qué modalidades de contratación utiliza o planea utilizar la organización?",
            input_type=InputType.MULTI_SELECT,
            options=ValidOptions.HIRING_MODALITIES,
            help_text="Cada modalidad tiene diferentes obligaciones legales y costos asociados.",
            block="human_resources",
            order=1,
        ),
        QuestionDefinition(
            id="contracts_valid",
            text="¿Los contratos o acuerdos con el personal están actualmente vigentes y formalizados?",
            input_type=InputType.ENUM,
            options=ValidOptions.YES_NO_NA,
            help_text="Contratos escritos y vigentes protegen tanto a la organización como a los trabajadores.",
            block="human_resources",
            order=2,
        ),
    ],
)

BLOCK_ACCOUNTING = QuestionBlock(
    id="accounting",
    name="Información contable",
    description="Registros financieros y documentación",
    icon="BookOpen",
    order=6,
    questions=[
        QuestionDefinition(
            id="has_accounting_records",
            text="¿Existen registros contables o financieros?",
            input_type=InputType.ENUM,
            options=ValidOptions.ACCOUNTING_STATUS,
            help_text="Los registros contables son obligatorios para organizaciones con RUC.",
            block="accounting",
            order=1,
        ),
        QuestionDefinition(
            id="available_documents",
            text="¿La organización cuenta con alguno de los siguientes documentos?",
            input_type=InputType.MULTI_SELECT,
            options=ValidOptions.AVAILABLE_DOCUMENTS,
            help_text="Estos documentos son importantes para la trazabilidad legal y financiera.",
            block="accounting",
            order=2,
        ),
    ],
)

BLOCK_GOVERNANCE = QuestionBlock(
    id="governance",
    name="Gobernanza y representación",
    description="Órganos de gobierno y representación legal",
    icon="Network",
    order=7,
    questions=[
        QuestionDefinition(
            id="has_governance_bodies",
            text="¿La organización tiene órganos de gobierno definidos (asamblea, consejo, directorio, etc.)?",
            input_type=InputType.BOOLEAN,
            help_text="Los órganos de gobierno son necesarios para la toma de decisiones válidas.",
            block="governance",
            order=1,
        ),
        QuestionDefinition(
            id="has_legal_representative",
            text="¿Existe una persona designada como representante legal inscrito en Registros Públicos?",
            input_type=InputType.ENUM,
            options=ValidOptions.YES_NO_IN_PROGRESS,
            help_text="El representante legal puede actuar en nombre de la organización.",
            block="governance",
            order=2,
        ),
    ],
)

BLOCK_INTANGIBLES = QuestionBlock(
    id="intangibles",
    name="Uso de intangibles",
    description="Software, datos y propiedad intelectual",
    icon="Lightbulb",
    order=8,
    questions=[
        QuestionDefinition(
            id="intangible_assets",
            text="¿La organización utiliza alguno de los siguientes?",
            input_type=InputType.MULTI_SELECT,
            options=ValidOptions.INTANGIBLE_ASSETS,
            help_text="El uso de intangibles puede generar obligaciones de licenciamiento y protección de datos.",
            block="intangibles",
            order=1,
        ),
    ],
)

# Lista de todos los bloques de la Ficha Legal Mínima
LEGAL_PROFILE_BLOCKS = [
    BLOCK_IDENTITY,
    BLOCK_FORMALIZATION,
    BLOCK_INCOME,
    BLOCK_INTERNATIONAL_COOPERATION,
    BLOCK_HUMAN_RESOURCES,
    BLOCK_ACCOUNTING,
    BLOCK_GOVERNANCE,
    BLOCK_INTANGIBLES,
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
            options=ValidOptions.URGENCY_LEVELS,
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
