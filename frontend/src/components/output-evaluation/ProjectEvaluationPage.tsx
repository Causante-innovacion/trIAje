import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Download, FileText, Calendar, ArrowLeft, Loader2 } from 'lucide-react'
import { ProjectEvaluation } from '../../types/evaluation.types'
import { useChatStore } from '../../stores/chatStore'
import { advisorPrepApi } from '../../shared/services/api'
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
    const locationState = location.state as { evaluationData?: ProjectEvaluation; skipAnimation?: boolean } | null

    // Only show the loading animation when fresh evaluation data is arriving
    // without the skipAnimation flag. All other paths (back-navigation, inline
    // link from chat, cached store) skip the overlay entirely.
    const [isLoading, setIsLoading] = useState(
        () => !!(locationState?.evaluationData && !locationState?.skipAnimation)
    )
    const [evaluationData, setEvaluationData] = useState<ProjectEvaluation | null>(null)
    const [isScrolled, setIsScrolled] = useState(false)
    const [isExporting, setIsExporting] = useState(false)
    const [isGeneratingAdviser, setIsGeneratingAdviser] = useState(false)
    const [adviserError, setAdviserError] = useState<string | null>(null)

    const handleGoToAdviser = async () => {
        setIsGeneratingAdviser(true)
        setAdviserError(null)
        try {
            const { messages, conversationId } = useChatStore.getState()
            const conversation = messages
                .filter(m =>
                    (m.sender === 'user' && m.contentType === 'text' && m.content?.trim()) ||
                    (m.sender === 'justo' &&
                        (m.contentType === 'semaphore_response' || m.contentType === 'text') &&
                        m.content?.trim() && !m.isStreaming)
                )
                .map(m => ({ role: m.sender === 'user' ? 'user' : 'assistant', content: m.content }))
            const response = await advisorPrepApi.prepareFromChat(conversation, conversationId ?? undefined)
            useChatStore.getState().setLastAdviserData(response.data)
            navigate('/legal-adviser', { state: { adviserData: response.data, skipAnimation: true } })
        } catch (err) {
            console.error('[ProjectEvaluation] adviser error:', err)
            setAdviserError('No se pudo generar el paquete. Intenta de nuevo.')
        } finally {
            setIsGeneratingAdviser(false)
        }
    }

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

                {/* Adviser CTA */}
                <section className="animate-fade-in pb-10">
                    <div className="rounded-2xl overflow-hidden border border-gray-200 shadow-sm">
                        <div className="bg-gray-900 px-6 py-5 flex items-center gap-4">
                            <div className="w-10 h-10 rounded-xl bg-gold/20 flex items-center justify-center flex-shrink-0">
                                <Calendar className="w-5 h-5 text-gold" />
                            </div>
                            <div>
                                <p className="font-bold text-white text-base leading-snug">Preparar reunión con asesor legal</p>
                                <p className="text-xs text-gray-400 mt-0.5">Preguntas clave, documentos requeridos y decisiones previas</p>
                            </div>
                        </div>
                        <div className="bg-white px-6 py-4 flex items-center justify-between gap-4">
                            <p className="text-sm text-gray-500 leading-relaxed">
                                Recomendado cuando hay condiciones críticas o brechas legales sin resolver.
                            </p>
                            <button
                                onClick={handleGoToAdviser}
                                disabled={isGeneratingAdviser}
                                className="btn-action-primary whitespace-nowrap flex-shrink-0 disabled:opacity-70 disabled:cursor-wait"
                            >
                                {isGeneratingAdviser
                                    ? <><Loader2 className="w-4 h-4 animate-spin" />Preparando...</>
                                    : <><Calendar className="w-4 h-4" />Ir al paquete</>}
                            </button>
                        </div>
                        {adviserError && (
                            <p className="text-xs text-red-600 font-medium px-6 pb-4">{adviserError}</p>
                        )}
                    </div>
                </section>
            </main>
        </div>
    )
}
