"""
RAG Module - Insufficient Evidence Protocol
Manejo de casos donde la evidencia es insuficiente.

Según spec, si evidence_score < 0.65:
- block_assertion
- Solo permitir: orientation_only, conditional_statement, advisor_recommendation
- Nunca: legal_requirement_claim, mandatory_statement, numeric obligation
"""

from enum import Enum
from typing import List
from pydantic import BaseModel


class ResponseType(str, Enum):
    """Tipos de respuesta permitidos según nivel de evidencia"""
    # Permitidos con evidencia insuficiente
    ORIENTATION_ONLY = "orientation_only"
    CONDITIONAL_STATEMENT = "conditional_statement"
    ADVISOR_RECOMMENDATION = "advisor_recommendation"

    # Requieren evidencia suficiente
    LEGAL_REQUIREMENT_CLAIM = "legal_requirement_claim"
    MANDATORY_STATEMENT = "mandatory_statement"
    NUMERIC_OBLIGATION = "numeric_obligation"


class InsufficientEvidenceResponse(BaseModel):
    """Respuesta cuando la evidencia es insuficiente"""
    message: str
    response_type: ResponseType
    suggestions: List[str]
    escalation_recommended: bool
    data_request: str | None = None  # Qué dato/fuente se necesita


class InsufficientEvidenceProtocol:
    """
    Protocolo para manejar casos de evidencia insuficiente.
    """

    # Respuestas prohibidas sin evidencia suficiente
    BLOCKED_RESPONSE_TYPES = [
        ResponseType.LEGAL_REQUIREMENT_CLAIM,
        ResponseType.MANDATORY_STATEMENT,
        ResponseType.NUMERIC_OBLIGATION,
    ]

    # Frases prohibidas sin evidencia
    BLOCKED_PHRASES = [
        "debes",
        "tienes que",
        "es obligatorio",
        "está prohibido",
        "la ley exige",
        "el plazo es",
        "la multa es",
        "se requiere exactamente",
    ]

    # Templates de respuesta segura
    SAFE_RESPONSE_TEMPLATES = {
        "insufficient_general": (
            "No tengo información suficiente para afirmar eso con seguridad. "
            "Te recomiendo {suggestion}."
        ),
        "insufficient_specific": (
            "Para responder con precisión sobre {topic}, necesitaría "
            "información adicional sobre {missing_data}. "
            "En general, {orientation}."
        ),
        "escalation": (
            "Este tema tiene implicaciones importantes que requieren "
            "validación profesional. Te sugiero consultar con {advisor_type}."
        ),
    }

    def __init__(self, confidence_threshold: float = 0.65):
        self.threshold = confidence_threshold

    def check_response_allowed(
        self,
        response_type: ResponseType,
        confidence: float
    ) -> bool:
        """
        Verifica si un tipo de respuesta está permitido dado el confidence.
        """
        if confidence >= self.threshold:
            return True

        return response_type not in self.BLOCKED_RESPONSE_TYPES

    def check_phrase_allowed(self, text: str, confidence: float) -> List[str]:
        """
        Verifica si el texto contiene frases prohibidas dado el confidence.
        Retorna lista de frases problemáticas encontradas.
        """
        if confidence >= self.threshold:
            return []

        text_lower = text.lower()
        problems = [
            phrase for phrase in self.BLOCKED_PHRASES
            if phrase in text_lower
        ]
        return problems

    def build_safe_response(
        self,
        confidence: float,
        topic: str | None = None,
        missing_data: str | None = None,
        orientation: str | None = None,
    ) -> InsufficientEvidenceResponse:
        """
        Construye una respuesta segura cuando la evidencia es insuficiente.
        """
        suggestions = [
            "Consultar con un abogado especializado",
            "Revisar directamente la normativa aplicable",
            "Contactar a la autoridad competente para confirmar",
        ]

        if missing_data:
            message = self.SAFE_RESPONSE_TEMPLATES["insufficient_specific"].format(
                topic=topic or "este tema",
                missing_data=missing_data,
                orientation=orientation or "se sugiere buscar asesoría especializada",
            )
        else:
            message = self.SAFE_RESPONSE_TEMPLATES["insufficient_general"].format(
                suggestion=suggestions[0].lower(),
            )

        return InsufficientEvidenceResponse(
            message=message,
            response_type=ResponseType.ORIENTATION_ONLY,
            suggestions=suggestions,
            escalation_recommended=True,
            data_request=missing_data,
        )

    def build_escalation_response(
        self,
        reason: str,
        advisor_type: str = "un abogado especializado"
    ) -> InsufficientEvidenceResponse:
        """
        Construye respuesta de escalamiento a asesor humano.
        """
        message = self.SAFE_RESPONSE_TEMPLATES["escalation"].format(
            advisor_type=advisor_type,
        )

        return InsufficientEvidenceResponse(
            message=message,
            response_type=ResponseType.ADVISOR_RECOMMENDATION,
            suggestions=[
                f"Consultar con {advisor_type}",
                "Preparar documentación del caso",
                "Agendar asesoría legal",
            ],
            escalation_recommended=True,
            data_request=None,
        )

    def sanitize_response(self, text: str, confidence: float) -> str:
        """
        Sanitiza una respuesta para remover afirmaciones no permitidas.
        Reemplaza frases prohibidas con versiones condicionales.
        """
        if confidence >= self.threshold:
            return text

        result = text

        replacements = {
            "debes": "podrías necesitar",
            "tienes que": "generalmente se requiere",
            "es obligatorio": "suele ser requerido",
            "está prohibido": "podría estar restringido",
            "la ley exige": "la normativa generalmente indica",
        }

        for blocked, safe in replacements.items():
            result = result.replace(blocked, safe)
            result = result.replace(blocked.capitalize(), safe.capitalize())

        return result
