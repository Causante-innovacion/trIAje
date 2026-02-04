# Advisor Package Generator Module
"""
Se activa condicionalmente para generar paquete de preparación para asesor.

Funciones:
- case_structuring
- open_question_generation
- document_request_list
- legal_issue_index
- advisor_brief_format

Formatos: json, pdf-ready, doc-ready
"""

from .service import AdvisorPackageGenerator
from .structurer import AdvisorPackage, CaseStructure

__all__ = [
    "AdvisorPackageGenerator",
    "AdvisorPackage",
    "CaseStructure",
]
