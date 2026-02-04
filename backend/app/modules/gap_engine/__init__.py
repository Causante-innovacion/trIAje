# Gap Engine Module
"""
Detecta brechas regulatorias.

Funciones:
- requirement_extraction
- user_state_mapping
- compliance_status_eval
- gap_classification

Output: gap = satisfied | missing | conditional | blocked
"""

from .service import GapEngine
from .evaluator import GapStatus, Gap, GapAnalysisResult

__all__ = [
    "GapEngine",
    "GapStatus",
    "Gap",
    "GapAnalysisResult",
]
