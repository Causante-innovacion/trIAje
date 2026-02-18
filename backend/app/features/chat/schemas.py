"""
Chat Feature - Schemas
Modelos Pydantic para entrada/salida del sistema de chat.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from .config import Intention, Semaphore


# =============================================================================
# ENUMS DE ACCIÓN
# =============================================================================

class ActionType(str, Enum):
    """Tipos de acción sugerida al usuario."""
    UPLOAD_FILE = "upload_file"
    DERIVE_TO_ADVISOR = "derive_to_advisor"
    PROVIDE_CONTEXT = "provide_context"
    NONE = "none"


# =============================================================================
# HISTORIAL DE CONVERSACIÓN
# =============================================================================

class HistoryMessage(BaseModel):
    """Turno de conversación anterior para memoria multi-turno."""
    role: str = Field(..., description="'user' o 'assistant'")
    content: str = Field(..., description="Contenido del mensaje")


# =============================================================================
# REQUEST
# =============================================================================

class ChatRequest(BaseModel):
    """Mensaje entrante del usuario."""
    message: str = Field(..., min_length=1, max_length=5000, description="Mensaje del usuario")
    conversation_id: Optional[str] = Field(None, description="ID de conversación para mantener contexto")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional (archivos, datos previos)")
    history: List[HistoryMessage] = Field(default_factory=list, description="Últimos N turnos de conversación")


# =============================================================================
# CLASIFICACIÓN
# =============================================================================

class ChatClassification(BaseModel):
    """Resultado de la clasificación de un mensaje."""
    intention: Intention = Field(..., description="Intención detectada (1 de 13)")
    intention_name: str = Field(..., description="Nombre legible de la intención")
    semaphore: Semaphore = Field(..., description="Semáforo: verde, amarillo o rojo")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza de la clasificación")
    gatillos_detected: List[str] = Field(default_factory=list, description="Gatillos (triggers) ROJO detectados")
    requires_context: List[str] = Field(default_factory=list, description="Datos adicionales requeridos (Amarillo)")


# =============================================================================
# FUENTE NORMATIVA
# =============================================================================

class LegalSource(BaseModel):
    """Fuente normativa citada en la respuesta."""
    title: str = Field(..., description="Nombre de la norma (ej: Código Civil)")
    article: Optional[str] = Field(None, description="Artículo específico (ej: Art. 80-82)")
    authority: Optional[str] = Field(None, description="Entidad emisora")
    url: Optional[str] = Field(None, description="Enlace SPIJ u oficial")


# =============================================================================
# ACCIÓN SUGERIDA
# =============================================================================

class SuggestedAction(BaseModel):
    """Acción sugerida al usuario como siguiente paso."""
    type: ActionType = Field(..., description="Tipo de acción")
    label: str = Field(..., description="Texto para el botón/enlace")
    description: str = Field("", description="Descripción detallada")
    endpoint: Optional[str] = Field(None, description="Endpoint a invocar si aplica")


# =============================================================================
# RESPONSE
# =============================================================================

class ChatResponse(BaseModel):
    """Respuesta completa del sistema de chat."""
    message: str = Field(..., description="Texto de respuesta al usuario")
    classification: ChatClassification = Field(..., description="Clasificación del mensaje")
    sources: List[LegalSource] = Field(default_factory=list, description="Fuentes normativas citadas")
    actions: List[SuggestedAction] = Field(default_factory=list, description="Acciones sugeridas")
    disclaimers: List[str] = Field(default_factory=list, description="Avisos legales")
    conversation_id: Optional[str] = Field(None, description="ID de conversación")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# ENDPOINTS AUXILIARES
# =============================================================================

class IntentionInfo(BaseModel):
    """Información de una intención para el endpoint de listado."""
    id: str
    name: str
    description: str
    example_questions: List[str]


class IntentionListResponse(BaseModel):
    """Lista de intenciones disponibles."""
    intentions: List[IntentionInfo]
    total: int


class GatilloInfo(BaseModel):
    """Información de un gatillo para el endpoint de listado."""
    intention: str
    intention_name: str
    trigger_phrases: List[str]
    derivation_reason: str


class GatilloListResponse(BaseModel):
    """Lista de gatillos configurados."""
    gatillos: List[GatilloInfo]
    total: int
