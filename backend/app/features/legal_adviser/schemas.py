"""
Legal Adviser Feature - Schemas
Request/Response models para paquete de asesor legal.
"""

from pydantic import BaseModel, Field
from app.modules.intake.schemas import NormalizedProjectIntake


class LegalAdviserRequest(BaseModel):
    """Request para generar paquete de asesor legal"""
    intake: NormalizedProjectIntake


class OrganizationProfileResponse(BaseModel):
    entity_name: str
    legal_status: str  # green | yellow | red
    stage: str         # prototipo | piloto | escalamiento | unknown
    funding_types: list[str]  # nacional | extranjero


class LegalStatusCardResponse(BaseModel):
    id: str
    label: str
    status: str  # green | yellow | red


class FundingRangeResponse(BaseModel):
    min: str
    max: str
    description: str


class CriticalTopicResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: str = "URGENTE"
    action_link: str | None = None
    action_label: str | None = None


class LawyerQuestionResponse(BaseModel):
    id: str
    number: int
    question: str


class RequiredDocumentResponse(BaseModel):
    id: str
    title: str
    completed: bool = False


class InternalDecisionOptionResponse(BaseModel):
    id: str
    label: str


class InternalDecisionResponse(BaseModel):
    id: str
    scenario: str
    options: list[InternalDecisionOptionResponse]


class LegalAdviserResponse(BaseModel):
    """Response completo del paquete de asesor legal"""
    page_title: str
    page_subtitle: str
    organization_profile: OrganizationProfileResponse
    legal_status_cards: list[LegalStatusCardResponse]
    funding_critical: FundingRangeResponse
    funding_description: str
    income_sources: list[str] = Field(default_factory=list)
    critical_topics: list[CriticalTopicResponse] = Field(default_factory=list)
    lawyer_questions: list[LawyerQuestionResponse] = Field(default_factory=list)
    required_documents: list[RequiredDocumentResponse] = Field(default_factory=list)
    internal_decisions: list[InternalDecisionResponse] = Field(default_factory=list)
