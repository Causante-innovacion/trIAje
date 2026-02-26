"""
Advisor Prep Feature - Service
Genera paquete para reunión con asesor a partir de la conversación del chat.
"""

import json
from typing import List, Dict, Any, Optional

from app.ai.router import AIRouter
from .schemas import AdvisorPrepFromChatRequest


# Esquema JSON que el LLM debe producir (coincide con LegalAdviserPackage del frontend)
_PACKAGE_SCHEMA = {
    "pageTitle": "string",
    "pageSubtitle": "string",
    "organizationProfile": {
        "entityName": "string",
        "legalStatus": "green|yellow|red",
        "stage": "prototipo|piloto|escalamiento|unknown",
        "fundingTypes": ["nacional", "extranjero"]
    },
    "legalStatusCards": [
        {"id": "string", "label": "string", "status": "green|yellow|red"}
    ],
    "fundingCritical": {
        "min": "string",
        "max": "string",
        "description": "string"
    },
    "fundingDescription": "string",
    "criticalTopics": [
        {
            "id": "string",
            "title": "string",
            "description": "string",
            "priority": "URGENTE"
        }
    ],
    "lawyerQuestions": [
        {"id": "string", "number": 1, "question": "string"}
    ],
    "requiredDocuments": [
        {"id": "string", "title": "string", "completed": False}
    ],
    "internalDecisions": [
        {
            "id": "string",
            "scenario": "string",
            "options": [{"id": "string", "label": "string"}]
        }
    ]
}

_SYSTEM_PROMPT = """
Eres un asistente legal especializado en derecho peruano para organizaciones civiles.
Tu tarea: analizar una conversación de consulta legal y generar un paquete estructurado
de preparación para una reunión con el asesor.

Reglas ESTRICTAS:
- SOLO incluye temas, áreas legales y problemas que aparezcan EXPLÍCITAMENTE en la conversación.
  NO inventes ni supongas temas no mencionados (ej: si no se habla de "sostenibilidad", no lo incluyas).
- Para campos sin información suficiente, usa "No especificado" o déjalo vacío. 
  NUNCA rellenes con temas inventados o de contexto general.
- pageTitle: siempre "Paquete de preparación para reunión con asesor legal".
- pageSubtitle: resume en UNA frase el tema legal central de la conversación
  (ej: "Denuncia SUNAFIL por ex-trabajador" o "Consulta sobre registro APCI").
  NUNCA copies mensajes del usuario verbatim como "Sí, la información es correcta".
- criticalTopics: OBLIGATORIO generar al menos 1 tema crítico basado en la conversación.
- lawyerQuestions: OBLIGATORIO generar al menos 3 preguntas específicas para el asesor.
- requiredDocuments: OBLIGATORIO listar al menos 2 documentos relevantes.
- fundingTypes: OBLIGATORIO — array con uno o ambos valores:
    "nacional" si solo recibe fondos locales o no se menciona financiamiento internacional.
    "extranjero" si se menciona cooperación internacional, APCI, donaciones del exterior, etc.
    NUNCA dejes este array vacío.
- internalDecisions: OBLIGATORIO generar al menos 2 decisiones internas que la organización debe votar o acordar antes de la reunión.
  Ejemplo: {"scenario": "Tipo de contratación del siguiente ciclo", "options": [{"label": "Contrato a plazo fijo"}, {"label": "Contrato por proyecto"}]}.
  Basa las decisiones en las brechas, el financiamiento y la situación legal identificada.
- Si el área es tributaria → legalStatusCards incluye SUNAT/RUC.
- Si es laboral → MTPE, contratos laborales.
- Si es formalización → SUNARP, estatutos.
- Si es APCI/cooperación → APCI, Ministerio de RREE; agrega "extranjero" en fundingTypes.
- legalStatus: 'red' si hay problema grave detectado, 'yellow' si hay incertidumbre, 'green' si está regularizado.
- Responde SOLO con JSON válido. Sin explicaciones. Sin markdown.
"""


