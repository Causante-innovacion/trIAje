"""
Chat Feature - Clasificador de Intenciones y Semáforo.

Implementa un sistema híbrido:
1. Detección de gatillos por reglas (determinista, rápido)
2. Clasificación de intención por keywords + LLM fallback
3. Clasificación de semáforo según gatillos y contexto

Para modificar las reglas, editar config.py (no este archivo).
"""

import re
import json
import unicodedata
from difflib import SequenceMatcher
from typing import Optional, Tuple, List

from app.ai.router import AIRouter
from app.core.config import settings

from .config import (
    Intention,
    Semaphore,
    INTENTIONS,
    GATILLOS,
    AMBER_CONTEXT_FIELDS,
    PROJECT_ANALYSIS_TRIGGERS,
)
from .schemas import ChatClassification


# =============================================================================
# PROMPT PARA CLASIFICACIÓN CON LLM
# =============================================================================

_INTENTION_DESCRIPTIONS = "\n".join(
    f"- {intent.value}: {cfg.name} — {cfg.description}"
    for intent, cfg in INTENTIONS.items()
    if intent != Intention.FUERA_DE_ALCANCE
)

CLASSIFICATION_SYSTEM_PROMPT = f"""Eres un clasificador de consultas legales para organizaciones civiles en Perú.

Tu tarea es clasificar el mensaje del usuario en UNA de las siguientes intenciones:

{_INTENTION_DESCRIPTIONS}
- fuera_de_alcance: La consulta NO está relacionada con ningún tema legal de los anteriores.

También debes determinar el nivel de semáforo:
- verde: Consulta informativa general que se puede responder directamente con normativa.
- amarillo: La consulta requiere contexto adicional del usuario para ser respondida correctamente.
- rojo: La consulta involucra un riesgo legal grave, un proceso de fiscalización/sanción activo, o situaciones que requieren un abogado.

Responde EXCLUSIVAMENTE en JSON con este formato:
{{
    "intention": "<id_de_intencion>",
    "semaphore": "<verde|amarillo|rojo>",
    "confidence": <0.0 a 1.0>,
    "reasoning": "<explicación breve>"
}}"""


def _normalize(text: str) -> str:
    """Normaliza texto: lowercase + quitar acentos para matching robusto."""
    text = text.lower()
    # Descomponer caracteres acentuados y filtrar marcas de combinación
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _fuzzy_contains(keyword: str, text_norm: str, threshold: float = 0.80) -> bool:
    """
    Comprueba si un keyword aparece en el texto normalizado.
    Estrategia en dos pasos:
      1. Coincidencia exacta de substring (rápida, sin costo).
      2. Fuzzy word-level con SequenceMatcher para tolerar errores tipográficos
         (solo para palabras de 5+ caracteres, evita falsos positivos en palabras cortas).

    Ejemplos que pasan:
      - 'baja provisional'  vs 'me dieron de baja probicional'  → True  (typo 'probicional')
      - 'SUNAT'             vs 'recibimos notificacion de SUNATT' → True  (typo doble t)
      - 'suspendid'         vs 'nos suspendio sunat'              → True  (variación morfológica)
      - 'ruc'               vs 'duc'                              → False (palabra corta, solo exacto)
    """
    kw_norm = _normalize(keyword)

    # 1. Coincidencia exacta de substring (prioritaria)
    if kw_norm in text_norm:
        return True

    kw_words = kw_norm.split()

    # Para keywords multi-palabra: las palabras cortas (< 5 chars) deben aparecer
    # exactamente en el texto. Evita que 'baja provisional' matchee 'secreto profesional'
    # porque 'baja' (4 chars) no está en el texto.
    if len(kw_words) > 1:
        for word in kw_words:
            if len(word) < 5 and word not in text_norm:
                return False

    # 2. Fuzzy solo para tokens de 5+ caracteres dentro del keyword
    kw_tokens = [w for w in kw_words if len(w) >= 5]
    if not kw_tokens:
        return False  # keyword corto: solo exacto

    text_words = text_norm.split()
    for kw_word in kw_tokens:
        # Filtrar palabras del texto de longitud similar (±2) para eficiencia
        candidates = [tw for tw in text_words if abs(len(tw) - len(kw_word)) <= 2]
        matched = any(
            SequenceMatcher(None, kw_word, tw).ratio() >= threshold
            for tw in candidates
        )
        if not matched:
            return False

    return True


