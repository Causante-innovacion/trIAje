# Intake Module
"""
Responsabilidad: recolectar datos estructurados sin ambigüedad.

Funciones:
- render_question_set()
- enforce_selector_inputs()
- validate_required_fields()
- normalize_answers()

Entradas permitidas: boolean, enum, multi-select, range, role-selector, text (solo para Query)
Nunca acepta: null, no_se para campos críticos
"""

from .service import IntakeService, intake_service
from .questions import (
    get_question_set,
    get_legal_profile_blocks,
    get_tool_specific_block,
    get_question_by_id,
    get_all_question_ids,
    count_questions_by_tool,
    LEGAL_PROFILE_BLOCKS,
)
from .schemas import (
    # Enums
    InputType,
    ToolType,
    RiskLevel,
    DerivationColor,
    # Options
    ValidOptions,
    # Question definitions
    QuestionDefinition,
    QuestionBlock,
    QuestionSet,
    # Legal Profile (Ficha Legal Mínima)
    LegalProfile,
    IdentityData,
    FormalizationData,
    IncomeData,
    InternationalCooperationData,
    HumanResourcesData,
    AccountingData,
    GovernanceData,
    IntangiblesData,
    # Tool-specific data
    ToolSpecificData,
    EvaluationSpecificData,
    ComplianceSpecificData,
    QuerySpecificData,
    # Request/Response
    IntakeRequest,
    IntakeValidationResponse,
    NormalizedIntake,
    ValidationError,
    ValidationWarning,
    RiskSignal,
    RiskAssessment,
)

__all__ = [
    # Service
    "IntakeService",
    "intake_service",
    # Functions
    "get_question_set",
    "get_legal_profile_blocks",
    "get_tool_specific_block",
    "get_question_by_id",
    "get_all_question_ids",
    "count_questions_by_tool",
    "LEGAL_PROFILE_BLOCKS",
    # Enums
    "InputType",
    "ToolType",
    "RiskLevel",
    "DerivationColor",
    # Options
    "ValidOptions",
    # Question definitions
    "QuestionDefinition",
    "QuestionBlock",
    "QuestionSet",
    # Legal Profile
    "LegalProfile",
    "IdentityData",
    "FormalizationData",
    "IncomeData",
    "InternationalCooperationData",
    "HumanResourcesData",
    "AccountingData",
    "GovernanceData",
    "IntangiblesData",
    # Tool-specific data
    "ToolSpecificData",
    "EvaluationSpecificData",
    "ComplianceSpecificData",
    "QuerySpecificData",
    # Request/Response
    "IntakeRequest",
    "IntakeValidationResponse",
    "NormalizedIntake",
    "ValidationError",
    "ValidationWarning",
    "RiskSignal",
    "RiskAssessment",
]