class AdvisorPrepService:
    """Genera paquetes de preparación para asesor a partir de la conversación del chat."""

    def __init__(self):
        self._ai_router = AIRouter()

    async def generate_from_chat(
        self,
        request: AdvisorPrepFromChatRequest,
    ) -> Dict[str, Any]:
        """
        Genera paquete para asesor a partir de la conversación del chat.
        Usa el LLM para extraer contexto y generar contenido personalizado.
        """
        conversation = request.conversation

        if not conversation:
            return _empty_package()

        conv_text = _format_conversation(conversation)

        prompt = (
            f"Analiza esta conversación de consulta legal y genera el paquete de preparación:\n\n"
            f"{conv_text}\n\n"
            f"Genera el paquete JSON completo siguiendo EXACTAMENTE esta estructura:\n"
            f"{json.dumps(_PACKAGE_SCHEMA, ensure_ascii=False, indent=2)}\n\n"
            f"Notas:\n"
            f"- IMPORTANTE: la conversación puede comenzar con un bloque '=== CONTEXTO DEL PROYECTO ===' "
            f"con datos extraídos del Plan Estratégico (organizaciones, brechas, financiamiento). "
            f"Úsalo para generar contenido específico y personalizado.\n"
            f"- entityName: nombre de la organización si se menciona, si no: 'Organización consultante'\n"
            f"- legalStatusCards: incluye los registros relevantes (SUNARP, RUC, SUNAT, APCI, MTPE, etc.) "
            f"con el estado que se infiere de la conversación\n"
            f"- fundingCritical.min/max: rangos estimados si se menciona financiamiento, si no: 'No especificado'\n"
            f"- lawyerQuestions: preguntas CONCRETAS y ESPECÍFICAS basadas en las brechas y situación real, NO genéricas\n"
            f"- internalDecisions: OBLIGATORIO mínimo 2 — escenarios reales de decisión pre-reunión basados "
            f"en las brechas del proyecto, tipo de financiamiento y situación legal detectada"
        )

        try:
            result = await self._ai_router.reason_json(
                prompt=prompt,
                schema=_PACKAGE_SCHEMA,
                system_prompt=_SYSTEM_PROMPT,
            )
            normalized = _normalize_package(result)
            # Validate that the package has meaningful content; if not, use fallback
            has_topics = bool(normalized.get("criticalTopics"))
            has_questions = bool(normalized.get("lawyerQuestions"))
            if not has_topics and not has_questions:
                return _fallback_package(conversation)
            return normalized
        except Exception:
            return _fallback_package(conversation)


# =============================================================================
# HELPERS (funciones puras, fuera de la clase)
# =============================================================================

def _format_conversation(conversation: List[Dict[str, str]]) -> str:
    """Formatea la conversación como texto legible para el prompt."""
    lines = []
    for turn in conversation:
        role = "Usuario" if turn.get("role") == "user" else "Asistente Legal (JUSTO)"
        content = turn.get("content", "").strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n\n".join(lines)


