"""
Risk Engine - Factors
Definición de factores de riesgo y sus evaluadores
"""

from typing import Dict, List, Any
from .levels import RiskLevel, RiskCategory


# Mapeo de temas a niveles de riesgo
TOPIC_RISK_MAP: Dict[str, RiskLevel] = {
    # Alto riesgo
    "Tributario (SUNAT)": RiskLevel.HIGH,
    "Cooperación internacional (APCI)": RiskLevel.HIGH,
    "Laboral": RiskLevel.HIGH,
    # Medio riesgo
    "Propiedad intelectual": RiskLevel.MEDIUM,
    "Protección de datos": RiskLevel.MEDIUM,
    "Contratos": RiskLevel.MEDIUM,
    # Bajo riesgo
    "Formalización": RiskLevel.LOW,
    "Otro": RiskLevel.MEDIUM,
}

# Mapeo de tipos de organización a riesgo estructural
STRUCTURE_RISK_MAP: Dict[str, RiskLevel] = {
    # Alto riesgo
    "Colectivo sin personería": RiskLevel.HIGH,
    "Colectivo estudiantil": RiskLevel.HIGH,
    # Medio riesgo
    "Otro": RiskLevel.MEDIUM,
    "Persona natural": RiskLevel.MEDIUM,
    # Bajo riesgo
    "Asociación civil": RiskLevel.LOW,
    "ONG registrada": RiskLevel.LOW,
    "Fundación": RiskLevel.LOW,
}

# Mapeo de fuentes de financiamiento a riesgo
FUNDING_RISK_MAP: Dict[str, RiskLevel] = {
    # Alto riesgo
    "Donaciones internacionales": RiskLevel.HIGH,
    "Grants/Subvenciones": RiskLevel.HIGH,
    # Medio riesgo
    "Mixto": RiskLevel.MEDIUM,
    "Venta de servicios": RiskLevel.MEDIUM,
    # Bajo riesgo
    "Donaciones nacionales": RiskLevel.LOW,
    "Autofinanciamiento": RiskLevel.LOW,
    "Sin financiamiento aún": RiskLevel.LOW,
}


def evaluate_topic_risk(legal_area: str | List[str] | None) -> RiskLevel:
    """Evalúa riesgo por tema legal"""
    if not legal_area:
        return RiskLevel.MEDIUM

    areas = [legal_area] if isinstance(legal_area, str) else legal_area

    # Tomar el mayor riesgo de todas las áreas
    max_risk = RiskLevel.LOW
    for area in areas:
        risk = TOPIC_RISK_MAP.get(area, RiskLevel.MEDIUM)
        if risk == RiskLevel.HIGH:
            return RiskLevel.HIGH
        elif risk == RiskLevel.MEDIUM:
            max_risk = RiskLevel.MEDIUM

    return max_risk


def evaluate_structure_risk(
    org_type: str | None,
    has_legal_entity: bool | None
) -> RiskLevel:
    """Evalúa riesgo por estructura organizacional"""
    if has_legal_entity is False:
        return RiskLevel.HIGH

    if org_type:
        return STRUCTURE_RISK_MAP.get(org_type, RiskLevel.MEDIUM)

    return RiskLevel.MEDIUM


def evaluate_funding_risk(funding_source: str | None) -> RiskLevel:
    """Evalúa riesgo por fuente de financiamiento"""
    if not funding_source:
        return RiskLevel.LOW

    return FUNDING_RISK_MAP.get(funding_source, RiskLevel.MEDIUM)


def evaluate_jurisdiction_risk(jurisdiction: str) -> RiskLevel:
    """Evalúa riesgo jurisdiccional"""
    # Por ahora solo soportamos Perú
    if jurisdiction == "PE":
        return RiskLevel.LOW

    return RiskLevel.HIGH  # Otras jurisdicciones no soportadas


def evaluate_data_sensitivity_risk(
    has_personal_data: bool = False,
    has_sensitive_data: bool = False,
) -> RiskLevel:
    """Evalúa riesgo por sensibilidad de datos"""
    if has_sensitive_data:
        return RiskLevel.HIGH
    elif has_personal_data:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def get_risk_indicators(category: RiskCategory, level: RiskLevel) -> List[str]:
    """Obtiene indicadores de riesgo por categoría y nivel"""
    indicators = {
        (RiskCategory.TOPIC, RiskLevel.HIGH): [
            "Implica obligaciones tributarias con SUNAT",
            "Requiere registro en APCI",
            "Involucra relaciones laborales",
        ],
        (RiskCategory.STRUCTURE, RiskLevel.HIGH): [
            "Organización sin personería jurídica",
            "Limitaciones para firmar contratos",
            "Responsabilidad personal de miembros",
        ],
        (RiskCategory.FUNDING, RiskLevel.HIGH): [
            "Fondos de cooperación internacional",
            "Obligaciones de reporte a APCI",
            "Requisitos de transparencia",
        ],
    }
    return indicators.get((category, level), [])


def get_risk_mitigations(category: RiskCategory, level: RiskLevel) -> List[str]:
    """Obtiene recomendaciones de mitigación"""
    mitigations = {
        (RiskCategory.TOPIC, RiskLevel.HIGH): [
            "Consultar con especialista tributario",
            "Mantener documentación al día",
            "Revisar obligaciones periódicamente",
        ],
        (RiskCategory.STRUCTURE, RiskLevel.HIGH): [
            "Considerar formalización",
            "Operar bajo paraguas de organización formal",
            "Documentar acuerdos internos",
        ],
        (RiskCategory.FUNDING, RiskLevel.HIGH): [
            "Registrarse en APCI antes de recibir fondos",
            "Implementar sistema de control interno",
            "Mantener contabilidad separada",
        ],
    }
    return mitigations.get((category, level), ["Consultar con especialista"])