class IntentionClassifier:
    """
    Clasifica la intención del mensaje del usuario.
    Usa keywords primero, LLM como fallback.
    """

    @staticmethod
    def classify_by_keywords(message: str) -> Tuple[Optional[Intention], float]:
        """
        Clasifica por coincidencia de keywords (rápido, sin costo).
        Retorna (intención, confianza) o (None, 0.0) si no hay match claro.
        """
        message_norm = _normalize(message)
        scores: dict[Intention, int] = {}

        for intention, config in INTENTIONS.items():
            if intention == Intention.FUERA_DE_ALCANCE:
                continue
            score = 0
            for kw in config.keywords:
                if _fuzzy_contains(kw, message_norm):
                    score += 1
            if score > 0:
                scores[intention] = score

        if not scores:
            return None, 0.0

        best = max(scores, key=scores.get)  # type: ignore
        # Cada acierto de palabra clave aporta 0.40 a la confianza
        confidence = min(scores[best] * 0.40, 1.0)

        return best, confidence

    @staticmethod
    async def classify_by_llm(message: str) -> Tuple[Intention, float, Optional["Semaphore"]]:
        """
        Clasifica usando el LLM.
        Retorna (intención, confianza, semáforo_opcional).
        El semáforo ya viene gratis en el mismo JSON — no hace falta una segunda llamada.
        """
        ai_router = AIRouter()

        schema = {
            "type": "object",
            "properties": {
                "intention": {"type": "string"},
                "semaphore": {"type": "string"},
                "confidence": {"type": "number"},
                "reasoning": {"type": "string"},
            },
            "required": ["intention", "semaphore", "confidence"],
        }

        try:
            result = await ai_router.intake_json(
                prompt=f"Clasifica esta consulta del usuario:\n\n\"{message}\"",
                schema=schema,
                system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
            )

            intention_str = result.get("intention", "fuera_de_alcance")
            confidence = float(result.get("confidence", 0.5))

            try:
                intention = Intention(intention_str)
            except ValueError:
                intention = Intention.FUERA_DE_ALCANCE
                confidence = 0.3

            # Capturar el semáforo que el LLM ya determinó en la misma llamada
            sem_str = result.get("semaphore", "").lower().strip()
            llm_semaphore: Optional[Semaphore] = None
            if sem_str == "rojo":
                llm_semaphore = Semaphore.ROJO
            elif sem_str == "amarillo":
                llm_semaphore = Semaphore.AMARILLO
            elif sem_str == "verde":
                llm_semaphore = Semaphore.VERDE

            return intention, confidence, llm_semaphore

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                "[IntentionClassifier] LLM call failed: %s: %s", type(e).__name__, e
            )
            return Intention.FUERA_DE_ALCANCE, 0.0, None

    @staticmethod
    async def classify(message: str) -> Tuple[Intention, float, Optional["Semaphore"]]:
        """
        Clasificación híbrida: keywords primero, LLM si no hay match claro.
        Retorna (intención, confianza, semáforo_del_llm_o_None).
        Cuando el semáforo viene del LLM, service.py puede usarlo directamente
        y omitir la segunda llamada al LLM para semáforo.
        """
        intention, confidence = IntentionClassifier.classify_by_keywords(message)

        # Si hay al menos un keyword match claro (> 0), saltar el lento LLM
        if intention and confidence >= 0.35:
            # Keywords suficientes para intención; semáforo se calcula por reglas (no LLM)
            return intention, confidence, None

        intention_llm, llm_confidence, llm_semaphore = await IntentionClassifier.classify_by_llm(message)

        if intention and confidence > 0:
            if intention_llm == intention:
                return intention, min(confidence + llm_confidence * 0.5, 1.0), llm_semaphore
            if llm_confidence > confidence:
                return intention_llm, llm_confidence, llm_semaphore
            return intention, confidence, llm_semaphore

        return intention_llm, llm_confidence, llm_semaphore


