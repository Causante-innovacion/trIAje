"""
Validation Module - Service
Valida consistencia de ficha legal mínima
"""

from typing import List
from app.modules.intake.schemas import NormalizedIntake
from .flags import ValidationFlag, ValidationResult
from .rules import get_rules_for_tool, RuleFunction


class ValidationModule:
    """
    Módulo de validación: verifica consistencia de datos del intake.
    """

    def __init__(self, custom_rules: List[RuleFunction] | None = None):
        self.custom_rules = custom_rules or []

    async def check(self, intake: NormalizedIntake) -> ValidationResult:
        """
        Ejecuta todas las validaciones sobre los datos del intake.

        Returns:
            ValidationResult con flag: pass, warning, o block
        """
        result = ValidationResult(
            flag=ValidationFlag.PASS,
            is_valid=True,
        )

        # 1. Verificar campos requeridos mínimos
        self._check_required_fields(intake, result)

        # 2. Ejecutar reglas de validación
        rules = get_rules_for_tool(intake.tool_id)
        rules.extend(self.custom_rules)

        for rule in rules:
            rule(intake, result)

        # 3. Detectar señales de riesgo adicionales
        self._detect_risk_signals(intake, result)

        return result

    def _check_required_fields(
        self,
        intake: NormalizedIntake,
        result: ValidationResult
    ):
        """Verifica campos mínimos requeridos"""
        required = ["organization_type", "legal_area"]

        for field in required:
            value = getattr(intake, field, None)
            if value is None or value == "":
                result.missing_fields.append(field)
                result.add_issue(
                    code="MISSING_REQUIRED",
                    message=f"Campo requerido faltante: {field}",
                    severity="error",
                    field=field,
                )

    def _detect_risk_signals(
        self,
        intake: NormalizedIntake,
        result: ValidationResult
    ):
        """Detecta señales de riesgo que requieren atención especial"""

        # Riesgo alto por tema
        if intake.topic_risk == "HIGH":
            result.risk_signals.append("high_topic_risk")
            if "HIGH" not in [s for s in result.risk_signals]:
                result.add_issue(
                    code="HIGH_TOPIC_RISK",
                    message="El tema consultado tiene implicaciones legales significativas",
                    severity="info",
                    suggestion="Se recomienda validar con un especialista",
                )

        # Riesgo alto por estructura
        if intake.structure_risk == "HIGH":
            result.risk_signals.append("high_structure_risk")
            result.add_issue(
                code="HIGH_STRUCTURE_RISK",
                message="Tu estructura organizacional puede limitar algunas opciones",
                severity="info",
                suggestion="Considera las opciones de formalización disponibles",
            )

    def add_custom_rule(self, rule: RuleFunction):
        """Agrega una regla de validación personalizada"""
        self.custom_rules.append(rule)

    async def validate_for_rag(self, intake: NormalizedIntake) -> bool:
        """
        Validación rápida para determinar si se puede proceder al RAG.
        Retorna False si hay bloqueos críticos.
        """
        result = await self.check(intake)
        return result.flag != ValidationFlag.BLOCK
