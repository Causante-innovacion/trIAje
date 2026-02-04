"""
Intake Module - Schemas
Tipos de entrada permitidos y estructuras de datos
"""

from enum import Enum
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class InputType(str, Enum):
    """Tipos de entrada permitidos según spec"""
    BOOLEAN = "boolean"
    ENUM = "enum"
    MULTI_SELECT = "multi_select"
    RANGE = "range"
    ROLE_SELECTOR = "role_selector"
    # Nunca permitidos para datos críticos:
    # FREE_TEXT = "free_text"  # Solo para campos no críticos


class QuestionDefinition(BaseModel):
    """Definición de una pregunta del intake"""
    id: str
    text: str
    input_type: InputType
    required: bool = True
    options: List[str] | None = None  # Para enum, multi_select
    range_min: int | None = None      # Para range
    range_max: int | None = None
    help_text: str | None = None      # Contextual help
    depends_on: str | None = None     # Conditional display


class IntakeData(BaseModel):
    """Datos crudos del intake (antes de normalizar)"""
    tool_id: int = Field(..., ge=1, le=4, description="ID del modo/herramienta")
    answers: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] | None = None


class NormalizedIntake(BaseModel):
    """Datos normalizados del intake"""
    tool_id: int

    # Datos de la organización
    organization_type: str | None = None
    has_legal_entity: bool | None = None
    registration_status: str | None = None

    # Datos del problema/consulta
    legal_area: str | None = None
    legal_question: str | None = None
    urgency_level: str | None = None

    # Datos de contexto
    funding_source: str | None = None
    jurisdiction: str = "PE"  # Default: Perú

    # Riesgos detectados en intake
    topic_risk: str | None = None
    structure_risk: str | None = None

    # Campos adicionales normalizados
    normalized_fields: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    intake_timestamp: str | None = None
    intake_version: str = "1.0"


class QuestionSet(BaseModel):
    """Conjunto de preguntas para un modo específico"""
    tool_id: int
    tool_name: str
    questions: List[QuestionDefinition]
    version: str = "1.0"
