import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Download, FileText, Calendar, ArrowLeft } from 'lucide-react'
import { ProjectEvaluation } from '../../types/evaluation.types'
import { useChatStore } from '../../stores/chatStore'
import { LoadingScreen } from './LoadingScreen'
import { TrafficLightCard } from './TrafficLightCard'
import { ProjectContextCard } from './ProjectContextCard'
import { LegalStatusTable } from './LegalStatusTable'
import { ViabilityConditionCard } from './ViabilityConditionCard'
import { ImplementationRoute } from './ImplementationRoute'
import { AlternativesSection } from './AlternativesSection'
import { exportEvaluationToDocx } from './evaluationExport'
import clsx from 'clsx'

export function ProjectEvaluationPage() {
    const navigate = useNavigate()
    const location = useLocation()
    const [isLoading, setIsLoading] = useState(true)
    const [evaluationData, setEvaluationData] = useState<ProjectEvaluation | null>(null)
    const [isScrolled, setIsScrolled] = useState(false)
    const [isExporting, setIsExporting] = useState(false)

    const handleExport = async () => {
        if (!evaluationData || isExporting) return
        setIsExporting(true)
        try {
            await exportEvaluationToDocx(evaluationData)
        } catch (err) {
            console.error('Error al exportar evaluación:', err)
        } finally {
            setIsExporting(false)
        }
    }

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 20)
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    useEffect(() => {
        const state = location.state as { evaluationData?: ProjectEvaluation; skipAnimation?: boolean } | null
        const stateData = state?.evaluationData

        if (stateData) {
            if (state?.skipAnimation) {
                setEvaluationData(stateData)
                setIsLoading(false)
                return
            }
            const timer = setTimeout(() => {
                setEvaluationData(stateData)
                setIsLoading(false)
            }, 2000)
            return () => clearTimeout(timer)
        }

        // Fallback to cached data from chat store (user navigated back from chat)
        const cached = useChatStore.getState().lastEvaluationData
        if (cached) {
            setEvaluationData(cached)
            setIsLoading(false)
            return
        }

        setIsLoading(false)
    }, [location.state])

    if (isLoading) {
        return <LoadingScreen />
    }

    if (!evaluationData) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center animate-slide-up">
                    <div className="w-16 h-16 rounded-2xl bg-cream flex items-center justify-center mx-auto mb-4">
                        <FileText className="w-8 h-8 text-gold" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">No se pudo cargar la evaluacion</h3>
                    <p className="text-sm text-gray-500 mb-6 max-w-xs">
                        No encontramos datos de evaluacion. Intenta realizar una nueva consulta.
                    </p>
                    <button
                        onClick={() => navigate('/')}
                        className="btn-action-primary"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Volver al inicio
                    </button>
                </div>
            </div>
        )
    }

    const hasYellowStatus = evaluationData.organizations.some(org => org.status === 'yellow')

    const criticalViabilityConditions = evaluationData.viabilityConditions.filter(
        condition => condition.severity === 'CRÍTICA' || condition.severity === 'ALTA'
    )

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header with scroll detection */}
            <header className={clsx(
                'sticky top-0 z-50 transition-all duration-300',
                isScrolled
                    ? 'bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm'
                    : 'bg-white border-b border-transparent'
            )}>
                <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate('/chat')}
                            className="flex items-center gap-1.5 text-sm font-semibold text-gray-400 hover:text-gray-700 transition-colors group"
                        >
                            <ArrowLeft className="w-4 h-4 transition-transform duration-200 group-hover:-translate-x-0.5" />
                            <span className="hidden sm:inline">Chat</span>
                        </button>
                        <div className="w-px h-5 bg-gray-200" />
                        <div className="flex items-center gap-3">
                            <div>
                                <h1 className="font-bold text-lg text-gray-900">{evaluationData.projectTitle}</h1>
                                <p className="text-xs text-gray-500">
                                    ID: {evaluationData.projectId} | Lider: {evaluationData.projectLeader}
                                </p>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={handleExport}
                        disabled={isExporting}
                        className="btn-action-primary text-sm disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                        <Download className="w-4 h-4" />
                        {isExporting ? 'Generando...' : 'Descargar Evaluación'}
                    </button>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 py-10 space-y-10">
                {/* Title */}
                <div className="animate-slide-up">
                    <h2 className="font-heading text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                        Evaluacion Legal de tu Proyecto
                    </h2>
                    <p className="text-gray-500">
                        ID: {evaluationData.projectId} | Lider: {evaluationData.projectLeader}
                    </p>
                </div>

                {/* Traffic Light Status */}
                <section className="animate-slide-up stagger-1">
                    <div className="grid grid-cols-1 gap-4">
                        {evaluationData.organizations.map(org => (
                            <TrafficLightCard key={org.id} organization={org} />
                        ))}
                    </div>
                </section>

                {/* Project Context */}
                <section className="animate-slide-up stagger-2">
                    <ProjectContextCard items={evaluationData.projectContext} />
                </section>

                {/* Legal Status Summary */}
                <section className="animate-slide-up stagger-3">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Estado Legal Actual</h3>
                    <LegalStatusTable entities={evaluationData.legalEntities} />
                </section>

                {/* Action Steps (conditional - only if yellow status) */}
                {hasYellowStatus && evaluationData.actionSteps && (
                    <section className="bg-yellow-50 rounded-2xl p-8 border-2 border-yellow-300 animate-slide-up">
                        <h3 className="text-xl font-bold text-gray-900 mb-6">
                            Pasos a Seguir
                        </h3>
                        <ul className="space-y-3">
                            {evaluationData.actionSteps.map((step, index) => (
                                <li key={index} className="flex items-start gap-3">
                                    <span className="w-7 h-7 rounded-full bg-gold text-white flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                                        {index + 1}
                                    </span>
                                    <span className="text-gray-800 font-medium leading-relaxed">{step}</span>
                                </li>
                            ))}
                        </ul>
                    </section>
                )}

                {/* Viability Conditions (only CRITICA and ALTA) */}
                {criticalViabilityConditions.length > 0 && (
                    <section className="animate-slide-up">
                        <h3 className="text-xl font-bold text-gray-900 mb-4">
                            Condiciones de Viabilidad (Plan de Accion)
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {criticalViabilityConditions.map(condition => (
                                <ViabilityConditionCard key={condition.id} condition={condition} />
                            ))}
                        </div>
                    </section>
                )}

                {/* Implementation Route */}
                <section className="animate-slide-up">
                    <ImplementationRoute
                        phases={evaluationData.implementationPhases}
                        actions={evaluationData.implementationActions}
                        disclaimer={evaluationData.disclaimer}
                    />
                </section>

                {/* Alternatives */}
                {evaluationData.alternatives.length > 0 && (
                    <section className="animate-slide-up">
                        <AlternativesSection alternatives={evaluationData.alternatives} />
                    </section>
                )}

                {/* Action Buttons */}
                <section className="flex justify-center pb-10 animate-fade-in">
                    <button
                        className="btn-action-primary"
                        onClick={() => navigate('/legal-adviser')}
                    >
                        <Calendar className="w-5 h-5" />
                        Reunión con asesor
                    </button>
                </section>
            </main>
        </div>
    )
}
