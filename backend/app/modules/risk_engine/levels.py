"""
Risk Engine - Levels
Estructuras para evaluación de riesgo
"""

from enum import Enum
from typing import List, Dict
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Nivel de riesgo según spec"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskCategory(str, Enum):
    """Categorías de riesgo según spec"""
    TOPIC = "topic"             # Riesgo por tema legal
    STRUCTURE = "structure"     # Riesgo por estructura organizacional
    FUNDING = "funding"         # Riesgo por financiamiento
    JURISDICTION = "jurisdiction"  # Riesgo jurisdiccional
    DATA_SENSITIVITY = "data_sensitivity"  # Riesgo por datos sensibles


class RiskFactor(BaseModel):
    """Un factor de riesgo evaluado"""
    category: RiskCategory
    level: RiskLevel
    weight: float = Field(ge=0.0, le=1.0, default=0.2)
    description: str
    indicators: List[str] = []
    mitigations: List[str] = []


class RiskAssessment(BaseModel):
    """Resultado de la evaluación de riesgo"""
    overall_level: RiskLevel
    overall_score: float = Field(ge=0.0, le=1.0)

    factors: List[RiskFactor] = []

    # Desglose por categoría
    topic_risk: RiskLevel = RiskLevel.MEDIUM
    structure_risk: RiskLevel = RiskLevel.MEDIUM
    funding_risk: RiskLevel = RiskLevel.LOW
    jurisdiction_risk: RiskLevel = RiskLevel.LOW
    data_risk: RiskLevel = RiskLevel.LOW

    # Recomendaciones
    high_risk_factors: List[str] = []
    mitigation_recommendations: List[str] = []

    # Flags
    requires_specialist: bool = False
    requires_urgent_attention: bool = False

    def get_factors_by_level(self, level: RiskLevel) -> List[RiskFactor]:
        return [f for f in self.factors if f.level == level]