class SemaphoreClassifier:
    """
    Clasifica el semáforo (Verde/Amarillo/Rojo) del mensaje.
    Prioridad: Gatillos ROJO > Contexto AMARILLO > VERDE por defecto.
    """

    @staticmethod
    def detect_gatillos(message: str, intention: Intention) -> List[str]:
        """
        Detecta gatillos ROJO en el mensaje (por reglas, determinista).
        Busca en los gatillos de la intención detectada + gatillos globales.
        Usa normalización sin acentos para matching robusto.
        """
        message_norm = _normalize(message)
        detected: List[str] = []

        # Buscar en gatillos de la intención detectada
        intention_gatillos = GATILLOS.get(intention, [])
        for gatillo in intention_gatillos:
            for phrase in gatillo.trigger_phrases:
                if _normalize(phrase) in message_norm:
                    detected.append(phrase)

        # Buscar en TODOS los gatillos (puede cruzar intenciones)
        for intent, gatillo_list in GATILLOS.items():
            if intent == intention:
                continue
            for gatillo in gatillo_list:
                for phrase in gatillo.trigger_phrases:
                    if _normalize(phrase) in message_norm and phrase not in detected:
                        detected.append(phrase)

        return detected

    @staticmethod
    def _is_specific_case(message: str) -> bool:
        """
        Determina si el usuario habla de un CASO ESPECÍFICO (no una pregunta general).
        Solo los casos específicos justifican pedir contexto adicional.
        """
        message_lower = message.lower()
        # Indicadores de que el usuario tiene un caso concreto
        specificity_indicators = [
            # Posesivos → habla de SU situación
            r"\b(mi|mis|nuestro|nuestra|nuestros|nuestras)\b",
            # Verbos en primera persona con problema concreto
            r"\b(tengo|tenemos|recibí|recibimos|nos llegó|nos notificaron|me notificaron)\b",
            # Formas pasivas: "me dieron de baja", "nos pusieron en baja", "nos cancelaron el RUC"
            r"\b(me|nos)\s+(dieron|pusieron|cancelaron|suspendieron|quitaron|asignaron|bloquearon|retiraron|notificaron|cerraron|inhabilitaron)\b",
            # Palabras de problema/situación
            r"\b(problema|error|observación|conflicto|multa|notificación|denuncia|demanda)\b",
            # Verbos que implican acción en curso
            r"\b(estoy|estamos|necesito|necesitamos|quiero|queremos)\s+(haciendo|tramitando|cambiando|corrigiendo|resolviendo)",
            # Situación concreta
            r"\b(caso|situación|incidente|suceso)\b",
            # Estado actual: "estamos en baja", "quedamos con estado baja"
            r"\b(estamos|quedamos|estoy|quedé)\s+(en|con)\b",
        ]
        return any(re.search(p, message_lower) for p in specificity_indicators)

    @staticmethod
    def needs_context(message: str, intention: Intention) -> List[str]:
        """
        Determina si el mensaje necesita contexto adicional (AMARILLO).
        Solo retorna preguntas si el usuario tiene un caso específico
        que requiere más datos para ser respondido correctamente.
        """
        # Solo pedir contexto si el usuario habla de un caso específico
        if not SemaphoreClassifier._is_specific_case(message):
            return []

        context_fields = AMBER_CONTEXT_FIELDS.get(intention, [])
        if not context_fields:
            return []

        message_norm = _normalize(message)

        # Verificar si el mensaje ya proporciona contexto relevante
        prompts_needed: List[str] = []
        for field in context_fields:
            # Si el campo tiene trigger_keywords, solo preguntar si el topic es relevante
            if field.trigger_keywords:
                topic_relevant = any(_fuzzy_contains(kw, message_norm) for kw in field.trigger_keywords)
                if not topic_relevant:
                    continue

            # Solo preguntar si el usuario no proporcionó ya el dato.
            # Se requiere que TODOS los tokens del field_name estén presentes;
            # si solo aparece uno (ej. 'voluntarios' pero no 'cantidad'), el
            # contexto específico sigue siendo necesario.
            field_keywords = field.field_name.replace("_", " ").split()
            has_context = all(_fuzzy_contains(kw, message_norm) for kw in field_keywords)
            if not has_context:
                prompts_needed.append(field.example_prompt)

        return prompts_needed

    @staticmethod
    def _is_informative_question(message: str) -> bool:
        """
        Determina si el mensaje es una pregunta informativa general
        que se puede responder directamente sin pedir más contexto.
        """
        message_lower = message.lower().strip()

        informative_patterns = [
            # "¿Qué es/son/significa/requisitos/necesito/pasos/documentos...?"
            r"¿?qu[ée]\s+(es|son|significa|requisitos|necesito|pasos|documentos?|debo|hay que|implica|incluye|se necesita|se requiere)",
            # "¿Cómo + verbo?" (constituir, formalizar, hacer, crear, registrar, etc.)
            r"¿?c[óo]mo\s+\w+",
            # "¿Cuál/Cuáles es/son...?"
            r"¿?cu[áa]l(es)?\s+(es|son|ser[íi]a)",
            # "¿Cuánto cuesta/vale/dura/tarda...?"
            r"¿?cu[áa]nto\s+(cuesta|vale|dura|tarda|demora|tiempo)",
            # "¿Cuándo debo/tengo/hay/se...?"
            r"¿?cu[áa]ndo\s+(debo|tengo|hay|se\s+debe|es\s+necesario)",
            # "¿Dónde debo/puedo/tengo...?"
            r"¿?d[óo]nde\s+(debo|puedo|tengo|se\s+puede|se\s+hace|se\s+tramita|se\s+registra)",
            # "¿Puedo + infinitivo?" / "¿Se puede...?"
            r"¿?(puedo|se\s+puede|es\s+posible|es\s+legal|es\s+obligatorio|es\s+necesario)\s+\w+",
            # "¿Necesito + algo?"
            r"¿?necesito\s+\w+",
            # "Diferencia entre X e Y"
            r"diferencia\s+entre",
            # Verbos imperativos: "Explica/Describe/Dime..."
            r"^(explica|describe|dime|cuéntame|indícame|detalla)",
            # "Quiero saber/entender/conocer..."
            r"quiero\s+(saber|entender|conocer|aprender|informarme)",
        ]

        return any(re.search(p, message_lower) for p in informative_patterns)

    @staticmethod
    @staticmethod
    async def _ask_llm_semaphore(message: str, intention: Intention) -> Semaphore:
        """
        Consulta al LLM para determinar el nivel de riesgo cuando las reglas
        de palabras clave no detectaron un trigger ROJO.
        El LLM ya recibe el prompt completo de clasificación (CLASSIFICATION_SYSTEM_PROMPT)
        que incluye la definición de ROJO: casos activos, fiscalizaciones, sanciones.
        Solo se invoca desde service.py cuando el caso es específico (no pregunta general).
        """
        import logging
        ai_router = AIRouter()
        schema = {
            "type": "object",
            "properties": {
                "semaphore": {"type": "string", "enum": ["verde", "amarillo", "rojo"]},
                "reasoning": {"type": "string"},
            },
            "required": ["semaphore"],
        }
        context = INTENTIONS.get(intention)
        intention_hint = f" (intención detectada: {context.name})" if context else ""
        try:
            result = await ai_router.intake_json(
                prompt=(
                    f"Clasifica el nivel de riesgo de esta consulta{intention_hint}:\n\n\"{message}\"\n\n"
                    "Responde con el campo 'semaphore': verde (consulta general informativa), "
                    "amarillo (caso concreto que necesita más información), o "
                    "rojo (situación de riesgo grave activa: denuncia, fiscalización, sanción, "
                    "procedimiento legal formal en curso, urgencia legal)."
                ),
                schema=schema,
                system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
            )
            sem_str = result.get("semaphore", "verde").lower().strip()
            if sem_str == "rojo":
                return Semaphore.ROJO
            if sem_str == "amarillo":
                return Semaphore.AMARILLO
            return Semaphore.VERDE
        except Exception as e:
            logging.getLogger(__name__).warning(
                "[SemaphoreClassifier] LLM call failed, defaulting to VERDE: %s", e
            )
            return Semaphore.VERDE

    @staticmethod
    def classify(
        message: str,
        intention: Intention,
    ) -> Tuple[Semaphore, List[str], List[str]]:
        """
        Clasifica el semáforo completo (síncrono, solo reglas).
        Retorna (semáforo, gatillos_detectados, contexto_requerido).
        Para el fallback LLM de alto riesgo, ver service.py que llama
        _ask_llm_semaphore cuando el resultado es VERDE y el caso es específico.
        """
        # 1. ROJO: detectar gatillos
        gatillos = SemaphoreClassifier.detect_gatillos(message, intention)
        if gatillos:
            return Semaphore.ROJO, gatillos, []

        # 2. FUERA DE ALCANCE: no es rojo ni amarillo
        if intention == Intention.FUERA_DE_ALCANCE:
            return Semaphore.VERDE, [], []

        # 3. Si es una pregunta informativa general Y no es un caso específico → VERDE directo
        if SemaphoreClassifier._is_informative_question(message) and not SemaphoreClassifier._is_specific_case(message):
            return Semaphore.VERDE, [], []

        # 4. AMARILLO: verificar si necesita contexto (solo para casos específicos)
        context_needed = SemaphoreClassifier.needs_context(message, intention)
        if context_needed:
            return Semaphore.AMARILLO, [], context_needed

        # 5. VERDE por defecto (service.py hará el fallback LLM si es caso específico)
        return Semaphore.VERDE, [], []


