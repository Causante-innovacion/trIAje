"""
Reasoning Module - Guards
Verifica condiciones antes de ejecutar razonamiento.
"""

from app.modules.rag.interfaces import RAGResult


class ReasoningGuard:
    """
    Guards que verifican si se puede ejecutar el razonamiento.

    Regla según spec:
    No puede operar si: rag_evidence == insufficient AND risk >= medium
    """

    def __init__(self, confidence_threshold: float = 0.65):
        self.confidence_threshold = confidence_threshold

    def can_reason(
        self,
        rag_result: RAGResult,
        risk_level: str,
    ) -> tuple[bool, str | None]:
        """
        Verifica si se puede ejecutar el razonamiento.

        Args:
            rag_result: Resultado del RAG
            risk_level: Nivel de riesgo (LOW, MEDIUM, HIGH)

        Returns:
            Tuple (can_proceed, reason_if_blocked)
        """
        evidence_sufficient = rag_result.confidence >= self.confidence_threshold
        risk_is_elevated = risk_level in ["MEDIUM", "HIGH"]

        # Regla: no operar si evidencia insuficiente Y riesgo >= medium
        if not evidence_sufficient and risk_is_elevated:
            return (
                False,
                f"Evidencia insuficiente (confidence: {rag_result.confidence:.2f}) "
                f"con riesgo {risk_level}. Se requiere escalamiento humano."
            )

        # Regla adicional: si hay contradicciones, advertir
        if rag_result.has_contradictions:
            return (
                True,  # Puede continuar pero con advertencia
                "Se detectaron contradicciones en la evidencia. "
                "El resultado debe validarse con un asesor."
            )

        return (True, None)

    def should_add_disclaimer(
        self,
        rag_result: RAGResult,
        risk_level: str,
    ) -> bool:
        """
        Determina si se debe agregar disclaimer adicional.
        """
        # Siempre disclaimer si:
        # - Confidence bajo
        # - Riesgo alto
        # - Contradicciones

        if rag_result.confidence < 0.8:
            return True
        if risk_level == "HIGH":
            return True
        if rag_result.has_contradictions:
            return True

        return False

    def get_reasoning_mode(
        self,
        rag_result: RAGResult,
        risk_level: str,
    ) -> str:
        """
        Determina el modo de razonamiento según evidencia y riesgo.

        Returns:
            "full": Razonamiento completo con afirmaciones
            "conditional": Solo statements condicionales
            "orientation": Solo orientación general
        """
        confidence = rag_result.confidence

        if confidence >= 0.8 and risk_level == "LOW":
            return "full"
        elif confidence >= self.confidence_threshold:
            return "conditional"
        else:
            return "orientation"
