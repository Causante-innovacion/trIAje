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
            result = await self._ai_router.intake_json(
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
    context_block = ""
    lines = []
    for turn in conversation:
        role = turn.get("role", "")
        content = turn.get("content", "").strip()
        if not content:
            continue
        if role == "context":
            # Project context block — displayed as background section, not as a chat turn
            context_block = content
        elif role == "user":
            lines.append(f"Usuario: {content}")
        else:
            lines.append(f"Asistente Legal (JUSTO): {content}")

    parts = []
    if context_block:
        parts.append(context_block)
        parts.append("")  # blank line separator

    if lines:
        parts.append("\n\n".join(lines))
    elif context_block:
        # No user turns — came from evaluation page. Use explicit directive.
        parts.append(
            "SOLICITUD: Genera el paquete de preparación basándote EXCLUSIVAMENTE en el análisis "
            "legal mostrado arriba. Cada pregunta, tema crítico y decisión interna debe hacer "
            "referencia directa a un problema concreto identificado en ese análisis."
        )

    return "\n".join(parts)


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
        if t.get("role") == "user"
        and t.get("content", "").strip().lower() not in FILLER
        # Skip the structured context block injected by the frontend
        and not t.get("content", "").startswith("===")
        and not t.get("content", "").startswith("Basándote")
    ]

    # Try to extract a meaningful summary from the context block
    context_blocks = [
        t["content"] for t in conversation if t.get("role") == "context"
    ]

    if context_blocks:
        # Extract project title line from the context block as the main concern
        for line in context_blocks[0].splitlines():
            if line.startswith("=== ANÁLISIS LEGAL DEL PROYECTO:"):
                main_concern = line.replace("===", "").replace("ANÁLISIS LEGAL DEL PROYECTO:", "").strip().rstrip(" =")
                break
            if line.startswith("Nombre del proyecto:"):
                main_concern = line.replace("Nombre del proyecto:", "").strip()
                break
        else:
            main_concern = user_messages[-1][:300] if user_messages else "Consulta legal general"
    else:
        # Use last substantive user message (most specific to the problem)
        main_concern = user_messages[-1][:300] if user_messages else "Consulta legal general"

    # Extract critical issues from context block to build specific fallback content
    critical_issues: List[str] = []
    legal_entities: List[str] = []
    if context_blocks:
        in_critical = False
        in_entities = False
        for line in context_blocks[0].splitlines():
            if "CONDICIONES DE VIABILIDAD CRÍTICAS" in line:
                in_critical = True
                in_entities = False
            elif "ENTIDADES LEGALES CON PROBLEMAS" in line:
                in_entities = True
                in_critical = False
            elif line.startswith("===") or (line.strip() == "" and (in_critical or in_entities)):
                in_critical = False
                in_entities = False
            elif in_critical and line.strip().startswith("-"):
                # Extract "- [CRÍTICA] Title: reason" → "Title: reason"
                issue = line.strip().lstrip("- ").split("]")[-1].strip().rstrip(".")
                if issue:
                    critical_issues.append(issue[:200])
            elif in_entities and line.strip().startswith("-"):
                entity = line.strip().lstrip("- ").split("]")[-1].strip().rstrip(".")
                if entity:
                    legal_entities.append(entity[:150])

    # Build specific topics
    topics = []
    if critical_issues:
        for i, issue in enumerate(critical_issues[:3], 1):
            topics.append({
                "id": str(i),
                "title": issue.split(":")[0].strip() if ":" in issue else issue[:60],
                "description": issue,
                "priority": "URGENTE",
            })
    if not topics:
        topics = [{"id": "1", "title": main_concern[:60], "description": main_concern, "priority": "URGENTE"}]

    # Build specific questions
    questions = []
    if critical_issues:
        for i, issue in enumerate(critical_issues[:3], 1):
            title = issue.split(":")[0].strip() if ":" in issue else issue
            questions.append({"id": str(i), "number": i,
                              "question": f"¿Cuáles son los pasos concretos y el plazo para resolver: {title}?"})
    if legal_entities:
        q_id = len(questions) + 1
        entity = legal_entities[0].split(":")[0].strip() if ":" in legal_entities[0] else legal_entities[0]
        questions.append({"id": str(q_id), "number": q_id,
                          "question": f"¿Qué documentos y acciones específicas requiere regularizar {entity}?"})
    if len(questions) < 3:
        questions.append({"id": str(len(questions)+1), "number": len(questions)+1,
                          "question": "¿Cuáles son los riesgos legales si no se regulariza esta situación a tiempo?"})

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
        "criticalTopics": topics,
        "lawyerQuestions": questions,
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
