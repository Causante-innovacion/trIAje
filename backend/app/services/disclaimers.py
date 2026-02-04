"""
Disclaimer Service
Manejo de disclaimers legales
"""

from typing import List
from pydantic import BaseModel


class Disclaimer(BaseModel):
    text: str
    type: str  # "legal", "limitation", "recommendation"
    prominent: bool = False


class DisclaimerService:
    """Servicio para manejo de disclaimers"""

    # Disclaimers estándar
    STANDARD_DISCLAIMERS = [
        Disclaimer(
            text="Este análisis no constituye asesoría legal profesional. "
                 "Para decisiones importantes, consulte con un abogado.",
            type="legal",
            prominent=True,
        ),
        Disclaimer(
            text="La información proporcionada está basada en normativa vigente "
                 "al momento del análisis. Las leyes pueden cambiar.",
            type="limitation",
        ),
        Disclaimer(
            text="Los resultados dependen de la precisión de la información proporcionada.",
            type="limitation",
        ),
    ]

    HIGH_RISK_DISCLAIMERS = [
        Disclaimer(
            text="Se han identificado factores de alto riesgo. "
                 "Se recomienda fuertemente consultar con un especialista.",
            type="recommendation",
            prominent=True,
        ),
    ]

    LOW_CONFIDENCE_DISCLAIMERS = [
        Disclaimer(
            text="La evidencia disponible es limitada. "
                 "Esta respuesta es orientativa y debe validarse.",
            type="limitation",
            prominent=True,
        ),
    ]

    @classmethod
    def get_standard_disclaimers(cls) -> List[Disclaimer]:
        """Retorna disclaimers estándar"""
        return cls.STANDARD_DISCLAIMERS.copy()

    @classmethod
    def get_disclaimers_for_context(
        cls,
        risk_level: str = "MEDIUM",
        confidence: float = 0.7,
        has_contradictions: bool = False,
    ) -> List[Disclaimer]:
        """Retorna disclaimers según contexto"""
        disclaimers = cls.STANDARD_DISCLAIMERS.copy()

        if risk_level == "HIGH":
            disclaimers.extend(cls.HIGH_RISK_DISCLAIMERS)

        if confidence < 0.65:
            disclaimers.extend(cls.LOW_CONFIDENCE_DISCLAIMERS)

        if has_contradictions:
            disclaimers.append(Disclaimer(
                text="Se detectaron fuentes con información potencialmente contradictoria. "
                     "Validar con asesor especializado.",
                type="limitation",
                prominent=True,
            ))

        return disclaimers

    @classmethod
    def format_for_display(cls, disclaimers: List[Disclaimer]) -> str:
        """Formatea disclaimers para mostrar"""
        prominent = [d for d in disclaimers if d.prominent]
        others = [d for d in disclaimers if not d.prominent]

        lines = []

        if prominent:
            lines.append("⚠️ **IMPORTANTE:**")
            for d in prominent:
                lines.append(f"- {d.text}")
            lines.append("")

        if others:
            lines.append("**Notas:**")
            for d in others:
                lines.append(f"- {d.text}")

        return "\n".join(lines)
