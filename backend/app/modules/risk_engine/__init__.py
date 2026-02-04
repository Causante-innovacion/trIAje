# Risk Engine Module
"""
Calcula riesgo final.

Inputs:
- topic_risk
- structure_risk
- funding_risk
- jurisdiction_risk
- data_sensitivity

Output: LOW | MEDIUM | HIGH
"""

from .service import RiskEngine
from .levels import RiskLevel, RiskFactor, RiskAssessment

__all__ = [
    "RiskEngine",
    "RiskLevel",
    "RiskFactor",
    "RiskAssessment",
]