class ProjectAnalysisDetector:
    """Detecta si el usuario quiere analizar un proyecto completo."""

    # Raíces verbales que indican voluntad de analizar/evaluar
    _VERB_STEMS = ("analiz", "evalú", "evalua", "revis", "viabilidad")
    # Palabras que indican un proyecto o emprendimiento
    _PROJECT_WORDS = ("proyecto", "emprendimiento", "iniciativa", "propuesta")

    # Formas canónicas completas para fuzzy matching (cubre también formas con tilde)
    _VERB_CANONICAL = (
        "analizar", "analiza", "analize", "analisis",
        "evaluar", "evalua", "evalúa", "evalúar",
        "revisar", "revisa",
        "viabilidad",
        "verificar", "checar",
    )
    _PROJECT_CANONICAL = (
        "proyecto", "proyectos",
        "emprendimiento", "emprendimientos",
        "iniciativa", "iniciativas",
        "propuesta", "propuestas",
        "negocio", "negocios",
        "startup",
    )
    # Umbral de similitud para fuzzy: 0.78 captura 1-2 chars intercambiados/faltantes
    _FUZZY_THRESHOLD = 0.78
    # Longitud mínima de token para evitar falsos positivos con palabras cortas
    _MIN_TOKEN_LEN = 4

    @staticmethod
    def _normalize(text: str) -> str:
        """Minúsculas y sin tildes/diacríticos para comparar sin importar acentuación."""
        nfkd = unicodedata.normalize("NFKD", text.lower())
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    @staticmethod
    def _fuzzy_token_matches(tokens: list, canonical: tuple) -> bool:
        """
        Devuelve True si algún token del mensaje tiene similitud ≥ FUZZY_THRESHOLD
        con cualquiera de los términos canónicos (después de normalizar ambos).
        """
        norm_canonical = [
            ProjectAnalysisDetector._normalize(c) for c in canonical
        ]
        for tok in tokens:
            if len(tok) < ProjectAnalysisDetector._MIN_TOKEN_LEN:
                continue
            for canon in norm_canonical:
                ratio = SequenceMatcher(None, tok, canon).ratio()
                if ratio >= ProjectAnalysisDetector._FUZZY_THRESHOLD:
                    return True
        return False

    @staticmethod
    def is_project_analysis(message: str) -> bool:
        """
        Verifica si el mensaje indica análisis de proyecto.

        Estrategias (en orden de costo):
        1. Match exacto de frases en PROJECT_ANALYSIS_TRIGGERS (rápido, determinista).
        2. Combinación de raíz verbal + palabra de proyecto (captura conjugaciones
           y artículos variados: "analiza mi proyecto", "evalúa el proyecto", …).
        3. Fuzzy token matching: detecta errores tipográficos como "royecto",
           "poryecto", "anaizar", etc. comparando cada token del mensaje contra
           formas canónicas usando similitud de cadenas (≥78 %).
        """
        message_lower = message.lower()

        # 1. Exact phrase match
        if any(trigger in message_lower for trigger in PROJECT_ANALYSIS_TRIGGERS):
            return True

        # 2. Verb stem + project word (substring)
        has_verb = any(stem in message_lower for stem in ProjectAnalysisDetector._VERB_STEMS)
        has_project = any(word in message_lower for word in ProjectAnalysisDetector._PROJECT_WORDS)
        if has_verb and has_project:
            return True

        # 3. Fuzzy token matching (handles typos)
        norm_msg = ProjectAnalysisDetector._normalize(message)
        tokens = re.findall(r"\w+", norm_msg)
        fuzzy_verb = ProjectAnalysisDetector._fuzzy_token_matches(tokens, ProjectAnalysisDetector._VERB_CANONICAL)
        fuzzy_project = ProjectAnalysisDetector._fuzzy_token_matches(tokens, ProjectAnalysisDetector._PROJECT_CANONICAL)
        return fuzzy_verb and fuzzy_project
