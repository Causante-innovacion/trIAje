"""
Output Builder - Language Enforcer
Aplica lenguaje condicional obligatorio según spec
"""

from typing import List, Tuple
import re


class ConditionalLanguageEnforcer:
    """
    Enforce lenguaje condicional en outputs.

    Según spec:
    - Lenguaje condicional (si/entonces) obligatorio
    - Aclaración de supuestos
    - Nunca absolutos sin evidencia suficiente
    """

    # Frases absolutas a evitar
    ABSOLUTE_PHRASES = [
        (r"\bdebes\b", "podrías necesitar"),
        (r"\btienes que\b", "generalmente se requiere"),
        (r"\bes obligatorio\b", "suele ser requerido"),
        (r"\bestá prohibido\b", "podría estar restringido"),
        (r"\bsiempre\b", "generalmente"),
        (r"\bnunca\b", "normalmente no"),
        (r"\bla ley exige\b", "la normativa generalmente indica"),
        (r"\bsin excepción\b", "en la mayoría de casos"),
    ]

    # Templates de lenguaje condicional
    CONDITIONAL_TEMPLATES = {
        "requirement": "Si {condition}, entonces {requirement}",
        "recommendation": "En caso de {situation}, se recomienda {action}",
        "warning": "Considerando {context}, es importante tener en cuenta que {warning}",
        "alternative": "Como alternativa, {alternative} podría ser viable si {condition}",
    }

    # Prefijos de incertidumbre
    UNCERTAINTY_PREFIXES = [
        "Según la información disponible, ",
        "De acuerdo con la normativa consultada, ",
        "En general, ",
        "Típicamente, ",
        "Basándose en los datos proporcionados, ",
    ]

    def __init__(self, confidence_threshold: float = 0.8):
        self.confidence_threshold = confidence_threshold

    def enforce(
        self,
        text: str,
        confidence: float,
        add_uncertainty_prefix: bool = True
    ) -> str:
        """
        Aplica enforcement de lenguaje condicional.

        Args:
            text: Texto original
            confidence: Nivel de confianza (0-1)
            add_uncertainty_prefix: Si agregar prefijo de incertidumbre

        Returns:
            Texto con lenguaje condicional
        """
        result = text

        # Reemplazar frases absolutas si confidence bajo
        if confidence < self.confidence_threshold:
            result = self._replace_absolutes(result)

        # Agregar prefijo de incertidumbre si aplica
        if add_uncertainty_prefix and confidence < self.confidence_threshold:
            result = self._add_uncertainty_prefix(result, confidence)

        return result

    def _replace_absolutes(self, text: str) -> str:
        """Reemplaza frases absolutas con versiones condicionales"""
        result = text

        for pattern, replacement in self.ABSOLUTE_PHRASES:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    def _add_uncertainty_prefix(self, text: str, confidence: float) -> str:
        """Agrega prefijo de incertidumbre apropiado"""
        if confidence >= 0.7:
            prefix = self.UNCERTAINTY_PREFIXES[0]
        elif confidence >= 0.5:
            prefix = self.UNCERTAINTY_PREFIXES[2]
        else:
            prefix = self.UNCERTAINTY_PREFIXES[4]

        # Solo agregar si no empieza con un prefijo similar
        if not any(text.startswith(p) for p in self.UNCERTAINTY_PREFIXES):
            return prefix + text[0].lower() + text[1:]

        return text

    def build_conditional_statement(
        self,
        template_type: str,
        **kwargs
    ) -> str:
        """
        Construye statement condicional usando template.

        Args:
            template_type: "requirement", "recommendation", "warning", "alternative"
            **kwargs: Variables para el template

        Returns:
            Statement formateado
        """
        template = self.CONDITIONAL_TEMPLATES.get(template_type)
        if not template:
            return str(kwargs)

        try:
            return template.format(**kwargs)
        except KeyError:
            return str(kwargs)

    def check_compliance(self, text: str) -> Tuple[bool, List[str]]:
        """
        Verifica si un texto cumple con los estándares de lenguaje.

        Returns:
            Tuple (is_compliant, list_of_violations)
        """
        violations = []

        for pattern, _ in self.ABSOLUTE_PHRASES:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                violations.append(f"Frase absoluta encontrada: {matches[0]}")

        return (len(violations) == 0, violations)

    def add_assumptions_section(
        self,
        assumptions: List[str]
    ) -> str:
        """Genera sección de supuestos formateada"""
        if not assumptions:
            return ""

        lines = ["**Supuestos de este análisis:**"]
        for i, assumption in enumerate(assumptions, 1):
            lines.append(f"{i}. {assumption}")

        return "\n".join(lines)

    def add_limitations_section(
        self,
        limitations: List[str]
    ) -> str:
        """Genera sección de limitaciones formateada"""
        if not limitations:
            return ""

        lines = ["**Limitaciones:**"]
        for limitation in limitations:
            lines.append(f"- {limitation}")

        return "\n".join(lines)
