"""
Custom exceptions for GPT Legal
"""

from typing import Any, Dict, List


class GPTLegalException(Exception):
    """Base exception for GPT Legal"""

    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(GPTLegalException):
    """Raised when validation fails"""

    def __init__(
        self,
        message: str,
        flag: str = "block",  # pass, warning, block
        missing_fields: List[str] | None = None,
        inconsistencies: List[str] | None = None,
    ):
        self.flag = flag
        self.missing_fields = missing_fields or []
        self.inconsistencies = inconsistencies or []
        super().__init__(
            message,
            {
                "flag": flag,
                "missing_fields": self.missing_fields,
                "inconsistencies": self.inconsistencies,
            }
        )


class RAGError(GPTLegalException):
    """Base exception for RAG-related errors"""
    pass


class InsufficientEvidenceError(RAGError):
    """
    Raised when RAG confidence is below threshold.
    Response should be orientation_only with advisor recommendation.
    """

    def __init__(
        self,
        message: str = "No tengo información suficiente para afirmar eso con seguridad",
        confidence_score: float = 0.0,
        threshold: float = 0.65,
        suggestion: str | None = None,
    ):
        self.confidence_score = confidence_score
        self.threshold = threshold
        self.suggestion = suggestion or "Se recomienda consultar con un asesor legal especializado"
        super().__init__(
            message,
            {
                "confidence_score": confidence_score,
                "threshold": threshold,
                "suggestion": self.suggestion,
                "requires_human_escalation": True,
            }
        )


class ContradictionDetectedError(RAGError):
    """
    Raised when contradicting evidence is found in RAG results.
    Triggers auto-escalation and advisor package generation.
    """

    def __init__(
        self,
        message: str = "Se detectaron fuentes con información contradictoria",
        conflicting_chunks: List[Dict[str, Any]] | None = None,
    ):
        self.conflicting_chunks = conflicting_chunks or []
        super().__init__(
            message,
            {
                "conflicting_chunks": self.conflicting_chunks,
                "auto_escalation": True,
                "advisor_package_trigger": True,
            }
        )


class PipelineError(GPTLegalException):
    """Raised when a pipeline module fails"""

    def __init__(
        self,
        message: str,
        module_name: str,
        step: int | None = None,
    ):
        self.module_name = module_name
        self.step = step
        super().__init__(
            message,
            {
                "module": module_name,
                "step": step,
            }
        )


class AIProviderError(GPTLegalException):
    """Raised when AI provider fails"""

    def __init__(
        self,
        message: str,
        provider: str,
        model: str | None = None,
    ):
        self.provider = provider
        self.model = model
        super().__init__(
            message,
            {
                "provider": provider,
                "model": model,
            }
        )
