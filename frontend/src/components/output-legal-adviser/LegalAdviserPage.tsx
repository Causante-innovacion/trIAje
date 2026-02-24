import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, Download, FileText } from 'lucide-react'
import { LegalAdviserPackage } from '../../types/adviser.types'
import { useChatStore } from '../../stores/chatStore'
import { LoadingScreen } from '../output-evaluation/LoadingScreen'
import { OrganizationProfileCard } from './OrganizationProfileCard'
import { CriticalTopicsSection } from './CriticalTopicsSection'
import { LawyerQuestionsSection } from './LawyerQuestionsSection'
import { RequiredDocumentsChecklist } from './RequiredDocumentsChecklist'
import { InternalDecisionsChecklist } from './InternalDecisionsChecklist'
import { exportAdviserToDocx } from './adviserExport'
import { mockAdviserData } from './mockAdviserData'
import clsx from 'clsx'

export function LegalAdviserPage() {
    const navigate = useNavigate()
    const location = useLocation()
    const locationState = location.state as { adviserData?: LegalAdviserPackage; skipAnimation?: boolean } | null

    const [isLoading, setIsLoading] = useState(
        () => !!(locationState?.adviserData && !locationState?.skipAnimation)
    )
    const [adviserData, setAdviserData] = useState<LegalAdviserPackage | null>(null)
    const [isScrolled, setIsScrolled] = useState(false)
    const [isExporting, setIsExporting] = useState(false)

    const handleExport = async () => {
        if (!adviserData || isExporting) return
        setIsExporting(true)
        try {
            await exportAdviserToDocx(adviserData)
        } catch (err) {
            console.error('Error al exportar paquete asesor:', err)
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
        const stateData = locationState?.adviserData

        if (stateData) {
            if (locationState?.skipAnimation) {
                setAdviserData(stateData)
                setIsLoading(false)
                return
            }
            const timer = setTimeout(() => {
                setAdviserData(stateData)
                setIsLoading(false)
            }, 2000)
            return () => clearTimeout(timer)
        }

        // Fallback to cached data from chat store
        const cached = useChatStore.getState().lastAdviserData
        if (cached) {
            setAdviserData(cached)
            setIsLoading(false)
            return
        }

        // Development fallback: mock data
        const timer = setTimeout(() => {
            setAdviserData(mockAdviserData)
            setIsLoading(false)
        }, 2000)
        return () => clearTimeout(timer)
    }, [location.state])

    if (isLoading) {
        return <LoadingScreen />
    }

    if (!adviserData) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center animate-slide-up">
                    <div className="w-16 h-16 rounded-2xl bg-cream flex items-center justify-center mx-auto mb-4">
                        <FileText className="w-8 h-8 text-gold" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">No se pudo cargar el paquete</h3>
                    <p className="text-sm text-gray-500 mb-6 max-w-xs">
                        No encontramos datos del asesor legal. Intenta realizar una nueva consulta.
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

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Sticky header */}
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
                        <h1 className="font-bold text-base text-gray-900">
                            {adviserData.organizationProfile.entityName}
                        </h1>
                    </div>

                    <button
                        onClick={handleExport}
                        disabled={isExporting}
                        className="btn-action-primary text-sm disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                        <Download className="w-4 h-4" />
                        {isExporting ? 'Generando...' : 'Descargar paquete'}
                    </button>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 py-10 space-y-10">
                {/* Title */}
                <div className="text-center animate-slide-up">
                    <div className="flex items-center justify-center gap-3 mb-3">
                        <div className="bg-gold w-6 h-6 transform rotate-45 rounded-sm" />
                        <h2 className="font-heading text-3xl md:text-4xl font-bold text-gray-900">{adviserData.pageTitle}</h2>
                    </div>
                    <p className="text-sm text-gray-500 uppercase tracking-wide font-medium">
                        {adviserData.pageSubtitle}
                    </p>
                </div>

                {/* Organization Profile */}
                <section className="animate-slide-up stagger-1">
                    <OrganizationProfileCard
                        profile={adviserData.organizationProfile}
                        fundingDescription={adviserData.fundingDescription}
                        legalStatusCards={adviserData.legalStatusCards}
                    />
                </section>

                {/* Critical Topics */}
                <section className="animate-slide-up stagger-2">
                    <CriticalTopicsSection
                        topics={adviserData.criticalTopics}
                        fundingRange={adviserData.fundingCritical}
                        incomeSources={adviserData.incomeSources}
                    />
                </section>

                {/* Lawyer Questions */}
                <section className="animate-slide-up stagger-3">
                    <LawyerQuestionsSection questions={adviserData.lawyerQuestions} />
                </section>

                {/* Two Column Layout for Checklists */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-slide-up stagger-4">
                    <RequiredDocumentsChecklist documents={adviserData.requiredDocuments} />
                    <InternalDecisionsChecklist decisions={adviserData.internalDecisions} />
                </div>
            </main>
        </div>
    )
}
