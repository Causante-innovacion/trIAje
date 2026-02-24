export type TrafficLightStatus = 'green' | 'yellow' | 'red'

export type PriorityLevel = 'BAJA' | 'ALTA' | 'CRÍTICA'

export interface OrganizationStatus {
    id: string
    name: string
    status: TrafficLightStatus
    message: string
}

export interface ProjectContextItem {
    icon: string
    label: string
    value: string
}

export interface LegalEntity {
    entity: string
    description: string
    status: TrafficLightStatus
    statusText: string
    priority: PriorityLevel
    action: string
}

export interface ViabilityCondition {
    id: string
    title: string
    icon: string
    severity: 'CRÍTICA' | 'ALTA' | 'MEDIA' | 'BAJA'
    time: string
    cost: string
    reason: string
    requirements: string[]
    organizationIds: string[] // Which organizations have this condition
}

export interface ImplementationPhase {
    id: number
    name: string
    status: 'completed' | 'current' | 'upcoming'
}

export interface ActionItem {
    text: string
    completed: boolean
}

export interface Alternative {
    title: string
    description: string
}

export interface ProjectEvaluation {
    projectId: string
    projectTitle: string
    projectLeader: string
    organizations: OrganizationStatus[]
    projectContext: ProjectContextItem[]
    legalEntities: LegalEntity[]
    actionSteps?: string[] // Only shown if any org has yellow status
    viabilityConditions: ViabilityCondition[]
    implementationPhases: ImplementationPhase[]
    implementationActions: ActionItem[]
    alternatives: Alternative[]
    disclaimer: string
}


// =============================================================================
// MAPEO: EvaluationResponse (backend) → ProjectEvaluation (display)
// =============================================================================

/** Respuesta cruda del backend /evaluation/intake */
export interface BackendEvaluationResponse {
    viability: string
    viability_explanation: string
    traffic_light: TrafficLightStatus
    organizations: Array<{
        organization_id: string
        organization_name: string
        role: string
        requirements_fulfilled: number
        requirements_partial: number
        requirements_not_fulfilled: number
        gaps: Array<{
            id: string
            organization_id?: string
            organization_name?: string
            severity: 'critical' | 'high' | 'medium' | 'low'
            intention: string
            description: string
            impact: string
            recommendation: string
            source_fields?: string[]
        }>
        detected_intentions: string[]
        risk_level: string
    }>
    shared_gaps: Array<{
        id: string
        severity: 'critical' | 'high' | 'medium' | 'low'
        intention: string
        description: string
        impact: string
        recommendation: string
    }>
    risk_summary: {
        overall_level: string
        derivation_color: string
        requires_professional_advice: boolean
        professional_advice_reason?: string
        risk_factors: string[]
    }
    total_requirements: number
    total_gaps: number
    critical_gaps: number
    project_intentions: string[]
    next_steps: string[]
    alternatives: string[]
    path_to_viability?: string
    evidence_sources: Array<{
        title: string
        authority_level: number
        url?: string
        relevance: string
    }>
    confidence_level: string
    assumptions: string[]
    limitations: string[]
    disclaimers: string[]
}

const SEVERITY_TO_PRIORITY: Record<string, PriorityLevel> = {
    critical: 'CRÍTICA',
    high: 'ALTA',
    medium: 'BAJA',
    low: 'BAJA',
}

const SEVERITY_TO_STATUS: Record<string, TrafficLightStatus> = {
    critical: 'red',
    high: 'yellow',
    medium: 'green',
    low: 'green',
}

const SEVERITY_TO_STATUS_TEXT: Record<string, string> = {
    critical: 'PENDIENTE',
    high: 'INEXISTENTE',
    medium: 'PARCIAL',
    low: 'REGULAR',
}

const INTENTION_LABELS: Record<string, string> = {
    formalization: 'Formalización',
    taxation: 'Tributación (SUNAT)',
    international_cooperation: 'APCI',
    hiring: 'Contratos Laborales',
    intellectual_property: 'Propiedad Intelectual',
    data_protection: 'Privacidad de Datos',
    governance: 'Gobernanza',
    accounting: 'Contabilidad',
    donations: 'Donaciones',
    risk_management: 'Gestión de Riesgos',
    meetings_documentation: 'Documentación',
    grey_cases: 'Casos Grises',
    viability_evaluation: 'Viabilidad',
    compliance_route: 'Cumplimiento',
}

