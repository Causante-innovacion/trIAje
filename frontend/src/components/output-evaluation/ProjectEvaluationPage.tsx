import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Download, FileText, Calendar } from 'lucide-react'
import { ProjectEvaluation } from '../../types/evaluation.types'
import { LoadingScreen } from './LoadingScreen'
import { TrafficLightCard } from './TrafficLightCard'
import { ProjectContextCard } from './ProjectContextCard'
import { LegalStatusTable } from './LegalStatusTable'
import { ViabilityConditionCard } from './ViabilityConditionCard'
import { ImplementationRoute } from './ImplementationRoute'
import { AlternativesSection } from './AlternativesSection'

export function ProjectEvaluationPage() {
    const navigate = useNavigate()
    const location = useLocation()
    const [isLoading, setIsLoading] = useState(true)
    const [evaluationData, setEvaluationData] = useState<ProjectEvaluation | null>(null)

    useEffect(() => {
        const stateData = (location.state as { evaluationData?: ProjectEvaluation })?.evaluationData

        if (stateData) {
            // Brief loading screen for UX, then show real data
            const timer = setTimeout(() => {
                setEvaluationData(stateData)
                setIsLoading(false)
            }, 2000)
            return () => clearTimeout(timer)
        }

        // No data passed - show error
        setIsLoading(false)
    }, [location.state])

    if (isLoading) {
        return <LoadingScreen />
    }

    if (!evaluationData) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <p className="text-gray-600">No se pudo cargar la evaluación.</p>
                    <button
                        onClick={() => navigate('/chat')}
                        className="mt-4 px-6 py-2 bg-yellow-400 text-white rounded-full hover:bg-yellow-500"
                    >
                        Volver al inicio
                    </button>
                </div>
            </div>
        )
    }

    // Check if any organization has yellow status to show action steps
    const hasYellowStatus = evaluationData.organizations.some(org => org.status === 'yellow')

    // Filter viability conditions to only show CRÍTICA and ALTA
    const criticalViabilityConditions = evaluationData.viabilityConditions.filter(
        condition => condition.severity === 'CRÍTICA' || condition.severity === 'ALTA'
    )

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
                <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="bg-yellow-400 w-5 h-5 transform rotate-45 rounded-sm" />
                        <div>
                            <h1 className="font-bold text-lg text-gray-900">{evaluationData.projectTitle}</h1>
                            <p className="text-xs text-gray-500">
                                ID: {evaluationData.projectId} | Líder: {evaluationData.projectLeader}
                            </p>
                        </div>
                    </div>

                    <button className="flex items-center gap-2 px-4 py-2 bg-yellow-400 text-white rounded-lg hover:bg-yellow-500 transition-colors">
                        <Download className="w-4 h-4" />
                        <span className="font-semibold text-sm">Descargar PDF</span>
                    </button>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
                {/* Title */}
                <div>
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">
                        Evaluación Legal de tu Proyecto
                    </h2>
                    <p className="text-gray-600">
                        ID: {evaluationData.projectId} | Líder: {evaluationData.projectLeader}
                    </p>
                </div>

                {/* Traffic Light Status */}
                <section>
                    <div className="grid grid-cols-1 gap-4">
                        {evaluationData.organizations.map(org => (
                            <TrafficLightCard key={org.id} organization={org} />
                        ))}
                    </div>
                </section>

                {/* Project Context */}
                <section>
                    <ProjectContextCard items={evaluationData.projectContext} />
                </section>

                {/* Legal Status Summary */}
                <section>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Estado Legal Actual</h3>
                    <LegalStatusTable entities={evaluationData.legalEntities} />
                </section>

                {/* Action Steps (conditional - only if yellow status) */}
                {hasYellowStatus && evaluationData.actionSteps && (
                    <section className="bg-yellow-50 rounded-xl p-6 border-2 border-yellow-400">
                        <h3 className="text-xl font-bold text-gray-900 mb-4">
                            Pasos a Seguir
                        </h3>
                        <ul className="space-y-2">
                            {evaluationData.actionSteps.map((step, index) => (
                                <li key={index} className="flex items-start gap-3">
                                    <span className="w-6 h-6 rounded-full bg-yellow-400 text-white flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                                        {index + 1}
                                    </span>
                                    <span className="text-gray-900 font-semibold">{step}</span>
                                </li>
                            ))}
                        </ul>
                    </section>
                )}

                {/* Viability Conditions (only CRÍTICA and ALTA) */}
                {criticalViabilityConditions.length > 0 && (
                    <section>
                        <h3 className="text-xl font-bold text-gray-900 mb-4">
                            Condiciones de Viabilidad (Plan de Acción)
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {criticalViabilityConditions.map(condition => (
                                <ViabilityConditionCard key={condition.id} condition={condition} />
                            ))}
                        </div>
                    </section>
                )}

                {/* Implementation Route */}
                <section>
                    <ImplementationRoute
                        phases={evaluationData.implementationPhases}
                        actions={evaluationData.implementationActions}
                        disclaimer={evaluationData.disclaimer}
                    />
                </section>

                {/* Alternatives */}
                {evaluationData.alternatives.length > 0 && (
                    <section>
                        <AlternativesSection alternatives={evaluationData.alternatives} />
                    </section>
                )}

                {/* Action Buttons */}
                <section className="flex gap-4 justify-center pb-8">
                    <button className="flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-900 text-gray-900 rounded-lg hover:bg-gray-50 transition-colors">
                        <FileText className="w-5 h-5" />
                        <span className="font-semibold">Ver ruta completa</span>
                    </button>
                    <button className="flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors">
                        <Calendar className="w-5 h-5" />
                        <span className="font-semibold">Reunión con asesor</span>
                    </button>
                </section>
            </main>
        </div>
    )
}
