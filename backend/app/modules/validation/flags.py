"""
Validation Module - Flags
Enums y estructuras para resultados de validación
"""

from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel


class ValidationFlag(str, Enum):
    """Flags de resultado de validación"""
    PASS = "pass"           # Todo ok, continuar pipeline
    WARNING = "warning"     # Continuar pero con advertencias
    BLOCK = "block"         # No continuar, requiere corrección


class ValidationIssue(BaseModel):
    """Representa un problema detectado en validación"""
    field: str | None = None
    code: str
    message: str
    severity: str  # "error", "warning", "info"
    suggestion: str | None = None


class ValidationResult(BaseModel):
    """Resultado completo de validación"""
    flag: ValidationFlag
    is_valid: bool
    issues: List[ValidationIssue] = []
    warnings: List[str] = []

    # Detalles específicos
    missing_fields: List[str] = []
    inconsistencies: List[str] = []
    legal_triggers: List[str] = []
    risk_signals: List[str] = []

    # Metadata
    checked_rules: int = 0
    passed_rules: int = 0

    def add_issue(
        self,
        code: str,
        message: str,
        severity: str = "error",
        field: str | None = None,
        suggestion: str | None = None
    ):
        """Agrega un issue a la lista"""
        self.issues.append(ValidationIssue(
            field=field,
            code=code,
            message=message,
            severity=severity,
            suggestion=suggestion,
        ))

        if severity == "error":
            self.is_valid = False
            self.flag = ValidationFlag.BLOCK
        elif severity == "warning" and self.flag == ValidationFlag.PASS:
            self.flag = ValidationFlag.WARNING