def _normalize_package(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza y completa campos faltantes del paquete generado por el LLM."""
    raw.setdefault("pageTitle", "Ruta de preparación para reunión con asesor legal")
    raw.setdefault("pageSubtitle", "GENERADA EN BASE A TU CONSULTA LEGAL")

    profile = raw.setdefault("organizationProfile", {})
    profile.setdefault("entityName", "Organización consultante")
    profile.setdefault("legalStatus", "yellow")
    profile.setdefault("stage", "unknown")
    # Always ensure fundingTypes is a non-empty list (override empty array too)
    if not profile.get("fundingTypes"):
        profile["fundingTypes"] = ["nacional"]

    raw.setdefault("legalStatusCards", [])
    raw.setdefault("fundingCritical", {
        "min": "No especificado",
        "max": "No especificado",
        "description": "Evaluar con el asesor según las necesidades de la organización",
    })
    raw.setdefault("fundingDescription", "Por determinar")
    raw.setdefault("criticalTopics", [])
    raw.setdefault("lawyerQuestions", [])
    raw.setdefault("requiredDocuments", [])
    raw.setdefault("internalDecisions", [])

    # Normalizar IDs y números
    for i, q in enumerate(raw.get("lawyerQuestions", []), 1):
        q["id"] = str(q.get("id", i))
        q["number"] = int(q.get("number", i))

    for i, doc in enumerate(raw.get("requiredDocuments", []), 1):
        doc["id"] = str(doc.get("id", i))
        doc.setdefault("completed", False)

    for i, topic in enumerate(raw.get("criticalTopics", []), 1):
        topic["id"] = str(topic.get("id", i))
        topic["priority"] = "URGENTE"

    for i, card in enumerate(raw.get("legalStatusCards", []), 1):
        card["id"] = str(card.get("id", i))

    for i, dec in enumerate(raw.get("internalDecisions", []), 1):
        dec["id"] = str(dec.get("id", i))
        for j, opt in enumerate(dec.get("options", []), 1):
            opt["id"] = str(opt.get("id", f"{i}{chr(96+j)}"))

    return raw


def _empty_package() -> Dict[str, Any]:
    """Paquete cuando no hay conversación disponible."""
    return {
        "pageTitle": "Ruta de preparación para reunión con asesor legal",
        "pageSubtitle": "NO HAY CONSULTAS REGISTRADAS — INICIA UNA CONSULTA EN EL CHAT",
        "organizationProfile": {
            "entityName": "Sin información",
            "legalStatus": "yellow",
            "stage": "unknown",
            "fundingTypes": ["nacional"],
        },
        "legalStatusCards": [],
        "fundingCritical": {
            "min": "—",
            "max": "—",
            "description": "Realiza una consulta en el chat para obtener orientación personalizada.",
        },
        "fundingDescription": "—",
        "criticalTopics": [{
            "id": "1",
            "title": "Iniciar consulta en el chat",
            "description": (
                "Ve al chat y describe tu situación legal. "
                "El sistema generará automáticamente este paquete con información de tu caso."
            ),
            "priority": "URGENTE",
        }],
        "lawyerQuestions": [],
        "requiredDocuments": [],
        "internalDecisions": [],
    }


def _fallback_package(conversation: List[Dict[str, str]]) -> Dict[str, Any]:
    """Paquete básico de fallback cuando el LLM falla."""
    FILLER = {'sí, la información es correcta', 'si, la información es correcta',
              'sí, es correcto', 'correcto', 'ok', 'okay', 'de acuerdo', 'entendido'}
    user_messages = [
        t["content"] for t in conversation
        if t.get("role") == "user" and t.get("content", "").strip().lower() not in FILLER
    ]
    # Use last substantive user message (most specific to the problem)
    main_concern = user_messages[-1][:300] if user_messages else "Consulta legal general"
    return {
        "pageTitle": "Ruta de preparación para reunión con asesor legal",
        "pageSubtitle": "GENERADA EN BASE A TU CONSULTA LEGAL",
        "organizationProfile": {
            "entityName": "Organización consultante",
            "legalStatus": "yellow",
            "stage": "unknown",
            "fundingTypes": ["nacional"],
        },
        "legalStatusCards": [
            {"id": "1", "label": "Estado general", "status": "yellow"},
        ],
        "fundingCritical": {
            "min": "No especificado",
            "max": "No especificado",
            "description": "Definir con el asesor según las necesidades de la organización.",
        },
        "fundingDescription": "Por determinar",
        "criticalTopics": [{
            "id": "1",
            "title": "Tema principal de consulta",
            "description": main_concern,
            "priority": "URGENTE",
        }],
        "lawyerQuestions": [
            {"id": "1", "number": 1, "question": "¿Cuál es la mejor estrategia para abordar esta situación?"},
            {"id": "2", "number": 2, "question": "¿Cuáles son los riesgos legales principales y cómo mitigarlos?"},
            {"id": "3", "number": 3, "question": "¿Cuál es el cronograma estimado y costo para regularizar la situación?"},
        ],
        "requiredDocuments": [
            {"id": "1", "title": "Documentos de identidad de los representantes", "completed": False},
            {"id": "2", "title": "Documentación de la organización disponible", "completed": False},
        ],
        "internalDecisions": [],
    }


# Singleton
_service: Optional[AdvisorPrepService] = None


def get_advisor_prep_service() -> AdvisorPrepService:
    global _service
    if _service is None:
        _service = AdvisorPrepService()
    return _service
