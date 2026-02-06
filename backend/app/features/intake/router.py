"""
Intake Feature - Router
Endpoints para la Ficha Legal Mínima y validación de intake
"""

from fastapi import APIRouter, HTTPException, Query

from app.modules.intake import (
    intake_service,
    IntakeRequest,
    IntakeValidationResponse,
    QuestionSet,
    ToolType,
    ValidOptions,
)
from app.modules.intake.schemas import (
    ProjectIntakeRequest,
    ProjectValidationResponse,
    OrganizationRole,
)

router = APIRouter()


@router.get("/questions/{tool}", response_model=QuestionSet)
async def get_questions(tool: ToolType):
    """
    Obtiene el conjunto completo de preguntas para una herramienta.

    Retorna la Ficha Legal Mínima (8 bloques) + preguntas específicas de la herramienta.

    Args:
        tool: Tipo de herramienta (evaluation, compliance, query)

    Returns:
        QuestionSet con todos los bloques y preguntas
    """
    try:
        return intake_service.render_question_set(tool)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo preguntas: {str(e)}")


@router.get("/questions", response_model=dict)
async def get_all_questions():
    """
    Obtiene las preguntas para todas las herramientas.

    Útil para pre-cargar todas las preguntas en el frontend.

    Returns:
        Dict con QuestionSet por cada herramienta
    """
    try:
        return {
            "evaluation": intake_service.render_question_set(ToolType.EVALUATION),
            "compliance": intake_service.render_question_set(ToolType.COMPLIANCE),
            "query": intake_service.render_question_set(ToolType.QUERY),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo preguntas: {str(e)}")


@router.get("/options")
async def get_valid_options():
    """
    Obtiene todas las opciones válidas para los campos del intake.

    Útil para validación en el frontend y para poblar selects/checkboxes.

    Returns:
        Dict con todas las opciones válidas por campo
    """
    return {
        "org_types": ValidOptions.ORG_TYPES,
        "org_purposes": ValidOptions.ORG_PURPOSES,
        "yes_no_in_progress": ValidOptions.YES_NO_IN_PROGRESS,
        "ruc_status": ValidOptions.RUC_STATUS,
        "special_registries": ValidOptions.SPECIAL_REGISTRIES,
        "apci_status": ValidOptions.APCI_STATUS,
        "income_sources": ValidOptions.INCOME_SOURCES,
        "hiring_modalities": ValidOptions.HIRING_MODALITIES,
        "yes_no_na": ValidOptions.YES_NO_NA,
        "accounting_status": ValidOptions.ACCOUNTING_STATUS,
        "available_documents": ValidOptions.AVAILABLE_DOCUMENTS,
        "intangible_assets": ValidOptions.INTANGIBLE_ASSETS,
        "evaluation_goals": ValidOptions.EVALUATION_GOALS,
        "legal_areas": ValidOptions.LEGAL_AREAS,
        "urgency_levels": ValidOptions.URGENCY_LEVELS,
        "compliance_goals": ValidOptions.COMPLIANCE_GOALS,
        "timeline_options": ValidOptions.TIMELINE_OPTIONS,
        "query_areas": ValidOptions.QUERY_AREAS,
    }


@router.post("/validate", response_model=IntakeValidationResponse)
async def validate_intake(request: IntakeRequest):
    """
    Valida el intake completo y retorna el resultado.

    Realiza:
    1. Validación de campos requeridos
    2. Validación de opciones de selector
    3. Validación de consistencia cross-field
    4. Evaluación de riesgos
    5. Detección de señales de derivación

    Args:
        request: IntakeRequest con toda la información del formulario

    Returns:
        IntakeValidationResponse con:
        - valid: bool
        - errors: lista de errores (bloquean)
        - warnings: lista de warnings (no bloquean)
        - risk_assessment: evaluación de riesgo y color de derivación
        - normalized_data: datos normalizados si es válido
    """
    try:
        return intake_service.validate(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en validación: {str(e)}")


@router.post("/submit", response_model=IntakeValidationResponse)
async def submit_intake(request: IntakeRequest):
    """
    Envía el intake para procesamiento.

    Similar a validate pero con intención de procesar.
    Si la validación falla, retorna errores.
    Si la validación pasa, retorna los datos normalizados listos para procesamiento.

    Este endpoint es el que debe usarse cuando el usuario hace clic en "Enviar".

    Args:
        request: IntakeRequest con toda la información del formulario

    Returns:
        IntakeValidationResponse con datos normalizados para el siguiente paso
    """
    try:
        response = intake_service.validate(request)

        if not response.valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "El formulario contiene errores",
                    "errors": [e.model_dump() for e in response.errors],
                    "warnings": [w.model_dump() for w in response.warnings],
                }
            )

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando intake: {str(e)}")


@router.get("/summary/{tool}")
async def get_intake_summary(tool: ToolType):
    """
    Obtiene un resumen del intake para una herramienta.

    Útil para mostrar información al usuario antes de empezar.

    Args:
        tool: Tipo de herramienta

    Returns:
        Resumen con nombre de herramienta, bloques y conteo de preguntas
    """
    question_set = intake_service.render_question_set(tool)

    return {
        "tool": tool,
        "tool_name": question_set.tool_name,
        "total_questions": question_set.total_questions,
        "blocks": [
            {
                "id": block.id,
                "name": block.name,
                "description": block.description,
                "icon": block.icon,
                "question_count": len(block.questions),
            }
            for block in question_set.blocks
        ],
        "version": question_set.version,
    }


# =============================================================================
# MULTI-ORGANIZACIÓN - Endpoints para proyectos con 1-3 organizaciones
# =============================================================================

@router.get("/organization-roles")
async def get_organization_roles():
    """
    Obtiene los roles disponibles para organizaciones en un proyecto.

    Returns:
        Lista de roles con id y nombre
    """
    return [
        {"id": role.value, "name": role.value}
        for role in OrganizationRole
    ]


@router.post("/project/validate", response_model=ProjectValidationResponse)
async def validate_project(request: ProjectIntakeRequest):
    """
    Valida un proyecto con múltiples organizaciones (1-3).

    Realiza validación de cada organización y detecta riesgos compartidos.

    Args:
        request: ProjectIntakeRequest con lista de organizaciones

    Returns:
        ProjectValidationResponse con:
        - valid: bool
        - errors: lista de errores por organización
        - warnings: lista de warnings
        - risk_assessment: evaluación de riesgo agregada del proyecto
        - normalized_data: datos normalizados listos para enviar a IA
    """
    try:
        return intake_service.validate_project(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validando proyecto: {str(e)}")


@router.post("/project/submit", response_model=ProjectValidationResponse)
async def submit_project(request: ProjectIntakeRequest):
    """
    Envía un proyecto con múltiples organizaciones para procesamiento.

    Este es el endpoint principal para el flujo multi-organización.
    Retorna los datos normalizados listos para enviar a la IA.

    Args:
        request: ProjectIntakeRequest con lista de organizaciones

    Returns:
        ProjectValidationResponse con normalized_data para la IA
    """
    try:
        response = intake_service.validate_project(request)

        if not response.valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "El proyecto contiene errores de validación",
                    "errors": [e.model_dump() for e in response.errors],
                    "warnings": [w.model_dump() for w in response.warnings],
                }
            )

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando proyecto: {str(e)}")
