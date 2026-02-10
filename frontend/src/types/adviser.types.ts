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
    criticalTopics: CriticalTopic[]
    lawyerQuestions: LawyerQuestion[]
    requiredDocuments: RequiredDocument[]
    internalDecisions: InternalDecision[]
}
