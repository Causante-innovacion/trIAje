# Core module - Infrastructure
from .config import settings
from .exceptions import (
    GPTLegalException,
    ValidationError,
    RAGError,
    InsufficientEvidenceError,
    ContradictionDetectedError,
)

__all__ = [
    "settings",
    "GPTLegalException",
    "ValidationError",
    "RAGError",
    "InsufficientEvidenceError",
    "ContradictionDetectedError",
]
