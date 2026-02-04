"""
Validation Module - Rules
Reglas de validación cross-field y legal triggers
"""

from typing import Callable, List, Dict, Any
from app.modules.intake.schemas import NormalizedIntake
from .flags import ValidationResult


# Tipo para funciones de regla
RuleFunction = Callable[[NormalizedIntake, ValidationResult], None]


def rule_org_type_consistency(intake: NormalizedIntake, result: ValidationResult):
    """
    Verifica consistencia entre tipo de organización y personería jurídica.
    """
    result.checked_rules += 1

    if intake.organization_type == "ONG registrada" and intake.has_legal_entity is False:
        result.add_issue(
            code="ORG_INCONSISTENCY",
            message="Una ONG registrada debe tener personería jurídica",
            severity="error",
            field="has_legal_entity",
            suggestion="Verifica si tu organización está realmente registrada como ONG",
        )
        result.inconsistencies.append("org_type vs has_legal_entity")
    else:
        result.passed_rules += 1


def rule_apci_requirements(intake: NormalizedIntake, result: ValidationResult):
    """
    Si menciona cooperación internacional, verifica requisitos APCI.
    """
    result.checked_rules += 1

    legal_area = intake.legal_area
    if isinstance(legal_area, str):
        areas = [legal_area]
    elif isinstance(legal_area, list):
        areas = legal_area
    else:
        areas = []

    if "Cooperación internacional (APCI)" in areas:
        result.legal_triggers.append("APCI_REQUIREMENTS")

        if intake.has_legal_entity is False:
            result.add_issue(
                code="APCI_NO_ENTITY",
                message="Para recibir cooperación internacional se requiere personería jurídica",
                severity="warning",
                field="has_legal_entity",
                suggestion="Considera formalizar tu organización antes de buscar fondos internacionales",
            )
        else:
            result.passed_rules += 1
    else:
        result.passed_rules += 1


def rule_funding_source_consistency(intake: NormalizedIntake, result: ValidationResult):
    """
    Verifica consistencia entre fuente de financiamiento y estructura.
    """
    result.checked_rules += 1

    if intake.funding_source == "Donaciones internacionales":
        if intake.has_legal_entity is False:
            result.add_issue(
                code="FUNDING_NO_ENTITY",
                message="Recibir donaciones internacionales sin personería jurídica es riesgoso",
                severity="warning",
                field="funding_source",
                suggestion="Las donaciones internacionales requieren registro en APCI",
            )
            result.risk_signals.append("international_funding_no_entity")
        else:
            result.passed_rules += 1
    else:
        result.passed_rules += 1


def rule_urgency_vs_complexity(intake: NormalizedIntake, result: ValidationResult):
    """
    Advierte si urgencia alta con tema complejo.
    """
    result.checked_rules += 1

    complex_areas = ["Tributario (SUNAT)", "Cooperación internacional (APCI)"]
    legal_area = intake.legal_area

    if isinstance(legal_area, str):
        areas = [legal_area]
    elif isinstance(legal_area, list):
        areas = legal_area
    else:
        areas = []

    is_complex = any(area in complex_areas for area in areas)
    is_urgent = intake.urgency_level in ["Inmediato (días)", "Lo antes posible"]

    if is_complex and is_urgent:
        result.add_issue(
            code="URGENCY_COMPLEXITY_MISMATCH",
            message="Temas tributarios o APCI requieren tiempo para resolver correctamente",
            severity="warning",
            suggestion="Considera consultar con un especialista dada la urgencia y complejidad",
        )
        result.risk_signals.append("urgent_complex_topic")
    else:
        result.passed_rules += 1


def rule_colectivo_limitations(intake: NormalizedIntake, result: ValidationResult):
    """
    Advierte sobre limitaciones de colectivos sin personería.
    """
    result.checked_rules += 1

    informal_types = ["Colectivo sin personería", "Colectivo estudiantil"]

    if intake.organization_type in informal_types:
        result.add_issue(
            code="INFORMAL_ORG_LIMITATIONS",
            message="Los colectivos sin personería tienen limitaciones legales importantes",
            severity="info",
            suggestion="Considera las opciones de formalización según tus necesidades",
        )
        result.risk_signals.append("informal_organization")
        # No falla, solo informa
        result.passed_rules += 1
    else:
        result.passed_rules += 1


# Lista de todas las reglas disponibles
ALL_RULES: List[RuleFunction] = [
    rule_org_type_consistency,
    rule_apci_requirements,
    rule_funding_source_consistency,
    rule_urgency_vs_complexity,
    rule_colectivo_limitations,
]


def get_rules_for_tool(tool_id: int) -> List[RuleFunction]:
    """Retorna las reglas aplicables según la herramienta"""
    # Por ahora todas las reglas aplican a todas las herramientas
    # Se puede personalizar según necesidad
    return ALL_RULES
