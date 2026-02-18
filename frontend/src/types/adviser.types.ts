export type LegalStatus = 'green' | 'yellow' | 'red'
export type FundingType = 'nacional' | 'extranjero'
export type Stage = 'prototipo' | 'piloto' | 'escalamiento' | 'unknown'

export interface OrganizationProfile {
    entityName: string
    legalStatus: LegalStatus
    stage: Stage
    fundingTypes: FundingType[]
}

export interface LegalStatusCard {
    id: string
    label: string
    status: LegalStatus
}

export interface FundingRange {
    min: string
    max: string
    description: string
}

export interface CriticalTopic {
    id: string
    title: string
    description: string
    priority: 'URGENTE'
    actionLink?: string
    actionLabel?: string
}

export interface LawyerQuestion {
    id: string
    number: number
    question: string
}

export interface RequiredDocument {
    id: string
    title: string
    completed: boolean
}

export interface InternalDecision {
    id: string
    scenario: string
    options: {
        id: string
        label: string
    }[]
}

export interface LegalAdviserPackage {
    pageTitle: string
    pageSubtitle: string
    organizationProfile: OrganizationProfile
    legalStatusCards: LegalStatusCard[]
    fundingCritical: FundingRange
    fundingDescription: string
    incomeSources?: string[]
    criticalTopics: CriticalTopic[]
    lawyerQuestions: LawyerQuestion[]
    requiredDocuments: RequiredDocument[]
    internalDecisions: InternalDecision[]
}


// =============================================================================
// MAPEO: BackendLegalAdviserResponse → LegalAdviserPackage (display)
// =============================================================================

/** Respuesta cruda del backend POST /api/v1/legal-adviser/intake */
export interface BackendLegalAdviserResponse {
    page_title: string
    page_subtitle: string
    organization_profile: {
        entity_name: string
        legal_status: string
        stage: string
        funding_types: string[]
    }
    legal_status_cards: Array<{
        id: string
        label: string
        status: string
    }>
    funding_critical: {
        min: string
        max: string
        description: string
    }
    funding_description: string
    income_sources: string[]
    critical_topics: Array<{
        id: string
        title: string
        description: string
        priority: string
        action_link?: string | null
        action_label?: string | null
    }>
    lawyer_questions: Array<{
        id: string
        number: number
        question: string
    }>
    required_documents: Array<{
        id: string
        title: string
        completed: boolean
    }>
    internal_decisions: Array<{
        id: string
        scenario: string
        options: Array<{
            id: string
            label: string
        }>
    }>
}

/**
 * Mapea la respuesta del backend al tipo de display LegalAdviserPackage.
 */
export function mapBackendToLegalAdviserPackage(
    response: BackendLegalAdviserResponse,
): LegalAdviserPackage {
    return {
        pageTitle: response.page_title,
        pageSubtitle: response.page_subtitle,
        organizationProfile: {
            entityName: response.organization_profile.entity_name,
            legalStatus: response.organization_profile.legal_status as LegalStatus,
            stage: response.organization_profile.stage as Stage,
            fundingTypes: response.organization_profile.funding_types as FundingType[],
        },
        legalStatusCards: response.legal_status_cards.map(card => ({
            id: card.id,
            label: card.label,
            status: card.status as LegalStatus,
        })),
        fundingCritical: {
            min: response.funding_critical.min,
            max: response.funding_critical.max,
            description: response.funding_critical.description,
        },
        fundingDescription: response.funding_description,
        incomeSources: response.income_sources,
        criticalTopics: response.critical_topics.map(topic => ({
            id: topic.id,
            title: topic.title,
            description: topic.description,
            priority: 'URGENTE' as const,
            actionLink: topic.action_link ?? undefined,
            actionLabel: topic.action_label ?? undefined,
        })),
        lawyerQuestions: response.lawyer_questions.map(q => ({
            id: q.id,
            number: q.number,
            question: q.question,
        })),
        requiredDocuments: response.required_documents.map(doc => ({
            id: doc.id,
            title: doc.title,
            completed: doc.completed,
        })),
        internalDecisions: response.internal_decisions.map(decision => ({
            id: decision.id,
            scenario: decision.scenario,
            options: decision.options.map(opt => ({
                id: opt.id,
                label: opt.label,
            })),
        })),
    }
}
