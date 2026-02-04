"""
Risk Engine - Service
Calcula nivel de riesgo
"""

from typing import Dict, Any
from app.modules.intake.schemas import NormalizedIntake
from .levels import RiskLevel, RiskCategory, RiskFactor, RiskAssessment
from .factors import (
    evaluate_topic_risk,
    evaluate_structure_risk,
    evaluate_funding_risk,
    evaluate_jurisdiction_risk,
    evaluate_data_sensitivity_risk,
    get_risk_indicators,
    get_risk_mitigations,
)


class RiskEngine:
    """
    Motor de cálculo de riesgo.
    """

    # Pesos por categoría
    WEIGHTS: Dict[RiskCategory, float] = {
        RiskCategory.TOPIC: 0.30,
        RiskCategory.STRUCTURE: 0.25,
        RiskCategory.FUNDING: 0.25,
        RiskCategory.JURISDICTION: 0.10,
        RiskCategory.DATA_SENSITIVITY: 0.10,
    }

    # Valores numéricos por nivel
    LEVEL_VALUES: Dict[RiskLevel, float] = {
        RiskLevel.LOW: 0.2,
        RiskLevel.MEDIUM: 0.5,
        RiskLevel.HIGH: 0.9,
    }

    def __init__(self, custom_weights: Dict[RiskCategory, float] | None = None):
        if custom_weights:
            self.weights = custom_weights
        else:
            self.weights = self.WEIGHTS.copy()

    async def calculate(
        self,
        intake: NormalizedIntake | None = None,
        topic_risk: str | None = None,
        structure_risk: str | None = None,
        funding_risk: str | None = None,
        gap_severity: str | None = None,
    ) -> RiskAssessment:
        """
        Calcula el riesgo total.

        Args:
            intake: Datos del intake (opcional si se pasan los otros parámetros)
            topic_risk: Override de riesgo por tema
            structure_risk: Override de riesgo por estructura
            funding_risk: Override de riesgo por financiamiento
            gap_severity: Severidad de brechas (afecta el cálculo)

        Returns:
            RiskAssessment con nivel de riesgo y detalles
        """
        factors = []

        # 1. Evaluar riesgo por tema
        if topic_risk:
            topic_level = RiskLevel(topic_risk)
        elif intake:
            topic_level = evaluate_topic_risk(intake.legal_area)
        else:
            topic_level = RiskLevel.MEDIUM

        factors.append(RiskFactor(
            category=RiskCategory.TOPIC,
            level=topic_level,
            weight=self.weights[RiskCategory.TOPIC],
            description="Riesgo por área legal consultada",
            indicators=get_risk_indicators(RiskCategory.TOPIC, topic_level),
            mitigations=get_risk_mitigations(RiskCategory.TOPIC, topic_level),
        ))

        # 2. Evaluar riesgo por estructura
        if structure_risk:
            struct_level = RiskLevel(structure_risk)
        elif intake:
            struct_level = evaluate_structure_risk(
                intake.organization_type,
                intake.has_legal_entity,
            )
        else:
            struct_level = RiskLevel.MEDIUM

        factors.append(RiskFactor(
            category=RiskCategory.STRUCTURE,
            level=struct_level,
            weight=self.weights[RiskCategory.STRUCTURE],
            description="Riesgo por estructura organizacional",
            indicators=get_risk_indicators(RiskCategory.STRUCTURE, struct_level),
            mitigations=get_risk_mitigations(RiskCategory.STRUCTURE, struct_level),
        ))

        # 3. Evaluar riesgo por financiamiento
        if funding_risk:
            fund_level = RiskLevel(funding_risk)
        elif intake:
            fund_level = evaluate_funding_risk(intake.funding_source)
        else:
            fund_level = RiskLevel.LOW

        factors.append(RiskFactor(
            category=RiskCategory.FUNDING,
            level=fund_level,
            weight=self.weights[RiskCategory.FUNDING],
            description="Riesgo por fuente de financiamiento",
            indicators=get_risk_indicators(RiskCategory.FUNDING, fund_level),
            mitigations=get_risk_mitigations(RiskCategory.FUNDING, fund_level),
        ))

        # 4. Evaluar riesgo jurisdiccional
        jurisdiction = intake.jurisdiction if intake else "PE"
        juris_level = evaluate_jurisdiction_risk(jurisdiction)

        factors.append(RiskFactor(
            category=RiskCategory.JURISDICTION,
            level=juris_level,
            weight=self.weights[RiskCategory.JURISDICTION],
            description="Riesgo por jurisdicción",
        ))

        # 5. Evaluar riesgo por datos
        data_level = evaluate_data_sensitivity_risk()

        factors.append(RiskFactor(
            category=RiskCategory.DATA_SENSITIVITY,
            level=data_level,
            weight=self.weights[RiskCategory.DATA_SENSITIVITY],
            description="Riesgo por sensibilidad de datos",
        ))

        # Calcular score total
        overall_score = self._calculate_weighted_score(factors)

        # Ajustar por severidad de brechas
        if gap_severity == "HIGH":
            overall_score = min(1.0, overall_score + 0.1)

        # Determinar nivel final
        overall_level = self._score_to_level(overall_score)

        # Identificar factores de alto riesgo
        high_risk_factors = [
            f.description for f in factors if f.level == RiskLevel.HIGH
        ]

        # Recopilar mitigaciones
        all_mitigations = []
        for f in factors:
            if f.level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
                all_mitigations.extend(f.mitigations)

        return RiskAssessment(
            overall_level=overall_level,
            overall_score=overall_score,
            factors=factors,
            topic_risk=topic_level,
            structure_risk=struct_level,
            funding_risk=fund_level,
            jurisdiction_risk=juris_level,
            data_risk=data_level,
            high_risk_factors=high_risk_factors,
            mitigation_recommendations=list(dict.fromkeys(all_mitigations))[:5],
            requires_specialist=overall_level == RiskLevel.HIGH,
            requires_urgent_attention=len(high_risk_factors) >= 2,
        )

    def _calculate_weighted_score(self, factors: list[RiskFactor]) -> float:
        """Calcula score ponderado"""
        total = 0.0
        for factor in factors:
            value = self.LEVEL_VALUES[factor.level]
            total += value * factor.weight
        return total

    def _score_to_level(self, score: float) -> RiskLevel:
        """Convierte score numérico a nivel"""
        if score >= 0.7:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def get_rules(self) -> Dict[str, Any]:
        """Retorna las reglas de riesgo para uso en reasoning"""
        return {
            "weights": self.weights,
            "level_values": self.LEVEL_VALUES,
            "high_risk_topics": ["Tributario (SUNAT)", "Cooperación internacional (APCI)", "Laboral"],
            "high_risk_structures": ["Colectivo sin personería", "Colectivo estudiantil"],
        }