const INTENTION_DESCRIPTIONS: Record<string, string> = {
    formalization: 'Constitución y registros públicos',
    taxation: 'Identificación tributaria',
    international_cooperation: 'Registro de cooperación técnica',
    hiring: 'Modalidades de contratación',
    intellectual_property: 'Protección de activos intangibles',
    data_protection: 'Protección de datos personales',
    governance: 'Órganos de gobierno y representación',
    accounting: 'Registros contables y financieros',
    donations: 'Registro como receptora de donaciones',
}

const INTENTION_ICONS: Record<string, string> = {
    formalization: 'file',
    taxation: 'file',
    international_cooperation: 'scale',
    hiring: 'users',
    intellectual_property: 'lightbulb',
    data_protection: 'lightbulb',
    governance: 'users',
    accounting: 'file',
}

/**
 * Mapea la respuesta del backend (EvaluationResponse) al tipo de display (ProjectEvaluation).
 */
export function mapBackendToProjectEvaluation(
    response: BackendEvaluationResponse,
    orgNames: Array<{ id: string; name: string; role: string }>,
): ProjectEvaluation {
    // Status label from per-org risk_level
    const riskToStatus: Record<string, TrafficLightStatus> = {
        critical: 'red', high: 'yellow', medium: 'green', low: 'green',
    }

    // Organizations semaphore - per org using their own risk_level
    const organizations: OrganizationStatus[] = response.organizations.map(org => {
        const status: TrafficLightStatus = riskToStatus[org.risk_level] ?? 'yellow'
        const criticalCount = org.gaps.filter(g => g.severity === 'critical').length
        const highCount = org.gaps.filter(g => g.severity === 'high').length
        const mediumCount = org.gaps.filter(g => g.severity === 'medium').length
        const lowCount = org.gaps.filter(g => g.severity === 'low').length
        let message: string
        if (status === 'red') {
            if (criticalCount > 0) {
                message = `${criticalCount} brecha${criticalCount > 1 ? 's' : ''} crítica${criticalCount > 1 ? 's' : ''} detectada${criticalCount > 1 ? 's' : ''} que requieren atención inmediata.`
            } else if (highCount > 0) {
                message = `${highCount} brecha${highCount > 1 ? 's' : ''} de alto impacto que requieren atención urgente.`
            } else {
                message = 'Situación crítica que requiere revisión profesional inmediata.'
            }
        } else if (status === 'yellow') {
            if (highCount > 0) {
                message = `${highCount} brecha${highCount > 1 ? 's' : ''} con impacto alto identificada${highCount > 1 ? 's' : ''}. Se requieren ajustes.`
            } else if (mediumCount > 0) {
                message = `${mediumCount} aspecto${mediumCount > 1 ? 's' : ''} de impacto medio detectado${mediumCount > 1 ? 's' : ''}. Se recomienda revisión profesional.`
            } else {
                message = 'Existen aspectos que requieren ajustes antes de continuar.'
            }
        } else {
            if (org.gaps.length === 0) {
                message = 'Cumplimiento satisfactorio en las áreas evaluadas.'
            } else if (lowCount > 0) {
                message = `${lowCount} observación${lowCount > 1 ? 'es' : ''} menor${lowCount > 1 ? 'es' : ''} sin impacto crítico en la viabilidad.`
            } else {
                message = 'Estado legal en orden. Sin brechas significativas detectadas.'
            }
        }
        return { id: org.organization_id, name: org.organization_name, status, message }
    })

    // Legal entities: derive from all gaps + fulfilled intentions
    const legalEntities: LegalEntity[] = []
    const seenIntentions = new Set<string>()

    for (const org of response.organizations) {
        for (const gap of org.gaps) {
            if (seenIntentions.has(gap.intention)) continue
            seenIntentions.add(gap.intention)

            legalEntities.push({
                entity: INTENTION_LABELS[gap.intention] || gap.intention,
                description: INTENTION_DESCRIPTIONS[gap.intention] || gap.description,
                status: SEVERITY_TO_STATUS[gap.severity] || 'yellow',
                statusText: SEVERITY_TO_STATUS_TEXT[gap.severity] || 'PENDIENTE',
                priority: SEVERITY_TO_PRIORITY[gap.severity] || 'BAJA',
                action: gap.recommendation,
            })
        }
    }

    // Add fulfilled intentions as green entries
    for (const org of response.organizations) {
        for (const intention of org.detected_intentions) {
            if (seenIntentions.has(intention)) continue
            seenIntentions.add(intention)
            legalEntities.push({
                entity: INTENTION_LABELS[intention] || intention,
                description: INTENTION_DESCRIPTIONS[intention] || '',
                status: 'green',
                statusText: 'REGULAR',
                priority: 'BAJA',
                action: 'Sin acciones pendientes.',
            })
        }
    }

    // Sort: critical first, then high, then rest
    const priorityOrder = { 'CRÍTICA': 0, 'ALTA': 1, 'BAJA': 2 }
    legalEntities.sort((a, b) =>
        (priorityOrder[a.priority] ?? 3) - (priorityOrder[b.priority] ?? 3)
    )

    // Viability conditions: only CRITICAL and HIGH gaps
    const viabilityConditions: ViabilityCondition[] = []
    for (const org of response.organizations) {
        for (const gap of org.gaps) {
            if (gap.severity !== 'critical' && gap.severity !== 'high') continue

            viabilityConditions.push({
                id: gap.id,
                title: gap.recommendation.split('.')[0],
                icon: INTENTION_ICONS[gap.intention] || 'alert',
                severity: gap.severity === 'critical' ? 'CRÍTICA' : 'ALTA',
                time: 'Por determinar',
                cost: 'Por determinar',
                reason: gap.impact,
                requirements: [],
                organizationIds: [org.organization_id],
            })
        }
    }

    // Action steps (only if yellow/red)
    const actionSteps = response.next_steps.length > 0 ? response.next_steps : undefined

    // Implementation phases (rudimentary)
    const implementationPhases: ImplementationPhase[] = [
        { id: 1, name: 'Saneamiento', status: response.critical_gaps > 0 ? 'current' : 'completed' },
        { id: 2, name: 'Cumplimiento', status: response.critical_gaps > 0 ? 'upcoming' : 'current' },
        { id: 3, name: 'Ejecución', status: 'upcoming' },
    ]

    // Implementation actions from next_steps
    const implementationActions: ActionItem[] = response.next_steps.map(step => ({
        text: step.replace('[URGENTE] ', ''),
        completed: false,
    }))

    // Alternatives
    const alternatives: Alternative[] = response.alternatives.map(alt => ({
        title: alt.split(':')[0] || alt,
        description: alt.includes(':') ? alt.split(':').slice(1).join(':').trim() : alt,
    }))

    // Project context items derived from response
    const projectContext: ProjectContextItem[] = [
        {
            icon: 'users',
            label: 'Organizaciones',
            value: `${response.organizations.length} evaluada${response.organizations.length > 1 ? 's' : ''}`,
        },
        {
            icon: 'alert',
            label: 'Brechas totales',
            value: response.total_gaps > 0 ? `${response.total_gaps} identificada${response.total_gaps > 1 ? 's' : ''}` : 'Sin brechas',
        },
        {
            icon: 'target',
            label: 'Nivel de riesgo',
            value: ({
                critical: 'Crítico',
                high: 'Alto',
                medium: 'Medio',
                low: 'Bajo',
            })[response.risk_summary.overall_level] ?? response.risk_summary.overall_level,
        },
        ...response.project_intentions.slice(0, 3).map(intention => ({
            icon: INTENTION_ICONS[intention] ?? 'file',
            label: 'Área legal',
            value: INTENTION_LABELS[intention] ?? intention,
        })),
    ]

    return {
        projectId: orgNames[0]?.name || 'proyecto',
        projectTitle: 'Ruta de evaluación de proyecto',
        projectLeader: orgNames[0]?.name || '',
        organizations,
        projectContext,
        legalEntities,
        actionSteps,
        viabilityConditions,
        implementationPhases,
        implementationActions,
        alternatives,
        disclaimer: response.disclaimers.join(' '),
    }
}
